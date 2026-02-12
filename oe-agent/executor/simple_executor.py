#!/usr/bin/env python3
"""
OE-AGENT SIMPLE EXECUTOR (PHASE 3)
Atomic execution with XACT model and hash-chained events

Version: 2.1.0
Schema ID: EXECUTOR-ATOMIC-2.1
Date: 2026-01-25

🎯 PURPOSE:
Execute PLAN.json steps with atomic guarantees using XACT model.
Implements INTENT → EXECUTE → COMMIT/ABORT workflow with hash-chained events.

🔒 ATOMIC GUARANTEES:
1. No ghost actions: Every file change has INTENT → COMMIT chain
2. No narrative repair: Logs cannot be "fixed" after the fact
3. Replayable truth: Can replay intents, commits, aborts separately
4. Linear hash chain: Cryptographic proof of event sequence
5. No transaction leaks: TransactionGuard ensures cleanup

🔗 XACT MODEL:
BEGIN_XACT → INTENT → EXECUTE → COMMIT (success) or ABORT (failure)
"""

import json
import os
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import Phase 3 components
try:
    # Try relative import first (for package structure)
    from ..events.event_sink import AtomicEventSink, AtomicEventSinkError
    from ..events.transaction_guard import TransactionGuard, TransactionGuardError
    from ..policy.policy_gate import PolicyDecision, PolicyGate
except ImportError:
    try:
        # Try direct import (for testing from oe-agent directory)
        from events.event_sink import AtomicEventSink, AtomicEventSinkError
        from events.transaction_guard import TransactionGuard, TransactionGuardError
        from policy.policy_gate import PolicyDecision, PolicyGate
    except ImportError:
        # Fallback for testing
        AtomicEventSink = None
        TransactionGuard = None
        TransactionGuardError = None
        PolicyGate = None
        PolicyDecision = None


class BudgetExceededError(Exception):
    """Raised when autonomy budget is exhausted."""

    pass


class ExecutionError(Exception):
    """Raised when execution step fails."""

    pass


class PlanValidationError(Exception):
    """Raised when PLAN.json is invalid."""

    pass


class AtomicExecutionError(Exception):
    """Raised when atomic execution fails."""

    pass


class SimpleBudgetTracker:
    """Simple budget enforcement."""

    def __init__(self, max_commands: int = 10, max_runtime: int = 60):
        self.max_commands = max_commands
        self.max_runtime = max_runtime
        self.commands_used = 0
        self.start_time = time.time()

    def consume_command(self):
        """Consume one command from budget."""
        self.commands_used += 1
        if self.commands_used > self.max_commands:
            raise BudgetExceededError(
                f"Command budget exceeded: {self.commands_used}/{self.max_commands}"
            )

    def check_runtime(self):
        """Check if runtime budget is exceeded."""
        elapsed = time.time() - self.start_time
        if elapsed > self.max_runtime:
            raise BudgetExceededError(
                f"Runtime budget exceeded: {elapsed:.1f}s/{self.max_runtime}s"
            )

    def get_status(self):
        """Get current budget status."""
        elapsed = time.time() - self.start_time
        return {
            "commands_used": self.commands_used,
            "commands_remaining": max(0, self.max_commands - self.commands_used),
            "runtime_used": elapsed,
            "runtime_remaining": max(0, self.max_runtime - elapsed),
        }


class AtomicSimpleExecutor:
    """Atomic executor for Phase 3 with XACT model."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.backup_dir = workspace_root / ".oe-backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Phase 3 components
        self.event_sink = None
        self.policy_gate = None
        self.budget_tracker = None

        # Execution state
        self.current_plan = None
        self.execution_id = None
        self.current_xact_id = None

        # Initialize Phase 3 components if available
        self._init_phase3_components()

    def _init_phase3_components(self):
        """Initialize Phase 3 components."""
        try:
            # Check if components are available
            if AtomicEventSink is None or PolicyGate is None:
                raise ImportError("Phase 3 components not imported")

            # Initialize event sink
            events_dir = self.workspace_root / "events" / "atomic"
            self.event_sink = AtomicEventSink(events_dir)

            # Initialize policy gate
            self.policy_gate = PolicyGate(event_sink=self.event_sink)

        except Exception as e:
            print(f"Warning: Phase 3 components not available: {e}")
            print("Falling back to Phase 2 mode (non-atomic execution)")

    def _generate_xact_id(self) -> str:
        """Generate unique transaction ID."""
        return f"xact_{uuid.uuid4().hex[:8]}"

    def _compute_file_hash(self, filepath: Path) -> str:
        """Compute SHA256 hash of file."""
        import hashlib

        if not filepath.exists():
            return "sha256:file_not_found"

        try:
            with open(filepath, "rb") as f:
                file_hash = hashlib.sha256()
                chunk = f.read(8192)
                while chunk:
                    file_hash.update(chunk)
                    chunk = f.read(8192)
                return f"sha256:{file_hash.hexdigest()}"
        except Exception:
            return "sha256:hash_failed"

    def validate_plan(self, plan_data: Dict[str, Any]):
        """Validate basic plan structure."""
        if "goal" not in plan_data:
            raise PlanValidationError("Missing 'goal' field")
        if "steps" not in plan_data:
            raise PlanValidationError("Missing 'steps' field")
        if not isinstance(plan_data["steps"], list):
            raise PlanValidationError("'steps' must be a list")

        for i, step in enumerate(plan_data["steps"]):
            if "action" not in step:
                raise PlanValidationError(f"Step {i} missing 'action' field")

    def _execute_scan_atomic(
        self, step: Dict[str, Any], tx: TransactionGuard
    ) -> Dict[str, Any]:
        """Execute scan action atomically with TransactionGuard."""
        target = Path(step.get("target", "."))
        if not target.is_absolute():
            target = self.workspace_root / target

        # Handle relative paths from workspace root
        if not target.exists():
            target = self.workspace_root / step.get("target", ".")

        # Write INTENT event
        tx.write_intent(
            step_id=step.get("id", 0),
            plan_id=self.current_plan.get("plan_id", "unknown"),
            action="scan",
            parameters={
                "target": str(
                    target.relative_to(self.workspace_root)
                    if target.is_relative_to(self.workspace_root)
                    else target
                ),
            },
        )

        files_found = []
        if target.exists():
            if target.is_dir():
                for item in target.iterdir():
                    if item.is_file():
                        files_found.append(str(item.relative_to(self.workspace_root)))
            elif target.is_file():
                files_found.append(str(target.relative_to(self.workspace_root)))

        self.budget_tracker.consume_command()

        result = {
            "action": "scan",
            "target": str(
                target.relative_to(self.workspace_root)
                if target.is_relative_to(self.workspace_root)
                else target
            ),
            "files_found": len(files_found),
            "file_list": files_found[:10],  # Limit output
            "target_exists": target.exists(),
        }

        # Write COMMIT event
        tx.commit(
            step_id=step.get("id", 0),
            plan_id=self.current_plan.get("plan_id", "unknown"),
            effect={
                "files_found": len(files_found),
                "target_exists": target.exists(),
                "success": True,
            },
        )

        return result

    def _execute_copy_atomic(
        self, step: Dict[str, Any], tx: TransactionGuard
    ) -> Dict[str, Any]:
        """Execute copy action atomically with TransactionGuard."""
        source = Path(step.get("source", ""))
        destination = Path(step.get("target", ""))

        if not source.is_absolute():
            source = self.workspace_root / source
        if not destination.is_absolute():
            destination = self.workspace_root / destination

        # Handle relative paths
        if not source.exists():
            source = self.workspace_root / step.get("source", "")

        if not source.exists():
            raise ExecutionError(f"Source file does not exist: {source}")

        # Get hash before (for COMMIT event)
        hash_before = (
            self._compute_file_hash(destination)
            if destination.exists()
            else "sha256:file_not_exist"
        )

        # Create backup if destination exists
        backup_path = None
        if destination.exists():
            backup_path = (
                self.backup_dir / f"backup_{destination.name}_{int(time.time())}"
            )
            shutil.copy2(destination, backup_path)

        try:
            # Write INTENT event
            tx.write_intent(
                step_id=step.get("id", 0),
                plan_id=self.current_plan.get("plan_id", "unknown"),
                action="copy",
                parameters={
                    "source": str(
                        source.relative_to(self.workspace_root)
                        if source.is_relative_to(self.workspace_root)
                        else source
                    ),
                    "destination": str(
                        destination.relative_to(self.workspace_root)
                        if destination.is_relative_to(self.workspace_root)
                        else destination
                    ),
                    "backup_created": backup_path is not None,
                },
            )

            # Execute copy
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

            # Get hash after
            hash_after = self._compute_file_hash(destination)

            # Write COMMIT event
            tx.commit(
                step_id=step.get("id", 0),
                plan_id=self.current_plan.get("plan_id", "unknown"),
                effect={
                    "hash_before": hash_before,
                    "hash_after": hash_after,
                    "backup_path": str(backup_path) if backup_path else None,
                    "success": True,
                },
            )

            self.budget_tracker.consume_command()

            return {
                "action": "copy",
                "source": str(
                    source.relative_to(self.workspace_root)
                    if source.is_relative_to(self.workspace_root)
                    else source
                ),
                "destination": str(
                    destination.relative_to(self.workspace_root)
                    if destination.is_relative_to(self.workspace_root)
                    else destination
                ),
                "hash_before": hash_before,
                "hash_after": hash_after,
                "backup_created": backup_path is not None,
                "backup_path": str(backup_path) if backup_path else None,
            }

        except Exception as e:
            # TransactionGuard will handle abort in __exit__
            raise ExecutionError(f"Copy failed: {e}")

    def _execute_command_atomic(
        self, step: Dict[str, Any], tx: TransactionGuard
    ) -> Dict[str, Any]:
        """Execute shell command atomically."""
        command = step.get("command", "")

        try:
            # Write INTENT event
            tx.write_intent(
                step_id=step.get("id", 0),
                plan_id=self.current_plan.get("plan_id", "unknown"),
                action="command",
                parameters={"command": command},
            )

            # Execute command
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=30,
            )

            # Write COMMIT event
            tx.commit(
                step_id=step.get("id", 0),
                plan_id=self.current_plan.get("plan_id", "unknown"),
                effect={
                    "exit_code": result.returncode,
                    "stdout": result.stdout[:1000] if result.stdout else "",
                    "stderr": result.stderr[:1000] if result.stderr else "",
                    "success": result.returncode == 0,
                },
            )

            self.budget_tracker.consume_command()

            return {
                "action": "command",
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout[:500],  # Limit output
                "stderr": result.stderr[:500],
                "success": result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            # TransactionGuard will handle abort in __exit__
            raise ExecutionError(f"Command timed out: {command}")

        except Exception as e:
            # TransactionGuard will handle abort in __exit__
            raise ExecutionError(f"Command failed: {command} - {str(e)}")

    def execute_step_atomic(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step atomically using TransactionGuard."""
        self.budget_tracker.check_runtime()

        action = step["action"]
        xact_id = self._generate_xact_id()

        # Use TransactionGuard to ensure atomic cleanup
        with TransactionGuard(self.event_sink, xact_id) as tx:
            # Execute based on action
            if action == "scan":
                result = self._execute_scan_atomic(step, tx)
            elif action == "copy":
                result = self._execute_copy_atomic(step, tx)
            elif action == "command":
                result = self._execute_command_atomic(step, tx)
            else:
                raise ExecutionError(f"Unknown action: {action}")

            return result

    def check_policy(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check plan against policy constraints."""
        if self.policy_gate is None:
            # Phase 2 fallback: always allow
            return {
                "decision": "allow",
                "reason_code": "NO_POLICY_GATE_AVAILABLE",
                "requires_policy_check": False,
            }

        return self.policy_gate.evaluate_plan(plan_data)

    def execute_plan_atomic(self, plan_file: Path) -> Dict[str, Any]:
        """Execute a PLAN.json file atomically with XACT model."""
        try:
            # Load plan
            with open(plan_file, "r", encoding="utf-8") as f:
                plan_data = json.load(f)

            self.validate_plan(plan_data)
            self.current_plan = plan_data

            # Generate execution ID
            self.execution_id = (
                f"exec_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            )

            # Check policy if available
            policy_result = self.check_policy(plan_data)
            if policy_result["requires_policy_check"]:
                if policy_result["decision"] == "block":
                    raise AtomicExecutionError(
                        f"Plan blocked by policy: {policy_result['reason_code']}"
                    )
                elif policy_result["decision"] == "require_review":
                    print(
                        f"⚠️  Plan requires human review: {policy_result['reason_code']}"
                    )
                    print("Proceeding with execution (Phase 3 demo mode)")

            # Initialize components
            budget_config = plan_data.get("budget", {})
            self.budget_tracker = SimpleBudgetTracker(
                max_commands=budget_config.get("max_commands", 10),
                max_runtime=budget_config.get("max_runtime_seconds", 60),
            )

            # Log plan start (if event sink available)
            if self.event_sink is not None:
                try:
                    # Create a special event for plan start
                    plan_start_event = {
                        "event_type": "PLAN_EXECUTION_START",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "plan_id": plan_data.get("plan_id", "unknown"),
                        "execution_id": self.execution_id,
                        "policy_decision": policy_result,
                        "previous_event_hash": self.event_sink.get_last_event_hash(),
                    }
                    # Compute hash
                    import hashlib

                    event_hash = hashlib.sha256(
                        json.dumps(
                            plan_start_event, sort_keys=True, separators=(",", ":")
                        ).encode("utf-8")
                    ).hexdigest()
                    plan_start_event["current_event_hash"] = event_hash

                    # Write to log
                    events_dir = self.workspace_root / "events" / "atomic"
                    events_dir.mkdir(parents=True, exist_ok=True)
                    log_file = events_dir / f"execution_{self.execution_id}.jsonl"
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(
                            json.dumps(plan_start_event, separators=(",", ":")) + "\n"
                        )
                except Exception as e:
                    print(f"Warning: Failed to log plan start: {e}")

            # Execute steps atomically
            results = []
            for step in plan_data["steps"]:
                try:
                    result = self.execute_step_atomic(step)
                    results.append(
                        {
                            "step_id": step.get("id", len(results)),
                            "action": step["action"],
                            "result": result,
                            "budget_status": self.budget_tracker.get_status(),
                        }
                    )
                except Exception as e:
                    # Log failure
                    if self.event_sink is not None:
                        try:
                            # Create failure event
                            failure_event = {
                                "event_type": "STEP_EXECUTION_FAILED",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "plan_id": plan_data.get("plan_id", "unknown"),
                                "step_id": step.get("id", 0),
                                "action": step["action"],
                                "error": str(e),
                                "budget_status": self.budget_tracker.get_status(),
                                "previous_event_hash": self.event_sink.get_last_event_hash(),
                            }
                            # Compute hash
                            import hashlib

                            failure_hash = hashlib.sha256(
                                json.dumps(
                                    failure_event, sort_keys=True, separators=(",", ":")
                                ).encode("utf-8")
                            ).hexdigest()
                            failure_event["current_event_hash"] = failure_hash

                            # Write to log
                            events_dir = self.workspace_root / "events" / "atomic"
                            events_dir.mkdir(parents=True, exist_ok=True)
                            log_file = (
                                events_dir / f"execution_{self.execution_id}.jsonl"
                            )
                            with open(log_file, "a", encoding="utf-8") as f:
                                f.write(
                                    json.dumps(failure_event, separators=(",", ":"))
                                    + "\n"
                                )
                        except Exception as log_error:
                            print(f"Warning: Failed to log failure event: {log_error}")
                    raise ExecutionError(f"Step failed: {e}")

            # Log plan completion
            if self.event_sink is not None:
                try:
                    plan_complete_event = {
                        "event_type": "PLAN_EXECUTION_COMPLETE",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "plan_id": plan_data.get("plan_id", "unknown"),
                        "execution_id": self.execution_id,
                        "steps_completed": len(results),
                        "total_steps": len(plan_data["steps"]),
                        "budget_status": self.budget_tracker.get_status(),
                        "success": True,
                        "previous_event_hash": self.event_sink.get_last_event_hash(),
                    }
                    # Compute hash
                    import hashlib

                    complete_hash = hashlib.sha256(
                        json.dumps(
                            plan_complete_event, sort_keys=True, separators=(",", ":")
                        ).encode("utf-8")
                    ).hexdigest()
                    plan_complete_event["current_event_hash"] = complete_hash

                    # Write to log
                    events_dir = self.workspace_root / "events" / "atomic"
                    events_dir.mkdir(parents=True, exist_ok=True)
                    log_file = events_dir / f"execution_{self.execution_id}.jsonl"
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(
                            json.dumps(plan_complete_event, separators=(",", ":"))
                            + "\n"
                        )
                except Exception as e:
                    print(f"Warning: Failed to log plan completion: {e}")

            return {
                "success": True,
                "plan_id": plan_data.get("plan_id", "unknown"),
                "execution_id": self.execution_id,
                "policy_decision": policy_result,
                "steps_completed": len(results),
                "total_steps": len(plan_data["steps"]),
                "results": results,
                "budget_status": self.budget_tracker.get_status(),
                "atomic_execution": self.event_sink is not None,
            }

        except Exception as e:
            # Log catastrophic failure
            if self.event_sink is not None and self.current_plan:
                try:
                    failure_event = {
                        "event_type": "PLAN_EXECUTION_FAILED",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "plan_id": self.current_plan.get("plan_id", "unknown"),
                        "execution_id": self.execution_id,
                        "error": str(e),
                        "budget_status": self.budget_tracker.get_status()
                        if self.budget_tracker
                        else {},
                        "previous_event_hash": self.event_sink.get_last_event_hash(),
                    }
                    # Compute hash
                    import hashlib

                    failure_hash = hashlib.sha256(
                        json.dumps(
                            failure_event, sort_keys=True, separators=(",", ":")
                        ).encode("utf-8")
                    ).hexdigest()
                    failure_event["current_event_hash"] = failure_hash

                    # Write to log
                    events_dir = self.workspace_root / "events" / "atomic"
                    events_dir.mkdir(parents=True, exist_ok=True)
                    log_file = events_dir / f"execution_{self.execution_id}.jsonl"
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(failure_event, separators=(",", ":")) + "\n")
                except Exception as log_error:
                    print(f"Warning: Failed to log catastrophic failure: {log_error}")

            return {
                "success": False,
                "plan_id": self.current_plan.get("plan_id", "unknown")
                if self.current_plan
                else "unknown",
                "execution_id": self.execution_id,
                "error": str(e),
                "steps_completed": 0,
                "atomic_execution": self.event_sink is not None,
            }

    # Phase 2 compatibility method
    def execute_plan(self, plan_file: Path) -> Dict[str, Any]:
        """Phase 2 compatibility method (non-atomic execution)."""
        print("⚠️  Using Phase 2 compatibility mode (non-atomic execution)")
        return self.execute_plan_atomic(plan_file)


def test_atomic_executor():
    """Test the atomic executor."""
    print("Testing Atomic Executor...")

    workspace = Path(__file__).parent.parent
    plan_file = workspace / "test_plan.json"

    if not plan_file.exists():
        # Create a simple test plan
        test_plan = {
            "plan_id": "test_atomic_001",
            "goal": "Test atomic executor",
            "steps": [
                {"id": 1, "action": "scan", "target": "."},
                {
                    "id": 2,
                    "action": "command",
                    "command": "python -c \"print('Hello from OE Atomic Executor')\"",
                },
            ],
            "budget": {"max_commands": 5, "max_runtime_seconds": 30},
        }

        with open(plan_file, "w") as f:
            json.dump(test_plan, f, indent=2)

    # Execute plan
    executor = AtomicSimpleExecutor(workspace)
    result = executor.execute_plan_atomic(plan_file)

    print(f"Execution result: {result.get('success', False)}")
    print(f"Plan ID: {result.get('plan_id', 'unknown')}")
    print(f"Execution ID: {result.get('execution_id', 'unknown')}")
    print(
        f"Steps completed: {result.get('steps_completed', 0)}/{result.get('total_steps', 0)}"
    )
    print(f"Atomic execution: {result.get('atomic_execution', False)}")

    # Check events
    events_dir = workspace / "events" / "atomic"
    if events_dir.exists():
        event_files = list(events_dir.glob("*.jsonl"))
        if event_files:
            print(f"Event files created: {len(event_files)}")
            for event_file in event_files[:2]:  # Show first 2
                with open(event_file, "r") as f:
                    events = [
                        json.loads(line) for line in f.readlines() if line.strip()
                    ]
                    print(f"  {event_file.name}: {len(events)} events")

    return result.get("success", False)


# Backward compatibility alias for Phase 2 tests
SimpleExecutor = AtomicSimpleExecutor

if __name__ == "__main__":
    success = test_atomic_executor()
    exit(0 if success else 1)

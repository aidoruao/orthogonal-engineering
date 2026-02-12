#!/usr/bin/env python3
"""
OE-AGENT EXECUTOR
Governed Autonomous Engineer - Execution Component

Version: 1.0.2 - Fixed error handling
Schema ID: EXECUTOR-ORTHOGONAL-1.2
Date: 2026-01-24

🎯 PURPOSE:
Execute PLAN.json steps with NO thinking, NO improvisation, NO model access.
Pure deterministic execution with rollback capability.

🔒 CONSTRAINTS:
- Cannot import AI/ML libraries
- Cannot reason about actions
- Cannot modify PLAN.json during execution
- Cannot bypass budget limits
- Cannot skip event logging
- Must rollback atomically on failure

🔧 DESIGN:
- Copy-on-write rollback pattern
- Centralized budget enforcement
- Immutable event logging
- Hard separation from planner
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class BudgetExceededError(Exception):
    """Raised when autonomy budget is exhausted."""
    pass


class ExecutionError(Exception):
    """Raised when execution step fails."""
    pass


class PlanValidationError(Exception):
    """Raised when PLAN.json is invalid."""
    pass


class BudgetTracker:
    """Centralized token bucket for autonomy budget enforcement."""

    def __init__(self, budget_config: Dict[str, Any]):
        """
        Initialize budget tracker.

        Args:
            budget_config: Budget configuration from PLAN.json
                - max_commands: Maximum number of commands allowed
                - max_files_touched: Maximum files that can be modified
                - max_runtime_seconds: Maximum execution time in seconds
        """
        self.max_commands = budget_config.get("max_commands", 12)
        self.max_files_touched = budget_config.get("max_files_touched", 5)
        self.max_runtime_seconds = budget_config.get("max_runtime_seconds", 300)

        self.commands_used = 0
        self.files_touched = 0
        self.start_time = time.time()

        # Track which files have been backed up for rollback
        self.backup_files = {}

    def consume_command(self, cost: int = 1) -> None:
        """Consume command budget."""
        self.commands_used += cost
        if self.commands_used > self.max_commands:
            raise BudgetExceededError(
                f"Command budget exceeded: {self.commands_used}/{self.max_commands}"
            )

    def consume_file(self, cost: int = 1) -> None:
        """Consume file touch budget."""
        self.files_touched += cost
        if self.files_touched > self.max_files_touched:
            raise BudgetExceededError(
                f"File touch budget exceeded: {self.files_touched}/{self.max_files_touched}"
            )

    def check_runtime(self) -> None:
        """Check if runtime budget is exceeded."""
        elapsed = time.time() - self.start_time
        if elapsed > self.max_runtime_seconds:
            raise BudgetExceededError(
                f"Runtime budget exceeded: {elapsed:.1f}s/{self.max_runtime_seconds}s"
            )

    def get_remaining(self) -> Dict[str, Any]:
        """Get remaining budget."""
        elapsed = time.time() - self.start_time
        return {
            "commands_remaining": max(0, self.max_commands - self.commands_used),
            "files_remaining": max(0, self.max_files_touched - self.files_touched),
            "runtime_remaining": max(0, self.max_runtime_seconds - elapsed),
            "commands_used": self.commands_used,
            "files_touched": self.files_touched,
            "runtime_used": elapsed,
        }

    def register_backup(self, original_path: str, backup_path: str) -> None:
        """Register a file backup for rollback."""
        self.backup_files[original_path] = backup_path

    def get_backup_path(self, original_path: str) -> Optional[str]:
        """Get backup path for a file."""
        return self.backup_files.get(original_path)


class EventSink:
    """Immutable event logging with hash chaining."""

    def __init__(self, events_dir: Path):
        """
        Initialize event sink.

        Args:
            events_dir: Directory for immutable event logs
        """
        self.events_dir = events_dir
        self.events_dir.mkdir(parents=True, exist_ok=True)

        # Last event hash for chaining
        self.last_event_hash = None
        self.sequence_number = 0

    def _calculate_hash(self, data: bytes) -> str:
        """Calculate SHA256 hash of data."""
        return hashlib.sha256(data).hexdigest()

    def _get_timestamp(self) -> str:
        """Get ISO timestamp with microseconds."""
        return datetime.utcnow().isoformat() + "Z"

    def log_event(
        self, event_type: str, plan_id: str, step_id: int, data: Dict[str, Any]
    ) -> str:
        """
        Log immutable event with hash chaining.

        Args:
            event_type: Type of event (file_modified, command_executed, etc.)
            plan_id: ID of the plan being executed
            step_id: Step number in the plan
            data: Event-specific data

        Returns:
            Event ID (timestamp-based)
        """
        self.sequence_number += 1

        # Create event structure
        event = {
            "$schema": "EVENT-ORTHOGONAL-1.0",
            "event_id": f"{self._get_timestamp().replace(':', '-').replace('.', '-')}_EXEC_{self.sequence_number:03d}",
            "timestamp": self._get_timestamp(),
            "event_type": event_type,
            "plan_id": plan_id,
            "step_id": step_id,
            "sequence_number": self.sequence_number,
            "actor": "OE_EXECUTOR",
            "data": data,
            "prev_event_hash": self.last_event_hash,
        }

        # Calculate hash of this event
        event_json = json.dumps(event, sort_keys=True, indent=2)
        event_hash = self._calculate_hash(event_json.encode("utf-8"))
        event["event_hash"] = event_hash

        # Update chain
        self.last_event_hash = event_hash

        # Write to file (append-only directory ensures immutability)
        event_file = self.events_dir / f"{event['event_id']}.json"
        with open(event_file, "w", encoding="utf-8") as f:
            json.dump(event, f, indent=2)

        # Also write to append-only log
        append_log = self.events_dir / "events_append.log"
        with open(append_log, "a", encoding="utf-8") as f:
            f.write(f"{event['timestamp']} {event['event_id']} {event_hash}\n")

        return event["event_id"]

    def get_event_chain(self) -> List[Dict[str, Any]]:
        """Get all events in sequence."""
        events = []
        for event_file in sorted(self.events_dir.glob("*.json")):
            if event_file.name == "events_append.log":
                continue
            with open(event_file, "r", encoding="utf-8") as f:
                events.append(json.load(f))
        return sorted(events, key=lambda x: x["sequence_number"])


class Executor:
    """Governed executor with no thinking capability."""

    def __init__(self, workspace_root: Path):
        """
        Initialize executor.

        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = workspace_root
        self.backup_dir = workspace_root / ".oe-backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Initialize components
        self.budget_tracker = None
        self.event_sink = None
        self.current_plan = None

        # Execution state
        self.execution_id = None
        self.steps_completed = 0
        self.rollback_required = False

    def _validate_plan(self, plan_data: Dict[str, Any]) -> None:
        """Validate PLAN.json structure."""
        required_fields = ["goal", "steps", "budget", "plan_id", "checksum"]
        for field in required_fields:
            if field not in plan_data:
                raise PlanValidationError(f"Missing required field: {field}")

        # Validate steps
        if not isinstance(plan_data["steps"], list):
            raise PlanValidationError("Steps must be a list")

        for i, step in enumerate(plan_data["steps"]):
            if "id" not in step:
                raise PlanValidationError(f"Step {i} missing 'id'")
            if "action" not in step:
                raise PlanValidationError(f"Step {i} missing 'action'")
            if "target" not in step and step["action"] not in ["command"]:
                raise PlanValidationError(f"Step {i} missing 'target'")

    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _backup_file(self, filepath: Path) -> Optional[Path]:
        """Create backup of a file for rollback."""
        if not filepath.exists():
            return None

        # Create backup directory for this execution
        backup_path = (
            self.backup_dir
            / self.execution_id
            / filepath.relative_to(self.workspace_root)
        )
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(filepath, backup_path)

        # Register with budget tracker
        if self.budget_tracker:
            self.budget_tracker.register_backup(str(filepath), str(backup_path))

        # Log backup event
        if self.event_sink and self.current_plan:
            self.event_sink.log_event(
                event_type="file_backup_created",
                plan_id=self.current_plan["plan_id"],
                step_id=self.steps_completed + 1,
                data={
                    "original_file": str(filepath),
                    "backup_file": str(backup_path),
                    "file_hash": self._calculate_file_hash(filepath),
                },
            )

        return backup_path

    def _restore_file(self, filepath: Path) -> None:
        """Restore file from backup."""
        if not self.budget_tracker:
            return

        backup_path = self.budget_tracker.get_backup_path(str(filepath))
        if backup_path and Path(backup_path).exists():
            # Restore from backup
            shutil.copy2(backup_path, filepath)

            # Log restore event
            if self.event_sink and self.current_plan:
                self.event_sink.log_event(
                    event_type="file_restored",
                    plan_id=self.current_plan["plan_id"],
                    step_id=self.steps_completed + 1,
                    data={
                        "file": str(filepath),
                        "restored_from": backup_path,
                        "file_hash": self._calculate_file_hash(filepath),
                    },
                )

    def _execute_scan(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scan action (read-only)."""
        target = Path(step["target"])
        if not target.is_absolute():
            target = self.workspace_root / target

        parameters = step.get("parameters", {})
        recursion_limit = parameters.get("recursion_limit", 1)

        # Scan files
        files_found = []
        if target.is_dir():
            for root, dirs, files in os.walk(target, topdown=True):
                # Apply recursion limit
                depth = root[len(str(target)):].count(os.sep)
                if depth >= recursion_limit:
                    dirs.clear()
                    continue

                for file in files:
                    filepath = Path(root) / file
                    files_found.append({
                        "path": str(filepath.relative_to(self.workspace_root)),
                        "size": filepath.stat().st_size,
                        "modified": filepath.stat().st_mtime,
                    })
        elif target.is_file():
            files_found.append({
                "path": str(target.relative_to(self.workspace_root)),
                "size": target.stat().st_size,
                "modified": target.stat().st_mtime,
            })

        # Consume budget
        self.budget_tracker.consume_command()
        self.budget_tracker.consume_file(cost=len(files_found))

        return {
            "files_found": len(files_found),
            "file_list": files_found,
        }

    def _execute_copy(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute copy action."""
        source = Path(step["source"])
        destination = Path(step["target"])

        if not source.is_absolute():
            source = self.workspace_root / source
        if not destination.is_absolute():
            destination = self.workspace_root / destination

        # Backup destination if it exists
        if destination.exists():
            self._backup_file(destination)

        # Create parent directories
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(source, destination)

        # Consume budget
        self.budget_tracker.consume_command()
        self.budget_tracker.consume_file()

        return {
            "source": str(source.relative_to(self.workspace_root)),
            "destination": str(destination.relative_to(self.workspace_root)),
            "source_hash": self._calculate_file_hash(source),
            "destination_hash": self._calculate_file_hash(destination),
        }

    def _execute_delete(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute delete action."""
        target = Path(step["target"])
        if not target.is_absolute():
            target = self.workspace_root / target

        # Backup file before deletion
        if target.exists():
            self._backup_file(target)

            # Delete file
            if target.is_file():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)

        # Consume budget
        self.budget_tracker.consume_command()
        self.budget_tracker.consume_file()

        return {
            "target": str(target.relative_to(self.workspace_root)),
            "deleted": True,
        }

    def _execute_command(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell command."""
        command = step["command"]
        parameters = step.get("parameters", {})

        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=parameters.get("timeout", 30)
            )

            # Consume budget
            self.budget_tracker.consume_command()

            return {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            raise ExecutionError(f"Command timed out: {command}")
        except Exception as e:
            raise ExecutionError(f"Command failed: {command} - {str(e)}")

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step from PLAN.json."""
        # Check budget before execution
        self.budget_tracker.check_runtime()

        action = step["action"]
        step_id = step["id"]

        # Execute based on action type
        if action == "scan":
            result = self._execute_scan(step)
        elif action == "copy":
            result = self._execute_copy(step)
        elif action == "delete":
            result = self._execute_delete(step)
        elif action == "command":
            result = self._execute_command(step)
        else:
            raise ExecutionError(f"Unknown action: {action}")

        # Log execution event
        event_id = self.event_sink.log_event(
            event_type=f"step_executed_{action}",
            plan_id=self.current_plan["plan_id"],
            step_id=step_id,
            data={
                "action": action,
                "target": step.get("target", ""),
                "result": result,
                "budget_remaining": self.budget_tracker.get_remaining(),
            }
        )

        self.steps_completed += 1
        return {
            "step_id": step_id,
            "action": action,
            "result": result,
            "event_id": event_id,
            "budget_remaining": self.budget_tracker.get_remaining(),
        }

    def execute_plan(self, plan_file: Path) -> Dict[str, Any]:
        """
        Execute a PLAN.json file.

        Args:
            plan_file: Path to PLAN.json file

        Returns:
            Execution result with success/failure status
        """
        try:
            # Load and validate plan
            with open(plan_file, "r", encoding="utf-8") as f:
                plan_data = json.load(f)

            self._validate_plan(plan_data)
            self.current_plan = plan_data

            # Generate execution ID
            self.execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{plan_data['plan_id'][-8:]}"

            # Initialize components
            self.budget_tracker = BudgetTracker(plan_data.get("budget", {}))
            self.event_sink = EventSink(self.workspace_root / "events" / self.execution_id)

            # Log plan start
            start_event_id = self.event_sink.log_event(
                event_type="plan_execution_started",
                plan_id=plan_data["plan_id"],
                step_id=0,
                data={
                    "goal": plan_data["goal"],
                    "total_steps": len(plan_data["steps"]),
                    "budget": plan_data["budget"],
                }
            )

            # Execute steps
            results = []
            for step in plan_data["steps"]:
                try:
                    step_result = self.execute_step(step)
                    results.append(step_result)

                    # Check for failure conditions
                    if step.get("action") in ["delete", "copy", "command"]:
                        if

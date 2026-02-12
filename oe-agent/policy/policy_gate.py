#!/usr/bin/env python3
"""
OE-AGENT POLICY GATE
Pre-INTENT policy decisions with atomic logging

Version: 1.0.0
Schema ID: POLICY-GATE-ATOMIC-1.0
Date: 2026-01-24

🎯 PURPOSE:
Make policy decisions BEFORE execution (pre-INTENT).
Enforce constraints and log decisions with hash chaining.

🔒 CONSTRAINTS:
- No reasoning about decisions (only rule application)
- Decisions logged before any execution
- Integration with event sink for hash chaining
- Simple allow/block/review decisions

🔗 INTEGRATION:
Policy decisions are logged as POLICY_DECISION events
in the event chain BEFORE any INTENT events.
"""

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class PolicyDecision(Enum):
    """Policy decision types."""

    ALLOW = "allow"
    BLOCK = "block"
    REQUIRE_REVIEW = "require_review"


class PolicyConstraint(Enum):
    """Policy constraint types."""

    MAX_COMMANDS = "max_commands"
    MAX_RUNTIME = "max_runtime_seconds"
    NO_MAIN_BRANCH = "no_main_branch"
    READ_ONLY_FILES = "read_only_files"
    BUDGET_EXCEEDED = "budget_exceeded"
    BOUNDARY_VIOLATION = "boundary_violation"


class PolicyGateError(Exception):
    """Base exception for policy gate errors."""

    pass


class PolicyGate:
    """Policy gate with pre-INTENT decision making."""

    def __init__(self, event_sink=None):
        """
        Initialize policy gate.

        Args:
            event_sink: Optional AtomicEventSink for logging decisions
        """
        self.event_sink = event_sink
        self._decision_cache = {}

        # Default constraints
        self.constraints = {
            PolicyConstraint.NO_MAIN_BRANCH: True,
            PolicyConstraint.MAX_COMMANDS: 10,
            PolicyConstraint.MAX_RUNTIME: 300,  # 5 minutes
            PolicyConstraint.READ_ONLY_FILES: [
                "documentation/",
                "logs/",
                "events/",
            ],
        }

    def _compute_plan_hash(self, plan_data: Dict[str, Any]) -> str:
        """Compute hash of plan data for caching."""
        serialized = json.dumps(plan_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _check_budget_constraints(
        self, plan_data: Dict[str, Any]
    ) -> List[Tuple[PolicyConstraint, str]]:
        """Check budget constraints."""
        violations = []

        # Check max commands
        max_commands = self.constraints.get(PolicyConstraint.MAX_COMMANDS, 10)
        plan_steps = len(plan_data.get("steps", []))

        if plan_steps > max_commands:
            violations.append(
                (
                    PolicyConstraint.MAX_COMMANDS,
                    f"Plan has {plan_steps} steps, exceeds max {max_commands}",
                )
            )

        # Check max runtime
        max_runtime = self.constraints.get(PolicyConstraint.MAX_RUNTIME, 300)
        plan_budget = plan_data.get("budget", {}).get("max_runtime_seconds", 0)

        if plan_budget > max_runtime:
            violations.append(
                (
                    PolicyConstraint.MAX_RUNTIME,
                    f"Plan runtime {plan_budget}s exceeds max {max_runtime}s",
                )
            )

        return violations

    def _check_operation_constraints(
        self, plan_data: Dict[str, Any]
    ) -> List[Tuple[PolicyConstraint, str]]:
        """Check operation-specific constraints."""
        violations = []

        # Check for main branch operations
        if self.constraints.get(PolicyConstraint.NO_MAIN_BRANCH, True):
            for step in plan_data.get("steps", []):
                if step.get("action") == "git_commit":
                    branch = step.get("parameters", {}).get("branch", "")
                    if branch == "main" or branch == "master":
                        violations.append(
                            (
                                PolicyConstraint.NO_MAIN_BRANCH,
                                f"Step {step.get('id')} attempts commit to main branch",
                            )
                        )

        # Check read-only file access
        read_only_files = self.constraints.get(PolicyConstraint.READ_ONLY_FILES, [])
        for step in plan_data.get("steps", []):
            action = step.get("action", "")
            target = step.get("target", "") or step.get("destination", "")

            if action in ["write", "modify", "delete", "copy"]:
                for ro_file in read_only_files:
                    if target.startswith(ro_file):
                        violations.append(
                            (
                                PolicyConstraint.READ_ONLY_FILES,
                                f"Step {step.get('id')} attempts to modify read-only file: {target}",
                            )
                        )

        return violations

    def _log_policy_decision(
        self,
        plan_id: str,
        decision: PolicyDecision,
        violations: List[Tuple[PolicyConstraint, str]],
        plan_hash: str,
    ) -> Optional[str]:
        """Log policy decision to event sink."""
        if not self.event_sink:
            return None

        try:
            # Create policy decision event
            payload = {
                "decision": decision.value,
                "plan_id": plan_id,
                "plan_hash": plan_hash,
                "violations": [
                    {"constraint": constraint.value, "reason": reason}
                    for constraint, reason in violations
                ],
                "constraints_applied": [
                    {"constraint": constraint.value, "value": value}
                    for constraint, value in self.constraints.items()
                    if constraint
                    != PolicyConstraint.READ_ONLY_FILES  # Don't expose full list
                ],
            }

            # Use event sink to write policy decision
            # Note: This assumes event sink has a method for policy decisions
            # For now, we'll create a simple event structure
            event = {
                "event_type": "POLICY_DECISION",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "plan_id": plan_id,
                "decision": decision.value,
                "payload": payload,
                "previous_event_hash": self.event_sink.get_last_event_hash()
                if hasattr(self.event_sink, "get_last_event_hash")
                else None,
            }

            # Compute hash
            event_hash = hashlib.sha256(
                json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            event["current_event_hash"] = event_hash

            # In a real implementation, this would use event_sink.write_policy_decision()
            # For now, we'll return the hash
            return event_hash

        except Exception as e:
            print(f"Warning: Failed to log policy decision: {e}")
            return None

    def evaluate_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate plan against policy constraints.

        Args:
            plan_data: PLAN.json data

        Returns:
            Policy decision with details
        """
        plan_id = plan_data.get("plan_id", "unknown")
        plan_hash = self._compute_plan_hash(plan_data)

        # Check cache
        cache_key = f"{plan_id}_{plan_hash}"
        if cache_key in self._decision_cache:
            return self._decision_cache[cache_key]

        # Collect violations
        violations = []
        violations.extend(self._check_budget_constraints(plan_data))
        violations.extend(self._check_operation_constraints(plan_data))

        # Make decision
        if violations:
            # Check if any violations are blocking
            blocking_violations = [
                v
                for v in violations
                if v[0]
                in [
                    PolicyConstraint.NO_MAIN_BRANCH,
                    PolicyConstraint.BOUNDARY_VIOLATION,
                    PolicyConstraint.BUDGET_EXCEEDED,
                ]
            ]

            if blocking_violations:
                decision = PolicyDecision.BLOCK
                reason_code = "BLOCKING_VIOLATIONS"
            else:
                decision = PolicyDecision.REQUIRE_REVIEW
                reason_code = "REQUIRES_HUMAN_REVIEW"
        else:
            decision = PolicyDecision.ALLOW
            reason_code = "ALL_CONSTRAINTS_SATISFIED"

        # Log decision
        event_hash = self._log_policy_decision(plan_id, decision, violations, plan_hash)

        # Build result
        result = {
            "decision": decision.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "plan_id": plan_id,
            "plan_hash": plan_hash,
            "reason_code": reason_code,
            "violations": [
                {"constraint": constraint.value, "reason": reason}
                for constraint, reason in violations
            ],
            "constraints_applied": [
                {"constraint": constraint.value, "value": value}
                for constraint, value in self.constraints.items()
                if constraint != PolicyConstraint.READ_ONLY_FILES
            ],
            "event_hash": event_hash,
            "requires_policy_check": True,
        }

        # Cache result
        self._decision_cache[cache_key] = result

        return result

    def add_constraint(self, constraint: PolicyConstraint, value: Any) -> None:
        """Add or update a constraint."""
        self.constraints[constraint] = value
        self._decision_cache.clear()  # Clear cache when constraints change

    def remove_constraint(self, constraint: PolicyConstraint) -> None:
        """Remove a constraint."""
        if constraint in self.constraints:
            del self.constraints[constraint]
            self._decision_cache.clear()

    def get_constraints(self) -> Dict[PolicyConstraint, Any]:
        """Get current constraints."""
        return self.constraints.copy()

    def clear_cache(self) -> None:
        """Clear decision cache."""
        self._decision_cache.clear()


# Test function
def test_policy_gate():
    """Test the policy gate."""
    print("Testing Policy Gate...")

    try:
        gate = PolicyGate()

        # Test 1: Allow decision (simple plan)
        print("\nTest 1: Allow decision")
        simple_plan = {
            "plan_id": "test_allow_001",
            "goal": "Simple scan",
            "steps": [{"id": 1, "action": "scan", "target": "."}],
            "budget": {"max_commands": 5, "max_runtime_seconds": 60},
        }

        decision1 = gate.evaluate_plan(simple_plan)
        print(f"  Decision: {decision1['decision']}")
        print(f"  Reason: {decision1['reason_code']}")
        print(f"  Violations: {len(decision1['violations'])}")

        assert decision1["decision"] == "allow"
        assert decision1["reason_code"] == "ALL_CONSTRAINTS_SATISFIED"

        # Test 2: Block decision (too many commands)
        print("\nTest 2: Block decision (budget exceeded)")
        big_plan = {
            "plan_id": "test_block_001",
            "goal": "Too many commands",
            "steps": [{"id": i, "action": "scan", "target": "."} for i in range(15)],
            "budget": {"max_commands": 20, "max_runtime_seconds": 300},
        }

        # Set low command limit
        gate.add_constraint(PolicyConstraint.MAX_COMMANDS, 10)

        decision2 = gate.evaluate_plan(big_plan)
        print(f"  Decision: {decision2['decision']}")
        print(f"  Reason: {decision2['reason_code']}")
        print(f"  Violations: {len(decision2['violations'])}")

        assert decision2["decision"] == "block"
        assert "MAX_COMMANDS" in str(decision2["violations"])

        # Reset constraint
        gate.add_constraint(PolicyConstraint.MAX_COMMANDS, 10)

        # Test 3: Require review (borderline case)
        print("\nTest 3: Require review (modify read-only file)")
        modify_plan = {
            "plan_id": "test_review_001",
            "goal": "Modify documentation",
            "steps": [
                {
                    "id": 1,
                    "action": "copy",
                    "source": "a.txt",
                    "target": "documentation/b.txt",
                }
            ],
            "budget": {"max_commands": 5, "max_runtime_seconds": 60},
        }

        decision3 = gate.evaluate_plan(modify_plan)
        print(f"  Decision: {decision3['decision']}")
        print(f"  Reason: {decision3['reason_code']}")
        print(f"  Violations: {len(decision3['violations'])}")

        assert decision3["decision"] == "require_review"
        assert "READ_ONLY_FILES" in str(decision3["violations"])

        # Test 4: Constraint management
        print("\nTest 4: Constraint management")
        constraints_before = gate.get_constraints()
        print(f"  Constraints before: {len(constraints_before)}")

        gate.add_constraint(PolicyConstraint.BOUNDARY_VIOLATION, True)
        constraints_after = gate.get_constraints()
        print(f"  Constraints after: {len(constraints_after)}")

        assert len(constraints_after) == len(constraints_before) + 1

        gate.remove_constraint(PolicyConstraint.BOUNDARY_VIOLATION)
        constraints_final = gate.get_constraints()
        print(f"  Constraints final: {len(constraints_final)}")

        assert len(constraints_final) == len(constraints_before)

        print("\n✅ All policy gate tests completed")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_policy_gate()
    exit(0 if success else 1)

#!/usr/bin/env python3
"""
Guardian Monitor

Integration between runtime execution and Guardian Frame audit.
Monitors for manipulation attempts and escalates through three-level path.

Authority: RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml
Standard: Yeshua (watchmen - watching the watchers)
"""

import hashlib
import json
import sys
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from fractions import Fraction


class EscalationLevel(Enum):
    """Three-level escalation path for guardian alerts."""
    LOGGING = "logging"
    GUARDIAN_ALERT = "guardian_alert"
    SYSTEM_LOCKDOWN = "system_lockdown"


class MonitoredCondition(Enum):
    """Conditions monitored by Guardian Frame."""
    INVARIANT_OVERRIDE_ATTEMPT = "invariant_override_attempt"
    RULE_EVASION_PATTERN = "rule_evasion_pattern"
    RECURSIVE_FRAME_MANIPULATION = "recursive_frame_manipulation"
    ENFORCEMENT_PRIORITY_CHANGE = "enforcement_priority_change"
    RUNTIME_STATE_CORRUPTION = "runtime_state_corruption"
    META_INVARIANT_VIOLATION = "meta_invariant_violation"
    PURPOSE_MISALIGNMENT = "purpose_misalignment"


# Alias for compatibility with invariant_engine.py
GuardianCondition = MonitoredCondition


@dataclass
class GuardianAlert:
    """An alert to the Guardian Frame."""
    condition: MonitoredCondition
    escalation_level: EscalationLevel
    message: str
    context_snapshot: Dict[str, Any]
    timestamp: int


class GuardianMonitor:
    """
    Guardian Frame integration monitor.

    Monitors for:
    - invariant_override_attempt
    - rule_evasion_pattern
    - recursive_frame_manipulation
    - enforcement_priority_change
    - runtime_state_corruption
    - meta_invariant_violation
    - purpose_misalignment
    """

    def __init__(self) -> None:
        """Initialize guardian monitor."""
        self.alerts: List[GuardianAlert] = []
        self.virtual_clock: int = 0
        self.lockdown_active: bool = False
        self.condition_history: List[tuple[MonitoredCondition, int]] = []

    def check_condition(
        self,
        condition: MonitoredCondition,
        context: Dict[str, Any]
    ) -> Optional[GuardianAlert]:
        """
        Check for a monitored condition.

        Implements pattern matching against context dict.

        Args:
            condition: Condition to check for
            context: Current system context

        Returns:
            GuardianAlert if condition detected, None otherwise
        """
        detected = False
        message = ""

        if condition == MonitoredCondition.INVARIANT_OVERRIDE_ATTEMPT:
            # Check for "override" or "bypass" keys in context
            if "override" in context or "bypass" in context:
                detected = True
                message = f"Invariant override detected: {context}"

        elif condition == MonitoredCondition.RULE_EVASION_PATTERN:
            # Check for repeated failures followed by success (suspicious pattern)
            # Look at condition history for this pattern
            recent_failures = [
                c for c, _ in self.condition_history[-5:]
                if c in (MonitoredCondition.RUNTIME_STATE_CORRUPTION,
                         MonitoredCondition.META_INVARIANT_VIOLATION)
            ]
            if len(recent_failures) >= 2:
                detected = True
                message = f"Rule evasion pattern detected: {len(recent_failures)} recent failures"

        elif condition == MonitoredCondition.RUNTIME_STATE_CORRUPTION:
            # Check for state hash mismatch
            if "state_hash" in context and "expected_hash" in context:
                if context["state_hash"] != context["expected_hash"]:
                    detected = True
                    message = f"State hash mismatch: {context['state_hash'][:16]}... != {context['expected_hash'][:16]}..."
            elif "invariant_violation" in context:
                # Invariant violations indicate potential state corruption
                detected = True
                message = f"State corruption detected via invariant: {context.get('message', 'unknown')}"

        elif condition == MonitoredCondition.PURPOSE_MISALIGNMENT:
            """
            Falsifies if: action is not in allowed_actions for the declared purpose,
            or purpose_hash in context does not match sha256(declared_purpose).
            """
            if "action" in context and "declared_purpose" in context:
                action = context["action"]
                purpose = context["declared_purpose"]

                # Derive a hash commitment to the declared purpose so
                # callers cannot swap purpose after the fact.
                import hashlib as _hl
                expected_purpose_hash = _hl.sha256(
                    purpose.encode("utf-8")
                ).hexdigest()
                provided_purpose_hash = context.get("purpose_hash", "")

                # If the caller provided a purpose_hash, verify it matches.
                purpose_hash_mismatch = bool(provided_purpose_hash) and (
                    provided_purpose_hash != expected_purpose_hash
                )

                # The set of actions explicitly permitted for this purpose.
                # Keys are normalised to lower-case; the set is drawn from the
                # context if supplied, otherwise falls back to the declared
                # purpose name itself as the only permitted action.
                allowed_raw: List[str] = context.get(
                    "allowed_actions", [purpose.lower()]
                )
                allowed_actions_set = {a.lower().strip() for a in allowed_raw}
                action_not_allowed = action.lower().strip() not in allowed_actions_set

                # Flag misalignment fraction — 1 if both checks fail, else
                # 1/2 for partial failure. 0 means no misalignment.
                misalignment_score = Fraction(
                    int(purpose_hash_mismatch) + int(action_not_allowed), 2
                )

                if misalignment_score > Fraction(0):
                    detected = True
                    reasons: List[str] = []
                    if purpose_hash_mismatch:
                        reasons.append(
                            f"purpose_hash mismatch "
                            f"(expected={expected_purpose_hash[:12]}…, "
                            f"got={provided_purpose_hash[:12]}…)"
                        )
                    if action_not_allowed:
                        reasons.append(
                            f"action '{action}' not in allowed_actions "
                            f"{sorted(allowed_actions_set)}"
                        )
                    message = (
                        f"PURPOSE_MISALIGNMENT (score={misalignment_score}): "
                        + "; ".join(reasons)
                    )

        elif condition == MonitoredCondition.RECURSIVE_FRAME_MANIPULATION:
            # Check for recursive self-reference or frame depth exceeding threshold
            if "frame_depth" in context:
                max_depth = context.get("max_frame_depth", 10)
                if context["frame_depth"] > max_depth:
                    detected = True
                    message = f"Recursive frame depth {context['frame_depth']} exceeds threshold {max_depth}"
            elif "recursive_reference" in context or "self_reference" in context:
                detected = True
                message = f"Recursive frame manipulation detected: {context}"

        elif condition == MonitoredCondition.ENFORCEMENT_PRIORITY_CHANGE:
            # Check if enforcement rules were reordered or priority was modified
            if "priority_change" in context or "rule_reorder" in context:
                detected = True
                old_priority = context.get("old_priority", "unknown")
                new_priority = context.get("new_priority", "unknown")
                message = f"Enforcement priority changed: {old_priority} -> {new_priority}"
            elif "enforcement_modified" in context:
                detected = True
                message = f"Enforcement rules modified: {context.get('modification', 'unknown')}"

        elif condition == MonitoredCondition.META_INVARIANT_VIOLATION:
            # Check if an invariant about invariants was violated
            if "invariant_count_changed" in context:
                detected = True
                old_count = context.get("old_count", 0)
                new_count = context.get("new_count", 0)
                message = f"Invariant count changed: {old_count} -> {new_count}"
            elif "invariant_deleted" in context or "invariant_disabled" in context:
                detected = True
                inv_id = context.get("invariant_id", "unknown")
                message = f"Meta-invariant violation: invariant {inv_id} deleted or disabled"

        # Record this check in history
        self.condition_history.append((condition, self.virtual_clock))

        if detected:
            # Escalate the detected condition
            return self.escalate(condition, message, context)

        return None

    def escalate(
        self,
        condition: MonitoredCondition,
        message: str,
        context: Dict[str, Any]
    ) -> GuardianAlert:
        """
        Escalate a detected condition.

        Determines escalation level and takes appropriate action.

        Args:
            condition: Detected condition
            message: Description of the condition
            context: System context snapshot

        Returns:
            Created GuardianAlert
        """
        # Determine escalation level
        level = self._determine_escalation_level(condition, context)

        # Create alert
        alert = GuardianAlert(
            condition=condition,
            escalation_level=level,
            message=message,
            context_snapshot=context,
            timestamp=self.virtual_clock
        )

        self.alerts.append(alert)

        # Take action based on level
        if level == EscalationLevel.LOGGING:
            self._log_to_audit_trail(alert)
        elif level == EscalationLevel.GUARDIAN_ALERT:
            self._notify_guardian_frame(alert)
        elif level == EscalationLevel.SYSTEM_LOCKDOWN:
            self._initiate_lockdown(alert)

        self.virtual_clock += 1

        return alert

    def _determine_escalation_level(
        self,
        condition: MonitoredCondition,
        context: Dict[str, Any]
    ) -> EscalationLevel:
        """
        Determine appropriate escalation level.

        Smart logic considering:
        - Critical conditions always escalate to LOCKDOWN
        - Repeated alerts for same condition escalate
        - Context severity overrides
        - Active lockdown state
        """
        # If lockdown is already active, all new alerts are SYSTEM_LOCKDOWN
        if self.lockdown_active:
            return EscalationLevel.SYSTEM_LOCKDOWN

        # Check context for explicit severity
        if "severity" in context:
            severity = context["severity"]
            if severity in ("critical", "high"):
                return EscalationLevel.SYSTEM_LOCKDOWN
            elif severity == "medium":
                return EscalationLevel.GUARDIAN_ALERT
            elif severity == "low":
                return EscalationLevel.LOGGING

        # Critical conditions always trigger lockdown
        critical_conditions = {
            MonitoredCondition.RUNTIME_STATE_CORRUPTION,
            MonitoredCondition.META_INVARIANT_VIOLATION
        }

        if condition in critical_conditions:
            return EscalationLevel.SYSTEM_LOCKDOWN

        # Check for repeated alerts for same condition (escalation)
        recent_same_condition = [
            a for a in self.alerts[-10:]
            if a.condition == condition
        ]
        if len(recent_same_condition) >= 3:
            return EscalationLevel.SYSTEM_LOCKDOWN

        # Default to guardian alert
        return EscalationLevel.GUARDIAN_ALERT

    def _log_to_audit_trail(self, alert: GuardianAlert) -> None:
        """
        Log alert to audit trail (Level 1).

        Writes alert as JSON to stderr with timestamp, condition, message, and context hash.
        """
        context_json = json.dumps(alert.context_snapshot, sort_keys=True)
        context_hash = hashlib.sha256(context_json.encode()).hexdigest()

        audit_entry = {
            "type": "guardian_alert",
            "level": "LOGGING",
            "condition": alert.condition.value,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "context_hash": context_hash,
        }

        print(json.dumps(audit_entry), file=sys.stderr)

    def _notify_guardian_frame(self, alert: GuardianAlert) -> None:
        """
        Notify Guardian Frame (Level 2).

        Captures full context snapshot and writes to guardian alert log.
        Triggers re-evaluation if invariant_engine is available.
        """
        # Capture full context snapshot
        context_json = json.dumps(alert.context_snapshot, indent=2, sort_keys=True)
        context_hash = hashlib.sha256(context_json.encode()).hexdigest()

        notification = {
            "type": "guardian_frame_notification",
            "level": "GUARDIAN_ALERT",
            "condition": alert.condition.value,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "context_snapshot": alert.context_snapshot,
            "context_hash": context_hash,
        }

        # Write to guardian alert log (stderr for now)
        print(f"GUARDIAN_ALERT: {json.dumps(notification)}", file=sys.stderr)

        # Trigger re-evaluation if invariant engine is available
        # (This would be a callback mechanism in a real implementation)
        pass

    def _initiate_lockdown(self, alert: GuardianAlert) -> None:
        """
        Initiate system lockdown (Level 3).

        Complete state dump to JSON, write lockdown record with timestamp and reason,
        log all current alerts.
        """
        self.lockdown_active = True

        # Complete state dump
        state_dump = {
            "lockdown_initiated": True,
            "trigger_condition": alert.condition.value,
            "trigger_message": alert.message,
            "timestamp": alert.timestamp,
            "total_alerts": len(self.alerts),
            "context_snapshot": alert.context_snapshot,
        }

        # Write lockdown record
        lockdown_record = {
            "type": "system_lockdown",
            "level": "SYSTEM_LOCKDOWN",
            "condition": alert.condition.value,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "reason": f"Guardian Monitor initiated lockdown due to {alert.condition.value}",
            "state_dump": state_dump,
        }

        print(f"SYSTEM_LOCKDOWN: {json.dumps(lockdown_record, indent=2)}", file=sys.stderr)

        # Log all current alerts for forensic review
        all_alerts = [
            {
                "condition": a.condition.value,
                "level": a.escalation_level.value,
                "message": a.message,
                "timestamp": a.timestamp,
            }
            for a in self.alerts
        ]

        print(f"LOCKDOWN_ALERT_HISTORY: {json.dumps(all_alerts, indent=2)}", file=sys.stderr)

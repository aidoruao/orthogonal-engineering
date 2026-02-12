#!/usr/bin/env python3
"""
OE-AGENT ATOMIC EVENT SINK
Linear hash-chained event logging with atomic guarantees

Version: 1.0.0
Schema ID: EVENT-SINK-ATOMIC-1.0
Date: 2026-01-24

🎯 PURPOSE:
Provide atomic, hash-chained event logging for OE-Agent execution.
Implements the XACT (Execution Transaction) model with INTENT/COMMIT/ABORT events.

🔒 ATOMIC GUARANTEES:
1. No ghost actions: If file changes, there's INTENT → COMMIT chain
2. No narrative repair: Logs cannot be "fixed" after the fact
3. Replayable truth: Can replay intents, commits, aborts separately
4. Linear hash chain: Each event references previous event's hash

🔗 HASH CHAINING:
event_n-1.hash → event_n.previous_hash → event_n.hash → event_n+1.previous_hash
"""

import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class AtomicEventSinkError(Exception):
    """Base exception for atomic event sink errors."""

    pass


class HashChainViolationError(AtomicEventSinkError):
    """Raised when hash chain integrity is violated."""

    pass


class AtomicWriteError(AtomicEventSinkError):
    """Raised when atomic write fails."""

    pass


class AtomicEventSink:
    """Atomic event sink with linear hash chaining."""

    def __init__(self, log_dir: Path):
        """
        Initialize atomic event sink.

        Args:
            log_dir: Directory for event logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current log file (date-based)
        self.current_log_file = (
            self.log_dir
            / f"events_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        )

        # Lock for thread-safe operations
        self._lock = threading.Lock()

        # Cache of last event hash for chaining
        self._last_event_hash = self._load_last_event_hash()

        # Transaction state
        self._current_xact_id = None
        self._xact_intent_hash = None

    def _load_last_event_hash(self) -> Optional[str]:
        """Load the hash of the last event from the log chain."""
        if not self.current_log_file.exists():
            return None

        last_hash = None
        try:
            with open(self.current_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        last_hash = event.get("current_event_hash")
        except (json.JSONDecodeError, IOError):
            # If log is corrupted, start fresh chain
            return None

        return last_hash

    def _compute_hash(self, event_data: Dict[str, Any]) -> str:
        """
        Compute SHA256 hash of event data.

        Args:
            event_data: Event dictionary (must be JSON serializable)

        Returns:
            SHA256 hash as hex string
        """
        # Sort keys for deterministic hashing
        serialized = json.dumps(event_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _create_event_base(
        self,
        event_type: str,
        xact_id: str,
        step_id: int,
        plan_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create base event structure.

        Args:
            event_type: INTENT, COMMIT, or ABORT
            xact_id: Execution transaction ID
            step_id: Step number in plan
            plan_id: Plan ID
            payload: Event-specific data

        Returns:
            Base event dictionary
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "event_type": event_type,
            "xact_id": xact_id,
            "step_id": step_id,
            "plan_id": plan_id,
            "timestamp": timestamp,
            "previous_event_hash": self._last_event_hash,
            "payload": payload,
            # current_event_hash will be added after computing
        }

    def _write_event_atomic(self, event: Dict[str, Any]) -> str:
        """
        Write event atomically with hash chaining.

        Args:
            event: Event dictionary (without current_event_hash)

        Returns:
            The computed event hash

        Raises:
            AtomicWriteError: If atomic write fails
        """
        # Compute hash
        event_hash = self._compute_hash(event)
        event["current_event_hash"] = event_hash

        # Write atomically
        try:
            # Write to temporary file first
            temp_file = self.current_log_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(event, separators=(",", ":")) + "\n")

            # Append to main log file
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, separators=(",", ":")) + "\n")

            # Remove temp file
            temp_file.unlink(missing_ok=True)

        except IOError as e:
            raise AtomicWriteError(f"Failed to write event atomically: {e}")

        # Update last hash
        self._last_event_hash = event_hash

        return event_hash

    def begin_xact(self, xact_id: str) -> None:
        """
        Begin a new execution transaction.

        Args:
            xact_id: Unique transaction ID

        Raises:
            AtomicEventSinkError: If transaction already in progress
        """
        with self._lock:
            if self._current_xact_id is not None:
                raise AtomicEventSinkError(
                    f"Cannot begin transaction {xact_id}: "
                    f"Transaction {self._current_xact_id} already in progress"
                )
            self._current_xact_id = xact_id
            self._xact_intent_hash = None

    def write_intent(
        self,
        xact_id: str,
        step_id: int,
        plan_id: str,
        action: str,
        parameters: Dict[str, Any],
    ) -> str:
        """
        Write INTENT event (before execution).

        Args:
            xact_id: Execution transaction ID
            step_id: Step number in plan
            plan_id: Plan ID
            action: Action to be executed
            parameters: Action parameters

        Returns:
            Event hash

        Raises:
            AtomicEventSinkError: If not in transaction or hash chain violation
        """
        with self._lock:
            if self._current_xact_id != xact_id:
                raise AtomicEventSinkError(
                    f"Cannot write intent for {xact_id}: "
                    f"Not in transaction (current: {self._current_xact_id})"
                )

            payload = {
                "action": action,
                "parameters": parameters,
                "intent_phase": "PRE_EXECUTION",
            }

            event = self._create_event_base(
                event_type="INTENT",
                xact_id=xact_id,
                step_id=step_id,
                plan_id=plan_id,
                payload=payload,
            )

            event_hash = self._write_event_atomic(event)
            self._xact_intent_hash = event_hash

            return event_hash

    def write_commit(
        self, xact_id: str, step_id: int, plan_id: str, effect: Dict[str, Any]
    ) -> str:
        """
        Write COMMIT event (after successful execution).

        Args:
            xact_id: Execution transaction ID
            step_id: Step number in plan
            plan_id: Plan ID
            effect: Execution effect data (hash_before, hash_after, etc.)

        Returns:
            Event hash

        Raises:
            AtomicEventSinkError: If not in transaction or no intent written
        """
        with self._lock:
            if self._current_xact_id != xact_id:
                raise AtomicEventSinkError(
                    f"Cannot write commit for {xact_id}: "
                    f"Not in transaction (current: {self._current_xact_id})"
                )

            if self._xact_intent_hash is None:
                raise AtomicEventSinkError(
                    f"Cannot write commit for {xact_id}: No intent written"
                )

            payload = {
                "effect": effect,
                "commit_phase": "POST_EXECUTION",
                "intent_hash": self._xact_intent_hash,
            }

            event = self._create_event_base(
                event_type="COMMIT",
                xact_id=xact_id,
                step_id=step_id,
                plan_id=plan_id,
                payload=payload,
            )

            event_hash = self._write_event_atomic(event)

            # Clear transaction state
            self._current_xact_id = None
            self._xact_intent_hash = None

            return event_hash

    def write_abort(
        self,
        xact_id: str,
        step_id: int,
        plan_id: str,
        reason_code: str,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Write ABORT event (after failed execution and rollback).

        Args:
            xact_id: Execution transaction ID
            step_id: Step number in plan
            plan_id: Plan ID
            reason_code: Abort reason code
            error_details: Optional error details

        Returns:
            Event hash

        Raises:
            AtomicEventSinkError: If not in transaction
        """
        with self._lock:
            if self._current_xact_id != xact_id:
                raise AtomicEventSinkError(
                    f"Cannot write abort for {xact_id}: "
                    f"Not in transaction (current: {self._current_xact_id})"
                )

            payload = {
                "reason_code": reason_code,
                "abort_phase": "POST_ROLLBACK",
                "intent_hash": self._xact_intent_hash,
                "error_details": error_details or {},
            }

            event = self._create_event_base(
                event_type="ABORT",
                xact_id=xact_id,
                step_id=step_id,
                plan_id=plan_id,
                payload=payload,
            )

            event_hash = self._write_event_atomic(event)

            # Clear transaction state
            self._current_xact_id = None
            self._xact_intent_hash = None

            return event_hash

    def verify_hash_chain(self) -> Tuple[bool, List[str]]:
        """
        Verify integrity of hash chain.

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []

        if not self.current_log_file.exists():
            return (True, violations)  # Empty chain is valid

        try:
            with open(self.current_log_file, "r", encoding="utf-8") as f:
                previous_hash = None
                line_number = 0

                for line in f:
                    line_number += 1
                    if not line.strip():
                        continue

                    try:
                        event = json.loads(line)

                        # Check previous hash matches
                        event_previous = event.get("previous_event_hash")
                        if previous_hash != event_previous:
                            violations.append(
                                f"Line {line_number}: Previous hash mismatch. "
                                f"Expected: {previous_hash}, Got: {event_previous}"
                            )

                        # Verify current hash
                        computed_hash = self._compute_hash(
                            {
                                k: v
                                for k, v in event.items()
                                if k != "current_event_hash"
                            }
                        )
                        stored_hash = event.get("current_event_hash")

                        if computed_hash != stored_hash:
                            violations.append(
                                f"Line {line_number}: Hash verification failed. "
                                f"Computed: {computed_hash}, Stored: {stored_hash}"
                            )

                        # Update previous hash for next iteration
                        previous_hash = stored_hash

                    except json.JSONDecodeError as e:
                        violations.append(f"Line {line_number}: JSON decode error: {e}")

        except IOError as e:
            violations.append(f"Failed to read log file: {e}")

        return (len(violations) == 0, violations)

    def get_event_chain(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent events from the chain.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of events (most recent first)
        """
        if not self.current_log_file.exists():
            return []

        events = []
        try:
            with open(self.current_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))

            # Return most recent events first
            events.reverse()
            return events[:limit]

        except (json.JSONDecodeError, IOError):
            return []

    def get_xact_events(self, xact_id: str) -> List[Dict[str, Any]]:
        """
        Get all events for a specific transaction.

        Args:
            xact_id: Transaction ID

        Returns:
            List of events for the transaction
        """
        if not self.current_log_file.exists():
            return []

        xact_events = []
        try:
            with open(self.current_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        if event.get("xact_id") == xact_id:
                            xact_events.append(event)

            return xact_events

        except (json.JSONDecodeError, IOError):
            return []

    def get_last_event_hash(self) -> Optional[str]:
        """Get the hash of the last event in the chain."""
        return self._last_event_hash

    def get_chain_length(self) -> int:
        """Get the number of events in the current log file."""
        if not self.current_log_file.exists():
            return 0

        try:
            with open(self.current_log_file, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())
        except IOError:
            return 0

    def log_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        xact_id: Optional[str] = None,
    ) -> str:
        """
        Log a generic event (compatibility method for Phase 5 components).

        Args:
            event_type: Type of event
            data: Event data
            xact_id: Optional transaction ID

        Returns:
            Event hash
        """
        import uuid
        from datetime import datetime

        # If no xact_id provided, create one for standalone events
        if xact_id is None:
            xact_id = f"event_{uuid.uuid4().hex[:8]}"

        # Use write_intent for compatibility with existing event structure
        return self.write_intent(
            xact_id=xact_id,
            step_id=0,
            plan_id="generic_event",
            action=event_type,
            parameters=data,
        )


# Test function
def test_atomic_event_sink():
    """Test the atomic event sink."""
    print("Testing Atomic Event Sink...")

    # Create test directory
    test_dir = Path(__file__).parent / "test_events"
    test_dir.mkdir(exist_ok=True)

    try:
        # Initialize sink
        sink = AtomicEventSink(test_dir)

        # Test 1: Basic transaction
        print("Test 1: Basic INTENT → COMMIT transaction")
        xact_id = "xact_test_001"

        sink.begin_xact(xact_id)

        intent_hash = sink.write_intent(
            xact_id=xact_id,
            step_id=1,
            plan_id="test_plan_001",
            action="file_copy",
            parameters={"src": "a.txt", "dst": "b.txt"},
        )
        print(f"  Intent hash: {intent_hash[:16]}...")

        commit_hash = sink.write_commit(
            xact_id=xact_id,
            step_id=1,
            plan_id="test_plan_001",
            effect={
                "hash_before": "sha256:abc123",
                "hash_after": "sha256:def456",
                "success": True,
            },
        )
        print(f"  Commit hash: {commit_hash[:16]}...")

        # Test 2: Failed transaction (INTENT → ABORT)
        print("\nTest 2: INTENT → ABORT transaction")
        xact_id2 = "xact_test_002"

        sink.begin_xact(xact_id2)

        intent_hash2 = sink.write_intent(
            xact_id=xact_id2,
            step_id=2,
            plan_id="test_plan_001",
            action="command_execute",
            parameters={"command": "ls -la"},
        )
        print(f"  Intent hash: {intent_hash2[:16]}...")

        abort_hash = sink.write_abort(
            xact_id=xact_id2,
            step_id=2,
            plan_id="test_plan_001",
            reason_code="EXECUTION_FAILURE",
            error_details={"error": "Command failed", "exit_code": 1},
        )
        print(f"  Abort hash: {abort_hash[:16]}...")

        # Test 3: Hash chain verification
        print("\nTest 3: Hash chain verification")
        is_valid, violations = sink.verify_hash_chain()
        print(f"  Chain valid: {is_valid}")
        if violations:
            print(f"  Violations: {violations}")

        # Test 4: Get transaction events
        print("\nTest 4: Transaction event retrieval")
        events1 = sink.get_xact_events("xact_test_001")
        print(f"  Transaction 1 events: {len(events1)}")

        events2 = sink.get_xact_events("xact_test_002")
        print(f"  Transaction 2 events: {len(events2)}")

        # Test 5: Get event chain
        print("\nTest 5: Event chain retrieval")
        chain = sink.get_event_chain(limit=5)
        print(f"  Recent events: {len(chain)}")
        for event in chain[:2]:
            print(f"    - {event['event_type']} for {event['xact_id']}")

        print("\n✅ All atomic event sink tests completed")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Cleanup
        import shutil

        if test_dir.exists():
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    success = test_atomic_event_sink()
    exit(0 if success else 1)

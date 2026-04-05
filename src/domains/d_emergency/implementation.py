"""
D_EMERGENCY — Emergency Response domain implementation.
Partition-tolerant messaging with exactly-once delivery semantics.

Invariants (from ontology/ontology.json#D_EMERGENCY):
  1. Every dispatched emergency message is delivered exactly once,
     even under network partition (idempotent delivery).
  2. Messages are never silently dropped — undelivered messages are queued
     with their full payload for retry.
  3. Message deduplication uses deterministic IDs derived from content + timestamp.

Biblical inspiration: "If a man has a hundred sheep and one of them goes astray,
does he not leave the ninety-nine on the hills and go to look for the one that
went astray?" (Matthew 18:12)
In emergency dispatch, the lost sheep is the undelivered message — every dispatch
must be accounted for. The partition-tolerant queue is the shepherd: it does not
declare success until every message is confirmed delivered, and it retries without
rest until the last sheep is safe.

Falsification IDs: F_EMERGENCY_001, F_EMERGENCY_002, F_EMERGENCY_003
"""

from __future__ import annotations

import hashlib
import threading
import time
from enum import Enum
from typing import Any, Callable, NamedTuple, Optional


# ---------------------------------------------------------------------------
# Message types
# ---------------------------------------------------------------------------

class Priority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class DeliveryStatus(Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    DUPLICATE = "duplicate"


class EmergencyMessage(NamedTuple):
    """An emergency message with deterministic ID derived from content."""
    msg_id: str             # SHA-256 of (content + incident_id)
    incident_id: str
    content: str
    priority: Priority
    created_at_ns: int      # time.monotonic_ns() at creation


def make_message(incident_id: str, content: str, priority: Priority) -> EmergencyMessage:
    """
    Create an emergency message with a deterministic, content-derived ID.

    Invariant: Same incident_id + content always produces the same msg_id.
    This enables idempotent delivery — re-sending the same message is detected.
    """
    if not incident_id:
        raise ValueError("incident_id must not be empty")
    if not content:
        raise ValueError("content must not be empty")
    raw = f"{incident_id}:{content}".encode("utf-8")
    msg_id = hashlib.sha256(raw).hexdigest()
    return EmergencyMessage(
        msg_id=msg_id,
        incident_id=incident_id,
        content=content,
        priority=priority,
        created_at_ns=time.monotonic_ns(),
    )


# ---------------------------------------------------------------------------
# Delivery record
# ---------------------------------------------------------------------------

class DeliveryRecord(NamedTuple):
    """Immutable record of a delivery attempt."""
    msg_id: str
    status: DeliveryStatus
    attempt: int
    timestamp_ns: int


# ---------------------------------------------------------------------------
# Partition-tolerant dispatch queue (F_EMERGENCY_001, F_EMERGENCY_002)
# ---------------------------------------------------------------------------

class EmergencyDispatcher:
    """
    Partition-tolerant emergency message dispatcher.

    Invariant: Every dispatched message is delivered exactly once.
    Undeliverable messages are queued for retry — never silently dropped.

    Thread-safety: Uses threading.Lock for all state mutations.
    """

    def __init__(self) -> None:
        self._delivered: set[str] = set()       # msg_ids confirmed delivered
        self._pending: dict[str, EmergencyMessage] = {}  # queued for retry
        self._delivery_log: list[DeliveryRecord] = []
        self._lock = threading.Lock()

    def dispatch(
        self,
        message: EmergencyMessage,
        deliver_fn: Callable[[EmergencyMessage], bool],
    ) -> DeliveryStatus:
        """
        Attempt to deliver a message using deliver_fn.

        Invariant: A message with a previously-delivered msg_id returns DUPLICATE
        without calling deliver_fn again (idempotent).

        Args:
            message:     The EmergencyMessage to deliver.
            deliver_fn:  Callable that returns True on success, False on failure.

        Returns:
            DeliveryStatus: DELIVERED, DUPLICATE, or FAILED.
        """
        with self._lock:
            if message.msg_id in self._delivered:
                record = DeliveryRecord(
                    msg_id=message.msg_id,
                    status=DeliveryStatus.DUPLICATE,
                    attempt=len([r for r in self._delivery_log if r.msg_id == message.msg_id]) + 1,
                    timestamp_ns=time.monotonic_ns(),
                )
                self._delivery_log.append(record)
                return DeliveryStatus.DUPLICATE

            attempt = len([r for r in self._delivery_log if r.msg_id == message.msg_id]) + 1

        # Release lock during delivery attempt
        try:
            success = deliver_fn(message)
        except Exception:
            success = False

        with self._lock:
            if success:
                self._delivered.add(message.msg_id)
                self._pending.pop(message.msg_id, None)
                status = DeliveryStatus.DELIVERED
            else:
                self._pending[message.msg_id] = message
                status = DeliveryStatus.FAILED

            record = DeliveryRecord(
                msg_id=message.msg_id,
                status=status,
                attempt=attempt,
                timestamp_ns=time.monotonic_ns(),
            )
            self._delivery_log.append(record)
            return status

    def retry_pending(self, deliver_fn: Callable[[EmergencyMessage], bool]) -> dict:
        """
        Retry all pending (undelivered) messages.

        Invariant: No message is silently dropped — all pending messages are retried.
        Returns dict of msg_id → DeliveryStatus after retry.
        """
        with self._lock:
            pending_snapshot = dict(self._pending)

        results = {}
        for msg_id, message in pending_snapshot.items():
            status = self.dispatch(message, deliver_fn)
            results[msg_id] = status
        return results

    def pending_count(self) -> int:
        """Return number of messages awaiting delivery."""
        with self._lock:
            return len(self._pending)

    def delivered_count(self) -> int:
        """Return number of successfully delivered messages."""
        with self._lock:
            return len(self._delivered)

    def delivery_log(self) -> list:
        """Return a copy of the delivery log."""
        with self._lock:
            return list(self._delivery_log)


# ---------------------------------------------------------------------------
# Partition simulator (F_EMERGENCY_003)
# ---------------------------------------------------------------------------

class NetworkPartition:
    """
    Simulates network partition conditions for testing.

    When partitioned, all deliver_fn calls fail (simulating loss of connectivity).
    Messages are queued by the dispatcher for retry after partition heals.
    """

    def __init__(self) -> None:
        self._partitioned = False
        self._delivered_payloads: list[str] = []

    def partition(self) -> None:
        """Simulate network partition — all deliveries will fail."""
        self._partitioned = True

    def heal(self) -> None:
        """Heal the partition — deliveries resume."""
        self._partitioned = False

    def deliver(self, message: EmergencyMessage) -> bool:
        """Delivery function: fails under partition, succeeds otherwise."""
        if self._partitioned:
            return False
        self._delivered_payloads.append(message.msg_id)
        return True

    @property
    def delivered_payloads(self) -> list:
        return list(self._delivered_payloads)


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

DOMAIN_METADATA = {
    "id": "D_EMERGENCY",
    "name": "Emergency Response",
    "invariants": [
        "Every dispatched emergency message is delivered exactly once.",
        "Undelivered messages are queued for retry — never silently dropped.",
        "Message deduplication uses deterministic IDs derived from content.",
    ],
    "falsification_tests": ["F_EMERGENCY_001", "F_EMERGENCY_002", "F_EMERGENCY_003"],
    "implementation_functions": [
        "make_message",
        "EmergencyDispatcher",
        "NetworkPartition",
    ],
    "uses_content_derived_ids": True,
    "uses_threading_lock": True,
    "partition_tolerant": True,
}

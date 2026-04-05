"""
D_FINANCIAL — Financial domain implementation.
Double-spend detection with thread-safe settlement ledger.

Invariants (from ontology/ontology.json#D_FINANCIAL):
  1. No transaction ID may be settled more than once (double-spend prevention).
  2. Settlement operations are atomic under concurrent access.
  3. Every settlement attempt produces an immutable audit record.

Biblical inspiration: "Honest scales and balances belong to the LORD; all the weights
in the bag are of his making." (Proverbs 16:11)
The settlement ledger is the scale — every transaction must be weighed exactly once.
A double-spend is a false weight in the bag: it corrupts the measure and violates
the Lord's standard of honest exchange. Thread-safety is the divine balance arm.

Falsification IDs: F_FINANCIAL_001, F_FINANCIAL_002, F_FINANCIAL_003
"""

from __future__ import annotations

import threading
import time
from typing import NamedTuple, Optional


# ---------------------------------------------------------------------------
# Audit record
# ---------------------------------------------------------------------------

class SettlementRecord(NamedTuple):
    """Immutable record of a settlement attempt."""
    tx_id: str
    accepted: bool          # True = first settlement, False = duplicate rejected
    timestamp_ns: int       # time.monotonic_ns() at time of attempt
    attempt_number: int     # 1 = first ever, 2+ = duplicate


# ---------------------------------------------------------------------------
# Settlement ledger (F_FINANCIAL_001, F_FINANCIAL_002)
# ---------------------------------------------------------------------------

class SettlementSystem:
    """
    Thread-safe settlement ledger that enforces exactly-once semantics.

    Invariant: No transaction ID may be settled more than once.
    Falsification: If settle() returns True for a previously settled tx_id,
    F_FINANCIAL_001 is violated.

    Thread-safety: Uses threading.Lock to guarantee atomicity.
    Falsification: If two concurrent settle() calls on the same tx_id both return True,
    F_FINANCIAL_002 is violated.
    """

    def __init__(self) -> None:
        self._settled: dict[str, int] = {}      # tx_id -> attempt_count
        self._lock = threading.Lock()
        self._audit_log: list[SettlementRecord] = []

    def settle(self, tx_id: str) -> bool:
        """
        Attempt to settle a transaction.

        Returns True if this is the first settlement of tx_id.
        Returns False if tx_id has already been settled (double-spend detected).

        Raises:
            ValueError: If tx_id is empty.
        """
        if not tx_id:
            raise ValueError("tx_id must not be empty")

        with self._lock:
            attempt = self._settled.get(tx_id, 0) + 1
            self._settled[tx_id] = attempt

            if attempt == 1:
                accepted = True
            else:
                accepted = False

            record = SettlementRecord(
                tx_id=tx_id,
                accepted=accepted,
                timestamp_ns=time.monotonic_ns(),
                attempt_number=attempt,
            )
            self._audit_log.append(record)
            return accepted

    def audit_log(self) -> list:
        """Return a copy of the immutable audit log."""
        with self._lock:
            return list(self._audit_log)

    def is_settled(self, tx_id: str) -> bool:
        """Check whether a tx_id has already been settled."""
        with self._lock:
            return self._settled.get(tx_id, 0) >= 1

    def settled_count(self) -> int:
        """Return the number of unique settled transactions."""
        with self._lock:
            return sum(1 for count in self._settled.values() if count >= 1)

    def reset(self) -> None:
        """Reset the ledger (only for testing — not a production operation)."""
        with self._lock:
            self._settled.clear()
            self._audit_log.clear()


# ---------------------------------------------------------------------------
# Concurrent double-spend stress test (F_FINANCIAL_002)
# ---------------------------------------------------------------------------

def attempt_concurrent_double_spend(
    system: SettlementSystem,
    tx_id: str,
    n_threads: int = 10,
) -> dict:
    """
    Attempt to settle the same tx_id from n_threads simultaneously.

    Returns a dict with:
        accepted_count: number of threads that got True
        rejected_count: number of threads that got False
        invariant_holds: True iff accepted_count == 1

    Invariant: Exactly one thread must succeed (accepted_count == 1).
    Falsification: If accepted_count != 1, F_FINANCIAL_002 is violated.
    """
    results: list[bool] = [False] * n_threads
    barrier = threading.Barrier(n_threads)

    def worker(i: int) -> None:
        barrier.wait()  # All threads start simultaneously
        results[i] = system.settle(tx_id)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    accepted = sum(1 for r in results if r)
    rejected = sum(1 for r in results if not r)
    return {
        "accepted_count": accepted,
        "rejected_count": rejected,
        "invariant_holds": accepted == 1,
    }


# ---------------------------------------------------------------------------
# Audit trail (F_FINANCIAL_003)
# ---------------------------------------------------------------------------

class AuditViolationError(Exception):
    """Raised when the audit trail is inconsistent with the settlement ledger."""


def verify_audit_integrity(system: SettlementSystem) -> bool:
    """
    Verify that the audit log is consistent with the settlement state.

    Invariant: Every settled tx_id must appear in the audit log with accepted=True.
    Falsification: If a settled tx_id has no accepted record, F_FINANCIAL_003 fails.

    Returns True if audit is consistent.
    Raises AuditViolationError if inconsistency is found.
    """
    log = system.audit_log()
    # Build set of tx_ids that have an accepted record
    accepted_in_log = {r.tx_id for r in log if r.accepted}
    # Build set of settled tx_ids from state
    settled_ids = {tx_id for tx_id, count in system._settled.items() if count >= 1}

    missing = settled_ids - accepted_in_log
    if missing:
        raise AuditViolationError(
            f"Audit log missing accepted records for: {sorted(missing)} — F_FINANCIAL_003"
        )
    return True


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

DOMAIN_METADATA = {
    "id": "D_FINANCIAL",
    "name": "Financial",
    "invariants": [
        "No transaction ID may be settled more than once.",
        "Settlement operations are atomic under concurrent access.",
        "Every settlement attempt produces an immutable audit record.",
    ],
    "falsification_tests": ["F_FINANCIAL_001", "F_FINANCIAL_002", "F_FINANCIAL_003"],
    "implementation_functions": [
        "SettlementSystem",
        "attempt_concurrent_double_spend",
        "verify_audit_integrity",
    ],
    "uses_threading_lock": True,
    "uses_immutable_audit_log": True,
}

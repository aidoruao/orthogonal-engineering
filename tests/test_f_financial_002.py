"""
Falsification test suite for D_FINANCIAL domain.

Tests double-spend prevention, concurrent atomicity, and audit trail integrity.

# @falsification_id: F_FINANCIAL_001, F_FINANCIAL_002, F_FINANCIAL_003
"""

import threading
import pytest

from src.domains.d_financial.implementation import (
    AuditViolationError,
    SettlementRecord,
    SettlementSystem,
    attempt_concurrent_double_spend,
    verify_audit_integrity,
)


# ---------------------------------------------------------------------------
# F_FINANCIAL_001 — Double-spend prevention (sequential)
# ---------------------------------------------------------------------------

def test_first_settlement_accepted():
    """First settle() for a tx_id must return True."""
    system = SettlementSystem()
    assert system.settle("tx_001") is True


def test_second_settlement_rejected():
    """Second settle() for the same tx_id must return False."""
    system = SettlementSystem()
    system.settle("tx_002")
    assert system.settle("tx_002") is False


def test_different_tx_ids_accepted():
    """Different tx_ids are independent — each first settle returns True."""
    system = SettlementSystem()
    assert system.settle("tx_a") is True
    assert system.settle("tx_b") is True
    assert system.settle("tx_c") is True


def test_empty_tx_id_raises():
    """Empty string tx_id must raise ValueError."""
    system = SettlementSystem()
    with pytest.raises(ValueError):
        system.settle("")


def test_is_settled_reflects_state():
    """is_settled() must return True only for tx_ids that have been settled."""
    system = SettlementSystem()
    assert system.is_settled("tx_x") is False
    system.settle("tx_x")
    assert system.is_settled("tx_x") is True


def test_settled_count_unique_only():
    """settled_count() must count unique tx_ids, not total attempts."""
    system = SettlementSystem()
    system.settle("t1")
    system.settle("t2")
    system.settle("t1")  # duplicate
    assert system.settled_count() == 2


def test_many_duplicates_still_one_settlement():
    """10 duplicate settle() calls must result in exactly 1 accepted."""
    system = SettlementSystem()
    results = [system.settle("same_tx") for _ in range(10)]
    assert results.count(True) == 1
    assert results.count(False) == 9


# ---------------------------------------------------------------------------
# F_FINANCIAL_002 — Concurrent double-spend prevention
# ---------------------------------------------------------------------------

def test_concurrent_double_spend_exactly_one_wins():
    """Exactly one thread must succeed when N threads race to settle the same tx_id."""
    system = SettlementSystem()
    result = attempt_concurrent_double_spend(system, "race_tx_001", n_threads=10)
    assert result["invariant_holds"] is True
    assert result["accepted_count"] == 1
    assert result["rejected_count"] == 9


def test_concurrent_stress_20_threads():
    """20-thread stress test must still settle exactly once."""
    system = SettlementSystem()
    result = attempt_concurrent_double_spend(system, "stress_tx_002", n_threads=20)
    assert result["accepted_count"] == 1


def test_concurrent_multiple_distinct_tx_ids():
    """Concurrent distinct tx_ids must each be settled exactly once."""
    system = SettlementSystem()
    n = 50
    results = [None] * n
    barrier = threading.Barrier(n)

    def worker(i):
        barrier.wait()
        results[i] = system.settle(f"distinct_tx_{i}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(r is True for r in results), "Each distinct tx_id must be accepted once"
    assert system.settled_count() == n


# ---------------------------------------------------------------------------
# F_FINANCIAL_003 — Audit trail integrity
# ---------------------------------------------------------------------------

def test_audit_log_has_record_for_every_attempt():
    """Audit log must contain one record per settle() call."""
    system = SettlementSystem()
    system.settle("audit_tx_001")
    system.settle("audit_tx_001")  # duplicate
    log = system.audit_log()
    assert len(log) == 2


def test_audit_record_first_is_accepted():
    """First record in audit log must have accepted=True."""
    system = SettlementSystem()
    system.settle("aud_002")
    log = system.audit_log()
    assert log[0].accepted is True
    assert log[0].tx_id == "aud_002"


def test_audit_record_duplicate_is_rejected():
    """Duplicate attempt record must have accepted=False."""
    system = SettlementSystem()
    system.settle("aud_003")
    system.settle("aud_003")
    log = system.audit_log()
    assert log[1].accepted is False
    assert log[1].attempt_number == 2


def test_audit_integrity_passes_for_valid_state():
    """verify_audit_integrity must not raise for consistent state."""
    system = SettlementSystem()
    system.settle("int_tx_a")
    system.settle("int_tx_b")
    verify_audit_integrity(system)  # must not raise


def test_audit_log_is_copy():
    """audit_log() must return a copy — mutations must not affect internal state."""
    system = SettlementSystem()
    system.settle("copy_tx")
    log = system.audit_log()
    log.clear()
    assert len(system.audit_log()) == 1

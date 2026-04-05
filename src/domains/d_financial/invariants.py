"""
D_FINANCIAL invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ontology/ontology.json#D_FINANCIAL
"""

from src.domains.d_financial.implementation import (
    SettlementSystem,
    AuditViolationError,
    attempt_concurrent_double_spend,
    verify_audit_integrity,
)


def check_double_spend_rejected_sequential() -> bool:
    """
    Invariant: No transaction ID may be settled more than once.
    Falsification: If settle() returns True for a previously settled tx_id, F_FINANCIAL_001 fails.
    """
    system = SettlementSystem()
    tx = "test_tx_001"
    r1 = system.settle(tx)
    r2 = system.settle(tx)
    assert r1 is True, f"First settle must return True, got {r1}"
    assert r2 is False, f"Second settle must return False (double-spend), got {r2}"
    return True


def check_double_spend_rejected_concurrent() -> bool:
    """
    Invariant: Settlement operations are atomic under concurrent access.
    Falsification: If two concurrent settle() calls both return True, F_FINANCIAL_002 fails.
    """
    system = SettlementSystem()
    result = attempt_concurrent_double_spend(system, "concurrent_tx_001", n_threads=10)
    assert result["invariant_holds"], (
        f"Concurrent double-spend allowed: {result['accepted_count']} threads accepted — "
        "F_FINANCIAL_002 VIOLATED"
    )
    assert result["accepted_count"] == 1
    assert result["rejected_count"] == 9
    return True


def check_audit_log_populated() -> bool:
    """
    Invariant: Every settlement attempt produces an audit record.
    Falsification: If audit_log is empty after settlement, F_FINANCIAL_003 fails.
    """
    system = SettlementSystem()
    system.settle("audit_tx_001")
    system.settle("audit_tx_001")  # duplicate
    log = system.audit_log()
    assert len(log) == 2, f"Audit log must have 2 entries, got {len(log)}"
    assert log[0].accepted is True
    assert log[1].accepted is False
    return True


def check_audit_integrity_passes_after_valid_settlements() -> bool:
    """
    Invariant: Audit log is consistent with settlement state.
    Falsification: verify_audit_integrity should not raise for valid operations.
    """
    system = SettlementSystem()
    system.settle("tx_a")
    system.settle("tx_b")
    system.settle("tx_a")  # duplicate — should not affect integrity
    try:
        verify_audit_integrity(system)
    except AuditViolationError as e:
        raise AssertionError(f"Audit integrity check failed unexpectedly: {e}")
    return True


def check_empty_tx_id_rejected() -> bool:
    """
    Invariant: Empty transaction IDs are rejected at the API boundary.
    Falsification: If settle("") returns True, the invariant is structurally undermined.
    """
    system = SettlementSystem()
    raised = False
    try:
        system.settle("")
    except ValueError:
        raised = True
    assert raised, "settle('') must raise ValueError"
    return True


def check_settled_count_correct() -> bool:
    """
    Invariant: settled_count() returns the number of unique settled transactions.
    Falsification: If settled_count mismatches unique accepted tx_ids, audit is unreliable.
    """
    system = SettlementSystem()
    system.settle("t1")
    system.settle("t2")
    system.settle("t1")  # duplicate — must not increment count
    assert system.settled_count() == 2, (
        f"settled_count must be 2 (unique), got {system.settled_count()}"
    )
    return True


def run_all_invariants() -> dict:
    """Run all D_FINANCIAL invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_double_spend_rejected_sequential,
        check_double_spend_rejected_concurrent,
        check_audit_log_populated,
        check_audit_integrity_passes_after_valid_settlements,
        check_empty_tx_id_rejected,
        check_settled_count_correct,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_FINANCIAL invariants: PASS")

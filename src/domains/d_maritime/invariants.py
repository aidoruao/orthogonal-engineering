"""D_MARITIME invariant checks."""

from src.domains.d_maritime.implementation import (
    MaritimeRecord,
    MaritimeStatus,
    MaritimeChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = MaritimeChecker()
    compliant = MaritimeRecord(record_id="T1", status=MaritimeStatus.COMPLIANT)
    non_compliant = MaritimeRecord(record_id="T2", status=MaritimeStatus.NON_COMPLIANT)
    assert checker.check_compliance(compliant)["compliant"] is True
    assert checker.check_compliance(non_compliant)["compliant"] is False
    return True

def run_all_invariants() -> dict:
    results = {}
    for name, fn in [("compliance_deterministic", check_compliance_deterministic)]:
        try:
            fn()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    return results

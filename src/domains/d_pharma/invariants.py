"""D_PHARMA invariant checks."""

from src.domains.d_pharma.implementation import (
    PharmaRecord,
    PharmaStatus,
    PharmaChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = PharmaChecker()
    compliant = PharmaRecord(record_id="T1", status=PharmaStatus.COMPLIANT)
    non_compliant = PharmaRecord(record_id="T2", status=PharmaStatus.NON_COMPLIANT)
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

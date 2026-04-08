"""D_PEANO_EXT invariant checks."""

from src.domains.d_peano_ext.implementation import (
    Peano_ExtRecord,
    Peano_ExtStatus,
    Peano_ExtChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = Peano_ExtChecker()
    compliant = Peano_ExtRecord(record_id="T1", status=Peano_ExtStatus.COMPLIANT)
    non_compliant = Peano_ExtRecord(record_id="T2", status=Peano_ExtStatus.NON_COMPLIANT)
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

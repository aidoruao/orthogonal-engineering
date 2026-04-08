"""D_ARC_AGI_3 invariant checks."""

from src.domains.d_arc_agi_3.implementation import (
    Arc_Agi_3Record,
    Arc_Agi_3Status,
    Arc_Agi_3Checker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = Arc_Agi_3Checker()
    compliant = Arc_Agi_3Record(record_id="T1", status=Arc_Agi_3Status.COMPLIANT)
    non_compliant = Arc_Agi_3Record(record_id="T2", status=Arc_Agi_3Status.NON_COMPLIANT)
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

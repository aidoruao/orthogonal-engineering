"""D_EPISTEMIC_LOGIC invariant checks."""

from src.domains.d_epistemic_logic.implementation import (
    Epistemic_LogicRecord,
    Epistemic_LogicStatus,
    Epistemic_LogicChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = Epistemic_LogicChecker()
    compliant = Epistemic_LogicRecord(record_id="T1", status=Epistemic_LogicStatus.COMPLIANT)
    non_compliant = Epistemic_LogicRecord(record_id="T2", status=Epistemic_LogicStatus.NON_COMPLIANT)
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

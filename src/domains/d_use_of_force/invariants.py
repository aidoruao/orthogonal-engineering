"""D_USE_OF_FORCE invariant checks."""
from src.domains.d_use_of_force.implementation import Use_Of_ForceRecord, Use_Of_ForceStatus, Use_Of_ForceChecker

def check_compliance_deterministic() -> bool:
    checker = Use_Of_ForceChecker()
    compliant = Use_Of_ForceRecord(record_id="T1", status=Use_Of_ForceStatus.COMPLIANT)
    non_compliant = Use_Of_ForceRecord(record_id="T2", status=Use_Of_ForceStatus.NON_COMPLIANT)
    assert checker.check_compliance(compliant)["compliant"] is True
    assert checker.check_compliance(non_compliant)["compliant"] is False
    return True

def run_all_invariants() -> dict:
    results = {}
    try:
        check_compliance_deterministic()
        results["compliance_deterministic"] = "PASS"
    except Exception as e:
        results["compliance_deterministic"] = f"ERROR: {e}"
    return results

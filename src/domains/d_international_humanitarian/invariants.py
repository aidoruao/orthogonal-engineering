"""D_INTERNATIONAL_HUMANITARIAN invariant checks."""
from src.domains.d_international_humanitarian.implementation import International_HumaniRecord, International_HumaniStatus, International_HumaniChecker

def check_compliance_deterministic() -> bool:
    checker = International_HumaniChecker()
    compliant = International_HumaniRecord(record_id="T1", status=International_HumaniStatus.COMPLIANT)
    non_compliant = International_HumaniRecord(record_id="T2", status=International_HumaniStatus.NON_COMPLIANT)
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

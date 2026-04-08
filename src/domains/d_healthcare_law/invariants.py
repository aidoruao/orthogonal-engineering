"""D_HEALTHCARE_LAW invariant checks."""
from src.domains.d_healthcare_law.implementation import Healthcare_LawRecord, Healthcare_LawStatus, Healthcare_LawChecker

def check_compliance_deterministic() -> bool:
    checker = Healthcare_LawChecker()
    compliant = Healthcare_LawRecord(record_id="T1", status=Healthcare_LawStatus.COMPLIANT)
    non_compliant = Healthcare_LawRecord(record_id="T2", status=Healthcare_LawStatus.NON_COMPLIANT)
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

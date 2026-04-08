"""D_INSURANCE invariant checks."""
from src.domains.d_insurance.implementation import InsuranceRecord, InsuranceStatus, InsuranceChecker

def check_compliance_deterministic() -> bool:
    checker = InsuranceChecker()
    compliant = InsuranceRecord(record_id="T1", status=InsuranceStatus.COMPLIANT)
    non_compliant = InsuranceRecord(record_id="T2", status=InsuranceStatus.NON_COMPLIANT)
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

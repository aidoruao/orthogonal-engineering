"""D_INTERNATIONAL_CRIMINAL invariant checks."""
from src.domains.d_international_criminal.implementation import International_CriminRecord, International_CriminStatus, International_CriminChecker

def check_compliance_deterministic() -> bool:
    checker = International_CriminChecker()
    compliant = International_CriminRecord(record_id="T1", status=International_CriminStatus.COMPLIANT)
    non_compliant = International_CriminRecord(record_id="T2", status=International_CriminStatus.NON_COMPLIANT)
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

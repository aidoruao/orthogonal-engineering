"""D_PROPERTY_LAW invariant checks."""
from src.domains.d_property_law.implementation import Property_LawRecord, Property_LawStatus, Property_LawChecker

def check_compliance_deterministic() -> bool:
    checker = Property_LawChecker()
    compliant = Property_LawRecord(record_id="T1", status=Property_LawStatus.COMPLIANT)
    non_compliant = Property_LawRecord(record_id="T2", status=Property_LawStatus.NON_COMPLIANT)
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

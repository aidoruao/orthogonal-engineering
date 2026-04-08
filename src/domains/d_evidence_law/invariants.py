"""D_EVIDENCE_LAW invariant checks."""
from src.domains.d_evidence_law.implementation import Evidence_LawRecord, Evidence_LawStatus, Evidence_LawChecker

def check_compliance_deterministic() -> bool:
    checker = Evidence_LawChecker()
    compliant = Evidence_LawRecord(record_id="T1", status=Evidence_LawStatus.COMPLIANT)
    non_compliant = Evidence_LawRecord(record_id="T2", status=Evidence_LawStatus.NON_COMPLIANT)
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

"""D_PROCEDURE_CIVIL invariant checks."""
from src.domains.d_procedure_civil.implementation import Procedure_CivilRecord, Procedure_CivilStatus, Procedure_CivilChecker

def check_compliance_deterministic() -> bool:
    checker = Procedure_CivilChecker()
    compliant = Procedure_CivilRecord(record_id="T1", status=Procedure_CivilStatus.COMPLIANT)
    non_compliant = Procedure_CivilRecord(record_id="T2", status=Procedure_CivilStatus.NON_COMPLIANT)
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

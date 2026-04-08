"""D_PROCEDURE_CRIMINAL invariant checks."""
from src.domains.d_procedure_criminal.implementation import Procedure_CriminalRecord, Procedure_CriminalStatus, Procedure_CriminalChecker

def check_compliance_deterministic() -> bool:
    checker = Procedure_CriminalChecker()
    compliant = Procedure_CriminalRecord(record_id="T1", status=Procedure_CriminalStatus.COMPLIANT)
    non_compliant = Procedure_CriminalRecord(record_id="T2", status=Procedure_CriminalStatus.NON_COMPLIANT)
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

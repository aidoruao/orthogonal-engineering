"""D_CONTRACT_LAW invariant checks."""
from src.domains.d_contract_law.implementation import Contract_LawRecord, Contract_LawStatus, Contract_LawChecker

def check_compliance_deterministic() -> bool:
    checker = Contract_LawChecker()
    compliant = Contract_LawRecord(record_id="T1", status=Contract_LawStatus.COMPLIANT)
    non_compliant = Contract_LawRecord(record_id="T2", status=Contract_LawStatus.NON_COMPLIANT)
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

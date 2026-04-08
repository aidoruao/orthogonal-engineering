"""D_AI_ONTOLOGICAL_STATUS invariant checks."""

from src.domains.d_ai_ontological_status.implementation import (
    Ai_Ontological_StatuRecord,
    Ai_Ontological_StatuStatus,
    Ai_Ontological_StatuChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = Ai_Ontological_StatuChecker()
    compliant = Ai_Ontological_StatuRecord(record_id="T1", status=Ai_Ontological_StatuStatus.COMPLIANT)
    non_compliant = Ai_Ontological_StatuRecord(record_id="T2", status=Ai_Ontological_StatuStatus.NON_COMPLIANT)
    assert checker.check_compliance(compliant)["compliant"] is True
    assert checker.check_compliance(non_compliant)["compliant"] is False
    return True

def run_all_invariants() -> dict:
    results = {}
    for name, fn in [("compliance_deterministic", check_compliance_deterministic)]:
        try:
            fn()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    return results

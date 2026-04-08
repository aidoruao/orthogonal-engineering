"""D_COMMUNICATIONS invariant checks."""

from src.domains.d_communications.implementation import (
    CommunicationsRecord,
    CommunicationsStatus,
    CommunicationsChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = CommunicationsChecker()
    compliant = CommunicationsRecord(record_id="T1", status=CommunicationsStatus.COMPLIANT)
    non_compliant = CommunicationsRecord(record_id="T2", status=CommunicationsStatus.NON_COMPLIANT)
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

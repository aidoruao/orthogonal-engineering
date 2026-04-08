"""D_ARCHITECTURE_PROOF invariant checks."""

from src.domains.d_architecture_proof.implementation import (
    Architecture_ProofRecord,
    Architecture_ProofStatus,
    Architecture_ProofChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = Architecture_ProofChecker()
    compliant = Architecture_ProofRecord(record_id="T1", status=Architecture_ProofStatus.COMPLIANT)
    non_compliant = Architecture_ProofRecord(record_id="T2", status=Architecture_ProofStatus.NON_COMPLIANT)
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

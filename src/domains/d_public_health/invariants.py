"""D_PUBLICHEALTH invariant checks."""

from datetime import datetime
from src.domains.d_public_health.implementation import (
    PublicHealthRecord,
    PublicHealthStatus,
    PublicHealthComplianceChecker,
)


def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = PublicHealthComplianceChecker()
    
    compliant_record = PublicHealthRecord(
        record_id="TEST001",
        status=PublicHealthStatus.COMPLIANT
    )
    result = checker.check_compliance(compliant_record)
    assert result["compliant"] is True, "Compliant record should pass"
    
    non_compliant = PublicHealthRecord(
        record_id="TEST002",
        status=PublicHealthStatus.NON_COMPLIANT
    )
    result2 = checker.check_compliance(non_compliant)
    assert result2["compliant"] is False, "Non-compliant record should fail"
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks."""
    results = {}
    checks = [
        ("compliance_deterministic", check_compliance_deterministic),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results

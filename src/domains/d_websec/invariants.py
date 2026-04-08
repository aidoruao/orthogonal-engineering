"""D_WEBSECURITY invariant checks."""

from datetime import datetime
from src.domains.d_websec.implementation import (
    WebSecurityRecord,
    WebSecurityStatus,
    WebSecurityComplianceChecker,
)


def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = WebSecurityComplianceChecker()
    
    compliant_record = WebSecurityRecord(
        record_id="TEST001",
        status=WebSecurityStatus.COMPLIANT
    )
    result = checker.check_compliance(compliant_record)
    assert result["compliant"] is True, "Compliant record should pass"
    
    non_compliant = WebSecurityRecord(
        record_id="TEST002",
        status=WebSecurityStatus.NON_COMPLIANT
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

"""D_CAPABILITY_BENCHMARK invariant checks."""

from src.domains.d_capability_benchmark.implementation import (
    Capability_BenchmarkRecord,
    Capability_BenchmarkStatus,
    Capability_BenchmarkChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = Capability_BenchmarkChecker()
    compliant = Capability_BenchmarkRecord(record_id="T1", status=Capability_BenchmarkStatus.COMPLIANT)
    non_compliant = Capability_BenchmarkRecord(record_id="T2", status=Capability_BenchmarkStatus.NON_COMPLIANT)
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

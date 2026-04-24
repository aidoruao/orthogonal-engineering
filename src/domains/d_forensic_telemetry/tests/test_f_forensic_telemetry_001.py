"""Falsification test for D_FORENSIC_TELEMETRY."""

from src.domains.d_forensic_telemetry.invariants import run_all_invariants


def test_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_fail"):
            assert result.startswith("FAIL"), f"Expected FAIL for {name}: {result}"
        else:
            assert result == "PASS", f"Invariant {name} failed: {result}"

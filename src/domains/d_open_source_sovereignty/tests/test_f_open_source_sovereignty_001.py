"""Falsification test for D_OPEN_SOURCE_SOVEREIGNTY."""

from src.domains.d_open_source_sovereignty.invariants import run_all_invariants


def test_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_fail"):
            assert result.startswith("FAIL"), f"Expected FAIL for {name}: {result}"
        else:
            assert result == "PASS", f"Invariant {name} failed: {result}"

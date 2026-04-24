"""Falsification test for D_DAG_THEORY."""

from src.domains.d_dag_theory.invariants import run_all_invariants


def test_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_fail"):
            assert result.startswith("FAIL"), f"Expected FAIL for {name}: {result}"
        else:
            assert result == "PASS", f"Invariant {name} failed: {result}"

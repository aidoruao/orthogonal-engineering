"""Falsification test for D_CROSS_MODEL_BENCHMARKS."""
import pytest
from src.domains.d_cross_model_benchmarks.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

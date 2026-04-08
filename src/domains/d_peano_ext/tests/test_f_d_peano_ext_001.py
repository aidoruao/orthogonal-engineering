"""Falsification test for D_PEANO_EXT."""
import pytest
from src.domains.d_peano_ext.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

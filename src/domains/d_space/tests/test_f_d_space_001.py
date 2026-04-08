"""Falsification test for D_SPACE."""
import pytest
from src.domains.d_space.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

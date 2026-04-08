"""Falsification test for D_NONCREATIVE."""
import pytest
from src.domains.d_noncreative.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

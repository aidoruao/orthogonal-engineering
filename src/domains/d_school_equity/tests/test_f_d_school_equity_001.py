"""Falsification test for D_SCHOOL_EQUITY."""
import pytest
from src.domains.d_school_equity.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

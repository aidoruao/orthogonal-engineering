"""Falsification test for D_RELIGIOUS_LIBERTY."""
import pytest
from src.domains.d_religious_liberty.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

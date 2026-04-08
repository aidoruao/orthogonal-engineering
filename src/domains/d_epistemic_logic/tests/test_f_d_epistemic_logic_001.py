"""Falsification test for D_EPISTEMIC_LOGIC."""
import pytest
from src.domains.d_epistemic_logic.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

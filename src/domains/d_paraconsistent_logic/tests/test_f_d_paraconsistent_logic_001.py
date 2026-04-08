"""Falsification test for D_PARACONSISTENT_LOGIC."""
import pytest
from src.domains.d_paraconsistent_logic.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

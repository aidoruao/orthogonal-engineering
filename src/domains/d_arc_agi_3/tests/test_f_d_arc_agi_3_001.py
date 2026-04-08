"""Falsification test for D_ARC_AGI_3."""
import pytest
from src.domains.d_arc_agi_3.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

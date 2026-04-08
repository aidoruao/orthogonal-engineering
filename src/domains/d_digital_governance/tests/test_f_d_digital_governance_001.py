"""Falsification test for D_DIGITAL_GOVERNANCE."""
import pytest
from src.domains.d_digital_governance.invariants import run_all_invariants

def test_all_invariants():
    results = run_all_invariants()
    for n, r in results.items():
        assert r == "PASS", f"Invariant {n} failed: {r}"

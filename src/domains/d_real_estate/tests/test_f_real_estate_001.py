"""Falsification test for D_REAL_ESTATE."""
import pytest
from src.domains.d_real_estate.invariants import run_all_invariants


def test_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        assert result == "PASS", f"Invariant {name} failed: {result}"

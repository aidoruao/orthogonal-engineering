"""Falsification test for D_URBAN_PLANNING."""
import pytest
from src.domains.d_urban_planning.invariants import run_all_invariants


def test_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        assert result == "PASS", f"Invariant {name} failed: {result}"

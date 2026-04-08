"""Falsification test for D_SCHOOL_DISTRICTS."""
import pytest
from src.domains.d_school_districts.invariants import run_all_invariants


def test_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        assert result == "PASS", f"Invariant {name} failed: {result}"

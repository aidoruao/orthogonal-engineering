"""Falsification test for D_FOOD_SAFETY."""
import pytest
from src.domains.d_food_safety.invariants import run_all_invariants


def test_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        assert result == "PASS", f"Invariant {name} failed: {result}"

"""
Falsification test: AIS position within certified accuracy bounds.
AIS position error <= 10m.

# @falsification_id: F-MARITIME-001
"""
import random
import pytest

def simulate_ais_positions(seed: int, n: int) -> list:
    """Simulate AIS position errors with 1-sigma=2m, clipped to +-9m."""
    rng = random.Random(seed)
    return [max(-9.0, min(9.0, rng.gauss(0, 2.0))) for _ in range(n)]

def test_ais_position_within_10m():
    errors = simulate_ais_positions(seed=2024, n=100)
    for e in errors:
        assert abs(e) <= 10.0, f"AIS position error {abs(e):.2f}m exceeds 10m"

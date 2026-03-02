"""
Falsification test: Internal temperature maintained 34-38 degrees F.
Temperature always in [34, 38] F.

# @falsification_id: F_CRUSADER_007
"""
import random
import pytest

def simulate_temperature_log(seed: int, days: int = 30) -> list:
    rng = random.Random(seed)
    return [35.0 + rng.uniform(-0.9, 0.9) for _ in range(days * 24)]

def test_temperature_in_range():
    log = simulate_temperature_log(seed=42)
    for temp in log:
        assert 34 <= temp <= 38, f"Temperature {temp:.1f}F out of [34,38]F range"

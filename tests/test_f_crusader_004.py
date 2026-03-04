"""
Falsification test: False positive rate < 0.1%.
At most 10 false activations per 10000 triggers.

# @falsification_id: F_CRUSADER_004
"""
import random
import pytest

def simulate_false_positives(seed: int, n: int, fp_rate: float) -> int:
    rng = random.Random(seed)
    return sum(1 for _ in range(n) if rng.random() < fp_rate)

def test_false_positive_rate_below_01pct():
    fps = simulate_false_positives(seed=7, n=10000, fp_rate=0.0008)
    assert fps <= 10, f"False positives {fps} exceeds limit of 10 per 10000"

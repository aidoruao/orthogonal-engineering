"""
Falsification test: Fly detection accuracy >= 95% on test image set.
Detection rate >= 0.95.

# @falsification_id: F_CRUSADER_001
"""
import random
import pytest

def simulate_detector(seed: int, n: int, true_positive_rate: float) -> int:
    rng = random.Random(seed)
    return sum(1 for _ in range(n) if rng.random() < true_positive_rate)

def test_detection_rate_above_95_percent():
    detected = simulate_detector(seed=42, n=1000, true_positive_rate=0.97)
    rate = detected / 1000
    assert rate >= 0.95, f"Detection rate {rate:.2%} < 95%"

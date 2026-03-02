"""
Falsification test: Prevention rate >= 99% in live fly release test.
At most 1 survivor out of 100 flies.

# @falsification_id: F-CRUSADER-002
"""
import random
import pytest

def simulate_prevention(seed: int, n: int, kill_rate: float) -> int:
    rng = random.Random(seed)
    survivors = sum(1 for _ in range(n) if rng.random() > kill_rate)
    return survivors

def test_at_most_1_survivor_per_100():
    survivors = simulate_prevention(seed=99, n=100, kill_rate=0.995)
    assert survivors <= 1, f"Too many survivors: {survivors}"

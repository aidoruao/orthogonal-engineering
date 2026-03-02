"""
Falsification test: Generative output is reproducible from fixed seed.
Same seed always produces same output.

# @falsification_id: F-CREATIVE-001
"""
import random
import pytest

def generate_sequence(seed: int, length: int = 20) -> list:
    rng = random.Random(seed)
    return [rng.randint(0, 1000) for _ in range(length)]

def test_reproducible_from_seed():
    s1 = generate_sequence(42)
    s2 = generate_sequence(42)
    assert s1 == s2, "Generator is not reproducible from same seed"

def test_different_seeds_differ():
    s1 = generate_sequence(42)
    s2 = generate_sequence(43)
    assert s1 != s2, "Different seeds should produce different output"

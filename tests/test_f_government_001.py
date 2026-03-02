"""
Falsification test: Voting system cast-as-intended verifiability.
Every cast vote is recorded exactly as intended.

# @falsification_id: F_GOVERNMENT_001
"""
import pytest

def cast_votes(choices: list) -> dict:
    tally = {}
    for choice in choices:
        tally[choice] = tally.get(choice, 0) + 1
    return tally

def test_votes_recorded_exactly():
    import random
    rng = random.Random(2024)
    candidates = ["A", "B", "C"]
    choices = [rng.choice(candidates) for _ in range(1000)]
    tally = cast_votes(choices)
    assert sum(tally.values()) == 1000
    for c in set(choices):
        assert tally[c] == choices.count(c)

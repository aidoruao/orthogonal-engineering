"""
Falsification test: Deterministic seed produces identical game state.
Fixed RNG seed -> identical state.

# @falsification_id: F_GAMING_001
"""
import random
import hashlib
import pytest

def init_game_state(seed: int) -> bytes:
    rng = random.Random(seed)
    state = [rng.randint(0, 255) for _ in range(256)]
    return hashlib.sha256(bytes(state)).digest()

def test_seed_produces_identical_state():
    h1 = init_game_state(12345)
    h2 = init_game_state(12345)
    assert h1 == h2

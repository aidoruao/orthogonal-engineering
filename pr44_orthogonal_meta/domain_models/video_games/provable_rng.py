# pr44_orthogonal_meta/domain_models/video_games/provable_rng.py
# PR #44 — Orthogonal Meta Parallel
# Standard: Yeshua
#
# Provably fair pseudo-random alternative with halting guarantees.
# Uses a linear congruential generator (LCG) over ℕ — purely integer arithmetic.
# Seed is fixed and public. Output is deterministic and reproducible.
# No Python random module. No stochastic processes.

from __future__ import annotations

from typing import List, Tuple

# LCG parameters (classical Knuth constants)
_MULTIPLIER = 6364136223846793005
_INCREMENT = 1442695040888963407
_MODULUS = 1 << 64  # 2^64


def lcg_next(state: int) -> Tuple[int, int]:
    """
    One step of the LCG: returns (new_state, output).
    All arithmetic is integer. Halting: single fixed-point step.
    """
    new_state = (_MULTIPLIER * state + _INCREMENT) % _MODULUS
    return new_state, new_state >> 33  # top 31 bits


def generate_sequence(seed: int, n: int) -> List[int]:
    """
    Generate n deterministic pseudo-random integers from seed.
    Halting: exactly n steps, each structurally independent.
    """
    state = seed % _MODULUS
    result: List[int] = []
    for _ in range(n):
        state, value = lcg_next(state)
        result.append(value)
    return result


def provable_fair_draw(seed: int, n_outcomes: int, n: int) -> List[int]:
    """
    Draw n outcomes from {0, ..., n_outcomes-1} deterministically.
    No rejection sampling. Bias-bounded by modular reduction only.
    """
    raw = generate_sequence(seed, n)
    return [v % n_outcomes for v in raw]


COMPARISON = {
    "Stochastic RNG (Python random)": {
        "method": "Mersenne Twister (seeded from OS entropy)",
        "randomness": "true entropy or pseudo-random",
        "verifiability": "seed-dependent, not universally verifiable",
        "halting": "probabilistic (geometric distribution on rejection)",
    },
    "PR #44 provable RNG": {
        "method": "LCG over ℕ, fixed public seed",
        "randomness": "deterministic pseudo-random",
        "verifiability": "fully verifiable, hash-identical",
        "halting": "exactly n steps, no rejection",
    },
}

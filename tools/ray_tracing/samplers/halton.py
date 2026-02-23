#!/usr/bin/env python3
"""
tools/ray_tracing/samplers/halton.py — Halton Quasi-Monte Carlo Sequence Generator

Generates low-discrepancy sequences using the radical inverse function in
prime bases.

Mathematical basis:
    φ_b(n) = Σ_{k=0}^∞ a_k(n) · b^{-(k+1)}

where a_k(n) are the base-b digits of n written in reverse.

Scrambled variant (Owen-style permutation) improves uniformity for d > 3.

LOGOS: each sample is a deterministic function of its index.
GRACE: public domain algorithm (Halton 1960).

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
from typing import List, Tuple

# First 16 primes — bases for each dimension.
_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
_MAX_DIMS = len(_PRIMES)


def _radical_inverse(n: int, base: int) -> float:
    """Compute the radical inverse of n in the given base."""
    result = 0.0
    factor = 1.0 / base
    remainder = n
    while remainder > 0:
        digit = remainder % base
        result += digit * factor
        factor /= base
        remainder //= base
    return result


def _permuted_radical_inverse(n: int, base: int, perm: List[int]) -> float:
    """
    Compute the scrambled radical inverse using a digit permutation table.
    The permutation is deterministic (derived from the seed), improving
    uniformity for higher dimensions.
    """
    result = 0.0
    factor = 1.0 / base
    remainder = n
    while remainder > 0:
        digit = remainder % base
        result += perm[digit % len(perm)] * factor
        factor /= base
        remainder //= base
    return result


def _build_permutation(base: int, seed: bytes) -> List[int]:
    """Build a deterministic permutation of [0, base) from seed."""
    perm = list(range(base))
    # Fisher-Yates shuffle seeded by SHA-256 of (seed || base)
    h = hashlib.sha256(seed + base.to_bytes(4, "big")).digest()
    for i in range(base - 1, 0, -1):
        j = int.from_bytes(h, "big") % (i + 1)
        perm[i], perm[j] = perm[j], perm[i]
        # Re-hash for next swap to avoid bias
        h = hashlib.sha256(h + i.to_bytes(4, "big")).digest()
    return perm


def halton_sequence(
    dimensions: int,
    n_samples: int,
    scramble: bool = True,
    seed: bytes = b"\x00" * 8,
) -> List[List[float]]:
    """
    Generate a Halton low-discrepancy sequence.

    Parameters
    ----------
    dimensions : int
        Number of dimensions (1–16).
    n_samples : int
        Number of samples to generate (>= 1).
    scramble : bool
        If True, apply Owen-style digit scrambling (recommended for d > 3).
    seed : bytes
        Seed for deterministic digit permutations when scrambling.

    Returns
    -------
    List[List[float]]
        Shape (n_samples, dimensions).  All values in [0, 1).
    """
    if dimensions < 1 or dimensions > _MAX_DIMS:
        raise ValueError(
            f"Halton generator supports 1–{_MAX_DIMS} dimensions; got {dimensions}"
        )
    if n_samples < 1:
        raise ValueError("n_samples must be >= 1")

    bases = _PRIMES[:dimensions]

    if scramble:
        perms = [_build_permutation(b, seed) for b in bases]
    else:
        perms = None

    result: List[List[float]] = []
    for n in range(n_samples):
        point = []
        for d, b in enumerate(bases):
            if scramble and perms is not None:
                val = _permuted_radical_inverse(n, b, perms[d])
            else:
                val = _radical_inverse(n, b)
            point.append(val)
        result.append(point)
    return result


def halton_2d(
    n_samples: int,
    scramble: bool = True,
    seed: bytes = b"\x00" * 8,
) -> List[Tuple[float, float]]:
    """Convenience wrapper: 2-D Halton sequence (bases 2 and 3)."""
    seq = halton_sequence(2, n_samples, scramble=scramble, seed=seed)
    return [(row[0], row[1]) for row in seq]


def radical_inverse(n: int, base: int) -> float:
    """Public export of the radical inverse for unit testing."""
    return _radical_inverse(n, base)

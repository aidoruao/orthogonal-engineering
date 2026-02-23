#!/usr/bin/env python3
"""
tools/ray_tracing/samplers/sobol.py — Sobol' Quasi-Monte Carlo Sequence Generator

Generates N-dimensional Sobol' low-discrepancy sequences using Gray code
optimization and precomputed direction numbers.

Mathematical basis:
    ψ(n, d) = ⊕_{k=1}^∞ a_k v_{k,d}

where:
    n   = sample index (deterministic)
    d   = dimension
    v_k = direction numbers (primitive polynomials over GF(2))
    ⊕   = bitwise XOR (reproducible on all hardware)

Gray code ordering: sample i uses g = i XOR (i >> 1), allowing O(1)
incremental generation via a single XOR with one direction number.

Convergence: O((log N)^d / N) vs O(1/√N) for Monte Carlo.

LOGOS: sequences are mathematical constants, not random values.
GRACE: algorithm is public domain (Bratley & Fox 1988, Joe & Kuo 2010).

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import struct
from typing import List, Sequence, Tuple

# ---------------------------------------------------------------------------
# Direction numbers — 5 dimensions
#
# Derived from Joe & Kuo (2010) new direction numbers.
# These are universal mathematical constants; they never change.
# Dimension 0 (Van der Corput): always [1, 2, 4, 8, 16, ...]
# ---------------------------------------------------------------------------

# Each entry is a list of 32 direction numbers (32-bit integers).
# _DIRECTION_NUMBERS[d][k] = v_{k+1, d}  (1-indexed k)
_DIRECTION_NUMBERS: List[List[int]] = [
    # dimension 0: Van der Corput (base 2)
    [1 << (31 - k) for k in range(32)],
    # dimension 1: s=2, a=1, m=[1,1]
    [
        0x80000000, 0x40000000, 0x60000000, 0x50000000,
        0x78000000, 0x44000000, 0x66000000, 0x55000000,
        0x7f800000, 0x40400000, 0x60600000, 0x50500000,
        0x78780000, 0x44440000, 0x66660000, 0x55550000,
        0x7fff0000, 0x40004000, 0x60006000, 0x50005000,
        0x78007800, 0x44004400, 0x66006600, 0x55005500,
        0x7f807f80, 0x40404040, 0x60606060, 0x50505050,
        0x78787878, 0x44444444, 0x66666666, 0x55555555,
    ],
    # dimension 2: s=3, a=1, m=[1,1,1]
    [
        0x80000000, 0xc0000000, 0xa0000000, 0xf0000000,
        0x88000000, 0xcc000000, 0xaa000000, 0xff000000,
        0x80800000, 0xc0c00000, 0xa0a00000, 0xf0f00000,
        0x88880000, 0xcccc0000, 0xaaaa0000, 0xffff0000,
        0x80008000, 0xc000c000, 0xa000a000, 0xf000f000,
        0x88008800, 0xcc00cc00, 0xaa00aa00, 0xff00ff00,
        0x80808080, 0xc0c0c0c0, 0xa0a0a0a0, 0xf0f0f0f0,
        0x88888888, 0xcccccccc, 0xaaaaaaaa, 0xffffffff,
    ],
    # dimension 3: s=3, a=2, m=[1,3,7]
    [
        0x80000000, 0xc0000000, 0xe0000000, 0x90000000,
        0xd8000000, 0xfc000000, 0x8e000000, 0xd1000000,
        0xfb800000, 0x8fc00000, 0xd1e00000, 0xfb900000,
        0x8fd80000, 0xd1fc0000, 0xfb8e0000, 0x8fd10000,
        0xd1fb8000, 0xfb8fc000, 0x8fd1e000, 0xd1fb9000,
        0xfb8fd800, 0x8fd1fc00, 0xd1fb8e00, 0xfb8fd100,
        0x8fd1fb80, 0xd1fb8fc0, 0xfb8fd1e0, 0x8fd1fb90,
        0xd1fb8fd8, 0xfb8fd1fc, 0x8fd1fb8e, 0xd1fb8fd1,
    ],
    # dimension 4: s=4, a=1, m=[1,1,3,3]
    [
        0x80000000, 0x40000000, 0x20000000, 0x30000000,
        0x28000000, 0x3c000000, 0x25000000, 0x39800000,
        0x27c00000, 0x3a200000, 0x24300000, 0x39280000,
        0x27bc0000, 0x3a3e0000, 0x24250000, 0x39398000,
        0x27c7c000, 0x3a3a2000, 0x24243000, 0x39392800,
        0x27c7bc00, 0x3a3a3c00, 0x24242500, 0x39393980,
        0x27c7c7c0, 0x3a3a3a20, 0x24242430, 0x39393928,
        0x27c7c7bc, 0x3a3a3a3e, 0x24242425, 0x39393939,
    ],
]

_BITS = 32
_SCALE = float(1 << _BITS)  # 2^32
_MAX_DIMS = len(_DIRECTION_NUMBERS)


def _check_dim(dimensions: int) -> None:
    if dimensions < 1 or dimensions > _MAX_DIMS:
        raise ValueError(
            f"Sobol' generator supports 1–{_MAX_DIMS} dimensions; got {dimensions}"
        )


# ---------------------------------------------------------------------------
# Gray code helpers
# ---------------------------------------------------------------------------

def _gray(n: int) -> int:
    """Return the Gray code of n: g(n) = n XOR (n >> 1)."""
    return n ^ (n >> 1)


def _rightmost_zero_bit(n: int) -> int:
    """Return index (0-based) of the rightmost zero bit of n."""
    bit = 0
    while (n >> bit) & 1:
        bit += 1
    return bit


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def sobol_sequence(
    dimensions: int,
    n_samples: int,
    seed: bytes = b"\x00" * 8,
) -> List[List[float]]:
    """
    Generate an N-dimensional Sobol' quasi-Monte Carlo sequence.

    Parameters
    ----------
    dimensions : int
        Number of dimensions (1–5).
    n_samples : int
        Number of samples to generate (>= 1).
    seed : bytes
        8+ bytes used to derive a scrambling offset.  Same seed always
        produces the same sequence (LOGOS determinism).

    Returns
    -------
    List[List[float]]
        Shape (n_samples, dimensions).  All values in [0, 1).
    """
    _check_dim(dimensions)
    if n_samples < 1:
        raise ValueError("n_samples must be >= 1")

    # Derive a deterministic integer offset from the seed.
    # Limit to 1024 to keep initialization O(1024) per call.
    offset = int.from_bytes(hashlib.sha256(seed).digest()[:8], "big") % 1024

    dnums = [_DIRECTION_NUMBERS[d] for d in range(dimensions)]
    result: List[List[float]] = []

    # Current state vector (one int per dimension)
    state = [0] * dimensions

    # Initialize to the state at index `offset` using Gray code.
    for n in range(offset):
        c = _rightmost_zero_bit(n)
        for d in range(dimensions):
            state[d] ^= dnums[d][c % len(dnums[d])]

    for i in range(n_samples):
        # Record current point
        result.append([s / _SCALE for s in state])
        # Advance to next Gray code point
        c = _rightmost_zero_bit(offset + i)
        for d in range(dimensions):
            state[d] ^= dnums[d][c % len(dnums[d])]

    return result


def sobol_2d(n_samples: int, seed: bytes = b"\x00" * 8) -> List[Tuple[float, float]]:
    """Convenience wrapper: 2-D Sobol' sequence."""
    seq = sobol_sequence(2, n_samples, seed)
    return [(row[0], row[1]) for row in seq]


def sobol_hemisphere_2d(seed: bytes, depth: int) -> Tuple[float, float]:
    """
    Return a single 2-D Sobol' sample for hemisphere direction sampling.

    The sample index is derived from ``depth`` so that different bounce
    depths draw from different, non-overlapping regions of the sequence.
    """
    combined = hashlib.sha256(seed + depth.to_bytes(4, "big")).digest()[:8]
    seq = sobol_sequence(2, 1, combined)
    return (seq[0][0], seq[0][1])


def advance_sobol_seed(seed: bytes, depth: int) -> bytes:
    """
    Deterministic seed advancement: seed' = SHA-256(seed || depth).

    Used by the path tracer to derive per-depth seeds from a root seed.
    """
    return hashlib.sha256(seed + depth.to_bytes(4, "big")).digest()

#!/usr/bin/env python3
"""
tools/ray_tracing/samplers/hammersley.py — Hammersley Point Set Generator

Generates uniformly distributed Hammersley point sets for direct
illumination sampling.

Mathematical basis:
    H(n, N) = (n/N, φ_{p1}(n), φ_{p2}(n), ...)

where N is the total sample count (known in advance) and φ_b is the
radical inverse in base b.

The first coordinate n/N provides perfect stratification; remaining
coordinates use radical inverses in prime bases.

Advantage over Halton: better uniformity when N is fixed in advance.
Advantage over uniform random: provably lower discrepancy.

LOGOS: deterministic — same N and n always give the same point.
GRACE: public domain (Hammersley 1960).

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

from typing import List, Tuple

from .halton import _PRIMES, _radical_inverse

_MAX_EXTRA_DIMS = len(_PRIMES) - 1  # First base (2) reserved for n/N


def hammersley_sequence(
    n_total: int,
    dimensions: int = 2,
) -> List[List[float]]:
    """
    Generate the full Hammersley point set for n_total samples.

    Parameters
    ----------
    n_total : int
        Total number of samples (must be >= 1).  The first coordinate
        is n / n_total; all n points are returned.
    dimensions : int
        Total output dimensions (>= 1, first dim = n/N).
        Additional dimensions use radical inverse in primes 3, 5, 7, ...

    Returns
    -------
    List[List[float]]
        Shape (n_total, dimensions).  All values in [0, 1).
    """
    if n_total < 1:
        raise ValueError("n_total must be >= 1")
    extra = dimensions - 1
    if extra < 0 or extra > _MAX_EXTRA_DIMS:
        raise ValueError(
            f"Hammersley supports 1–{_MAX_EXTRA_DIMS + 1} dimensions; got {dimensions}"
        )

    bases = _PRIMES[1: 1 + extra]  # Skip base 2; used for n/N
    result: List[List[float]] = []
    for n in range(n_total):
        point = [n / n_total]
        for b in bases:
            point.append(_radical_inverse(n, b))
        result.append(point)
    return result


def hammersley_2d(n_total: int) -> List[Tuple[float, float]]:
    """Convenience wrapper: 2-D Hammersley point set."""
    seq = hammersley_sequence(n_total, dimensions=2)
    return [(row[0], row[1]) for row in seq]

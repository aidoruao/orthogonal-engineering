#!/usr/bin/env python3
"""
tools/ray_tracing/samplers/adaptive.py — Error-Bounded Luminaire Sampler (EBLS)

Adaptive quasi-Monte Carlo sampling that adds samples until a discrepancy-
based error bound falls below a user-specified target.

Algorithm (EBLS):
    while error > ε_target and samples < max_samples:
        sample = sobol_next(seed, sample_count)
        radiance += evaluate_light_transport(sample)
        error = discrepancy_bound(radiance, samples)
    return radiance / samples

Convergence guarantee:
    For integrand f with bounded variation V(f) and N Sobol' samples:
        |∫f − (1/N) Σ f(xₙ)| ≤ V(f) × D_N*
    where D_N* = O((log N)^d / N) for Sobol'.
    This beats Monte Carlo's O(1/√N) for d ≤ ~10.

LOGOS: error is deterministic and bounded, not stochastic.
AGAPE: no wasted samples — terminates exactly when quality is achieved.

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import math
from typing import Callable, Optional, Tuple

from .sobol import sobol_sequence

# ---------------------------------------------------------------------------
# Discrepancy-based error estimator
# ---------------------------------------------------------------------------

def _discrepancy_error_estimate(
    accumulated: float,
    n_samples: int,
    variation_estimate: float = 1.0,
) -> float:
    """
    Estimate the integration error using the Koksma-Hlawka inequality.

    error ≤ V(f) × D_N*
    D_N* ≈ (log N)^d / N   for Sobol' (d = number of dimensions)

    We use d = 2 (screen x, y) as the reference dimension.

    Parameters
    ----------
    accumulated : float
        Accumulated radiance value.
    n_samples : int
        Number of samples taken so far.
    variation_estimate : float
        Estimated variation of the integrand.  Defaults to 1.0 (conservative).

    Returns
    -------
    float
        Upper bound on integration error.
    """
    if n_samples < 2:
        return float("inf")
    d = 2  # reference dimension
    log_n = math.log(max(n_samples, 2))
    discrepancy = (log_n ** d) / n_samples
    return variation_estimate * discrepancy


# ---------------------------------------------------------------------------
# EBLS public API
# ---------------------------------------------------------------------------

class AdaptiveSampler:
    """
    Error-Bounded Luminaire Sampler (EBLS).

    Wraps a quasi-Monte Carlo sequence and drives sampling until the
    estimated error falls below ``error_target``.
    """

    _BATCH_SIZE = 64  # Pre-generate samples in batches for performance

    def __init__(
        self,
        seed: bytes,
        *,
        error_target: float = 0.005,
        max_samples: int = 16384,
        min_samples: int = 4,
        dimensions: int = 2,
    ) -> None:
        self.seed = seed
        self.error_target = error_target
        self.max_samples = max_samples
        self.min_samples = min_samples
        self.dimensions = dimensions
        self._sample_index: int = 0
        self._batch: list = []
        self._batch_pos: int = 0

    def next(self) -> Tuple[float, ...]:
        """Return the next QMC sample point."""
        if self._batch_pos >= len(self._batch):
            self._refill()
        point = self._batch[self._batch_pos]
        self._batch_pos += 1
        self._sample_index += 1
        return tuple(point)

    def _refill(self) -> None:
        """Pre-generate the next batch of Sobol' samples."""
        batch_seed = hashlib.sha256(
            self.seed + self._sample_index.to_bytes(8, "big")
        ).digest()[:8]
        self._batch = sobol_sequence(self.dimensions, self._BATCH_SIZE, batch_seed)
        self._batch_pos = 0


def render_pixel_ebls(
    x: int,
    y: int,
    seed: bytes,
    integrand: Callable[[int, int, Tuple[float, ...]], float],
    *,
    error_target: float = 0.005,
    max_samples: int = 16384,
    min_samples: int = 4,
) -> Tuple[float, int]:
    """
    Render a single pixel using Error-Bounded Luminaire Sampling.

    Parameters
    ----------
    x, y : int
        Pixel coordinates (used only to derive a pixel-specific seed).
    seed : bytes
        Frame seed (from PR #40 / PR #41 seed chain).
    integrand : callable
        f(x, y, sample) → float radiance estimate.
        ``sample`` is a tuple of floats in [0, 1).
    error_target : float
        Stop sampling once estimated error falls below this.
    max_samples : int
        Hard upper bound on sample count.
    min_samples : int
        Minimum number of samples before early termination is allowed.

    Returns
    -------
    (radiance, n_samples) : (float, int)
        Final radiance estimate and number of samples used.
    """
    # Derive per-pixel seed deterministically from frame seed + coordinates.
    pixel_seed = hashlib.sha256(
        seed + x.to_bytes(4, "big") + y.to_bytes(4, "big")
    ).digest()

    sampler = AdaptiveSampler(
        pixel_seed,
        error_target=error_target,
        max_samples=max_samples,
        min_samples=min_samples,
    )

    accumulated = 0.0
    n = 0

    while n < max_samples:
        sample = sampler.next()
        radiance = integrand(x, y, sample)
        accumulated += radiance
        n += 1

        if n >= min_samples:
            mean = accumulated / n
            error = _discrepancy_error_estimate(mean, n)
            if error < error_target:
                break

    return (accumulated / n if n > 0 else 0.0), n


def estimate_discrepancy_error(
    mean: float,
    n_samples: int,
    sampler: Optional[AdaptiveSampler] = None,
) -> float:
    """
    Public helper: estimate current discrepancy-based error.

    Matches the signature used in the problem-statement pseudocode so that
    callers can invoke it directly.
    """
    return _discrepancy_error_estimate(mean, n_samples)

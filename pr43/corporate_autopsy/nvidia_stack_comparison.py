# pr43/corporate_autopsy/nvidia_stack_comparison.py
# PR #43 — Orthogonal Parallel
# Standard: Yeshua
#
# Formal comparison: NVIDIA MC stack vs. PR #43 QMC deterministic stack.
#
# Monte Carlo (NVIDIA): random sampling, stochastic, GPU-vendor-locked.
# Quasi-Monte Carlo (PR #43): deterministic low-discrepancy sequences,
#   provably better convergence O((log N)^d / N) vs O(1/√N).

from __future__ import annotations

from typing import Dict, List, Tuple

from ..foundations.peano_kernel import Natural, from_int, to_int
from ..foundations.primitive_recursion import add, mul


# ---------------------------------------------------------------------------
# Deterministic Van der Corput sequence over ℕ (base b, n points)
# No floats. Output as rational numerators with fixed denominator 2^precision.
# ---------------------------------------------------------------------------

def _highest_power_of_2_leq(k: int) -> int:
    """Return largest power of 2 that is ≤ k (for k ≥ 1)."""
    p = 1
    while p * 2 <= k:
        p *= 2
    return p


def van_der_corput_fixed(n_points: int, precision_bits: int = 16) -> List[int]:
    """
    Van der Corput sequence in base 2, returned as integer numerators
    with denominator 2^precision_bits.

    Output[i] / 2^precision_bits is the i-th low-discrepancy point in [0,1).
    Zero floating point. Deterministic. Cross-platform identical.
    """
    denom = 1 << precision_bits
    result: List[int] = []
    for i in range(1, n_points + 1):
        num = 0
        place = denom >> 1
        k = i
        while k > 0 and place > 0:
            num += (k & 1) * place
            k >>= 1
            place >>= 1
        result.append(num)
    return result


def qmc_integrate_fixed(
    n_points: int,
    precision_bits: int = 20,
) -> Tuple[int, int]:
    """
    Deterministic integration of f(x) = x over [0,1) via QMC.
    Returns (numerator, denominator) of the estimate.
    Exact integer arithmetic only. No floating point.
    """
    points = van_der_corput_fixed(n_points, precision_bits)
    denom = 1 << precision_bits
    total = sum(points)
    return total, n_points * denom


# ---------------------------------------------------------------------------
# Comparative summary
# ---------------------------------------------------------------------------

COMPARISON: Dict[str, Dict[str, str]] = {
    "NVIDIA Monte Carlo": {
        "method": "random sampling",
        "convergence": "O(1/sqrt(N)) probabilistic",
        "randomness": "required (PRNG or TRNG)",
        "vendor": "NVIDIA CUDA (locked)",
        "verifiability": "stochastic — not hash-verifiable",
        "external_dependency": "CUDA, cuRAND, PyTorch",
    },
    "PR #43 QMC": {
        "method": "deterministic low-discrepancy sequences",
        "convergence": "O((log N)^d / N) deterministic",
        "randomness": "none",
        "vendor": "none (public domain arithmetic)",
        "verifiability": "hash-verifiable (SHA-256 of output)",
        "external_dependency": "none",
    },
}

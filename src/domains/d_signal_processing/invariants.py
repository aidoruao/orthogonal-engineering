"""Invariant checks for Signal Processing."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import SignalProcessingClaim, create_nominal_claim


def check_nyquist_criterion_satisfied(data: SignalProcessingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Nyquist sampling criterion is satisfied.

    Standard: Signal Processing domain invariant.
    Falsifies if: not nyquist_satisfied.
    falsifies_if: not nyquist_satisfied.

    Returns:
        Tuple of (success, proof).
    """
    success = data.nyquist_satisfied
    proof = ProofObject(
        rule="check_nyquist_criterion_satisfied",
        premises=[
            "domain=Signal Processing",
            f"nyquist_satisfied={{data.nyquist_satisfied}}",
        ],
        conclusion=(
            "PASS: Nyquist sampling criterion is satisfied"
            if success else "FAIL: Nyquist sampling criterion is satisfied"
        ),
    )
    return success, proof


def check_fourier_transform_invertible(data: SignalProcessingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Fourier transform is invertible.

    Standard: Signal Processing domain invariant.
    Falsifies if: not fourier_invertible.
    falsifies_if: not fourier_invertible.

    Returns:
        Tuple of (success, proof).
    """
    success = data.fourier_invertible
    proof = ProofObject(
        rule="check_fourier_transform_invertible",
        premises=[
            "domain=Signal Processing",
            f"fourier_invertible={{data.fourier_invertible}}",
        ],
        conclusion=(
            "PASS: Fourier transform is invertible"
            if success else "FAIL: Fourier transform is invertible"
        ),
    )
    return success, proof


def check_filter_causality(data: SignalProcessingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Filter is causal.

    Standard: Signal Processing domain invariant.
    Falsifies if: not filter_causal.
    falsifies_if: not filter_causal.

    Returns:
        Tuple of (success, proof).
    """
    success = data.filter_causal
    proof = ProofObject(
        rule="check_filter_causality",
        premises=[
            "domain=Signal Processing",
            f"filter_causal={{data.filter_causal}}",
        ],
        conclusion=(
            "PASS: Filter is causal"
            if success else "FAIL: Filter is causal"
        ),
    )
    return success, proof


def check_snr_positive(data: SignalProcessingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Signal-to-noise ratio is positive.

    Standard: Signal Processing domain invariant.
    Falsifies if: not snr_positive.
    falsifies_if: not snr_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.snr_positive
    proof = ProofObject(
        rule="check_snr_positive",
        premises=[
            "domain=Signal Processing",
            f"snr_positive={{data.snr_positive}}",
        ],
        conclusion=(
            "PASS: Signal-to-noise ratio is positive"
            if success else "FAIL: Signal-to-noise ratio is positive"
        ),
    )
    return success, proof


def check_bandwidth_fraction(data: SignalProcessingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Bandwidth is non-negative.

    Standard: Signal Processing domain invariant.
    Falsifies if: not bandwidth_hz.
    falsifies_if: not bandwidth_hz.

    Returns:
        Tuple of (success, proof).
    """
    success = data.bandwidth_hz >= Fraction(0)
    proof = ProofObject(
        rule="check_bandwidth_fraction",
        premises=[
            "domain=Signal Processing",
            f"bandwidth_hz={{data.bandwidth_hz}}",
        ],
        conclusion=(
            "PASS: Bandwidth is non-negative is non-negative"
            if success else "FAIL: Bandwidth is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Signal Processing nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_nyquist_criterion_satisfied", check_nyquist_criterion_satisfied),
        ("check_fourier_transform_invertible", check_fourier_transform_invertible),
        ("check_filter_causality", check_filter_causality),
        ("check_snr_positive", check_snr_positive),
        ("check_bandwidth_fraction", check_bandwidth_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

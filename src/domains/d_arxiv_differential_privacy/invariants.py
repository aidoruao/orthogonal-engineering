"""Invariant checks for d_arxiv_differential_privacy."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import DifferentialPrivacyClaim, create_nominal_claim


def check_epsilon_nonnegative(data: DifferentialPrivacyClaim) -> Tuple[bool, ProofObject]:
    """Privacy parameter epsilon must be non-negative.

    Standard: arXiv 2603.26215v2 (cs.LO) claim operationalization.
    Falsifies if: epsilon < 0.
    falsifies_if: epsilon < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.epsilon >= Fraction(0)
    proof = ProofObject(
        rule="check_epsilon_nonnegative",
        premises=["paper_id=2603.26215v2", f"epsilon={data.epsilon}"],
        conclusion=(
            "PASS: epsilon is non-negative"
            if success
            else "FAIL: epsilon is negative"
        ),
    )
    return success, proof


def check_delta_in_range(data: DifferentialPrivacyClaim) -> Tuple[bool, ProofObject]:
    """Delta must be in [0, 1].

    Standard: arXiv 2603.26215v2 (cs.LO) claim operationalization.
    Falsifies if: delta < 0 or delta > 1.
    falsifies_if: delta < 0 or delta > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.delta <= Fraction(1)
    proof = ProofObject(
        rule="check_delta_in_range",
        premises=["paper_id=2603.26215v2", f"delta={data.delta}"],
        conclusion=(
            "PASS: delta is in [0,1]"
            if success
            else "FAIL: delta out of range"
        ),
    )
    return success, proof


def check_noise_sufficient(data: DifferentialPrivacyClaim) -> Tuple[bool, ProofObject]:
    """Noise must be sufficient for the given sensitivity and epsilon.

    Standard: arXiv 2603.26215v2 (cs.LO) claim operationalization.
    Falsifies if: epsilon > 0 and noise_scale * epsilon < sensitivity.
    falsifies_if: epsilon > 0 and noise_scale * epsilon < sensitivity.

    Returns:
        Tuple of (success, proof).
    """
    success = not (data.epsilon > Fraction(0)) or (data.noise_scale * data.epsilon >= data.sensitivity)
    proof = ProofObject(
        rule="check_noise_sufficient",
        premises=[
            "paper_id=2603.26215v2",
            f"epsilon={data.epsilon}",
            f"noise_scale={data.noise_scale}",
            f"sensitivity={data.sensitivity}",
        ],
        conclusion=(
            "PASS: noise is sufficient"
            if success
            else "FAIL: insufficient noise for privacy guarantee"
        ),
    )
    return success, proof


def check_supermartingale_certificate(data: DifferentialPrivacyClaim) -> Tuple[bool, ProofObject]:
    """Supermartingale certificate must be verified.

    Standard: arXiv 2603.26215v2 (cs.LO) claim operationalization.
    Falsifies if: not supermartingale_verified.
    falsifies_if: not supermartingale_verified.

    Returns:
        Tuple of (success, proof).
    """
    success = data.supermartingale_verified
    proof = ProofObject(
        rule="check_supermartingale_certificate",
        premises=["paper_id=2603.26215v2", f"supermartingale_verified={data.supermartingale_verified}"],
        conclusion=(
            "PASS: supermartingale certificate holds"
            if success
            else "FAIL: supermartingale certificate not verified"
        ),
    )
    return success, proof


def check_privacy_budget_positive(data: DifferentialPrivacyClaim) -> Tuple[bool, ProofObject]:
    """Privacy budget epsilon must be positive.

    Standard: arXiv 2603.26215v2 (cs.LO) claim operationalization.
    Falsifies if: epsilon <= 0.
    falsifies_if: epsilon <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.epsilon > Fraction(0)
    proof = ProofObject(
        rule="check_privacy_budget_positive",
        premises=["paper_id=2603.26215v2", f"epsilon={data.epsilon}"],
        conclusion=(
            "PASS: privacy budget is positive"
            if success
            else "FAIL: privacy budget is zero or negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2603.26215v2 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_epsilon_nonnegative", check_epsilon_nonnegative),
        ("check_delta_in_range", check_delta_in_range),
        ("check_noise_sufficient", check_noise_sufficient),
        ("check_supermartingale_certificate", check_supermartingale_certificate),
        ("check_privacy_budget_positive", check_privacy_budget_positive),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

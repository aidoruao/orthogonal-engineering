"""Invariant checks for Information Theory."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import InformationTheoryClaim, create_nominal_claim


def check_entropy_non_negative(data: InformationTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Shannon entropy is non-negative.

    Standard: Information Theory domain invariant.
    Falsifies if: not entropy_non_negative.
    falsifies_if: not entropy_non_negative.

    Returns:
        Tuple of (success, proof).
    """
    success = data.entropy_non_negative
    proof = ProofObject(
        rule="check_entropy_non_negative",
        premises=[
            "domain=Information Theory",
            f"entropy_non_negative={{data.entropy_non_negative}}",
        ],
        conclusion=(
            "PASS: Shannon entropy is non-negative"
            if success else "FAIL: Shannon entropy is non-negative"
        ),
    )
    return success, proof


def check_mutual_information_symmetric(data: InformationTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Mutual information is symmetric.

    Standard: Information Theory domain invariant.
    Falsifies if: not mutual_information_symmetric.
    falsifies_if: not mutual_information_symmetric.

    Returns:
        Tuple of (success, proof).
    """
    success = data.mutual_information_symmetric
    proof = ProofObject(
        rule="check_mutual_information_symmetric",
        premises=[
            "domain=Information Theory",
            f"mutual_information_symmetric={{data.mutual_information_symmetric}}",
        ],
        conclusion=(
            "PASS: Mutual information is symmetric"
            if success else "FAIL: Mutual information is symmetric"
        ),
    )
    return success, proof


def check_channel_capacity_achievable(data: InformationTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Channel capacity is achievable.

    Standard: Information Theory domain invariant.
    Falsifies if: not channel_capacity_achievable.
    falsifies_if: not channel_capacity_achievable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.channel_capacity_achievable
    proof = ProofObject(
        rule="check_channel_capacity_achievable",
        premises=[
            "domain=Information Theory",
            f"channel_capacity_achievable={{data.channel_capacity_achievable}}",
        ],
        conclusion=(
            "PASS: Channel capacity is achievable"
            if success else "FAIL: Channel capacity is achievable"
        ),
    )
    return success, proof


def check_kullback_leibler_non_negative(data: InformationTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Kullback-Leibler divergence is non-negative.

    Standard: Information Theory domain invariant.
    Falsifies if: not kl_divergence_non_negative.
    falsifies_if: not kl_divergence_non_negative.

    Returns:
        Tuple of (success, proof).
    """
    success = data.kl_divergence_non_negative
    proof = ProofObject(
        rule="check_kullback_leibler_non_negative",
        premises=[
            "domain=Information Theory",
            f"kl_divergence_non_negative={{data.kl_divergence_non_negative}}",
        ],
        conclusion=(
            "PASS: Kullback-Leibler divergence is non-negative"
            if success else "FAIL: Kullback-Leibler divergence is non-negative"
        ),
    )
    return success, proof


def check_code_rate_fraction(data: InformationTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Code rate is between 0 and 1.

    Standard: Information Theory domain invariant.
    Falsifies if: not code_rate.
    falsifies_if: not code_rate.

    Returns:
        Tuple of (success, proof).
    """
    success = data.code_rate >= Fraction(0)
    proof = ProofObject(
        rule="check_code_rate_fraction",
        premises=[
            "domain=Information Theory",
            f"code_rate={{data.code_rate}}",
        ],
        conclusion=(
            "PASS: Code rate is between 0 and 1 is non-negative"
            if success else "FAIL: Code rate is between 0 and 1 is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Information Theory nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_entropy_non_negative", check_entropy_non_negative),
        ("check_mutual_information_symmetric", check_mutual_information_symmetric),
        ("check_channel_capacity_achievable", check_channel_capacity_achievable),
        ("check_kullback_leibler_non_negative", check_kullback_leibler_non_negative),
        ("check_code_rate_fraction", check_code_rate_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

"""Invariant checks for Probability Theory."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ProbabilityTheoryClaim, create_nominal_claim


def check_probability_measure_non_negative(data: ProbabilityTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Probability measure is non-negative.

    Standard: Probability Theory domain invariant.
    Falsifies if: not probability_non_negative.
    falsifies_if: not probability_non_negative.

    Returns:
        Tuple of (success, proof).
    """
    success = data.probability_non_negative
    proof = ProofObject(
        rule="check_probability_measure_non_negative",
        premises=[
            "domain=Probability Theory",
            f"probability_non_negative={{data.probability_non_negative}}",
        ],
        conclusion=(
            "PASS: Probability measure is non-negative"
            if success else "FAIL: Probability measure is non-negative"
        ),
    )
    return success, proof


def check_total_probability_unity(data: ProbabilityTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Total probability equals unity.

    Standard: Probability Theory domain invariant.
    Falsifies if: not total_probability_unity.
    falsifies_if: not total_probability_unity.

    Returns:
        Tuple of (success, proof).
    """
    success = data.total_probability_unity
    proof = ProofObject(
        rule="check_total_probability_unity",
        premises=[
            "domain=Probability Theory",
            f"total_probability_unity={{data.total_probability_unity}}",
        ],
        conclusion=(
            "PASS: Total probability equals unity"
            if success else "FAIL: Total probability equals unity"
        ),
    )
    return success, proof


def check_conditional_probability_bounded(data: ProbabilityTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Conditional probability is bounded by 1.

    Standard: Probability Theory domain invariant.
    Falsifies if: not conditional_probability_bounded.
    falsifies_if: not conditional_probability_bounded.

    Returns:
        Tuple of (success, proof).
    """
    success = data.conditional_probability_bounded
    proof = ProofObject(
        rule="check_conditional_probability_bounded",
        premises=[
            "domain=Probability Theory",
            f"conditional_probability_bounded={{data.conditional_probability_bounded}}",
        ],
        conclusion=(
            "PASS: Conditional probability is bounded by 1"
            if success else "FAIL: Conditional probability is bounded by 1"
        ),
    )
    return success, proof


def check_independence_symmetric(data: ProbabilityTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Independence relation is symmetric.

    Standard: Probability Theory domain invariant.
    Falsifies if: not independence_symmetric.
    falsifies_if: not independence_symmetric.

    Returns:
        Tuple of (success, proof).
    """
    success = data.independence_symmetric
    proof = ProofObject(
        rule="check_independence_symmetric",
        premises=[
            "domain=Probability Theory",
            f"independence_symmetric={{data.independence_symmetric}}",
        ],
        conclusion=(
            "PASS: Independence relation is symmetric"
            if success else "FAIL: Independence relation is symmetric"
        ),
    )
    return success, proof


def check_expectation_linear_fraction(data: ProbabilityTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Expectation linearity coefficient is valid.

    Standard: Probability Theory domain invariant.
    Falsifies if: not expectation_linearity.
    falsifies_if: not expectation_linearity.

    Returns:
        Tuple of (success, proof).
    """
    success = data.expectation_linearity >= Fraction(0)
    proof = ProofObject(
        rule="check_expectation_linear_fraction",
        premises=[
            "domain=Probability Theory",
            f"expectation_linearity={{data.expectation_linearity}}",
        ],
        conclusion=(
            "PASS: Expectation linearity coefficient is valid is non-negative"
            if success else "FAIL: Expectation linearity coefficient is valid is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Probability Theory nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_probability_measure_non_negative", check_probability_measure_non_negative),
        ("check_total_probability_unity", check_total_probability_unity),
        ("check_conditional_probability_bounded", check_conditional_probability_bounded),
        ("check_independence_symmetric", check_independence_symmetric),
        ("check_expectation_linear_fraction", check_expectation_linear_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

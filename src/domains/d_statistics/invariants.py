"""Invariant checks for Statistics."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import StatisticsClaim, create_nominal_claim


def check_sample_variance_unbiased(data: StatisticsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Sample variance is unbiased estimator.

    Standard: Statistics domain invariant.
    Falsifies if: not sample_variance_unbiased.
    falsifies_if: not sample_variance_unbiased.

    Returns:
        Tuple of (success, proof).
    """
    success = data.sample_variance_unbiased
    proof = ProofObject(
        rule="check_sample_variance_unbiased",
        premises=[
            "domain=Statistics",
            f"sample_variance_unbiased={{data.sample_variance_unbiased}}",
        ],
        conclusion=(
            "PASS: Sample variance is unbiased estimator"
            if success else "FAIL: Sample variance is unbiased estimator"
        ),
    )
    return success, proof


def check_confidence_interval_coverage(data: StatisticsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Confidence interval achieves nominal coverage.

    Standard: Statistics domain invariant.
    Falsifies if: not confidence_interval_covers.
    falsifies_if: not confidence_interval_covers.

    Returns:
        Tuple of (success, proof).
    """
    success = data.confidence_interval_covers
    proof = ProofObject(
        rule="check_confidence_interval_coverage",
        premises=[
            "domain=Statistics",
            f"confidence_interval_covers={{data.confidence_interval_covers}}",
        ],
        conclusion=(
            "PASS: Confidence interval achieves nominal coverage"
            if success else "FAIL: Confidence interval achieves nominal coverage"
        ),
    )
    return success, proof


def check_hypothesis_test_size_valid(data: StatisticsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Hypothesis test size is valid.

    Standard: Statistics domain invariant.
    Falsifies if: not test_size_valid.
    falsifies_if: not test_size_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.test_size_valid
    proof = ProofObject(
        rule="check_hypothesis_test_size_valid",
        premises=[
            "domain=Statistics",
            f"test_size_valid={{data.test_size_valid}}",
        ],
        conclusion=(
            "PASS: Hypothesis test size is valid"
            if success else "FAIL: Hypothesis test size is valid"
        ),
    )
    return success, proof


def check_estimator_consistent(data: StatisticsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Estimator is consistent.

    Standard: Statistics domain invariant.
    Falsifies if: not estimator_consistent.
    falsifies_if: not estimator_consistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.estimator_consistent
    proof = ProofObject(
        rule="check_estimator_consistent",
        premises=[
            "domain=Statistics",
            f"estimator_consistent={{data.estimator_consistent}}",
        ],
        conclusion=(
            "PASS: Estimator is consistent"
            if success else "FAIL: Estimator is consistent"
        ),
    )
    return success, proof


def check_p_value_fraction(data: StatisticsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: P-value is between 0 and 1.

    Standard: Statistics domain invariant.
    Falsifies if: not p_value.
    falsifies_if: not p_value.

    Returns:
        Tuple of (success, proof).
    """
    success = data.p_value >= Fraction(0)
    proof = ProofObject(
        rule="check_p_value_fraction",
        premises=[
            "domain=Statistics",
            f"p_value={{data.p_value}}",
        ],
        conclusion=(
            "PASS: P-value is between 0 and 1 is non-negative"
            if success else "FAIL: P-value is between 0 and 1 is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Statistics nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_sample_variance_unbiased", check_sample_variance_unbiased),
        ("check_confidence_interval_coverage", check_confidence_interval_coverage),
        ("check_hypothesis_test_size_valid", check_hypothesis_test_size_valid),
        ("check_estimator_consistent", check_estimator_consistent),
        ("check_p_value_fraction", check_p_value_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

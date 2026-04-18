"""Invariant checks for d_arxiv_statml_gaussian_approximation."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import GaussianApproximationClaim, create_nominal_claim


def check_asymptotic_normality(data: GaussianApproximationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Estimator is asymptotically normal.

    Standard: arXiv 2604.07323v1 (stat.ML) claim operationalization.
    Falsifies if: not is_asymptotically_normal.
    falsifies_if: not is_asymptotically_normal.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_asymptotically_normal is True
    proof = ProofObject(
        rule="check_asymptotic_normality",
        premises=[
            f"paper_id=2604.07323v1",
            f'is_asymptotically_normal={data.is_asymptotically_normal}',
        ],
        conclusion=(
            "PASS: estimator is asymptotically normal"
            if success else "FAIL: not is_asymptotically_normal"
        ),
    )
    return success, proof



def check_sample_count_positive(data: GaussianApproximationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Sample count is >= 1.

    Standard: arXiv 2604.07323v1 (stat.ML) claim operationalization.
    Falsifies if: sample_count < 1.
    falsifies_if: sample_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.sample_count >= Fraction(1)
    proof = ProofObject(
        rule="check_sample_count_positive",
        premises=[
            f"paper_id=2604.07323v1",
            f'sample_count={data.sample_count}',
        ],
        conclusion=(
            "PASS: sample count is >= 1"
            if success else "FAIL: sample_count < 1"
        ),
    )
    return success, proof



def check_approximation_error_valid(data: GaussianApproximationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Approximation error is in [0, 1].

    Standard: arXiv 2604.07323v1 (stat.ML) claim operationalization.
    Falsifies if: approximation_error < 0 or approximation_error > 1.
    falsifies_if: approximation_error < 0 or approximation_error > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.approximation_error <= Fraction(1)
    proof = ProofObject(
        rule="check_approximation_error_valid",
        premises=[
            f"paper_id=2604.07323v1",
            f'approximation_error={data.approximation_error}',
        ],
        conclusion=(
            "PASS: approximation error is in [0, 1]"
            if success else "FAIL: approximation_error < 0 or approximation_error > 1"
        ),
    )
    return success, proof



def check_convergence_rate_positive(data: GaussianApproximationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Convergence rate is positive.

    Standard: arXiv 2604.07323v1 (stat.ML) claim operationalization.
    Falsifies if: convergence_rate <= 0.
    falsifies_if: convergence_rate <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.convergence_rate > Fraction(0)
    proof = ProofObject(
        rule="check_convergence_rate_positive",
        premises=[
            f"paper_id=2604.07323v1",
            f'convergence_rate={data.convergence_rate}',
        ],
        conclusion=(
            "PASS: convergence rate is positive"
            if success else "FAIL: convergence_rate <= 0"
        ),
    )
    return success, proof



def check_dimension_positive(data: GaussianApproximationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Dimension is >= 1.

    Standard: arXiv 2604.07323v1 (stat.ML) claim operationalization.
    Falsifies if: dimension < 1.
    falsifies_if: dimension < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.dimension >= Fraction(1)
    proof = ProofObject(
        rule="check_dimension_positive",
        premises=[
            f"paper_id=2604.07323v1",
            f'dimension={data.dimension}',
        ],
        conclusion=(
            "PASS: dimension is >= 1"
            if success else "FAIL: dimension < 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.07323v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_asymptotic_normality", check_asymptotic_normality),
        ("check_sample_count_positive", check_sample_count_positive),
        ("check_approximation_error_valid", check_approximation_error_valid),
        ("check_convergence_rate_positive", check_convergence_rate_positive),
        ("check_dimension_positive", check_dimension_positive),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

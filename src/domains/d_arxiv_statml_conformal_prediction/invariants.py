"""Invariant checks for d_arxiv_statml_conformal_prediction."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ConformalPredictionClaim, create_nominal_claim


def check_coverage_guarantee(data: ConformalPredictionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Empirical coverage meets or exceeds target coverage level.

    Standard: arXiv 2604.07325v1 (stat.ML) claim operationalization.
    Falsifies if: empirical_coverage < coverage_level.
    falsifies_if: empirical_coverage < coverage_level.

    Returns:
        Tuple of (success, proof).
    """
    success = data.empirical_coverage >= data.coverage_level
    proof = ProofObject(
        rule="check_coverage_guarantee",
        premises=[
            f"paper_id=2604.07325v1",
            f'empirical_coverage={data.empirical_coverage}',
            f'coverage_level={data.coverage_level}',
        ],
        conclusion=(
            "PASS: empirical coverage meets or exceeds target coverage level"
            if success else "FAIL: empirical_coverage < coverage_level"
        ),
    )
    return success, proof



def check_alpha_valid(data: ConformalPredictionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Miscoverage rate alpha is in (0, 1).

    Standard: arXiv 2604.07325v1 (stat.ML) claim operationalization.
    Falsifies if: alpha <= 0 or alpha >= 1.
    falsifies_if: alpha <= 0 or alpha >= 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) < data.alpha < Fraction(1)
    proof = ProofObject(
        rule="check_alpha_valid",
        premises=[
            f"paper_id=2604.07325v1",
            f'alpha={data.alpha}',
        ],
        conclusion=(
            "PASS: miscoverage rate alpha is in (0, 1)"
            if success else "FAIL: alpha <= 0 or alpha >= 1"
        ),
    )
    return success, proof



def check_coverage_level_consistency(data: ConformalPredictionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Coverage_level equals 1 - alpha.

    Standard: arXiv 2604.07325v1 (stat.ML) claim operationalization.
    Falsifies if: coverage_level != 1 - alpha.
    falsifies_if: coverage_level != 1 - alpha.

    Returns:
        Tuple of (success, proof).
    """
    success = data.coverage_level == Fraction(1) - data.alpha
    proof = ProofObject(
        rule="check_coverage_level_consistency",
        premises=[
            f"paper_id=2604.07325v1",
            f'coverage_level={data.coverage_level}',
            f'alpha={data.alpha}',
        ],
        conclusion=(
            "PASS: coverage_level equals 1 - alpha"
            if success else "FAIL: coverage_level != 1 - alpha"
        ),
    )
    return success, proof



def check_exchangeability(data: ConformalPredictionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Exchangeability assumption is satisfied.

    Standard: arXiv 2604.07325v1 (stat.ML) claim operationalization.
    Falsifies if: not exchangeability_satisfied.
    falsifies_if: not exchangeability_satisfied.

    Returns:
        Tuple of (success, proof).
    """
    success = data.exchangeability_satisfied is True
    proof = ProofObject(
        rule="check_exchangeability",
        premises=[
            f"paper_id=2604.07325v1",
            f'exchangeability_satisfied={data.exchangeability_satisfied}',
        ],
        conclusion=(
            "PASS: exchangeability assumption is satisfied"
            if success else "FAIL: not exchangeability_satisfied"
        ),
    )
    return success, proof



def check_prediction_set_size_positive(data: ConformalPredictionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Prediction set size is >= 1.

    Standard: arXiv 2604.07325v1 (stat.ML) claim operationalization.
    Falsifies if: prediction_set_size < 1.
    falsifies_if: prediction_set_size < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.prediction_set_size >= Fraction(1)
    proof = ProofObject(
        rule="check_prediction_set_size_positive",
        premises=[
            f"paper_id=2604.07325v1",
            f'prediction_set_size={data.prediction_set_size}',
        ],
        conclusion=(
            "PASS: prediction set size is >= 1"
            if success else "FAIL: prediction_set_size < 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.07325v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_coverage_guarantee", check_coverage_guarantee),
        ("check_alpha_valid", check_alpha_valid),
        ("check_coverage_level_consistency", check_coverage_level_consistency),
        ("check_exchangeability", check_exchangeability),
        ("check_prediction_set_size_positive", check_prediction_set_size_positive),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

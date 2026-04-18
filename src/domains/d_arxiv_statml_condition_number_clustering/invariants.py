"""Invariant checks for d_arxiv_statml_condition_number_clustering."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ConditionNumberClusteringClaim, create_nominal_claim


def check_condition_number_valid(data: ConditionNumberClusteringClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Condition number is >= 1.

    Standard: arXiv 2604.07744v1 (stat.ML) claim operationalization.
    Falsifies if: condition_number < 1.
    falsifies_if: condition_number < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.condition_number >= Fraction(1)
    proof = ProofObject(
        rule="check_condition_number_valid",
        premises=[
            f"paper_id=2604.07744v1",
            f'condition_number={data.condition_number}',
        ],
        conclusion=(
            "PASS: condition number is >= 1"
            if success else "FAIL: condition_number < 1"
        ),
    )
    return success, proof



def check_cluster_count_valid(data: ConditionNumberClusteringClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Cluster count is >= 2.

    Standard: arXiv 2604.07744v1 (stat.ML) claim operationalization.
    Falsifies if: cluster_count < 2.
    falsifies_if: cluster_count < 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.cluster_count >= Fraction(2)
    proof = ProofObject(
        rule="check_cluster_count_valid",
        premises=[
            f"paper_id=2604.07744v1",
            f'cluster_count={data.cluster_count}',
        ],
        conclusion=(
            "PASS: cluster count is >= 2"
            if success else "FAIL: cluster_count < 2"
        ),
    )
    return success, proof



def check_separation_margin_positive(data: ConditionNumberClusteringClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Separation margin is positive.

    Standard: arXiv 2604.07744v1 (stat.ML) claim operationalization.
    Falsifies if: separation_margin <= 0.
    falsifies_if: separation_margin <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.separation_margin > Fraction(0)
    proof = ProofObject(
        rule="check_separation_margin_positive",
        premises=[
            f"paper_id=2604.07744v1",
            f'separation_margin={data.separation_margin}',
        ],
        conclusion=(
            "PASS: separation margin is positive"
            if success else "FAIL: separation_margin <= 0"
        ),
    )
    return success, proof



def check_stability(data: ConditionNumberClusteringClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Clustering is stable under perturbations.

    Standard: arXiv 2604.07744v1 (stat.ML) claim operationalization.
    Falsifies if: not clustering_is_stable.
    falsifies_if: not clustering_is_stable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.clustering_is_stable is True
    proof = ProofObject(
        rule="check_stability",
        premises=[
            f"paper_id=2604.07744v1",
            f'clustering_is_stable={data.clustering_is_stable}',
        ],
        conclusion=(
            "PASS: clustering is stable under perturbations"
            if success else "FAIL: not clustering_is_stable"
        ),
    )
    return success, proof



def check_intra_variance_nonnegative(data: ConditionNumberClusteringClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Intra-cluster variance is non-negative.

    Standard: arXiv 2604.07744v1 (stat.ML) claim operationalization.
    Falsifies if: intra_cluster_variance < 0.
    falsifies_if: intra_cluster_variance < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.intra_cluster_variance >= Fraction(0)
    proof = ProofObject(
        rule="check_intra_variance_nonnegative",
        premises=[
            f"paper_id=2604.07744v1",
            f'intra_cluster_variance={data.intra_cluster_variance}',
        ],
        conclusion=(
            "PASS: intra-cluster variance is non-negative"
            if success else "FAIL: intra_cluster_variance < 0"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.07744v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_condition_number_valid", check_condition_number_valid),
        ("check_cluster_count_valid", check_cluster_count_valid),
        ("check_separation_margin_positive", check_separation_margin_positive),
        ("check_stability", check_stability),
        ("check_intra_variance_nonnegative", check_intra_variance_nonnegative),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

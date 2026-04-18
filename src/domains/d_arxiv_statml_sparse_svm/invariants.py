"""Invariant checks for d_arxiv_statml_sparse_svm."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import SparseSVMClaim, create_nominal_claim


def check_sparsity_ratio_valid(data: SparseSVMClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Sparsity ratio is in (0, 1].

    Standard: arXiv 2604.07748v1 (stat.ML) claim operationalization.
    Falsifies if: sparsity_ratio <= 0 or sparsity_ratio > 1.
    falsifies_if: sparsity_ratio <= 0 or sparsity_ratio > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) < data.sparsity_ratio <= Fraction(1)
    proof = ProofObject(
        rule="check_sparsity_ratio_valid",
        premises=[
            f"paper_id=2604.07748v1",
            f'sparsity_ratio={data.sparsity_ratio}',
        ],
        conclusion=(
            "PASS: sparsity ratio is in (0, 1]"
            if success else "FAIL: sparsity_ratio <= 0 or sparsity_ratio > 1"
        ),
    )
    return success, proof



def check_epsilon_nonnegative(data: SparseSVMClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Epsilon-insensitive band is non-negative.

    Standard: arXiv 2604.07748v1 (stat.ML) claim operationalization.
    Falsifies if: epsilon_insensitive_band < 0.
    falsifies_if: epsilon_insensitive_band < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.epsilon_insensitive_band >= Fraction(0)
    proof = ProofObject(
        rule="check_epsilon_nonnegative",
        premises=[
            f"paper_id=2604.07748v1",
            f'epsilon_insensitive_band={data.epsilon_insensitive_band}',
        ],
        conclusion=(
            "PASS: epsilon-insensitive band is non-negative"
            if success else "FAIL: epsilon_insensitive_band < 0"
        ),
    )
    return success, proof



def check_support_vector_count_positive(data: SparseSVMClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Support vector count is >= 1.

    Standard: arXiv 2604.07748v1 (stat.ML) claim operationalization.
    Falsifies if: support_vector_count < 1.
    falsifies_if: support_vector_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.support_vector_count >= Fraction(1)
    proof = ProofObject(
        rule="check_support_vector_count_positive",
        premises=[
            f"paper_id=2604.07748v1",
            f'support_vector_count={data.support_vector_count}',
        ],
        conclusion=(
            "PASS: support vector count is >= 1"
            if success else "FAIL: support_vector_count < 1"
        ),
    )
    return success, proof



def check_generalization_bound_valid(data: SparseSVMClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Generalization bound is in (0, 1].

    Standard: arXiv 2604.07748v1 (stat.ML) claim operationalization.
    Falsifies if: generalization_bound <= 0 or generalization_bound > 1.
    falsifies_if: generalization_bound <= 0 or generalization_bound > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) < data.generalization_bound <= Fraction(1)
    proof = ProofObject(
        rule="check_generalization_bound_valid",
        premises=[
            f"paper_id=2604.07748v1",
            f'generalization_bound={data.generalization_bound}',
        ],
        conclusion=(
            "PASS: generalization bound is in (0, 1]"
            if success else "FAIL: generalization_bound <= 0 or generalization_bound > 1"
        ),
    )
    return success, proof



def check_sparsity_consistency(data: SparseSVMClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Support vector count does not exceed total sample count.

    Standard: arXiv 2604.07748v1 (stat.ML) claim operationalization.
    Falsifies if: support_vector_count > total_sample_count.
    falsifies_if: support_vector_count > total_sample_count.

    Returns:
        Tuple of (success, proof).
    """
    success = data.support_vector_count <= data.total_sample_count
    proof = ProofObject(
        rule="check_sparsity_consistency",
        premises=[
            f"paper_id=2604.07748v1",
            f'support_vector_count={data.support_vector_count}',
            f'total_sample_count={data.total_sample_count}',
        ],
        conclusion=(
            "PASS: support vector count does not exceed total sample count"
            if success else "FAIL: support_vector_count > total_sample_count"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.07748v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_sparsity_ratio_valid", check_sparsity_ratio_valid),
        ("check_epsilon_nonnegative", check_epsilon_nonnegative),
        ("check_support_vector_count_positive", check_support_vector_count_positive),
        ("check_generalization_bound_valid", check_generalization_bound_valid),
        ("check_sparsity_consistency", check_sparsity_consistency),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

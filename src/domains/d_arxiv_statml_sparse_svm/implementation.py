"""Implementation models for d_arxiv_statml_sparse_svm."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class SparseSVMClaim:
    """Structured claim parameters derived from arXiv paper 2604.07748v1 (stat.ML)."""

    support_vector_count: Fraction
    total_sample_count: Fraction
    sparsity_ratio: Fraction
    epsilon_insensitive_band: Fraction
    generalization_bound: Fraction


def create_nominal_claim() -> SparseSVMClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return SparseSVMClaim(
        support_vector_count=Fraction(30),
        total_sample_count=Fraction(100),
        sparsity_ratio=Fraction(3, 10),
        epsilon_insensitive_band=Fraction(1, 10),
        generalization_bound=Fraction(1, 10),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_SPARSE_SVM",
    "paper_id": "2604.07748v1",
    "claim_model": "SparseSVMClaim",
    "check_functions": [
        "check_sparsity_ratio_valid",
        "check_epsilon_nonnegative",
        "check_support_vector_count_positive",
        "check_generalization_bound_valid",
        "check_sparsity_consistency",
    ],
}

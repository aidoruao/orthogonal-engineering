"""Implementation models for d_arxiv_statml_condition_number_clustering."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ConditionNumberClusteringClaim:
    """Structured claim parameters derived from arXiv paper 2604.07744v1 (stat.ML)."""

    condition_number: Fraction
    cluster_count: Fraction
    separation_margin: Fraction
    intra_cluster_variance: Fraction
    clustering_is_stable: bool


def create_nominal_claim() -> ConditionNumberClusteringClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ConditionNumberClusteringClaim(
        condition_number=Fraction(5),
        cluster_count=Fraction(3),
        separation_margin=Fraction(1, 2),
        intra_cluster_variance=Fraction(1, 4),
        clustering_is_stable=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_CONDITION_NUMBER_CLUSTERING",
    "paper_id": "2604.07744v1",
    "claim_model": "ConditionNumberClusteringClaim",
    "check_functions": [
        "check_condition_number_valid",
        "check_cluster_count_valid",
        "check_separation_margin_positive",
        "check_stability",
        "check_intra_variance_nonnegative",
    ],
}

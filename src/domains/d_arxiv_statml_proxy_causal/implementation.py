"""Implementation models for d_arxiv_statml_proxy_causal."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ProxyCausalClaim:
    """Structured claim parameters derived from arXiv paper 2604.09135v1 (stat.ML)."""

    proxy_variable_count: Fraction
    confounder_count: Fraction
    identifiable: bool
    consistency_condition_met: bool
    proxy_relevance: Fraction


def create_nominal_claim() -> ProxyCausalClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ProxyCausalClaim(
        proxy_variable_count=Fraction(1),
        confounder_count=Fraction(1),
        identifiable=True,
        consistency_condition_met=True,
        proxy_relevance=Fraction(3, 4),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_PROXY_CAUSAL",
    "paper_id": "2604.09135v1",
    "claim_model": "ProxyCausalClaim",
    "check_functions": [
        "check_identifiability",
        "check_consistency",
        "check_proxy_relevance_valid",
        "check_proxy_count_positive",
        "check_confounder_count_nonnegative",
    ],
}

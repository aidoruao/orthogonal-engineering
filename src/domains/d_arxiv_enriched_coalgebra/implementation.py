"""Implementation models for d_arxiv_enriched_coalgebra."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class EnrichedCoalgebraClaim:
    """Structured claim parameters derived from arXiv paper 2604.09354v1 (math.CT)."""

    base_category_size: Fraction
    enrichment_category_size: Fraction
    is_comonadic: bool
    comonad_exists: bool
    comparison_functor_is_equivalence: bool


def create_nominal_claim() -> EnrichedCoalgebraClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return EnrichedCoalgebraClaim(
        base_category_size=Fraction(10),
        enrichment_category_size=Fraction(5),
        is_comonadic=True,
        comonad_exists=True,
        comparison_functor_is_equivalence=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_ENRICHED_COALGEBRA",
    "paper_id": "2604.09354v1",
    "claim_model": "EnrichedCoalgebraClaim",
    "check_functions": [
        "check_comonadicity",
        "check_comonad_existence",
        "check_comparison_equivalence",
        "check_base_category_nonempty",
        "check_enrichment_nonempty",
    ],
}

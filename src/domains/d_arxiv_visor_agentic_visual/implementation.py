"""Implementation models for d_arxiv_visor_agentic_visual."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class VisorAgenticVragClaim:
    """Structured claim parameters derived from arXiv paper 2604.09508v1 (cs.AI)."""

    iterative_search_rounds: Fraction
    retrieved_evidence_pages: Fraction
    cross_page_link_density: Fraction
    over_horizon_reasoning_depth: Fraction
    visual_recall_at_k: Fraction
    answer_grounding_score: Fraction
    hallucination_rate: Fraction
    final_consistency_score: Fraction

def create_nominal_claim() -> VisorAgenticVragClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return VisorAgenticVragClaim(
        iterative_search_rounds=Fraction(4),
        retrieved_evidence_pages=Fraction(9),
        cross_page_link_density=Fraction(2, 5),
        over_horizon_reasoning_depth=Fraction(3),
        visual_recall_at_k=Fraction(4, 5),
        answer_grounding_score=Fraction(17, 20),
        hallucination_rate=Fraction(3, 20),
        final_consistency_score=Fraction(4, 5),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_VISOR_AGENTIC_VISUAL",
    "paper_id": "2604.09508v1",
    "claim_model": "VisorAgenticVragClaim",
    "check_functions": [
        "check_iterative_search_depth",
        "check_cross_page_reasoning_connectivity",
        "check_over_horizon_alignment",
        "check_visual_recall_floor",
        "check_grounding_over_hallucination",
    ],
}

"""Implementation models for d_arxiv_strategic_algorithmic_monoculture."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class StrategicMonocultureClaim:
    """Structured claim parameters derived from arXiv paper 2604.09502v1 (cs.AI)."""

    baseline_action_similarity: Fraction
    incentivized_action_similarity: Fraction
    human_similarity_shift: Fraction
    llm_similarity_shift: Fraction
    coordination_payoff_gain: Fraction
    strategy_concentration_index: Fraction
    diversity_preservation_floor: Fraction
    equilibrium_reach_rate: Fraction

def create_nominal_claim() -> StrategicMonocultureClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return StrategicMonocultureClaim(
        baseline_action_similarity=Fraction(3, 5),
        incentivized_action_similarity=Fraction(4, 5),
        human_similarity_shift=Fraction(1, 10),
        llm_similarity_shift=Fraction(1, 5),
        coordination_payoff_gain=Fraction(3, 20),
        strategy_concentration_index=Fraction(3, 5),
        diversity_preservation_floor=Fraction(1, 5),
        equilibrium_reach_rate=Fraction(4, 5),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STRATEGIC_ALGORITHMIC_MONOCULTURE",
    "paper_id": "2604.09502v1",
    "claim_model": "StrategicMonocultureClaim",
    "check_functions": [
        "check_strategic_similarity_response",
        "check_llm_shift_exceeds_human_shift",
        "check_coordination_payoff_positive",
        "check_concentration_bounded_by_diversity_floor",
        "check_equilibrium_coordination_rate",
    ],
}

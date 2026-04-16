"""Implementation models for d_arxiv_do_we_really."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ManyObjectiveParetoFocusClaim:
    """Structured claim parameters derived from arXiv paper 2604.09417v1 (cs.AI)."""

    objective_dimension: Fraction
    hypervolume_ratio: Fraction
    knee_region_coverage: Fraction
    full_front_evaluation_cost: Fraction
    focused_search_cost: Fraction
    decision_useful_solution_ratio: Fraction
    knee_region_regret: Fraction
    sample_efficiency_gain: Fraction

def create_nominal_claim() -> ManyObjectiveParetoFocusClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return ManyObjectiveParetoFocusClaim(
        objective_dimension=Fraction(6),
        hypervolume_ratio=Fraction(4, 5),
        knee_region_coverage=Fraction(17, 20),
        full_front_evaluation_cost=Fraction(1_000),
        focused_search_cost=Fraction(420),
        decision_useful_solution_ratio=Fraction(4, 5),
        knee_region_regret=Fraction(1, 20),
        sample_efficiency_gain=Fraction(3, 10),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_DO_WE_REALLY",
    "paper_id": "2604.09417v1",
    "claim_model": "ManyObjectiveParetoFocusClaim",
    "check_functions": [
        "check_many_objective_regime",
        "check_knee_region_priority",
        "check_focus_cost_advantage",
        "check_decision_utility_density",
        "check_knee_regret_bound",
    ],
}

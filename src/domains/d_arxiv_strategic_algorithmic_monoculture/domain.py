"""D_ARXIV_STRATEGIC_ALGORITHMIC_MONOCULTURE domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STRATEGIC_ALGORITHMIC_MONOCULTURE"
DOMAIN_NAME = "Arxiv Strategic Algorithmic Monoculture"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09502v1",
]

INVARIANTS = [
    "check_strategic_similarity_response",
    "check_llm_shift_exceeds_human_shift",
    "check_coordination_payoff_positive",
    "check_concentration_bounded_by_diversity_floor",
    "check_equilibrium_coordination_rate",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STRATEGIC_ALGORITHMIC_MONOCULTURE_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STRATEGIC_ALGORITHMIC_MONOCULTURE_001"]

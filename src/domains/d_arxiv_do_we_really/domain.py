"""D_ARXIV_DO_WE_REALLY domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_DO_WE_REALLY"
DOMAIN_NAME = "Arxiv Do We Really"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09417v1",
]

INVARIANTS = [
    "check_many_objective_regime",
    "check_knee_region_priority",
    "check_focus_cost_advantage",
    "check_decision_utility_density",
    "check_knee_regret_bound",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_DO_WE_REALLY_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_DO_WE_REALLY_001"]

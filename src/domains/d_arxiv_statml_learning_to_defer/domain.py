"""D_ARXIV_STATML_LEARNING_TO_DEFER domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_LEARNING_TO_DEFER"
DOMAIN_NAME = "Arxiv StatML Learning To Defer"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.09414v1",
]

INVARIANTS = [
    "check_expert_count_positive",
    "check_deferral_rate_valid",
    "check_system_accuracy_valid",
    "check_human_accuracy_valid",
    "check_system_outperforms_ai_alone",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_LEARNING_TO_DEFER_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_LEARNING_TO_DEFER_001"]

"""D_ARXIV_STATML_CONFORMAL_PREDICTION domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_CONFORMAL_PREDICTION"
DOMAIN_NAME = "Arxiv StatML Conformal Prediction"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.07325v1",
]

INVARIANTS = [
    "check_coverage_guarantee",
    "check_alpha_valid",
    "check_coverage_level_consistency",
    "check_exchangeability",
    "check_prediction_set_size_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_CONFORMAL_PREDICTION_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_CONFORMAL_PREDICTION_001"]

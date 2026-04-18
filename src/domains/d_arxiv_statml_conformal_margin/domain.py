"""D_ARXIV_STATML_CONFORMAL_MARGIN domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_CONFORMAL_MARGIN"
DOMAIN_NAME = "Arxiv StatML Conformal Margin"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.06468v2",
]

INVARIANTS = [
    "check_margin_positive",
    "check_noise_rate_valid",
    "check_coverage_valid",
    "check_robustness",
    "check_risk_bound_valid",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_CONFORMAL_MARGIN_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_CONFORMAL_MARGIN_001"]

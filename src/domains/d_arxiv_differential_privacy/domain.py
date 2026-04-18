"""D_ARXIV_DIFFERENTIAL_PRIVACY domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_DIFFERENTIAL_PRIVACY"
DOMAIN_NAME = "SuperDP Differential Privacy via Supermartingales"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2603.26215v2",
]

INVARIANTS = [
    "check_epsilon_nonnegative",
    "check_delta_in_range",
    "check_noise_sufficient",
    "check_supermartingale_certificate",
    "check_privacy_budget_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_DIFFERENTIAL_PRIVACY_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_DIFFERENTIAL_PRIVACY_001"]

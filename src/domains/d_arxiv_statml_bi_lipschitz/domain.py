"""D_ARXIV_STATML_BI_LIPSCHITZ domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_BI_LIPSCHITZ"
DOMAIN_NAME = "Arxiv StatML Bi Lipschitz"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.06701v1",
]

INVARIANTS = [
    "check_injectivity",
    "check_lipschitz_constant_valid",
    "check_dimension_valid",
    "check_bi_lipschitz_lower_positive",
    "check_input_dimension_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_BI_LIPSCHITZ_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_BI_LIPSCHITZ_001"]

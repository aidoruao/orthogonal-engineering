"""D_ARXIV_STATML_TRANSPORT_MAPS domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_TRANSPORT_MAPS"
DOMAIN_NAME = "Arxiv StatML Transport Maps"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.07671v1",
]

INVARIANTS = [
    "check_unique_recovery",
    "check_transport_cost_nonnegative",
    "check_support_sizes_positive",
    "check_data_sufficient",
    "check_finite_data",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_TRANSPORT_MAPS_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_TRANSPORT_MAPS_001"]

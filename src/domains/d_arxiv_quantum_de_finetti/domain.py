"""D_ARXIV_QUANTUM_DE_FINETTI domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_DE_FINETTI"
DOMAIN_NAME = "Quantum De Finetti"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.09410v1",
]

INVARIANTS = [
    "check_exchangeability",
    "check_subsystem_count_valid",
    "check_de_finetti_error_nonnegative",
    "check_dimension_positive",
    "check_party_count_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_DE_FINETTI_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_DE_FINETTI_001"]

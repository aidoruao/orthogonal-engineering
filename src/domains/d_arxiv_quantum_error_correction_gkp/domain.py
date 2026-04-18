"""D_ARXIV_QUANTUM_ERROR_CORRECTION_GKP domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_ERROR_CORRECTION_GKP"
DOMAIN_NAME = "Quantum Error Correction GKP"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.08247v1",
]

INVARIANTS = [
    "check_error_rate_suppression",
    "check_squeezing_nonnegative",
    "check_physical_error_rate_valid",
    "check_logical_error_rate_valid",
    "check_code_distance_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_ERROR_CORRECTION_GKP_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_ERROR_CORRECTION_GKP_001"]

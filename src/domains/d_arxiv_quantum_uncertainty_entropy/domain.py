"""D_ARXIV_QUANTUM_UNCERTAINTY_ENTROPY domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_UNCERTAINTY_ENTROPY"
DOMAIN_NAME = "Quantum Uncertainty Entropy"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.09384v1",
]

INVARIANTS = [
    "check_von_neumann_nonnegative",
    "check_purity_valid",
    "check_entropy_purity_tradeoff",
    "check_min_entropy_nonnegative",
    "check_uncertainty_lower_bound",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_UNCERTAINTY_ENTROPY_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_UNCERTAINTY_ENTROPY_001"]

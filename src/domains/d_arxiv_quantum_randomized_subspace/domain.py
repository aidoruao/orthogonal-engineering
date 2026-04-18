"""D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE"
DOMAIN_NAME = "Quantum Randomized Subspace"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.09483v1",
]

INVARIANTS = [
    "check_subspace_dimension_valid",
    "check_spectral_gap_positive",
    "check_iteration_count_positive",
    "check_approximation_error_nonnegative",
    "check_ambient_dimension_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE_001"]

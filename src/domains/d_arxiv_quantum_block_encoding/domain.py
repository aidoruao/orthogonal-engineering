"""D_ARXIV_QUANTUM_BLOCK_ENCODING domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_BLOCK_ENCODING"
DOMAIN_NAME = "Quantum Block Encoding"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.09538v1",
]

INVARIANTS = [
    "check_subnormalization_valid",
    "check_ancilla_count_positive",
    "check_circuit_depth_positive",
    "check_efficiency",
    "check_subnormalization_factor_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_BLOCK_ENCODING_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_BLOCK_ENCODING_001"]

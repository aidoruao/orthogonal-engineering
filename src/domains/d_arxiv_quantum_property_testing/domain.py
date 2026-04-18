"""D_ARXIV_QUANTUM_PROPERTY_TESTING domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_PROPERTY_TESTING"
DOMAIN_NAME = "Quantum Property Testing"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.07954v1",
]

INVARIANTS = [
    "check_vertex_count_positive",
    "check_max_degree_positive",
    "check_query_complexity_positive",
    "check_epsilon_valid",
    "check_quantum_speedup",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_PROPERTY_TESTING_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_PROPERTY_TESTING_001"]

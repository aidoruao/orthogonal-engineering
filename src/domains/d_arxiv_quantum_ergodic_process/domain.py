"""D_ARXIV_QUANTUM_ERGODIC_PROCESS domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_ERGODIC_PROCESS"
DOMAIN_NAME = "Quantum Ergodic Process"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.09422v1",
]

INVARIANTS = [
    "check_ergodicity",
    "check_period_positive",
    "check_convergence_rate_valid",
    "check_dimension_valid",
    "check_periodicity_flag",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_ERGODIC_PROCESS_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_ERGODIC_PROCESS_001"]

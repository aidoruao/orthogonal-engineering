"""D_ARXIV_QUANTUM_NONLOCAL_GAMES domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_NONLOCAL_GAMES"
DOMAIN_NAME = "Quantum Nonlocal Games"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.09458v1",
]

INVARIANTS = [
    "check_classical_probability_valid",
    "check_quantum_probability_valid",
    "check_quantum_advantage",
    "check_entanglement_dimension_positive",
    "check_pseudo_telepathy_consistency",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_NONLOCAL_GAMES_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_NONLOCAL_GAMES_001"]

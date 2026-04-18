"""D_ARXIV_QUANTUM_RIGIDITY domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_RIGIDITY"
DOMAIN_NAME = "CHSH Rigidity Formalization in Lean 4"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2604.03884v1",
]

INVARIANTS = [
    "check_chsh_classical_bound",
    "check_chsh_quantum_bound",
    "check_quantum_requires_entanglement",
    "check_rigidity",
    "check_quantum_advantage",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_RIGIDITY_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_RIGIDITY_001"]

"""D_ARXIV_QUANTUM_STATE_TELEPORTATION domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_STATE_TELEPORTATION"
DOMAIN_NAME = "Quantum State Teleportation"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.07849v1",
]

INVARIANTS = [
    "check_fidelity_valid",
    "check_classical_communication_sufficient",
    "check_gate_noise_nonnegative",
    "check_entanglement_fidelity_valid",
    "check_teleportation_success",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_STATE_TELEPORTATION_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_STATE_TELEPORTATION_001"]

"""D_ARXIV_QUANTUM_FOCK_LATTICE domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_QUANTUM_FOCK_LATTICE"
DOMAIN_NAME = "Quantum Fock Lattice"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "quant-ph",
    "paper:2604.09341v1",
]

INVARIANTS = [
    "check_lattice_structure",
    "check_distributivity",
    "check_mode_count_positive",
    "check_photon_number_nonnegative",
    "check_lattice_size_valid",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_QUANTUM_FOCK_LATTICE_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_QUANTUM_FOCK_LATTICE_001"]

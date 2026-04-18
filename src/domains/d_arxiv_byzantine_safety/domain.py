"""D_ARXIV_BYZANTINE_SAFETY domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_BYZANTINE_SAFETY"
DOMAIN_NAME = "Byzantine Fault Safety and Liveness"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2604.03844v1",
]

INVARIANTS = [
    "check_byzantine_fault_tolerance",
    "check_safety_property",
    "check_liveness_property",
    "check_threshold_formula",
    "check_quorum_validity",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_BYZANTINE_SAFETY_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_BYZANTINE_SAFETY_001"]

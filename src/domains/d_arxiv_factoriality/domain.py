"""D_ARXIV_FACTORIALITY domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_FACTORIALITY"
DOMAIN_NAME = "Nagata Factoriality Theorem in Lean 4"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2604.05238v1",
]

INVARIANTS = [
    "check_ufd_property",
    "check_noetherian_property",
    "check_localization_ufd",
    "check_prime_generators_positive",
    "check_nagata_criterion",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_FACTORIALITY_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_FACTORIALITY_001"]

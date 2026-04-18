"""D_ARXIV_DEONTIC_STIT domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_DEONTIC_STIT"
DOMAIN_NAME = "Deontic STIT Logic and Ought-Implies-Can"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2604.00967v1",
]

INVARIANTS = [
    "check_ought_implies_can",
    "check_stit_model_validity",
    "check_oic_consistency",
    "check_alternatives_positive",
    "check_agency_requirement",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_DEONTIC_STIT_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_DEONTIC_STIT_001"]

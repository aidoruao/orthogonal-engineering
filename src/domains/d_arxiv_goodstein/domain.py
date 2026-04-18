"""D_ARXIV_GOODSTEIN domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_GOODSTEIN"
DOMAIN_NAME = "Arxiv Ouroboros Goodstein Principle"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "math.LO",
    "paper:2603.19981v1",
]

INVARIANTS = [
    "check_termination",
    "check_transfinite_required",
    "check_sequence_length_positive",
    "check_base_positive",
    "check_unprovable_in_peano",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_GOODSTEIN_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_GOODSTEIN_001"]

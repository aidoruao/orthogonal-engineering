"""D_ARXIV_RAMSEY_ARITHMETIC domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_RAMSEY_ARITHMETIC"
DOMAIN_NAME = "Arxiv Ramsey Theory and Bounding in Arithmetic"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "math.LO",
    "paper:2603.23704v2",
]

INVARIANTS = [
    "check_vertex_count_positive",
    "check_coloring_count_positive",
    "check_ramsey_number_valid",
    "check_bounding_principle",
    "check_provability",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_RAMSEY_ARITHMETIC_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_RAMSEY_ARITHMETIC_001"]

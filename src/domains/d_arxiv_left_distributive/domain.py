"""D_ARXIV_LEFT_DISTRIBUTIVE domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_LEFT_DISTRIBUTIVE"
DOMAIN_NAME = "Arxiv Left Distributive Algebras"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "math.LO",
    "paper:2604.08768v1",
]

INVARIANTS = [
    "check_left_distributivity",
    "check_freeness",
    "check_generator_count_positive",
    "check_word_problem_decidability",
    "check_algebra_size_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_LEFT_DISTRIBUTIVE_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_LEFT_DISTRIBUTIVE_001"]

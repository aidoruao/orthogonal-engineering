"""D_ARXIV_TENSE_LOGIC domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_TENSE_LOGIC"
DOMAIN_NAME = "Intuitionistic Tense Logics via Nested Sequents"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2603.29424v1",
]

INVARIANTS = [
    "check_intuitionistic_base",
    "check_loop_termination",
    "check_counter_model_extraction",
    "check_sequent_depth_positive",
    "check_decidability_via_loop_check",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_TENSE_LOGIC_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_TENSE_LOGIC_001"]

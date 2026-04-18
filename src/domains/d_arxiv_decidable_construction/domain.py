"""D_ARXIV_DECIDABLE_CONSTRUCTION domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_DECIDABLE_CONSTRUCTION"
DOMAIN_NAME = "Decidable By Construction Design-Time Verification"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2603.25414v1",
]

INVARIANTS = [
    "check_decidability",
    "check_design_time_verification",
    "check_soundness",
    "check_completeness",
    "check_verification_steps_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_DECIDABLE_CONSTRUCTION_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_DECIDABLE_CONSTRUCTION_001"]

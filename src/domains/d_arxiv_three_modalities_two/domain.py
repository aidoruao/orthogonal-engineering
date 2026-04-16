"""D_ARXIV_THREE_MODALITIES_TWO domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_THREE_MODALITIES_TWO"
DOMAIN_NAME = "Arxiv Three Modalities Two"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09426v1",
]

INVARIANTS = [
    "check_audio_channel_accessibility_floor",
    "check_haptic_channel_accessibility_floor",
    "check_text_channel_accessibility_floor",
    "check_nonvisual_navigation_success",
    "check_co_design_iteration_sufficiency",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_THREE_MODALITIES_TWO_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_THREE_MODALITIES_TWO_001"]

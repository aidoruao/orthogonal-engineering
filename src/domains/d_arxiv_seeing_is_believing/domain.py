"""D_ARXIV_SEEING_IS_BELIEVING domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_SEEING_IS_BELIEVING"
DOMAIN_NAME = "Arxiv Seeing Is Believing"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09532v1",
]

INVARIANTS = [
    "check_visual_signal_dominance",
    "check_noise_reliance_bound",
    "check_noisy_accuracy_floor",
    "check_clean_noisy_gap_control",
    "check_cross_modal_prompt_gain",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_SEEING_IS_BELIEVING_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_SEEING_IS_BELIEVING_001"]

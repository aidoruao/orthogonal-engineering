"""D_ARXIV_VISOR_AGENTIC_VISUAL domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_VISOR_AGENTIC_VISUAL"
DOMAIN_NAME = "Arxiv Visor Agentic Visual"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09508v1",
]

INVARIANTS = [
    "check_iterative_search_depth",
    "check_cross_page_reasoning_connectivity",
    "check_over_horizon_alignment",
    "check_visual_recall_floor",
    "check_grounding_over_hallucination",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_VISOR_AGENTIC_VISUAL_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_VISOR_AGENTIC_VISUAL_001"]

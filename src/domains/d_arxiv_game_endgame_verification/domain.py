"""D_ARXIV_GAME_ENDGAME_VERIFICATION domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_GAME_ENDGAME_VERIFICATION"
DOMAIN_NAME = "Chess Endgame Tablebase Verification"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2604.07907v1",
]

INVARIANTS = [
    "check_tablebase_completeness",
    "check_tablebase_consistency",
    "check_positions_positive",
    "check_capture_quiet_ratio_valid",
    "check_decomposition_depth_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_GAME_ENDGAME_VERIFICATION_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_GAME_ENDGAME_VERIFICATION_001"]

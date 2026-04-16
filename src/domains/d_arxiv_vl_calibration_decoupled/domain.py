"""D_ARXIV_VL_CALIBRATION_DECOUPLED domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_VL_CALIBRATION_DECOUPLED"
DOMAIN_NAME = "Arxiv Vl Calibration Decoupled"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09529v1",
]

INVARIANTS = [
    "check_answer_channel_calibration_gain",
    "check_reasoning_channel_calibration_gain",
    "check_overconfidence_control_answer_channel",
    "check_overconfidence_control_reasoning_channel",
    "check_risk_aware_selective_prediction",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_VL_CALIBRATION_DECOUPLED_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_VL_CALIBRATION_DECOUPLED_001"]

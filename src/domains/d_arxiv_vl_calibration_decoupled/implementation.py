"""Implementation models for d_arxiv_vl_calibration_decoupled."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DecoupledCalibrationClaim:
    """Structured claim parameters derived from arXiv paper 2604.09529v1 (cs.AI)."""

    answer_channel_ece_before: Fraction
    answer_channel_ece_after: Fraction
    reasoning_channel_ece_before: Fraction
    reasoning_channel_ece_after: Fraction
    answer_confidence_when_wrong: Fraction
    reasoning_confidence_when_wrong: Fraction
    risk_coverage_auc: Fraction
    abstention_precision: Fraction

def create_nominal_claim() -> DecoupledCalibrationClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return DecoupledCalibrationClaim(
        answer_channel_ece_before=Fraction(9, 50),
        answer_channel_ece_after=Fraction(1, 10),
        reasoning_channel_ece_before=Fraction(1, 5),
        reasoning_channel_ece_after=Fraction(11, 100),
        answer_confidence_when_wrong=Fraction(11, 20),
        reasoning_confidence_when_wrong=Fraction(1, 2),
        risk_coverage_auc=Fraction(4, 5),
        abstention_precision=Fraction(17, 20),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_VL_CALIBRATION_DECOUPLED",
    "paper_id": "2604.09529v1",
    "claim_model": "DecoupledCalibrationClaim",
    "check_functions": [
        "check_answer_channel_calibration_gain",
        "check_reasoning_channel_calibration_gain",
        "check_overconfidence_control_answer_channel",
        "check_overconfidence_control_reasoning_channel",
        "check_risk_aware_selective_prediction",
    ],
}

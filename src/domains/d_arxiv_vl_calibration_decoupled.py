"""arXiv-derived domain invariants for VL-Calibration: Decoupled Confidence Calibration for Large Vision-Language Models Reasoning."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject


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


def check_answer_channel_calibration_gain(data: DecoupledCalibrationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Answer-channel calibration error should improve after decoupling.

    Standard: arXiv 2604.09529v1 (cs.AI) claim operationalization.
    falsifies_if: answer_channel_ece_after >= answer_channel_ece_before.

    Returns:
        Tuple of (success, proof).
    """
    success = data.answer_channel_ece_after < data.answer_channel_ece_before
    proof = ProofObject(
        rule="check_answer_channel_calibration_gain",
        premises=[
            "paper_id=2604.09529v1",
            f"answer_channel_ece_before={data.answer_channel_ece_before}",
            f"answer_channel_ece_after={data.answer_channel_ece_after}",
        ],
        conclusion=(
            "PASS: answer-channel calibration improves"
            if success else "FAIL: answer-channel calibration does not improve"
        ),
    )
    return success, proof

def check_reasoning_channel_calibration_gain(data: DecoupledCalibrationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Reasoning-channel calibration error should improve after decoupling.

    Standard: arXiv 2604.09529v1 (cs.AI) claim operationalization.
    falsifies_if: reasoning_channel_ece_after >= reasoning_channel_ece_before.

    Returns:
        Tuple of (success, proof).
    """
    success = data.reasoning_channel_ece_after < data.reasoning_channel_ece_before
    proof = ProofObject(
        rule="check_reasoning_channel_calibration_gain",
        premises=[
            "paper_id=2604.09529v1",
            f"reasoning_channel_ece_before={data.reasoning_channel_ece_before}",
            f"reasoning_channel_ece_after={data.reasoning_channel_ece_after}",
        ],
        conclusion=(
            "PASS: reasoning-channel calibration improves"
            if success else "FAIL: reasoning-channel calibration does not improve"
        ),
    )
    return success, proof

def check_overconfidence_control_answer_channel(data: DecoupledCalibrationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Wrong-answer confidence should remain bounded.

    Standard: arXiv 2604.09529v1 (cs.AI) claim operationalization.
    falsifies_if: answer_confidence_when_wrong > 3/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.answer_confidence_when_wrong <= Fraction(3, 5)
    proof = ProofObject(
        rule="check_overconfidence_control_answer_channel",
        premises=[
            "paper_id=2604.09529v1",
            f"answer_confidence_when_wrong={data.answer_confidence_when_wrong}",
        ],
        conclusion=(
            "PASS: answer-channel overconfidence is controlled"
            if success else "FAIL: answer-channel remains overconfident when wrong"
        ),
    )
    return success, proof

def check_overconfidence_control_reasoning_channel(data: DecoupledCalibrationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Wrong-reasoning confidence should remain bounded.

    Standard: arXiv 2604.09529v1 (cs.AI) claim operationalization.
    falsifies_if: reasoning_confidence_when_wrong > 3/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.reasoning_confidence_when_wrong <= Fraction(3, 5)
    proof = ProofObject(
        rule="check_overconfidence_control_reasoning_channel",
        premises=[
            "paper_id=2604.09529v1",
            f"reasoning_confidence_when_wrong={data.reasoning_confidence_when_wrong}",
        ],
        conclusion=(
            "PASS: reasoning-channel overconfidence is controlled"
            if success else "FAIL: reasoning-channel remains overconfident when wrong"
        ),
    )
    return success, proof

def check_risk_aware_selective_prediction(data: DecoupledCalibrationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Decoupled calibration should improve risk-aware abstention quality.

    Standard: arXiv 2604.09529v1 (cs.AI) claim operationalization.
    falsifies_if: risk_coverage_auc < 3/4 OR abstention_precision < 4/5.

    Returns:
        Tuple of (success, proof).
    """
    success = (data.risk_coverage_auc >= Fraction(3, 4)) and (data.abstention_precision >= Fraction(4, 5))
    proof = ProofObject(
        rule="check_risk_aware_selective_prediction",
        premises=[
            "paper_id=2604.09529v1",
            f"risk_coverage_auc={data.risk_coverage_auc}",
            f"abstention_precision={data.abstention_precision}",
        ],
        conclusion=(
            "PASS: selective prediction quality is high"
            if success else "FAIL: selective prediction quality is insufficient"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """
    Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09529v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = DecoupledCalibrationClaim(
        answer_channel_ece_before=Fraction(9, 50),
        answer_channel_ece_after=Fraction(1, 10),
        reasoning_channel_ece_before=Fraction(1, 5),
        reasoning_channel_ece_after=Fraction(11, 100),
        answer_confidence_when_wrong=Fraction(11, 20),
        reasoning_confidence_when_wrong=Fraction(1, 2),
        risk_coverage_auc=Fraction(4, 5),
        abstention_precision=Fraction(17, 20),
    )

    checks = [
        ("check_answer_channel_calibration_gain", check_answer_channel_calibration_gain),
        ("check_reasoning_channel_calibration_gain", check_reasoning_channel_calibration_gain),
        ("check_overconfidence_control_answer_channel", check_overconfidence_control_answer_channel),
        ("check_overconfidence_control_reasoning_channel", check_overconfidence_control_reasoning_channel),
        ("check_risk_aware_selective_prediction", check_risk_aware_selective_prediction),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

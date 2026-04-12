"""D_FORENSIC_PSYCHOLOGY invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes Dusky competency standards,
Daubert admissibility, civil commitment review intervals, and actuarial risk assessment
validity requirements.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    CompetencyEvaluation,
    ExpertTestimony,
    CivilCommitment,
    RiskAssessment,
)


def check_competency_to_stand_trial(
    evaluation: CompetencyEvaluation,
) -> Tuple[bool, ProofObject]:
    """
    Rule: Defendant must understand charges and be able to assist counsel (Dusky v. United States, 362 U.S. 402, 1960).

    falsifies_if: understands_charges is False OR can_assist_counsel is False.
    """
    understands = evaluation.understands_charges
    can_assist = evaluation.can_assist_counsel

    if not (understands and can_assist):
        return False, ProofObject(
            rule="competency_to_stand_trial",
            premises=[
                f"eval_id={evaluation.eval_id}",
                f"defendant_id={evaluation.defendant_id}",
                f"understands_charges={understands}",
                f"can_assist_counsel={can_assist}",
            ],
            conclusion="VIOLATION: Defendant lacks competency per Dusky standard",
        )

    return True, ProofObject(
        rule="competency_to_stand_trial",
        premises=[
            f"eval_id={evaluation.eval_id}",
            f"defendant_id={evaluation.defendant_id}",
            "understands_charges=True",
            "can_assist_counsel=True",
        ],
        conclusion="Defendant competent to stand trial per Dusky v. United States",
    )


def check_daubert_admissibility(testimony: ExpertTestimony) -> Tuple[bool, ProofObject]:
    """
    Rule: Expert methodology must satisfy at least three of four Daubert factors, be peer-reviewed,
    and be testable (Daubert v. Merrell Dow Pharmaceuticals, 509 U.S. 579, 1993).

    falsifies_if: daubert_factors_met < Fraction(3, 4) OR methodology_peer_reviewed is False
                  OR methodology_testable is False.
    """
    factors_sufficient = testimony.daubert_factors_met >= Fraction(3, 4)
    peer_reviewed = testimony.methodology_peer_reviewed
    testable = testimony.methodology_testable

    if not (factors_sufficient and peer_reviewed and testable):
        return False, ProofObject(
            rule="daubert_admissibility",
            premises=[
                f"testimony_id={testimony.testimony_id}",
                f"daubert_factors_met={testimony.daubert_factors_met}",
                f"methodology_peer_reviewed={peer_reviewed}",
                f"methodology_testable={testable}",
            ],
            conclusion="VIOLATION: Expert testimony fails Daubert admissibility standard",
        )

    return True, ProofObject(
        rule="daubert_admissibility",
        premises=[
            f"testimony_id={testimony.testimony_id}",
            f"daubert_factors_met={testimony.daubert_factors_met}",
            "methodology_peer_reviewed=True",
            "methodology_testable=True",
        ],
        conclusion="Expert testimony admissible per Daubert v. Merrell Dow Pharmaceuticals",
    )


def check_evaluator_qualifications(
    evaluation: CompetencyEvaluation,
) -> Tuple[bool, ProofObject]:
    """
    Rule: Forensic evaluators must be licensed and board-certified to conduct competency evaluations
    (APA Specialty Guidelines for Forensic Psychology, 2013).

    falsifies_if: evaluator_licensed is False OR evaluator_board_certified is False.
    """
    licensed = evaluation.evaluator_licensed
    board_certified = evaluation.evaluator_board_certified

    if not (licensed and board_certified):
        return False, ProofObject(
            rule="evaluator_qualifications",
            premises=[
                f"eval_id={evaluation.eval_id}",
                f"evaluator_id={evaluation.evaluator_id}",
                f"evaluator_licensed={licensed}",
                f"evaluator_board_certified={board_certified}",
            ],
            conclusion="VIOLATION: Evaluator lacks required licensure or board certification",
        )

    return True, ProofObject(
        rule="evaluator_qualifications",
        premises=[
            f"eval_id={evaluation.eval_id}",
            f"evaluator_id={evaluation.evaluator_id}",
            "evaluator_licensed=True",
            "evaluator_board_certified=True",
        ],
        conclusion="Evaluator meets APA Specialty Guidelines qualification requirements",
    )


def check_civil_commitment_review(commitment: CivilCommitment) -> Tuple[bool, ProofObject]:
    """
    Rule: Civil commitment orders must be reviewed within the maximum allowable interval
    (Jackson v. Indiana, 406 U.S. 715, 1972).

    falsifies_if: days_since_last_review > max_review_interval_days.
    """
    review_current = commitment.days_since_last_review <= commitment.max_review_interval_days

    if not review_current:
        return False, ProofObject(
            rule="civil_commitment_review",
            premises=[
                f"commitment_id={commitment.commitment_id}",
                f"patient_id={commitment.patient_id}",
                f"days_since_last_review={commitment.days_since_last_review}",
                f"max_review_interval_days={commitment.max_review_interval_days}",
            ],
            conclusion="VIOLATION: Civil commitment review interval exceeded per Jackson v. Indiana",
        )

    return True, ProofObject(
        rule="civil_commitment_review",
        premises=[
            f"commitment_id={commitment.commitment_id}",
            f"patient_id={commitment.patient_id}",
            f"days_since_last_review={commitment.days_since_last_review}",
            f"max_review_interval_days={commitment.max_review_interval_days}",
        ],
        conclusion="Civil commitment review is current per Jackson v. Indiana",
    )


def check_risk_assessment_validity(assessment: RiskAssessment) -> Tuple[bool, ProofObject]:
    """
    Rule: Actuarial risk instruments must meet minimum AUC, inter-rater reliability thresholds,
    and be validated against the target population
    (APA Specialty Guidelines; actuarial instrument validation requirements).

    falsifies_if: auc_score < min_acceptable_auc OR inter_rater_reliability < min_inter_rater_reliability
                  OR validated_population_match is False.
    """
    auc_valid = assessment.auc_score >= assessment.min_acceptable_auc
    irr_valid = assessment.inter_rater_reliability >= assessment.min_inter_rater_reliability
    population_valid = assessment.validated_population_match

    if not (auc_valid and irr_valid and population_valid):
        return False, ProofObject(
            rule="risk_assessment_validity",
            premises=[
                f"assessment_id={assessment.assessment_id}",
                f"tool_name={assessment.tool_name}",
                f"auc_score={assessment.auc_score}",
                f"min_acceptable_auc={assessment.min_acceptable_auc}",
                f"inter_rater_reliability={assessment.inter_rater_reliability}",
                f"min_inter_rater_reliability={assessment.min_inter_rater_reliability}",
                f"validated_population_match={population_valid}",
            ],
            conclusion="VIOLATION: Risk assessment instrument fails validity requirements",
        )

    return True, ProofObject(
        rule="risk_assessment_validity",
        premises=[
            f"assessment_id={assessment.assessment_id}",
            f"tool_name={assessment.tool_name}",
            f"auc_score={assessment.auc_score}",
            f"inter_rater_reliability={assessment.inter_rater_reliability}",
            "validated_population_match=True",
        ],
        conclusion="Risk assessment instrument meets APA Specialty Guidelines validity requirements",
    )


def check_least_restrictive_alternative(commitment: CivilCommitment) -> Tuple[bool, ProofObject]:
    """
    Rule: Civil commitment is only permissible when danger criteria are met and the least restrictive
    alternative has been applied (O'Connor v. Donaldson, 422 U.S. 563, 1975; due process).

    falsifies_if: (danger_to_self OR danger_to_others OR gravely_disabled) AND least_restrictive_alternative is False.
    """
    danger_present = (
        commitment.danger_to_self
        or commitment.danger_to_others
        or commitment.gravely_disabled
    )
    lra_applied = commitment.least_restrictive_alternative

    violated = danger_present and not lra_applied

    if violated:
        return False, ProofObject(
            rule="least_restrictive_alternative",
            premises=[
                f"commitment_id={commitment.commitment_id}",
                f"danger_to_self={commitment.danger_to_self}",
                f"danger_to_others={commitment.danger_to_others}",
                f"gravely_disabled={commitment.gravely_disabled}",
                f"least_restrictive_alternative={lra_applied}",
            ],
            conclusion=(
                "VIOLATION: Commitment applies without least restrictive alternative "
                "per O'Connor v. Donaldson"
            ),
        )

    return True, ProofObject(
        rule="least_restrictive_alternative",
        premises=[
            f"commitment_id={commitment.commitment_id}",
            f"danger_present={danger_present}",
            f"least_restrictive_alternative={lra_applied}",
        ],
        conclusion="Civil commitment satisfies least restrictive alternative requirement per O'Connor v. Donaldson",
    )


def run_all_invariants() -> dict:
    """Run all D_FORENSIC_PSYCHOLOGY invariants with nominal sample data.

    falsifies_if: any forensic psychology invariant fails or raises an exception.
    """
    evaluation = CompetencyEvaluation(
        eval_id="EVAL-001",
        evaluator_id="EVAL-PSY-001",
        defendant_id="DEF-001",
        understands_charges=True,
        can_assist_counsel=True,
        evaluation_tools_used=("ECST-R", "MacCAT-CA"),
        evaluator_licensed=True,
        evaluator_board_certified=True,
    )
    testimony = ExpertTestimony(
        testimony_id="TEST-001",
        expert_id="EXPERT-001",
        methodology_peer_reviewed=True,
        methodology_testable=True,
        known_error_rate=Fraction(5, 100),
        max_acceptable_error_rate=Fraction(10, 100),
        general_acceptance=True,
        daubert_factors_met=Fraction(4, 4),
    )
    commitment = CivilCommitment(
        commitment_id="COMMIT-001",
        patient_id="PATIENT-001",
        danger_to_self=False,
        danger_to_others=True,
        gravely_disabled=False,
        least_restrictive_alternative=True,
        periodic_review_days=Fraction(90),
        max_review_interval_days=Fraction(180),
        days_since_last_review=Fraction(90),
    )
    assessment = RiskAssessment(
        assessment_id="RISK-001",
        tool_name="HCR-20",
        auc_score=Fraction(75, 100),
        min_acceptable_auc=Fraction(70, 100),
        inter_rater_reliability=Fraction(80, 100),
        min_inter_rater_reliability=Fraction(70, 100),
        validated_population_match=True,
    )

    checks = [
        (
            "check_competency_to_stand_trial",
            lambda: check_competency_to_stand_trial(evaluation),
        ),
        (
            "check_daubert_admissibility",
            lambda: check_daubert_admissibility(testimony),
        ),
        (
            "check_evaluator_qualifications",
            lambda: check_evaluator_qualifications(evaluation),
        ),
        (
            "check_civil_commitment_review",
            lambda: check_civil_commitment_review(commitment),
        ),
        (
            "check_risk_assessment_validity",
            lambda: check_risk_assessment_validity(assessment),
        ),
        (
            "check_least_restrictive_alternative",
            lambda: check_least_restrictive_alternative(commitment),
        ),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_FORENSIC_PSYCHOLOGY invariants: PASS")

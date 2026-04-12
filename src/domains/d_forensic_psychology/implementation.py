"""D_FORENSIC_PSYCHOLOGY Implementation — competency, testimony, commitment, and risk records.

All arithmetic uses Fraction. No floats.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class CompetencyEvaluation:
    """Competency-to-stand-trial evaluation record (Dusky v. United States, 362 U.S. 402, 1960)."""

    eval_id: str
    evaluator_id: str
    defendant_id: str
    understands_charges: bool
    can_assist_counsel: bool
    evaluation_tools_used: Tuple[str, ...]
    evaluator_licensed: bool
    evaluator_board_certified: bool


@dataclass(frozen=True)
class ExpertTestimony:
    """Expert testimony admissibility record (Daubert v. Merrell Dow Pharmaceuticals, 509 U.S. 579, 1993)."""

    testimony_id: str
    expert_id: str
    methodology_peer_reviewed: bool
    methodology_testable: bool
    known_error_rate: Fraction
    max_acceptable_error_rate: Fraction
    general_acceptance: bool
    daubert_factors_met: Fraction  # proportion of 4 Daubert factors, e.g. Fraction(3, 4)


@dataclass(frozen=True)
class CivilCommitment:
    """Civil commitment record with periodic review tracking (Jackson v. Indiana, 406 U.S. 715, 1972)."""

    commitment_id: str
    patient_id: str
    danger_to_self: bool
    danger_to_others: bool
    gravely_disabled: bool
    least_restrictive_alternative: bool
    periodic_review_days: Fraction
    max_review_interval_days: Fraction
    days_since_last_review: Fraction


@dataclass(frozen=True)
class RiskAssessment:
    """Actuarial risk assessment instrument record (APA Specialty Guidelines, 2013)."""

    assessment_id: str
    tool_name: str
    auc_score: Fraction
    min_acceptable_auc: Fraction
    inter_rater_reliability: Fraction
    min_inter_rater_reliability: Fraction
    validated_population_match: bool

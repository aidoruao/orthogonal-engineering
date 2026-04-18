"""Implementation models for d_arxiv_statml_learning_to_defer."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class LearningToDeferClaim:
    """Structured claim parameters derived from arXiv paper 2604.09414v1 (stat.ML)."""

    expert_count: Fraction
    deferral_rate: Fraction
    system_accuracy: Fraction
    human_accuracy: Fraction
    ai_accuracy: Fraction


def create_nominal_claim() -> LearningToDeferClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return LearningToDeferClaim(
        expert_count=Fraction(3),
        deferral_rate=Fraction(1, 4),
        system_accuracy=Fraction(9, 10),
        human_accuracy=Fraction(19, 20),
        ai_accuracy=Fraction(4, 5),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_LEARNING_TO_DEFER",
    "paper_id": "2604.09414v1",
    "claim_model": "LearningToDeferClaim",
    "check_functions": [
        "check_expert_count_positive",
        "check_deferral_rate_valid",
        "check_system_accuracy_valid",
        "check_human_accuracy_valid",
        "check_system_outperforms_ai_alone",
    ],
}

"""Implementation models for d_arxiv_safeadapt_provably_safe."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class SafeAdaptPolicyUpdateClaim:
    """Structured claim parameters derived from arXiv paper 2604.09452v1 (cs.AI)."""

    safety_constraint_satisfaction_before: Fraction
    safety_constraint_satisfaction_after: Fraction
    task_return_before: Fraction
    task_return_after: Fraction
    constraint_violation_probability: Fraction
    adaptation_step_count: Fraction
    formal_safety_margin: Fraction
    distribution_shift_resilience: Fraction

def create_nominal_claim() -> SafeAdaptPolicyUpdateClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return SafeAdaptPolicyUpdateClaim(
        safety_constraint_satisfaction_before=Fraction(9, 10),
        safety_constraint_satisfaction_after=Fraction(19, 20),
        task_return_before=Fraction(7, 10),
        task_return_after=Fraction(3, 4),
        constraint_violation_probability=Fraction(1, 50),
        adaptation_step_count=Fraction(12),
        formal_safety_margin=Fraction(1, 10),
        distribution_shift_resilience=Fraction(4, 5),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_SAFEADAPT_PROVABLY_SAFE",
    "paper_id": "2604.09452v1",
    "claim_model": "SafeAdaptPolicyUpdateClaim",
    "check_functions": [
        "check_safety_constraint_preservation",
        "check_violation_probability_cap",
        "check_return_non_degradation",
        "check_formal_margin_positive",
        "check_shift_resilience_floor",
    ],
}

"""Implementation models for d_arxiv_case_grounded_evidence."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class CaseGroundedVerificationClaim:
    """Structured claim parameters derived from arXiv paper 2604.09537v1 (cs.AI)."""

    supported_case_count: Fraction
    evaluated_case_count: Fraction
    evidence_dependency_drop: Fraction
    counterfactual_flip_rate: Fraction
    retrieval_leakage_rate: Fraction
    case_specific_evidence_ratio: Fraction
    label_only_baseline_score: Fraction
    evidence_conditioned_score: Fraction

def create_nominal_claim() -> CaseGroundedVerificationClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return CaseGroundedVerificationClaim(
        supported_case_count=Fraction(88),
        evaluated_case_count=Fraction(100),
        evidence_dependency_drop=Fraction(3, 10),
        counterfactual_flip_rate=Fraction(1, 2),
        retrieval_leakage_rate=Fraction(1, 10),
        case_specific_evidence_ratio=Fraction(4, 5),
        label_only_baseline_score=Fraction(7, 10),
        evidence_conditioned_score=Fraction(17, 20),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_CASE_GROUNDED_EVIDENCE",
    "paper_id": "2604.09537v1",
    "claim_model": "CaseGroundedVerificationClaim",
    "check_functions": [
        "check_case_support_coverage",
        "check_evidence_sensitivity",
        "check_counterfactual_consistency",
        "check_retrieval_leakage_control",
        "check_evidence_conditioning_gain",
    ],
}

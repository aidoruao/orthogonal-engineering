"""D_ARXIV_INV_STABILIZATION_WITHOUT_SIMPLIFICATION domain metadata and claim model.

Paper: arXiv 2604.06709v1 (cs.SE)
Title: "Stabilization Without Simplification: A Two-Dimensional Model of Software Evolution"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class StabilizationClaim:
    """Structured claim parameters for the Yeshua Inversion.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    system_name: str
    has_structural_regularization: bool
    has_process_stabilization: bool
    has_covariance_control: bool
    structural_burden: Fraction
    uncertainty: Fraction
    burden_change: Fraction
    uncertainty_change: Fraction


@dataclass(frozen=True)
class StabilizationEvidence:
    """Evidence bundle for the inversion verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: StabilizationClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_STABILIZATION_WITHOUT_SIMPLIFICATION",
    "claim_model": "StabilizationClaim",
    "evidence_model": "StabilizationEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "paper_id": "2604.06709v1",
    "paper_title": "Stabilization Without Simplification: A Two-Dimensional Model of Software Evolution",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

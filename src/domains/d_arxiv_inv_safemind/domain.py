"""D_ARXIV_INV_SAFEMIND domain metadata and claim model.

Paper: arXiv 2604.09474v1 (cs.AI / cs.RO)
Title: "SafeMind: A Risk-Aware Differentiable Control Framework for Adaptive and Safe Quadruped Locomotion"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class SafeMindClaim:
    """Structured claim parameters for the Yeshua Inversion.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    perception_noise_variance: Fraction
    friction_coefficient_min: Fraction
    friction_coefficient_max: Fraction
    model_uncertainty_confidence: Fraction
    controller_name: str
    uses_variance_aware_barrier: bool
    uses_differentiable_qp: bool
    has_meta_adaptive_risk: bool
    safety_violation_rate: Fraction
    safety_threshold: Fraction


@dataclass(frozen=True)
class SafeMindEvidence:
    """Evidence bundle for the inversion verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: SafeMindClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_SAFEMIND",
    "claim_model": "SafeMindClaim",
    "evidence_model": "SafeMindEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "paper_id": "2604.09474v1",
    "paper_title": "SafeMind: A Risk-Aware Differentiable Control Framework for Adaptive and Safe Quadruped Locomotion",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

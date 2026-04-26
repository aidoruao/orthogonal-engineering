"""D_ARXIV_INV_TRACTABILITY_FRONTIER domain metadata and claim model.

Paper: arXiv 2604.07349v1 (cs.LO / cs.CC / cs.AI)
Title: "Toward a Tractability Frontier for Exact Relevance Certification"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class TractabilityFrontierClaim:
    """Structured claim parameters for the Yeshua Inversion.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    problem_name: str
    has_bounded_coordinate_influence: bool
    has_separable_quotient_structure: bool
    coordinate_count: int
    is_exact: bool
    is_efficiently_checkable: bool
    obstruction_family_present: bool


@dataclass(frozen=True)
class TractabilityFrontierEvidence:
    """Evidence bundle for the inversion verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: TractabilityFrontierClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_TRACTABILITY_FRONTIER",
    "claim_model": "TractabilityFrontierClaim",
    "evidence_model": "TractabilityFrontierEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "paper_id": "2604.07349v1",
    "paper_title": "Toward a Tractability Frontier for Exact Relevance Certification",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

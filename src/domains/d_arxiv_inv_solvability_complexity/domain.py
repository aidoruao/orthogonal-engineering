"""D_ARXIV_INV_SOLVABILITY_COMPLEXITY domain metadata and claim model.

Paper: arXiv 2603.18955v1 (math.LO / cs.LO / math.SP)
Title: "Foundational Analysis Of The Solvability Complexity Index: The Weihrauch-SCI Intermediate Hierarchy And A Koopman Operator Example"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class SolvabilityComplexityClaim:
    """Structured claim parameters for the Yeshua Inversion.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    problem_name: str
    base_regularity_class: str
    uses_fixed_query_policy: bool
    uses_adaptive_query_policy: bool
    sci_height: int
    weihrauch_sci_rank: int
    rank_comparable: bool


@dataclass(frozen=True)
class SolvabilityComplexityEvidence:
    """Evidence bundle for the inversion verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: SolvabilityComplexityClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_SOLVABILITY_COMPLEXITY",
    "claim_model": "SolvabilityComplexityClaim",
    "evidence_model": "SolvabilityComplexityEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "paper_id": "2603.18955v1",
    "paper_title": "Foundational Analysis Of The Solvability Complexity Index: The Weihrauch-SCI Intermediate Hierarchy And A Koopman Operator Example",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

"""D_ARXIV_INV_DEFENSE_TRILEMMA domain metadata and claim model.

Paper: arXiv 2604.06436v2 (cs.CR)
Title: "The Defense Trilemma: Why Prompt Injection Defense Wrappers Fail?"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DefenseTrilemmaClaim:
    """Structured claim parameters for the Yeshua Inversion.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    defense_name: str
    is_continuous: bool
    preserves_utility: bool
    is_complete: bool
    prompt_space_finite: bool
    uses_allow_list: bool
    unsafe_inputs_detected: Fraction
    total_inputs: Fraction
    safety_threshold: Fraction


@dataclass(frozen=True)
class DefenseTrilemmaEvidence:
    """Evidence bundle for the inversion verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: DefenseTrilemmaClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_DEFENSE_TRILEMMA",
    "claim_model": "DefenseTrilemmaClaim",
    "evidence_model": "DefenseTrilemmaEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "paper_id": "2604.06436v2",
    "paper_title": "The Defense Trilemma: Why Prompt Injection Defense Wrappers Fail?",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

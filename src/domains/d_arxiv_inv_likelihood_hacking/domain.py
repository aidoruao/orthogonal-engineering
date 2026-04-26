"""D_ARXIV_INV_LIKELIHOOD_HACKING domain metadata and claim model.

Paper: arXiv 2603.24126v1 (cs.PL / cs.LG)
Title: "Likelihood hacking in probabilistic program synthesis"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class LikelihoodHackingClaim:
    """Structured claim parameters for the Yeshua Inversion.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    program_name: str
    language_fragment: str
    enforces_normalisation: bool
    has_syntactic_safety_checks: bool
    uses_rl_training: bool
    optimisation_pressure: Fraction
    violation_rate_threshold: Fraction
    observed_violation_rate: Fraction


@dataclass(frozen=True)
class LikelihoodHackingEvidence:
    """Evidence bundle for the inversion verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: LikelihoodHackingClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_LIKELIHOOD_HACKING",
    "claim_model": "LikelihoodHackingClaim",
    "evidence_model": "LikelihoodHackingEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "paper_id": "2603.24126v1",
    "paper_title": "Likelihood hacking in probabilistic program synthesis",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

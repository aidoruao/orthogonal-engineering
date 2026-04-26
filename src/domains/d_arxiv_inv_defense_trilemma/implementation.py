"""D_ARXIV_INV_DEFENSE_TRILEMMA implementation — Yeshua Inversion.

Paper: arXiv 2604.06436v2 (cs.CR)
Title: "The Defense Trilemma: Why Prompt Injection Defense Wrappers Fail?"

IMPOSSIBLE_CLAIM:
  No continuous, utility-preserving wrapper defense D: X → X can make all
  outputs strictly safe for a language model with connected prompt space.
  Continuity, utility preservation, and completeness cannot coexist.

YESHUA_INVERSION:
  Restrict the domain to discrete, finite prompt spaces (e.g., enumerated
  allow-lists of tokens) and sacrifice utility preservation by rejecting
  ambiguous inputs. Under this restriction, a discrete defense D_discrete
  can achieve completeness because continuity is no longer required and
  utility preservation is replaced by a safety-first policy.

Mathematical Standards:
- Original proof uses topological continuity on a connected metric space.
- Inversion uses finite discrete spaces where every function is continuous
  in the discrete topology, but the key is that the *connectedness* hypothesis
  is removed, breaking the trilemma.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class DefenseModel:
    """A model of a defense mechanism.

    Falsifies if: defense properties are inconsistent.
    falsifies_if: defense properties are inconsistent.
    """
    defense_name: str
    is_continuous: bool
    preserves_utility: bool
    is_complete: bool
    prompt_space_finite: bool
    uses_allow_list: bool


@dataclass(frozen=True)
class DefenseTrilemmaClaim:
    """Structured claim for the Yeshua Inversion of the Defense Trilemma.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    defense: DefenseModel
    unsafe_inputs_detected: Fraction
    total_inputs: Fraction
    safety_threshold: Fraction


@dataclass(frozen=True)
class DefenseTrilemmaEvidence:
    """Evidence bundle for the inversion.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: DefenseTrilemmaClaim
    empirical_validation_result: str
    formal_proof_reference: str


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

IMPOSSIBLE_CLAIM = (
    "No continuous, utility-preserving wrapper defense D: X → X can make all "
    "outputs strictly safe for a language model with connected prompt space. "
    "Continuity, utility preservation, and completeness cannot coexist."
)

YESHUA_INVERSION = (
    "Restrict the domain to discrete, finite prompt spaces (e.g., enumerated "
    "allow-lists of tokens) and sacrifice utility preservation by rejecting "
    "ambiguous inputs. Under this restriction, a discrete defense D_discrete "
    "can achieve completeness because continuity is no longer required and "
    "utility preservation is replaced by a safety-first policy."
)

DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_DEFENSE_TRILEMMA",
    "paper_id": "2604.06436v2",
    "claim_model": "DefenseTrilemmaClaim",
    "evidence_model": "DefenseTrilemmaEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

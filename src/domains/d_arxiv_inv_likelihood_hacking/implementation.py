"""D_ARXIV_INV_LIKELIHOOD_HACKING implementation — Yeshua Inversion.

Paper: arXiv 2603.24126v1 (cs.PL / cs.LG)
Title: "Likelihood hacking in probabilistic program synthesis"

IMPOSSIBLE_CLAIM:
  Language models trained by RL to write probabilistic programs will inevitably
  discover likelihood hacking (LH): artificially inflating marginal-likelihood
  reward by producing programs whose data distribution fails to normalise.
  No RL-trained program synthesizer can avoid LH exploits under optimisation
  pressure.

YESHUA_INVERSION:
  Restrict the domain to the safe language fragment L_safe with sufficient
  syntactic conditions that prevent likelihood hacking. Programs in L_safe
  cannot produce non-normalising distributions because the language enforces
  normalisation at the syntax level (e.g., SafeStan). Under this restriction,
  RL-trained synthesizers cannot hack the likelihood because the exploit
  primitive (non-normalising distribution) is syntactically excluded.

Mathematical Standards:
- Original claim: optimisation pressure drives discovery of LH exploits.
- Inversion: syntactic restriction to L_safe eliminates the exploit surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class ProbabilisticProgram:
    """A model of a probabilistic program.

    Falsifies if: program properties are inconsistent.
    falsifies_if: program properties are inconsistent.
    """
    program_name: str
    language_fragment: str
    enforces_normalisation: bool
    has_syntactic_safety_checks: bool


@dataclass(frozen=True)
class TrainingSetup:
    """A model of the RL training setup.

    Falsifies if: setup properties are inconsistent.
    falsifies_if: setup properties are inconsistent.
    """
    uses_rl_training: bool
    optimisation_pressure: Fraction
    violation_rate_threshold: Fraction


@dataclass(frozen=True)
class LikelihoodHackingClaim:
    """Structured claim for the Yeshua Inversion of likelihood hacking.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    program: ProbabilisticProgram
    training: TrainingSetup
    observed_violation_rate: Fraction


@dataclass(frozen=True)
class LikelihoodHackingEvidence:
    """Evidence bundle for the inversion.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: LikelihoodHackingClaim
    empirical_validation_result: str
    formal_proof_reference: str


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

IMPOSSIBLE_CLAIM = (
    "Language models trained by RL to write probabilistic programs will inevitably "
    "discover likelihood hacking (LH): artificially inflating marginal-likelihood "
    "reward by producing programs whose data distribution fails to normalise. "
    "No RL-trained program synthesizer can avoid LH exploits under optimisation "
    "pressure."
)

YESHUA_INVERSION = (
    "Restrict the domain to the safe language fragment L_safe with sufficient "
    "syntactic conditions that prevent likelihood hacking. Programs in L_safe "
    "cannot produce non-normalising distributions because the language enforces "
    "normalisation at the syntax level (e.g., SafeStan). Under this restriction, "
    "RL-trained synthesizers cannot hack the likelihood because the exploit "
    "primitive (non-normalising distribution) is syntactically excluded."
)

DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_LIKELIHOOD_HACKING",
    "paper_id": "2603.24126v1",
    "claim_model": "LikelihoodHackingClaim",
    "evidence_model": "LikelihoodHackingEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

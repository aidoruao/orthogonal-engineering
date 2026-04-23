"""D_EPISTEMOLOGY_SUBSTRATE implementation — Epistemological substrate.

Phase B1 of Depositive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class EpistemicState:
    """Epistemological state of a knowledge system.

    falsifies_if: bayesian_evidence == Fraction(0, 1).
    falsifies_if: falsifiability_ratio < Fraction(1, 1).
    """
    knowledge_claims: int
    falsifiable_claims: int
    falsifiability_ratio: Fraction
    bayesian_prior: Fraction
    bayesian_likelihood: Fraction
    bayesian_evidence: Fraction
    bayesian_posterior: Fraction
    information_gain: Fraction
    gettier_situations: int
    epistemic_closure_violations: int
    grounding_model: str
    explanatory_debt: Fraction


DOMAIN_METADATA = {
    "id": "EPISTEMOLOGY_SUBSTRATE",
    "claim_model": "EpistemicState",
    "check_functions": [
        "check_universal_falsifiability",
        "check_bayesian_coherence",
        "check_information_gain_positive",
        "check_gettier_immunity",
        "check_epistemic_closure",
        "check_grounding_model_debt",
        "check_regress_convergence",
    ],
}

"""D_ARXIV_INV_SHARP_LOCAL_MINIMA domain metadata and claim model.

Paper: arXiv 2604.09412v1 (stat.ML / cs.LG)
Title: "Sharp description of local minima in the loss landscape of high-dimensional two-layer ReLU neural networks"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class SharpLocalMinimaClaim:
    """Structured claim parameters for the Yeshua Inversion.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    network_name: str
    width: int
    teacher_dimensionality: int
    is_overparameterised: bool
    uses_sgd: bool
    converged_to_global_minimum: bool
    spurious_solution_rate: Fraction
    spurious_rate_threshold: Fraction


@dataclass(frozen=True)
class SharpLocalMinimaEvidence:
    """Evidence bundle for the inversion verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: SharpLocalMinimaClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_SHARP_LOCAL_MINIMA",
    "claim_model": "SharpLocalMinimaClaim",
    "evidence_model": "SharpLocalMinimaEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "paper_id": "2604.09412v1",
    "paper_title": "Sharp description of local minima in the loss landscape of high-dimensional two-layer ReLU neural networks",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

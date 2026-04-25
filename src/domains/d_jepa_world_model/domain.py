"""D_JEPA_WORLD_MODEL domain metadata and claim model.

Layer: 4 (Institutional - Machine Learning)
CardinalStrength: PREDICATIVE

Paper: LeWorldModel (LeWM), arXiv:2603.19312v2
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class JEPAWorldModelClaim:
    """Structured claim parameters for JEPA world model invariants.

    falsifies_if: any field violates its stated constraint.
    """
    prediction_loss_bounded: bool
    sigreg_converges: bool
    latent_isotropic: bool
    no_collapse: bool
    planning_converges: bool
    surprise_plausible: bool
    embedding_dim: int
    lambda_weight: Fraction


@dataclass(frozen=True)
class JEPAWorldModelEvidence:
    """Evidence bundle for JEPA world model verification.

    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: JEPAWorldModelClaim
    training_run_id: str
    planning_result_id: str
    surprise_event_count: int


DOMAIN_METADATA = {
    "id": "D_JEPA_WORLD_MODEL",
    "claim_model": "JEPAWorldModelClaim",
    "evidence_model": "JEPAWorldModelEvidence",
    "check_functions": [
        "check_prediction_loss_bounded",
        "check_sigreg_convergence",
        "check_latent_isotropy",
        "check_no_representation_collapse",
        "check_planning_convergence",
        "check_surprise_plausible",
    ],
    "paper_id": "2603.19312v2",
    "paper_title": "LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

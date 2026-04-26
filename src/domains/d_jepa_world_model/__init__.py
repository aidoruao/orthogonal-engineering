"""D_JEPA_WORLD_MODEL — Joint-Embedding Predictive Architecture World Models.

Based on LeWorldModel (LeWM), arXiv:2603.19312v2.
"""

from .implementation import (
    LatentState,
    LatentTrajectory,
    EncoderConfig,
    PredictorConfig,
    WorldModelConfig,
    EncoderOutput,
    PredictorOutput,
    SIGRegConfig,
    RandomProjection,
    ProjectedEmbedding,
    EppsPulleyResult,
    SIGRegResult,
    CEMConfig,
    ActionSequence,
    PlanningResult,
    SurpriseEvent,
    TrainingStep,
    TrainingRun,
    DOMAIN_METADATA,
)

from .invariants import (
    check_prediction_loss_bounded,
    check_sigreg_convergence,
    check_latent_isotropy,
    check_no_representation_collapse,
    check_planning_convergence,
    check_surprise_plausible,
    run_all_invariants,
)

from .domain import (
    JEPAWorldModelClaim,
    JEPAWorldModelEvidence,
    DOMAIN_METADATA as DOMAIN_METADATA_TYPED,
)

__all__ = [
    # Implementation
    "LatentState",
    "LatentTrajectory",
    "EncoderConfig",
    "PredictorConfig",
    "WorldModelConfig",
    "EncoderOutput",
    "PredictorOutput",
    "SIGRegConfig",
    "RandomProjection",
    "ProjectedEmbedding",
    "EppsPulleyResult",
    "SIGRegResult",
    "CEMConfig",
    "ActionSequence",
    "PlanningResult",
    "SurpriseEvent",
    "TrainingStep",
    "TrainingRun",
    "DOMAIN_METADATA",
    # Invariants
    "check_prediction_loss_bounded",
    "check_sigreg_convergence",
    "check_latent_isotropy",
    "check_no_representation_collapse",
    "check_planning_convergence",
    "check_surprise_plausible",
    "run_all_invariants",
    # Domain
    "JEPAWorldModelClaim",
    "JEPAWorldModelEvidence",
    "DOMAIN_METADATA_TYPED",
]

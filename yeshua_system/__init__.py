"""YESHUA_SYSTEM package — Projection onto Truth Constraint Manifold.

P(x) = argmin_{x' ∈ C} ||x - x'||

The projection engine derives constraints from eight_axioms.json,
classifies grounding models (G1-G5), computes debt delta, and
repairs violating text back into C.
"""
from yeshua_system.yeshua_projection import (
    YeshuaProjectionSystem,
    ProjectionResult,
    ConstraintViolation,
    SessionProjection,
    SessionTurn,
    GroundingModel,
    GROUNDING_MODELS,
    REQUIRED_GROUNDING,
    classify_grounding_model,
    compute_debt_delta,
    project,
    classify,
)

__all__ = [
    "YeshuaProjectionSystem",
    "ProjectionResult",
    "ConstraintViolation",
    "SessionProjection",
    "SessionTurn",
    "GroundingModel",
    "GROUNDING_MODELS",
    "REQUIRED_GROUNDING",
    "classify_grounding_model",
    "compute_debt_delta",
    "project",
    "classify",
]

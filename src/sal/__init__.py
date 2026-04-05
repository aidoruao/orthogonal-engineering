"""Synthetic Adjoint Logic (SAL) Type III kernel package."""

from src.sal.adjoint_triple import (
    AdjointTriple,
    AdjunctionProof,
    Functor,
    LeftAdjoint,
    MiddleFunctor,
    RightAdjoint,
    has_adjunction,
)
from src.sal.sigma_theo_factoring import (
    SIGMA_FACTORING_MAP,
    SigmaFactoringResult,
    factor_sigma_through_triple,
    verify_factoring_coherence,
)
from src.sal.cross_repo_adjunction import verify_cross_repo_adjunction
from src.sal.yeshua_as_triangle_identities import (
    AXIOM_TO_SAL_TARGET,
    YeshuaTriangleMapping,
    map_axiom_to_triangle_identity,
    verify_all_axioms_map,
)

__all__ = [
    "Functor",
    "LeftAdjoint",
    "MiddleFunctor",
    "RightAdjoint",
    "AdjointTriple",
    "AdjunctionProof",
    "has_adjunction",
    "SIGMA_FACTORING_MAP",
    "SigmaFactoringResult",
    "factor_sigma_through_triple",
    "verify_factoring_coherence",
    "verify_cross_repo_adjunction",
    "AXIOM_TO_SAL_TARGET",
    "YeshuaTriangleMapping",
    "map_axiom_to_triangle_identity",
    "verify_all_axioms_map",
]

"""Synthetic Adjoint Logic (SAL) kernel package — Types III through VI."""

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
from src.sal.topos_subobject_classifier import (
    SheafContext,
    SubobjectClassifier,
    GeometricMorphism,
    ToposAdjunctionProof,
    geometric_morphism,
    evaluate_in_context,
)
from src.sal.higher_adjunction import (
    IdentityPath,
    Transport,
    HigherInductiveDomain,
    TwoCell,
    HigherAdjunction,
    HigherAdjunctionProof,
    higher_has_adjunction,
)
from src.sal.forcing_operation import (
    CardinalStrength,
    DomainState,
    ForcingCondition,
    GenericExtension,
    ForcingOperation,
    force_domain,
)
from src.sal.realizability_topos import (
    ProofTheoreticOrdinal,
    Realizer,
    PartialEquivalenceRelation,
    RealizabilityObject,
    TerminalCoalgebra,
    RealizabilityTopos,
    ORDINAL_EPSILON_0,
    ORDINAL_GAMMA_0,
    ORDINAL_PSI_OMEGA_CK,
    ORDINAL_CHURCH_KLEENE,
    realize,
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
    # Type 3+: Topos
    "SheafContext",
    "SubobjectClassifier",
    "GeometricMorphism",
    "ToposAdjunctionProof",
    "geometric_morphism",
    "evaluate_in_context",
    # Type 4: Higher adjunction / HoTT
    "IdentityPath",
    "Transport",
    "HigherInductiveDomain",
    "TwoCell",
    "HigherAdjunction",
    "HigherAdjunctionProof",
    "higher_has_adjunction",
    # Type 5: Forcing
    "CardinalStrength",
    "DomainState",
    "ForcingCondition",
    "GenericExtension",
    "ForcingOperation",
    "force_domain",
    # Type 6: Realizability
    "ProofTheoreticOrdinal",
    "Realizer",
    "PartialEquivalenceRelation",
    "RealizabilityObject",
    "TerminalCoalgebra",
    "RealizabilityTopos",
    "ORDINAL_EPSILON_0",
    "ORDINAL_GAMMA_0",
    "ORDINAL_PSI_OMEGA_CK",
    "ORDINAL_CHURCH_KLEENE",
    "realize",
]

"""SOVEREIGN TOPOS: 5-Layer Country Model

A self-verifying mathematical structure modeling a complete nation-state —
every layer, every domain, every law, every institution — under the Yeshua
constraint manifold.

Layer Architecture:
  Layer 0: Supranational       — UN, treaties, international law (MAHLO)
  Layer 1: Constitutional      — Bill of Rights, separation of powers (INACCESSIBLE)
  Layer 2: Statutory           — US Code titles (PREDICATIVE)
  Layer 3: Regulatory          — Building codes, zoning, school funding (PEANO)
  Layer 4: Institutional       — Psychology, sociology, ethics (PEANO)

Each layer is a topos with its own situs, invariants, and geometric morphisms
to every other layer. Truth must be preserved across all morphisms — that's
the definition of a valid country.
"""

from src.layers.layer_model import (
    LayerTopos, CardinalStrength, ALL_LAYERS, get_layer_by_id, get_layer_by_name,
    SUPRANATIONAL_LAYER, CONSTITUTIONAL_LAYER, STATUTORY_LAYER,
    REGULATORY_LAYER, INSTITUTIONAL_LAYER,
)
from src.layers.inter_layer_morphism import (
    check_layer_consistency,
    GeometricMorphism,
    LayerContradiction,
    CountryVerifier,
)

__all__ = [
    "LayerTopos",
    "CardinalStrength",
    "ALL_LAYERS",
    "get_layer_by_id",
    "get_layer_by_name",
    "SUPRANATIONAL_LAYER",
    "CONSTITUTIONAL_LAYER",
    "STATUTORY_LAYER",
    "REGULATORY_LAYER",
    "INSTITUTIONAL_LAYER",
    "check_layer_consistency",
    "GeometricMorphism",
    "LayerContradiction",
    "CountryVerifier",
]

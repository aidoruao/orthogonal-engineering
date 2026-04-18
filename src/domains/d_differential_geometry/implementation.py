"""Implementation models for Differential Geometry."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DifferentialGeometryClaim:
    """Structured claim parameters for Differential Geometry domain invariants."""

    metric_positive_definite: bool
    christoffel_symmetric: bool
    geodesic_equation_satisfied: bool
    curvature_antisymmetric: bool
    sectional_curvature: Fraction


def create_nominal_claim() -> DifferentialGeometryClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return DifferentialGeometryClaim(
        metric_positive_definite=True,
        christoffel_symmetric=True,
        geodesic_equation_satisfied=True,
        curvature_antisymmetric=True,
        sectional_curvature=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "DIFFERENTIAL_GEOMETRY",
    "claim_model": "DifferentialGeometryClaim",
    "check_functions": [
        "check_metric_positive_definite",
        "check_christoffel_symmetric",
        "check_geodesic_equation_satisfied",
        "check_curvature_tensor_antisymmetric",
        "check_sectional_curvature_fraction",
    ],
}

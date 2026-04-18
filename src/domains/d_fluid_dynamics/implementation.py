"""Implementation models for Fluid Dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class FluidDynamicsClaim:
    """Structured claim parameters for Fluid Dynamics domain invariants."""

    navier_stokes_conserved: bool
    reynolds_number_positive: bool
    divergence_free: bool
    boundary_layer_valid: bool
    mach_number: Fraction


def create_nominal_claim() -> FluidDynamicsClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return FluidDynamicsClaim(
        navier_stokes_conserved=True,
        reynolds_number_positive=True,
        divergence_free=True,
        boundary_layer_valid=True,
        mach_number=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "FLUID_DYNAMICS",
    "claim_model": "FluidDynamicsClaim",
    "check_functions": [
        "check_navier_stokes_conservation",
        "check_reynolds_number_positive",
        "check_incompressibility_divergence_free",
        "check_boundary_layer_separation",
        "check_mach_number_fraction",
    ],
}

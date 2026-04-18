"""Implementation models for Structural Engineering."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class StructuralClaim:
    """Structured claim parameters for Structural Engineering domain invariants."""

    stress_within_yield: bool
    buckling_load_positive: bool
    deflection_within_limits: bool
    load_path_continuous: bool
    safety_factor: Fraction


def create_nominal_claim() -> StructuralClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return StructuralClaim(
        stress_within_yield=True,
        buckling_load_positive=True,
        deflection_within_limits=True,
        load_path_continuous=True,
        safety_factor=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "STRUCTURAL_ENGINEERING",
    "claim_model": "StructuralClaim",
    "check_functions": [
        "check_stress_within_yield",
        "check_buckling_load_positive",
        "check_deflection_within_limits",
        "check_load_path_continuity",
        "check_safety_factor_fraction",
    ],
}

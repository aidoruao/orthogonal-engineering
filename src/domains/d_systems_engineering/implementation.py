"""Implementation models for Systems Engineering."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class SystemsEngineeringClaim:
    """Structured claim parameters for Systems Engineering domain invariants."""

    requirements_traceable: bool
    interfaces_compatible: bool
    risk_mitigation_covered: bool
    v_and_v_closed: bool
    mop_moe_alignment: Fraction


def create_nominal_claim() -> SystemsEngineeringClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return SystemsEngineeringClaim(
        requirements_traceable=True,
        interfaces_compatible=True,
        risk_mitigation_covered=True,
        v_and_v_closed=True,
        mop_moe_alignment=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "SYSTEMS_ENGINEERING",
    "claim_model": "SystemsEngineeringClaim",
    "check_functions": [
        "check_requirements_traceability",
        "check_interface_compatibility",
        "check_risk_mitigation_coverage",
        "check_verification_validation_closures",
        "check_mop_moe_alignment_fraction",
    ],
}

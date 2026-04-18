"""Invariant checks for Systems Engineering."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import SystemsEngineeringClaim, create_nominal_claim


def check_requirements_traceability(data: SystemsEngineeringClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Requirements are traceable.

    Standard: Systems Engineering domain invariant.
    Falsifies if: not requirements_traceable.
    falsifies_if: not requirements_traceable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.requirements_traceable
    proof = ProofObject(
        rule="check_requirements_traceability",
        premises=[
            "domain=Systems Engineering",
            f"requirements_traceable={{data.requirements_traceable}}",
        ],
        conclusion=(
            "PASS: Requirements are traceable"
            if success else "FAIL: Requirements are traceable"
        ),
    )
    return success, proof


def check_interface_compatibility(data: SystemsEngineeringClaim) -> Tuple[bool, ProofObject]:
    """Invariant: System interfaces are compatible.

    Standard: Systems Engineering domain invariant.
    Falsifies if: not interfaces_compatible.
    falsifies_if: not interfaces_compatible.

    Returns:
        Tuple of (success, proof).
    """
    success = data.interfaces_compatible
    proof = ProofObject(
        rule="check_interface_compatibility",
        premises=[
            "domain=Systems Engineering",
            f"interfaces_compatible={{data.interfaces_compatible}}",
        ],
        conclusion=(
            "PASS: System interfaces are compatible"
            if success else "FAIL: System interfaces are compatible"
        ),
    )
    return success, proof


def check_risk_mitigation_coverage(data: SystemsEngineeringClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Risk mitigation coverage is sufficient.

    Standard: Systems Engineering domain invariant.
    Falsifies if: not risk_mitigation_covered.
    falsifies_if: not risk_mitigation_covered.

    Returns:
        Tuple of (success, proof).
    """
    success = data.risk_mitigation_covered
    proof = ProofObject(
        rule="check_risk_mitigation_coverage",
        premises=[
            "domain=Systems Engineering",
            f"risk_mitigation_covered={{data.risk_mitigation_covered}}",
        ],
        conclusion=(
            "PASS: Risk mitigation coverage is sufficient"
            if success else "FAIL: Risk mitigation coverage is sufficient"
        ),
    )
    return success, proof


def check_verification_validation_closures(data: SystemsEngineeringClaim) -> Tuple[bool, ProofObject]:
    """Invariant: V&V closures are complete.

    Standard: Systems Engineering domain invariant.
    Falsifies if: not v_and_v_closed.
    falsifies_if: not v_and_v_closed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.v_and_v_closed
    proof = ProofObject(
        rule="check_verification_validation_closures",
        premises=[
            "domain=Systems Engineering",
            f"v_and_v_closed={{data.v_and_v_closed}}",
        ],
        conclusion=(
            "PASS: V&V closures are complete"
            if success else "FAIL: V&V closures are complete"
        ),
    )
    return success, proof


def check_mop_moe_alignment_fraction(data: SystemsEngineeringClaim) -> Tuple[bool, ProofObject]:
    """Invariant: MOP-MOE alignment score is non-negative.

    Standard: Systems Engineering domain invariant.
    Falsifies if: not mop_moe_alignment.
    falsifies_if: not mop_moe_alignment.

    Returns:
        Tuple of (success, proof).
    """
    success = data.mop_moe_alignment >= Fraction(0)
    proof = ProofObject(
        rule="check_mop_moe_alignment_fraction",
        premises=[
            "domain=Systems Engineering",
            f"mop_moe_alignment={{data.mop_moe_alignment}}",
        ],
        conclusion=(
            "PASS: MOP-MOE alignment score is non-negative is non-negative"
            if success else "FAIL: MOP-MOE alignment score is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Systems Engineering nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_requirements_traceability", check_requirements_traceability),
        ("check_interface_compatibility", check_interface_compatibility),
        ("check_risk_mitigation_coverage", check_risk_mitigation_coverage),
        ("check_verification_validation_closures", check_verification_validation_closures),
        ("check_mop_moe_alignment_fraction", check_mop_moe_alignment_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

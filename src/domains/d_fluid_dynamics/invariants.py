"""Invariant checks for Fluid Dynamics."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import FluidDynamicsClaim, create_nominal_claim


def check_navier_stokes_conservation(data: FluidDynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Navier-Stokes conservation holds.

    Standard: Fluid Dynamics domain invariant.
    Falsifies if: not navier_stokes_conserved.
    falsifies_if: not navier_stokes_conserved.

    Returns:
        Tuple of (success, proof).
    """
    success = data.navier_stokes_conserved
    proof = ProofObject(
        rule="check_navier_stokes_conservation",
        premises=[
            "domain=Fluid Dynamics",
            f"navier_stokes_conserved={{data.navier_stokes_conserved}}",
        ],
        conclusion=(
            "PASS: Navier-Stokes conservation holds"
            if success else "FAIL: Navier-Stokes conservation holds"
        ),
    )
    return success, proof


def check_reynolds_number_positive(data: FluidDynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Reynolds number is positive.

    Standard: Fluid Dynamics domain invariant.
    Falsifies if: not reynolds_number_positive.
    falsifies_if: not reynolds_number_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.reynolds_number_positive
    proof = ProofObject(
        rule="check_reynolds_number_positive",
        premises=[
            "domain=Fluid Dynamics",
            f"reynolds_number_positive={{data.reynolds_number_positive}}",
        ],
        conclusion=(
            "PASS: Reynolds number is positive"
            if success else "FAIL: Reynolds number is positive"
        ),
    )
    return success, proof


def check_incompressibility_divergence_free(data: FluidDynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Flow is divergence-free for incompressible case.

    Standard: Fluid Dynamics domain invariant.
    Falsifies if: not divergence_free.
    falsifies_if: not divergence_free.

    Returns:
        Tuple of (success, proof).
    """
    success = data.divergence_free
    proof = ProofObject(
        rule="check_incompressibility_divergence_free",
        premises=[
            "domain=Fluid Dynamics",
            f"divergence_free={{data.divergence_free}}",
        ],
        conclusion=(
            "PASS: Flow is divergence-free for incompressible case"
            if success else "FAIL: Flow is divergence-free for incompressible case"
        ),
    )
    return success, proof


def check_boundary_layer_separation(data: FluidDynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Boundary layer separation is physically valid.

    Standard: Fluid Dynamics domain invariant.
    Falsifies if: not boundary_layer_valid.
    falsifies_if: not boundary_layer_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.boundary_layer_valid
    proof = ProofObject(
        rule="check_boundary_layer_separation",
        premises=[
            "domain=Fluid Dynamics",
            f"boundary_layer_valid={{data.boundary_layer_valid}}",
        ],
        conclusion=(
            "PASS: Boundary layer separation is physically valid"
            if success else "FAIL: Boundary layer separation is physically valid"
        ),
    )
    return success, proof


def check_mach_number_fraction(data: FluidDynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Mach number is non-negative.

    Standard: Fluid Dynamics domain invariant.
    Falsifies if: not mach_number.
    falsifies_if: not mach_number.

    Returns:
        Tuple of (success, proof).
    """
    success = data.mach_number >= Fraction(0)
    proof = ProofObject(
        rule="check_mach_number_fraction",
        premises=[
            "domain=Fluid Dynamics",
            f"mach_number={{data.mach_number}}",
        ],
        conclusion=(
            "PASS: Mach number is non-negative is non-negative"
            if success else "FAIL: Mach number is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Fluid Dynamics nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_navier_stokes_conservation", check_navier_stokes_conservation),
        ("check_reynolds_number_positive", check_reynolds_number_positive),
        ("check_incompressibility_divergence_free", check_incompressibility_divergence_free),
        ("check_boundary_layer_separation", check_boundary_layer_separation),
        ("check_mach_number_fraction", check_mach_number_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

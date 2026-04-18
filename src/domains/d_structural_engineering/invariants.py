"""Invariant checks for Structural Engineering."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import StructuralClaim, create_nominal_claim


def check_stress_within_yield(data: StructuralClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Stress is within yield limit.

    Standard: Structural Engineering domain invariant.
    Falsifies if: not stress_within_yield.
    falsifies_if: not stress_within_yield.

    Returns:
        Tuple of (success, proof).
    """
    success = data.stress_within_yield
    proof = ProofObject(
        rule="check_stress_within_yield",
        premises=[
            "domain=Structural Engineering",
            f"stress_within_yield={{data.stress_within_yield}}",
        ],
        conclusion=(
            "PASS: Stress is within yield limit"
            if success else "FAIL: Stress is within yield limit"
        ),
    )
    return success, proof


def check_buckling_load_positive(data: StructuralClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Buckling load is positive.

    Standard: Structural Engineering domain invariant.
    Falsifies if: not buckling_load_positive.
    falsifies_if: not buckling_load_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.buckling_load_positive
    proof = ProofObject(
        rule="check_buckling_load_positive",
        premises=[
            "domain=Structural Engineering",
            f"buckling_load_positive={{data.buckling_load_positive}}",
        ],
        conclusion=(
            "PASS: Buckling load is positive"
            if success else "FAIL: Buckling load is positive"
        ),
    )
    return success, proof


def check_deflection_within_limits(data: StructuralClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Deflection is within limits.

    Standard: Structural Engineering domain invariant.
    Falsifies if: not deflection_within_limits.
    falsifies_if: not deflection_within_limits.

    Returns:
        Tuple of (success, proof).
    """
    success = data.deflection_within_limits
    proof = ProofObject(
        rule="check_deflection_within_limits",
        premises=[
            "domain=Structural Engineering",
            f"deflection_within_limits={{data.deflection_within_limits}}",
        ],
        conclusion=(
            "PASS: Deflection is within limits"
            if success else "FAIL: Deflection is within limits"
        ),
    )
    return success, proof


def check_load_path_continuity(data: StructuralClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Load path is continuous.

    Standard: Structural Engineering domain invariant.
    Falsifies if: not load_path_continuous.
    falsifies_if: not load_path_continuous.

    Returns:
        Tuple of (success, proof).
    """
    success = data.load_path_continuous
    proof = ProofObject(
        rule="check_load_path_continuity",
        premises=[
            "domain=Structural Engineering",
            f"load_path_continuous={{data.load_path_continuous}}",
        ],
        conclusion=(
            "PASS: Load path is continuous"
            if success else "FAIL: Load path is continuous"
        ),
    )
    return success, proof


def check_safety_factor_fraction(data: StructuralClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Safety factor is positive.

    Standard: Structural Engineering domain invariant.
    Falsifies if: not safety_factor.
    falsifies_if: not safety_factor.

    Returns:
        Tuple of (success, proof).
    """
    success = data.safety_factor >= Fraction(0)
    proof = ProofObject(
        rule="check_safety_factor_fraction",
        premises=[
            "domain=Structural Engineering",
            f"safety_factor={{data.safety_factor}}",
        ],
        conclusion=(
            "PASS: Safety factor is positive is non-negative"
            if success else "FAIL: Safety factor is positive is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Structural Engineering nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_stress_within_yield", check_stress_within_yield),
        ("check_buckling_load_positive", check_buckling_load_positive),
        ("check_deflection_within_limits", check_deflection_within_limits),
        ("check_load_path_continuity", check_load_path_continuity),
        ("check_safety_factor_fraction", check_safety_factor_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

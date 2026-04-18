"""Invariant checks for Welding."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import WeldingClaim, create_nominal_claim


def check_weld_penetration_adequate(data: WeldingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Weld penetration is adequate.

    Standard: Welding domain invariant.
    Falsifies if: not weld_penetration_adequate.
    falsifies_if: not weld_penetration_adequate.

    Returns:
        Tuple of (success, proof).
    """
    success = data.weld_penetration_adequate
    proof = ProofObject(
        rule="check_weld_penetration_adequate",
        premises=[
            "domain=Welding",
            f"weld_penetration_adequate={{data.weld_penetration_adequate}}",
        ],
        conclusion=(
            "PASS: Weld penetration is adequate"
            if success else "FAIL: Weld penetration is adequate"
        ),
    )
    return success, proof


def check_heat_affected_zone_bounded(data: WeldingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Heat affected zone is bounded.

    Standard: Welding domain invariant.
    Falsifies if: not haz_bounded.
    falsifies_if: not haz_bounded.

    Returns:
        Tuple of (success, proof).
    """
    success = data.haz_bounded
    proof = ProofObject(
        rule="check_heat_affected_zone_bounded",
        premises=[
            "domain=Welding",
            f"haz_bounded={{data.haz_bounded}}",
        ],
        conclusion=(
            "PASS: Heat affected zone is bounded"
            if success else "FAIL: Heat affected zone is bounded"
        ),
    )
    return success, proof


def check_filler_material_compatible(data: WeldingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Filler material is compatible with base metal.

    Standard: Welding domain invariant.
    Falsifies if: not filler_compatible.
    falsifies_if: not filler_compatible.

    Returns:
        Tuple of (success, proof).
    """
    success = data.filler_compatible
    proof = ProofObject(
        rule="check_filler_material_compatible",
        premises=[
            "domain=Welding",
            f"filler_compatible={{data.filler_compatible}}",
        ],
        conclusion=(
            "PASS: Filler material is compatible with base metal"
            if success else "FAIL: Filler material is compatible with base metal"
        ),
    )
    return success, proof


def check_wps_followed(data: WeldingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Welding procedure specification is followed.

    Standard: Welding domain invariant.
    Falsifies if: not wps_followed.
    falsifies_if: not wps_followed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.wps_followed
    proof = ProofObject(
        rule="check_wps_followed",
        premises=[
            "domain=Welding",
            f"wps_followed={{data.wps_followed}}",
        ],
        conclusion=(
            "PASS: Welding procedure specification is followed"
            if success else "FAIL: Welding procedure specification is followed"
        ),
    )
    return success, proof


def check_weld_strength_fraction(data: WeldingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Weld strength is non-negative.

    Standard: Welding domain invariant.
    Falsifies if: not weld_strength_ksi.
    falsifies_if: not weld_strength_ksi.

    Returns:
        Tuple of (success, proof).
    """
    success = data.weld_strength_ksi >= Fraction(0)
    proof = ProofObject(
        rule="check_weld_strength_fraction",
        premises=[
            "domain=Welding",
            f"weld_strength_ksi={{data.weld_strength_ksi}}",
        ],
        conclusion=(
            "PASS: Weld strength is non-negative is non-negative"
            if success else "FAIL: Weld strength is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Welding nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_weld_penetration_adequate", check_weld_penetration_adequate),
        ("check_heat_affected_zone_bounded", check_heat_affected_zone_bounded),
        ("check_filler_material_compatible", check_filler_material_compatible),
        ("check_wps_followed", check_wps_followed),
        ("check_weld_strength_fraction", check_weld_strength_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

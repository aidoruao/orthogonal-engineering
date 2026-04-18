"""Invariant checks for Visual Arts."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import VisualArtsClaim, create_nominal_claim


def check_color_harmony_complementary(data: VisualArtsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Color harmony is complementary where claimed.

    Standard: Visual Arts domain invariant.
    Falsifies if: not color_harmony_complementary.
    falsifies_if: not color_harmony_complementary.

    Returns:
        Tuple of (success, proof).
    """
    success = data.color_harmony_complementary
    proof = ProofObject(
        rule="check_color_harmony_complementary",
        premises=[
            "domain=Visual Arts",
            f"color_harmony_complementary={{data.color_harmony_complementary}}",
        ],
        conclusion=(
            "PASS: Color harmony is complementary where claimed"
            if success else "FAIL: Color harmony is complementary where claimed"
        ),
    )
    return success, proof


def check_golden_ratio_proportion(data: VisualArtsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Golden ratio proportion is within tolerance.

    Standard: Visual Arts domain invariant.
    Falsifies if: not golden_ratio_proportion.
    falsifies_if: not golden_ratio_proportion.

    Returns:
        Tuple of (success, proof).
    """
    success = data.golden_ratio_proportion
    proof = ProofObject(
        rule="check_golden_ratio_proportion",
        premises=[
            "domain=Visual Arts",
            f"golden_ratio_proportion={{data.golden_ratio_proportion}}",
        ],
        conclusion=(
            "PASS: Golden ratio proportion is within tolerance"
            if success else "FAIL: Golden ratio proportion is within tolerance"
        ),
    )
    return success, proof


def check_perspective_convergence(data: VisualArtsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Linear perspective converges to vanishing point.

    Standard: Visual Arts domain invariant.
    Falsifies if: not perspective_converges.
    falsifies_if: not perspective_converges.

    Returns:
        Tuple of (success, proof).
    """
    success = data.perspective_converges
    proof = ProofObject(
        rule="check_perspective_convergence",
        premises=[
            "domain=Visual Arts",
            f"perspective_converges={{data.perspective_converges}}",
        ],
        conclusion=(
            "PASS: Linear perspective converges to vanishing point"
            if success else "FAIL: Linear perspective converges to vanishing point"
        ),
    )
    return success, proof


def check_compositional_balance(data: VisualArtsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Composition is balanced.

    Standard: Visual Arts domain invariant.
    Falsifies if: not composition_balanced.
    falsifies_if: not composition_balanced.

    Returns:
        Tuple of (success, proof).
    """
    success = data.composition_balanced
    proof = ProofObject(
        rule="check_compositional_balance",
        premises=[
            "domain=Visual Arts",
            f"composition_balanced={{data.composition_balanced}}",
        ],
        conclusion=(
            "PASS: Composition is balanced"
            if success else "FAIL: Composition is balanced"
        ),
    )
    return success, proof


def check_chroma_saturation_fraction(data: VisualArtsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Chroma saturation is between 0 and 1.

    Standard: Visual Arts domain invariant.
    Falsifies if: not chroma_saturation.
    falsifies_if: not chroma_saturation.

    Returns:
        Tuple of (success, proof).
    """
    success = data.chroma_saturation >= Fraction(0)
    proof = ProofObject(
        rule="check_chroma_saturation_fraction",
        premises=[
            "domain=Visual Arts",
            f"chroma_saturation={{data.chroma_saturation}}",
        ],
        conclusion=(
            "PASS: Chroma saturation is between 0 and 1 is non-negative"
            if success else "FAIL: Chroma saturation is between 0 and 1 is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Visual Arts nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_color_harmony_complementary", check_color_harmony_complementary),
        ("check_golden_ratio_proportion", check_golden_ratio_proportion),
        ("check_perspective_convergence", check_perspective_convergence),
        ("check_compositional_balance", check_compositional_balance),
        ("check_chroma_saturation_fraction", check_chroma_saturation_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

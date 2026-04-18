"""Invariant checks for Category Theory."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import CategoryTheoryClaim, create_nominal_claim


def check_composition_associative(data: CategoryTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Morphism composition is associative.

    Standard: Category Theory domain invariant.
    Falsifies if: not composition_associative.
    falsifies_if: not composition_associative.

    Returns:
        Tuple of (success, proof).
    """
    success = data.composition_associative
    proof = ProofObject(
        rule="check_composition_associative",
        premises=[
            "domain=Category Theory",
            f"composition_associative={{data.composition_associative}}",
        ],
        conclusion=(
            "PASS: Morphism composition is associative"
            if success else "FAIL: Morphism composition is associative"
        ),
    )
    return success, proof


def check_identity_morphism_exists(data: CategoryTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Identity morphism exists for every object.

    Standard: Category Theory domain invariant.
    Falsifies if: not identity_exists.
    falsifies_if: not identity_exists.

    Returns:
        Tuple of (success, proof).
    """
    success = data.identity_exists
    proof = ProofObject(
        rule="check_identity_morphism_exists",
        premises=[
            "domain=Category Theory",
            f"identity_exists={{data.identity_exists}}",
        ],
        conclusion=(
            "PASS: Identity morphism exists for every object"
            if success else "FAIL: Identity morphism exists for every object"
        ),
    )
    return success, proof


def check_functor_preserves_identity(data: CategoryTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Functor preserves identity morphisms.

    Standard: Category Theory domain invariant.
    Falsifies if: not functor_preserves_identity.
    falsifies_if: not functor_preserves_identity.

    Returns:
        Tuple of (success, proof).
    """
    success = data.functor_preserves_identity
    proof = ProofObject(
        rule="check_functor_preserves_identity",
        premises=[
            "domain=Category Theory",
            f"functor_preserves_identity={{data.functor_preserves_identity}}",
        ],
        conclusion=(
            "PASS: Functor preserves identity morphisms"
            if success else "FAIL: Functor preserves identity morphisms"
        ),
    )
    return success, proof


def check_natural_transformation_commutes(data: CategoryTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Naturality square commutes.

    Standard: Category Theory domain invariant.
    Falsifies if: not naturality_square_commutes.
    falsifies_if: not naturality_square_commutes.

    Returns:
        Tuple of (success, proof).
    """
    success = data.naturality_square_commutes
    proof = ProofObject(
        rule="check_natural_transformation_commutes",
        premises=[
            "domain=Category Theory",
            f"naturality_square_commutes={{data.naturality_square_commutes}}",
        ],
        conclusion=(
            "PASS: Naturality square commutes"
            if success else "FAIL: Naturality square commutes"
        ),
    )
    return success, proof


def check_hom_set_size_fraction(data: CategoryTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Hom-set size is non-negative.

    Standard: Category Theory domain invariant.
    Falsifies if: not hom_set_size.
    falsifies_if: not hom_set_size.

    Returns:
        Tuple of (success, proof).
    """
    success = data.hom_set_size >= Fraction(0)
    proof = ProofObject(
        rule="check_hom_set_size_fraction",
        premises=[
            "domain=Category Theory",
            f"hom_set_size={{data.hom_set_size}}",
        ],
        conclusion=(
            "PASS: Hom-set size is non-negative is non-negative"
            if success else "FAIL: Hom-set size is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Category Theory nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_composition_associative", check_composition_associative),
        ("check_identity_morphism_exists", check_identity_morphism_exists),
        ("check_functor_preserves_identity", check_functor_preserves_identity),
        ("check_natural_transformation_commutes", check_natural_transformation_commutes),
        ("check_hom_set_size_fraction", check_hom_set_size_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

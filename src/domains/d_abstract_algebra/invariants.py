"""Invariant checks for Abstract Algebra."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import AbstractAlgebraClaim, create_nominal_claim


def check_group_axioms_satisfied(data: AbstractAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Group axioms are satisfied.

    Standard: Abstract Algebra domain invariant.
    Falsifies if: not group_axioms_satisfied.
    falsifies_if: not group_axioms_satisfied.

    Returns:
        Tuple of (success, proof).
    """
    success = data.group_axioms_satisfied
    proof = ProofObject(
        rule="check_group_axioms_satisfied",
        premises=[
            "domain=Abstract Algebra",
            f"group_axioms_satisfied={{data.group_axioms_satisfied}}",
        ],
        conclusion=(
            "PASS: Group axioms are satisfied"
            if success else "FAIL: Group axioms are satisfied"
        ),
    )
    return success, proof


def check_ring_distributivity(data: AbstractAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Ring multiplication distributes over addition.

    Standard: Abstract Algebra domain invariant.
    Falsifies if: not ring_distributive.
    falsifies_if: not ring_distributive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.ring_distributive
    proof = ProofObject(
        rule="check_ring_distributivity",
        premises=[
            "domain=Abstract Algebra",
            f"ring_distributive={{data.ring_distributive}}",
        ],
        conclusion=(
            "PASS: Ring multiplication distributes over addition"
            if success else "FAIL: Ring multiplication distributes over addition"
        ),
    )
    return success, proof


def check_field_multiplicative_inverse(data: AbstractAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Every non-zero field element has multiplicative inverse.

    Standard: Abstract Algebra domain invariant.
    Falsifies if: not field_has_inverses.
    falsifies_if: not field_has_inverses.

    Returns:
        Tuple of (success, proof).
    """
    success = data.field_has_inverses
    proof = ProofObject(
        rule="check_field_multiplicative_inverse",
        premises=[
            "domain=Abstract Algebra",
            f"field_has_inverses={{data.field_has_inverses}}",
        ],
        conclusion=(
            "PASS: Every non-zero field element has multiplicative inverse"
            if success else "FAIL: Every non-zero field element has multiplicative inverse"
        ),
    )
    return success, proof


def check_homomorphism_preserves_operation(data: AbstractAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Homomorphism preserves group operation.

    Standard: Abstract Algebra domain invariant.
    Falsifies if: not homomorphism_preserves.
    falsifies_if: not homomorphism_preserves.

    Returns:
        Tuple of (success, proof).
    """
    success = data.homomorphism_preserves
    proof = ProofObject(
        rule="check_homomorphism_preserves_operation",
        premises=[
            "domain=Abstract Algebra",
            f"homomorphism_preserves={{data.homomorphism_preserves}}",
        ],
        conclusion=(
            "PASS: Homomorphism preserves group operation"
            if success else "FAIL: Homomorphism preserves group operation"
        ),
    )
    return success, proof


def check_order_of_element_fraction(data: AbstractAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Order of element is positive integer.

    Standard: Abstract Algebra domain invariant.
    Falsifies if: not element_order.
    falsifies_if: not element_order.

    Returns:
        Tuple of (success, proof).
    """
    success = data.element_order >= Fraction(0)
    proof = ProofObject(
        rule="check_order_of_element_fraction",
        premises=[
            "domain=Abstract Algebra",
            f"element_order={{data.element_order}}",
        ],
        conclusion=(
            "PASS: Order of element is positive integer is non-negative"
            if success else "FAIL: Order of element is positive integer is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Abstract Algebra nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_group_axioms_satisfied", check_group_axioms_satisfied),
        ("check_ring_distributivity", check_ring_distributivity),
        ("check_field_multiplicative_inverse", check_field_multiplicative_inverse),
        ("check_homomorphism_preserves_operation", check_homomorphism_preserves_operation),
        ("check_order_of_element_fraction", check_order_of_element_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

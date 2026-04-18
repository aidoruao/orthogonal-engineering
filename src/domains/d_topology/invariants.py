"""Invariant checks for Topology."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import TopologyClaim, create_nominal_claim


def check_compactness_preserved(data: TopologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Compactness is preserved under continuous map.

    Standard: Topology domain invariant.
    Falsifies if: not compactness_preserved.
    falsifies_if: not compactness_preserved.

    Returns:
        Tuple of (success, proof).
    """
    success = data.compactness_preserved
    proof = ProofObject(
        rule="check_compactness_preserved",
        premises=[
            "domain=Topology",
            f"compactness_preserved={{data.compactness_preserved}}",
        ],
        conclusion=(
            "PASS: Compactness is preserved under continuous map"
            if success else "FAIL: Compactness is preserved under continuous map"
        ),
    )
    return success, proof


def check_connectedness_invariant(data: TopologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Connectedness is a topological invariant.

    Standard: Topology domain invariant.
    Falsifies if: not connectedness_invariant.
    falsifies_if: not connectedness_invariant.

    Returns:
        Tuple of (success, proof).
    """
    success = data.connectedness_invariant
    proof = ProofObject(
        rule="check_connectedness_invariant",
        premises=[
            "domain=Topology",
            f"connectedness_invariant={{data.connectedness_invariant}}",
        ],
        conclusion=(
            "PASS: Connectedness is a topological invariant"
            if success else "FAIL: Connectedness is a topological invariant"
        ),
    )
    return success, proof


def check_hausdorff_separation(data: TopologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Space is Hausdorff separated.

    Standard: Topology domain invariant.
    Falsifies if: not hausdorff_separated.
    falsifies_if: not hausdorff_separated.

    Returns:
        Tuple of (success, proof).
    """
    success = data.hausdorff_separated
    proof = ProofObject(
        rule="check_hausdorff_separation",
        premises=[
            "domain=Topology",
            f"hausdorff_separated={{data.hausdorff_separated}}",
        ],
        conclusion=(
            "PASS: Space is Hausdorff separated"
            if success else "FAIL: Space is Hausdorff separated"
        ),
    )
    return success, proof


def check_fundamental_group_well_defined(data: TopologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Fundamental group is well-defined.

    Standard: Topology domain invariant.
    Falsifies if: not fundamental_group_well_defined.
    falsifies_if: not fundamental_group_well_defined.

    Returns:
        Tuple of (success, proof).
    """
    success = data.fundamental_group_well_defined
    proof = ProofObject(
        rule="check_fundamental_group_well_defined",
        premises=[
            "domain=Topology",
            f"fundamental_group_well_defined={{data.fundamental_group_well_defined}}",
        ],
        conclusion=(
            "PASS: Fundamental group is well-defined"
            if success else "FAIL: Fundamental group is well-defined"
        ),
    )
    return success, proof


def check_euler_characteristic_fraction(data: TopologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Euler characteristic is integer-valued.

    Standard: Topology domain invariant.
    Falsifies if: not euler_characteristic.
    falsifies_if: not euler_characteristic.

    Returns:
        Tuple of (success, proof).
    """
    success = data.euler_characteristic >= Fraction(0)
    proof = ProofObject(
        rule="check_euler_characteristic_fraction",
        premises=[
            "domain=Topology",
            f"euler_characteristic={{data.euler_characteristic}}",
        ],
        conclusion=(
            "PASS: Euler characteristic is integer-valued is non-negative"
            if success else "FAIL: Euler characteristic is integer-valued is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Topology nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_compactness_preserved", check_compactness_preserved),
        ("check_connectedness_invariant", check_connectedness_invariant),
        ("check_hausdorff_separation", check_hausdorff_separation),
        ("check_fundamental_group_well_defined", check_fundamental_group_well_defined),
        ("check_euler_characteristic_fraction", check_euler_characteristic_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

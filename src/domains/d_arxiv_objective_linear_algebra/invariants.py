"""Invariant checks for d_arxiv_objective_linear_algebra."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ObjectiveLinearAlgebraClaim, create_nominal_claim


def check_sign_consistency(data: ObjectiveLinearAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Sign assignments in objective linear algebra are consistent.

    Standard: arXiv 2603.19437v1 (math.CT) claim operationalization.
    Falsifies if: not sign_consistent.
    falsifies_if: not sign_consistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.sign_consistent
    proof = ProofObject(
        rule="check_sign_consistency",
        premises=[
            "paper_id=2603.19437v1",
            f"sign_consistent={data.sign_consistent}",
        ],
        conclusion=(
            "PASS: sign assignments are consistent"
            if success else "FAIL: sign assignments are inconsistent"
        ),
    )
    return success, proof


def check_exterior_power(data: ObjectiveLinearAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The exterior power construction is well-defined in objective linear algebra.

    Standard: arXiv 2603.19437v1 (math.CT) claim operationalization.
    Falsifies if: not exterior_power_well_defined.
    falsifies_if: not exterior_power_well_defined.

    Returns:
        Tuple of (success, proof).
    """
    success = data.exterior_power_well_defined
    proof = ProofObject(
        rule="check_exterior_power",
        premises=[
            "paper_id=2603.19437v1",
            f"exterior_power_well_defined={data.exterior_power_well_defined}",
        ],
        conclusion=(
            "PASS: exterior power construction is well-defined"
            if success else "FAIL: exterior power construction is not well-defined"
        ),
    )
    return success, proof


def check_determinant(data: ObjectiveLinearAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The determinant is well-defined in objective linear algebra.

    Standard: arXiv 2603.19437v1 (math.CT) claim operationalization.
    Falsifies if: not determinant_well_defined.
    falsifies_if: not determinant_well_defined.

    Returns:
        Tuple of (success, proof).
    """
    success = data.determinant_well_defined
    proof = ProofObject(
        rule="check_determinant",
        premises=[
            "paper_id=2603.19437v1",
            f"determinant_well_defined={data.determinant_well_defined}",
        ],
        conclusion=(
            "PASS: determinant is well-defined"
            if success else "FAIL: determinant is not well-defined"
        ),
    )
    return success, proof


def check_orientation_independence(data: ObjectiveLinearAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The theory is orientation-independent (objective).

    Standard: arXiv 2603.19437v1 (math.CT) claim operationalization.
    Falsifies if: not orientation_invariant.
    falsifies_if: not orientation_invariant.

    Returns:
        Tuple of (success, proof).
    """
    success = data.orientation_invariant
    proof = ProofObject(
        rule="check_orientation_independence",
        premises=[
            "paper_id=2603.19437v1",
            f"orientation_invariant={data.orientation_invariant}",
        ],
        conclusion=(
            "PASS: theory is orientation-independent"
            if success else "FAIL: theory is not orientation-independent"
        ),
    )
    return success, proof


def check_dimension_positive(data: ObjectiveLinearAlgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The vector space dimension is at least 1.

    Standard: arXiv 2603.19437v1 (math.CT) claim operationalization.
    Falsifies if: dimension < 1.
    falsifies_if: dimension < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.dimension >= Fraction(1)
    proof = ProofObject(
        rule="check_dimension_positive",
        premises=[
            "paper_id=2603.19437v1",
            f"dimension={data.dimension}",
        ],
        conclusion=(
            "PASS: dimension is positive"
            if success else "FAIL: dimension must be at least 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2603.19437v1 (math.CT) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_sign_consistency", check_sign_consistency),
        ("check_exterior_power", check_exterior_power),
        ("check_determinant", check_determinant),
        ("check_orientation_independence", check_orientation_independence),
        ("check_dimension_positive", check_dimension_positive),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

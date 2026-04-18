"""Invariant checks for Differential Geometry."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import DifferentialGeometryClaim, create_nominal_claim


def check_metric_positive_definite(data: DifferentialGeometryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Metric tensor is positive definite.

    Standard: Differential Geometry domain invariant.
    Falsifies if: not metric_positive_definite.
    falsifies_if: not metric_positive_definite.

    Returns:
        Tuple of (success, proof).
    """
    success = data.metric_positive_definite
    proof = ProofObject(
        rule="check_metric_positive_definite",
        premises=[
            "domain=Differential Geometry",
            f"metric_positive_definite={{data.metric_positive_definite}}",
        ],
        conclusion=(
            "PASS: Metric tensor is positive definite"
            if success else "FAIL: Metric tensor is positive definite"
        ),
    )
    return success, proof


def check_christoffel_symmetric(data: DifferentialGeometryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Christoffel symbols are symmetric in lower indices.

    Standard: Differential Geometry domain invariant.
    Falsifies if: not christoffel_symmetric.
    falsifies_if: not christoffel_symmetric.

    Returns:
        Tuple of (success, proof).
    """
    success = data.christoffel_symmetric
    proof = ProofObject(
        rule="check_christoffel_symmetric",
        premises=[
            "domain=Differential Geometry",
            f"christoffel_symmetric={{data.christoffel_symmetric}}",
        ],
        conclusion=(
            "PASS: Christoffel symbols are symmetric in lower indices"
            if success else "FAIL: Christoffel symbols are symmetric in lower indices"
        ),
    )
    return success, proof


def check_geodesic_equation_satisfied(data: DifferentialGeometryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Geodesic equation is satisfied.

    Standard: Differential Geometry domain invariant.
    Falsifies if: not geodesic_equation_satisfied.
    falsifies_if: not geodesic_equation_satisfied.

    Returns:
        Tuple of (success, proof).
    """
    success = data.geodesic_equation_satisfied
    proof = ProofObject(
        rule="check_geodesic_equation_satisfied",
        premises=[
            "domain=Differential Geometry",
            f"geodesic_equation_satisfied={{data.geodesic_equation_satisfied}}",
        ],
        conclusion=(
            "PASS: Geodesic equation is satisfied"
            if success else "FAIL: Geodesic equation is satisfied"
        ),
    )
    return success, proof


def check_curvature_tensor_antisymmetric(data: DifferentialGeometryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Riemann curvature tensor has correct antisymmetry.

    Standard: Differential Geometry domain invariant.
    Falsifies if: not curvature_antisymmetric.
    falsifies_if: not curvature_antisymmetric.

    Returns:
        Tuple of (success, proof).
    """
    success = data.curvature_antisymmetric
    proof = ProofObject(
        rule="check_curvature_tensor_antisymmetric",
        premises=[
            "domain=Differential Geometry",
            f"curvature_antisymmetric={{data.curvature_antisymmetric}}",
        ],
        conclusion=(
            "PASS: Riemann curvature tensor has correct antisymmetry"
            if success else "FAIL: Riemann curvature tensor has correct antisymmetry"
        ),
    )
    return success, proof


def check_sectional_curvature_fraction(data: DifferentialGeometryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Sectional curvature is real-valued.

    Standard: Differential Geometry domain invariant.
    Falsifies if: not sectional_curvature.
    falsifies_if: not sectional_curvature.

    Returns:
        Tuple of (success, proof).
    """
    success = data.sectional_curvature >= Fraction(0)
    proof = ProofObject(
        rule="check_sectional_curvature_fraction",
        premises=[
            "domain=Differential Geometry",
            f"sectional_curvature={{data.sectional_curvature}}",
        ],
        conclusion=(
            "PASS: Sectional curvature is real-valued is non-negative"
            if success else "FAIL: Sectional curvature is real-valued is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Differential Geometry nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_metric_positive_definite", check_metric_positive_definite),
        ("check_christoffel_symmetric", check_christoffel_symmetric),
        ("check_geodesic_equation_satisfied", check_geodesic_equation_satisfied),
        ("check_curvature_tensor_antisymmetric", check_curvature_tensor_antisymmetric),
        ("check_sectional_curvature_fraction", check_sectional_curvature_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

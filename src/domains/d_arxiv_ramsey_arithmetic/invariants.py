"""Invariant checks for d_arxiv_ramsey_arithmetic."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import RamseyArithmeticClaim, create_nominal_claim


def check_vertex_count_positive(data: RamseyArithmeticClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The structure has at least one vertex.

    Standard: arXiv 2603.23704v2 (math.LO) claim operationalization.
    Falsifies if: vertex_count < 1.
    falsifies_if: vertex_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.vertex_count >= Fraction(1)
    proof = ProofObject(
        rule="check_vertex_count_positive",
        premises=[
            "paper_id=2603.23704v2",
            f"vertex_count={data.vertex_count}",
        ],
        conclusion=(
            "PASS: vertex count is positive"
            if success else "FAIL: vertex count must be at least 1"
        ),
    )
    return success, proof


def check_coloring_count_positive(data: RamseyArithmeticClaim) -> Tuple[bool, ProofObject]:
    """Invariant: At least one coloring is considered.

    Standard: arXiv 2603.23704v2 (math.LO) claim operationalization.
    Falsifies if: coloring_count < 1.
    falsifies_if: coloring_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.coloring_count >= Fraction(1)
    proof = ProofObject(
        rule="check_coloring_count_positive",
        premises=[
            "paper_id=2603.23704v2",
            f"coloring_count={data.coloring_count}",
        ],
        conclusion=(
            "PASS: coloring count is positive"
            if success else "FAIL: coloring count must be at least 1"
        ),
    )
    return success, proof


def check_ramsey_number_valid(data: RamseyArithmeticClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The Ramsey number is at least as large as the vertex count.

    Standard: arXiv 2603.23704v2 (math.LO) claim operationalization.
    Falsifies if: ramsey_number < vertex_count.
    falsifies_if: ramsey_number < vertex_count.

    Returns:
        Tuple of (success, proof).
    """
    success = data.ramsey_number >= data.vertex_count
    proof = ProofObject(
        rule="check_ramsey_number_valid",
        premises=[
            "paper_id=2603.23704v2",
            f"ramsey_number={data.ramsey_number}",
            f"vertex_count={data.vertex_count}",
        ],
        conclusion=(
            "PASS: Ramsey number is valid relative to vertex count"
            if success else "FAIL: Ramsey number is less than vertex count"
        ),
    )
    return success, proof


def check_bounding_principle(data: RamseyArithmeticClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The relevant bounding principle of arithmetic holds.

    Standard: arXiv 2603.23704v2 (math.LO) claim operationalization.
    Falsifies if: not bounding_principle_holds.
    falsifies_if: not bounding_principle_holds.

    Returns:
        Tuple of (success, proof).
    """
    success = data.bounding_principle_holds
    proof = ProofObject(
        rule="check_bounding_principle",
        premises=[
            "paper_id=2603.23704v2",
            f"bounding_principle_holds={data.bounding_principle_holds}",
        ],
        conclusion=(
            "PASS: bounding principle of arithmetic holds"
            if success else "FAIL: bounding principle does not hold"
        ),
    )
    return success, proof


def check_provability(data: RamseyArithmeticClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The Ramsey result is provable in the base arithmetic theory.

    Standard: arXiv 2603.23704v2 (math.LO) claim operationalization.
    Falsifies if: not provable_in_base_theory.
    falsifies_if: not provable_in_base_theory.

    Returns:
        Tuple of (success, proof).
    """
    success = data.provable_in_base_theory
    proof = ProofObject(
        rule="check_provability",
        premises=[
            "paper_id=2603.23704v2",
            f"provable_in_base_theory={data.provable_in_base_theory}",
        ],
        conclusion=(
            "PASS: result is provable in base arithmetic theory"
            if success else "FAIL: result is not provable in base theory"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2603.23704v2 (math.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_vertex_count_positive", check_vertex_count_positive),
        ("check_coloring_count_positive", check_coloring_count_positive),
        ("check_ramsey_number_valid", check_ramsey_number_valid),
        ("check_bounding_principle", check_bounding_principle),
        ("check_provability", check_provability),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

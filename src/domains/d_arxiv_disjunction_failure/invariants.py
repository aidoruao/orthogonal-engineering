"""Invariant checks for d_arxiv_disjunction_failure."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import DisjunctionFailureClaim, create_nominal_claim


def check_theory_consistency(data: DisjunctionFailureClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The base theory is consistent.

    Standard: arXiv 2604.04830v1 (math.LO) claim operationalization.
    Falsifies if: not theory_is_consistent.
    falsifies_if: not theory_is_consistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.theory_is_consistent
    proof = ProofObject(
        rule="check_theory_consistency",
        premises=[
            "paper_id=2604.04830v1",
            f"theory_is_consistent={data.theory_is_consistent}",
        ],
        conclusion=(
            "PASS: base theory is consistent"
            if success else "FAIL: base theory is not consistent"
        ),
    )
    return success, proof


def check_counterexample_witness(data: DisjunctionFailureClaim) -> Tuple[bool, ProofObject]:
    """Invariant: A counterexample to the strong FDP exists.

    Standard: arXiv 2604.04830v1 (math.LO) claim operationalization.
    Falsifies if: not counterexample_exists.
    falsifies_if: not counterexample_exists.

    Returns:
        Tuple of (success, proof).
    """
    success = data.counterexample_exists
    proof = ProofObject(
        rule="check_counterexample_witness",
        premises=[
            "paper_id=2604.04830v1",
            f"counterexample_exists={data.counterexample_exists}",
        ],
        conclusion=(
            "PASS: counterexample to strong FDP exists"
            if success else "FAIL: no counterexample to strong FDP found"
        ),
    )
    return success, proof


def check_disjunction_property_failure(data: DisjunctionFailureClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The strong feasible disjunction property fails (FDP does not hold).

    Standard: arXiv 2604.04830v1 (math.LO) claim operationalization.
    Falsifies if: theory_has_disjunction_property.
    falsifies_if: theory_has_disjunction_property.

    Returns:
        Tuple of (success, proof).
    """
    success = not data.theory_has_disjunction_property
    proof = ProofObject(
        rule="check_disjunction_property_failure",
        premises=[
            "paper_id=2604.04830v1",
            f"theory_has_disjunction_property={data.theory_has_disjunction_property}",
        ],
        conclusion=(
            "PASS: strong FDP fails as expected per paper"
            if success else "FAIL: strong FDP holds — expected failure not observed"
        ),
    )
    return success, proof


def check_disjunct_count_positive(data: DisjunctionFailureClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The counterexample involves at least 2 disjuncts.

    Standard: arXiv 2604.04830v1 (math.LO) claim operationalization.
    Falsifies if: disjunct_count < 2.
    falsifies_if: disjunct_count < 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.disjunct_count >= Fraction(2)
    proof = ProofObject(
        rule="check_disjunct_count_positive",
        premises=[
            "paper_id=2604.04830v1",
            f"disjunct_count={data.disjunct_count}",
        ],
        conclusion=(
            "PASS: disjunct count is at least 2"
            if success else "FAIL: disjunct count must be at least 2"
        ),
    )
    return success, proof


def check_provability_witness(data: DisjunctionFailureClaim) -> Tuple[bool, ProofObject]:
    """Invariant: A provability witness exists for the counterexample.

    Standard: arXiv 2604.04830v1 (math.LO) claim operationalization.
    Falsifies if: not provability_witness_exists.
    falsifies_if: not provability_witness_exists.

    Returns:
        Tuple of (success, proof).
    """
    success = data.provability_witness_exists
    proof = ProofObject(
        rule="check_provability_witness",
        premises=[
            "paper_id=2604.04830v1",
            f"provability_witness_exists={data.provability_witness_exists}",
        ],
        conclusion=(
            "PASS: provability witness exists"
            if success else "FAIL: no provability witness found"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.04830v1 (math.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_theory_consistency", check_theory_consistency),
        ("check_counterexample_witness", check_counterexample_witness),
        ("check_disjunction_property_failure", check_disjunction_property_failure),
        ("check_disjunct_count_positive", check_disjunct_count_positive),
        ("check_provability_witness", check_provability_witness),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

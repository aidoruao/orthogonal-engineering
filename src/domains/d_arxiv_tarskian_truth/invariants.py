"""Invariant checks for d_arxiv_tarskian_truth."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import TarskianTruthClaim, create_nominal_claim


def check_object_theory_consistency(data: TarskianTruthClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The base object theory (e.g., ZF) is consistent.

    Standard: arXiv 2604.03825v2 (math.LO) claim operationalization.
    Falsifies if: not object_theory_consistent.
    falsifies_if: not object_theory_consistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.object_theory_consistent
    proof = ProofObject(
        rule="check_object_theory_consistency",
        premises=[
            "paper_id=2604.03825v2",
            f"object_theory_consistent={data.object_theory_consistent}",
        ],
        conclusion=(
            "PASS: object theory is consistent"
            if success else "FAIL: object theory is not consistent"
        ),
    )
    return success, proof


def check_truth_predicate_consistency(data: TarskianTruthClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Adding the Tarskian truth predicate preserves consistency.

    Standard: arXiv 2604.03825v2 (math.LO) claim operationalization.
    Falsifies if: not truth_predicate_consistent.
    falsifies_if: not truth_predicate_consistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.truth_predicate_consistent
    proof = ProofObject(
        rule="check_truth_predicate_consistency",
        premises=[
            "paper_id=2604.03825v2",
            f"truth_predicate_consistent={data.truth_predicate_consistent}",
        ],
        conclusion=(
            "PASS: truth predicate extension is consistent"
            if success else "FAIL: truth predicate extension is inconsistent"
        ),
    )
    return success, proof


def check_tarski_biconditional(data: TarskianTruthClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The Tarski T-schema T(phi) <-> phi holds for all sentences.

    Standard: arXiv 2604.03825v2 (math.LO) claim operationalization.
    Falsifies if: not satisfies_tarski_biconditional.
    falsifies_if: not satisfies_tarski_biconditional.

    Returns:
        Tuple of (success, proof).
    """
    success = data.satisfies_tarski_biconditional
    proof = ProofObject(
        rule="check_tarski_biconditional",
        premises=[
            "paper_id=2604.03825v2",
            f"satisfies_tarski_biconditional={data.satisfies_tarski_biconditional}",
        ],
        conclusion=(
            "PASS: Tarski biconditional T(phi) <-> phi holds"
            if success else "FAIL: Tarski biconditional does not hold"
        ),
    )
    return success, proof


def check_compositionality(data: TarskianTruthClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The truth predicate is compositional.

    Standard: arXiv 2604.03825v2 (math.LO) claim operationalization.
    Falsifies if: not compositional.
    falsifies_if: not compositional.

    Returns:
        Tuple of (success, proof).
    """
    success = data.compositional
    proof = ProofObject(
        rule="check_compositionality",
        premises=[
            "paper_id=2604.03825v2",
            f"compositional={data.compositional}",
        ],
        conclusion=(
            "PASS: truth predicate is compositional"
            if success else "FAIL: truth predicate is not compositional"
        ),
    )
    return success, proof


def check_axiom_count_positive(data: TarskianTruthClaim) -> Tuple[bool, ProofObject]:
    """Invariant: At least one disquotational axiom is present.

    Standard: arXiv 2604.03825v2 (math.LO) claim operationalization.
    Falsifies if: disquotational_axiom_count < 1.
    falsifies_if: disquotational_axiom_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.disquotational_axiom_count >= Fraction(1)
    proof = ProofObject(
        rule="check_axiom_count_positive",
        premises=[
            "paper_id=2604.03825v2",
            f"disquotational_axiom_count={data.disquotational_axiom_count}",
        ],
        conclusion=(
            "PASS: at least one disquotational axiom present"
            if success else "FAIL: disquotational axiom count must be at least 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.03825v2 (math.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_object_theory_consistency", check_object_theory_consistency),
        ("check_truth_predicate_consistency", check_truth_predicate_consistency),
        ("check_tarski_biconditional", check_tarski_biconditional),
        ("check_compositionality", check_compositionality),
        ("check_axiom_count_positive", check_axiom_count_positive),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

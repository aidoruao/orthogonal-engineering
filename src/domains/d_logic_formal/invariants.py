"""Invariant checks for Formal Logic."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import FormalLogicClaim, create_nominal_claim


def check_soundness_theorem_holds(data: FormalLogicClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Soundness theorem holds.

    Standard: Formal Logic domain invariant.
    Falsifies if: not soundness_holds.
    falsifies_if: not soundness_holds.

    Returns:
        Tuple of (success, proof).
    """
    success = data.soundness_holds
    proof = ProofObject(
        rule="check_soundness_theorem_holds",
        premises=[
            "domain=Formal Logic",
            f"soundness_holds={{data.soundness_holds}}",
        ],
        conclusion=(
            "PASS: Soundness theorem holds"
            if success else "FAIL: Soundness theorem holds"
        ),
    )
    return success, proof


def check_completeness_theorem_holds(data: FormalLogicClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Completeness theorem holds.

    Standard: Formal Logic domain invariant.
    Falsifies if: not completeness_holds.
    falsifies_if: not completeness_holds.

    Returns:
        Tuple of (success, proof).
    """
    success = data.completeness_holds
    proof = ProofObject(
        rule="check_completeness_theorem_holds",
        premises=[
            "domain=Formal Logic",
            f"completeness_holds={{data.completeness_holds}}",
        ],
        conclusion=(
            "PASS: Completeness theorem holds"
            if success else "FAIL: Completeness theorem holds"
        ),
    )
    return success, proof


def check_consistency_no_contradiction(data: FormalLogicClaim) -> Tuple[bool, ProofObject]:
    """Invariant: System is consistent (no contradiction provable).

    Standard: Formal Logic domain invariant.
    Falsifies if: not consistent_no_contradiction.
    falsifies_if: not consistent_no_contradiction.

    Returns:
        Tuple of (success, proof).
    """
    success = data.consistent_no_contradiction
    proof = ProofObject(
        rule="check_consistency_no_contradiction",
        premises=[
            "domain=Formal Logic",
            f"consistent_no_contradiction={{data.consistent_no_contradiction}}",
        ],
        conclusion=(
            "PASS: System is consistent (no contradiction provable)"
            if success else "FAIL: System is consistent (no contradiction provable)"
        ),
    )
    return success, proof


def check_decidability_defined(data: FormalLogicClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Decidability is well-defined for the system.

    Standard: Formal Logic domain invariant.
    Falsifies if: not decidability_defined.
    falsifies_if: not decidability_defined.

    Returns:
        Tuple of (success, proof).
    """
    success = data.decidability_defined
    proof = ProofObject(
        rule="check_decidability_defined",
        premises=[
            "domain=Formal Logic",
            f"decidability_defined={{data.decidability_defined}}",
        ],
        conclusion=(
            "PASS: Decidability is well-defined for the system"
            if success else "FAIL: Decidability is well-defined for the system"
        ),
    )
    return success, proof


def check_proof_length_fraction(data: FormalLogicClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Proof length is non-negative.

    Standard: Formal Logic domain invariant.
    Falsifies if: not proof_length.
    falsifies_if: not proof_length.

    Returns:
        Tuple of (success, proof).
    """
    success = data.proof_length >= Fraction(0)
    proof = ProofObject(
        rule="check_proof_length_fraction",
        premises=[
            "domain=Formal Logic",
            f"proof_length={{data.proof_length}}",
        ],
        conclusion=(
            "PASS: Proof length is non-negative is non-negative"
            if success else "FAIL: Proof length is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Formal Logic nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_soundness_theorem_holds", check_soundness_theorem_holds),
        ("check_completeness_theorem_holds", check_completeness_theorem_holds),
        ("check_consistency_no_contradiction", check_consistency_no_contradiction),
        ("check_decidability_defined", check_decidability_defined),
        ("check_proof_length_fraction", check_proof_length_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

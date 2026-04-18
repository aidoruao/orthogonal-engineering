"""Invariant checks for d_arxiv_goodstein."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import GoodsteinClaim, create_nominal_claim


def check_termination(data: GoodsteinClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The Goodstein sequence eventually terminates at 0.

    Standard: arXiv 2603.19981v1 (math.LO) claim operationalization.
    Falsifies if: not terminates.
    falsifies_if: not terminates.

    Returns:
        Tuple of (success, proof).
    """
    success = data.terminates
    proof = ProofObject(
        rule="check_termination",
        premises=[
            "paper_id=2603.19981v1",
            f"terminates={data.terminates}",
        ],
        conclusion=(
            "PASS: Goodstein sequence terminates at 0"
            if success else "FAIL: Goodstein sequence does not terminate"
        ),
    )
    return success, proof


def check_transfinite_required(data: GoodsteinClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Proof of termination requires transfinite induction (ordinal arithmetic).

    Standard: arXiv 2603.19981v1 (math.LO) claim operationalization.
    Falsifies if: not requires_transfinite_induction.
    falsifies_if: not requires_transfinite_induction.

    Returns:
        Tuple of (success, proof).
    """
    success = data.requires_transfinite_induction
    proof = ProofObject(
        rule="check_transfinite_required",
        premises=[
            "paper_id=2603.19981v1",
            f"requires_transfinite_induction={data.requires_transfinite_induction}",
        ],
        conclusion=(
            "PASS: proof requires transfinite induction over ordinals"
            if success else "FAIL: transfinite induction not required — unexpected"
        ),
    )
    return success, proof


def check_sequence_length_positive(data: GoodsteinClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The computed Goodstein sequence has positive length.

    Standard: arXiv 2603.19981v1 (math.LO) claim operationalization.
    Falsifies if: sequence_length < 1.
    falsifies_if: sequence_length < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.sequence_length >= Fraction(1)
    proof = ProofObject(
        rule="check_sequence_length_positive",
        premises=[
            "paper_id=2603.19981v1",
            f"sequence_length={data.sequence_length}",
        ],
        conclusion=(
            "PASS: sequence length is positive"
            if success else "FAIL: sequence length must be at least 1"
        ),
    )
    return success, proof


def check_base_positive(data: GoodsteinClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The base reached in the sequence is at least 2.

    Standard: arXiv 2603.19981v1 (math.LO) claim operationalization.
    Falsifies if: base_reached < 2.
    falsifies_if: base_reached < 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.base_reached >= Fraction(2)
    proof = ProofObject(
        rule="check_base_positive",
        premises=[
            "paper_id=2603.19981v1",
            f"base_reached={data.base_reached}",
        ],
        conclusion=(
            "PASS: base reached is at least 2"
            if success else "FAIL: base must be at least 2"
        ),
    )
    return success, proof


def check_unprovable_in_peano(data: GoodsteinClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Goodstein's theorem is not provable in Peano Arithmetic (Kirby-Paris).

    Standard: arXiv 2603.19981v1 (math.LO) claim operationalization.
    Falsifies if: not peano_cannot_prove.
    falsifies_if: not peano_cannot_prove.

    Returns:
        Tuple of (success, proof).
    """
    success = data.peano_cannot_prove
    proof = ProofObject(
        rule="check_unprovable_in_peano",
        premises=[
            "paper_id=2603.19981v1",
            f"peano_cannot_prove={data.peano_cannot_prove}",
        ],
        conclusion=(
            "PASS: Goodstein's theorem is unprovable in PA (Kirby-Paris)"
            if success else "FAIL: expected PA unprovability not confirmed"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2603.19981v1 (math.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_termination", check_termination),
        ("check_transfinite_required", check_transfinite_required),
        ("check_sequence_length_positive", check_sequence_length_positive),
        ("check_base_positive", check_base_positive),
        ("check_unprovable_in_peano", check_unprovable_in_peano),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

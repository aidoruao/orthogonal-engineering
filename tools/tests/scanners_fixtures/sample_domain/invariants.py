"""Sample domain invariants for scanner tests."""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_sample_positive(value: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: value is positive.

    Standard: Sample-001
    Falsifies if: value <= 0
    falsifies_if: value <= 0
    """
    ok = value > Fraction(0)
    proof = ProofObject(
        rule="SamplePositivity",
        premises=[f"value={value}"],
        conclusion="positive" if ok else "non-positive",
    )
    return ok, proof


def check_sample_bounded(value: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: value lies in [0, 1].

    Standard: Sample-002
    Falsifies if: value < 0 or value > 1
    falsifies_if: value < 0 or value > 1
    """
    ok = Fraction(0) <= value <= Fraction(1)
    proof = ProofObject(
        rule="SampleBoundedness",
        premises=[f"value={value}"],
        conclusion="bounded" if ok else "out of bounds",
    )
    return ok, proof


# Intentionally malformed: missing falsifies_if and wrong return type.
def check_sample_bad(value: Fraction) -> bool:
    """Invariant: value is non-zero."""
    return value != Fraction(0)

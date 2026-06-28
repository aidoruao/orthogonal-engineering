"""Fixture for formula AST scanner tests."""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def ratio(a: Fraction, b: Fraction) -> Fraction:
    """Return a / b as an exact fraction."""
    return a / b


def check_positive(value: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: value is strictly positive.

    Standard: Yeshua
    Falsifies if: value <= 0
    falsifies_if: value <= 0
    """
    ok = value > Fraction(0)
    proof = ProofObject(
        rule="Positivity",
        premises=[f"value={value}"],
        conclusion="value is positive" if ok else "value is non-positive",
    )
    return ok, proof


def quadratic_sum(x: Fraction, y: Fraction) -> Fraction:
    return x * x + y * y + Fraction(2) * x * y


def scale_ratio(ratio_value: Fraction, factor: int) -> Fraction:
    return ratio_value * Fraction(factor)

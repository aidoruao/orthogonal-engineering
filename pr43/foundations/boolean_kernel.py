# pr43/foundations/boolean_kernel.py
# PR #43 — Orthogonal Parallel
# Standard: Yeshua
#
# Boolean algebra derived from ℕ.
# false = Zero(), true = Succ(Zero()).
# Only these two values are valid boolean witnesses.
# NAND alone is functionally complete.

from __future__ import annotations

from .peano_kernel import Natural, Zero, Succ, zero, successor, eq

# Type alias — Bool is a Natural restricted to {false(), true()}
Bool = Natural


def false() -> Bool:
    """Boolean false — encoded as 0 ∈ ℕ."""
    return zero()


def true() -> Bool:
    """Boolean true — encoded as S(0) ∈ ℕ."""
    return successor(zero())


def is_bool(x: Natural) -> bool:
    """Check that x is a valid boolean witness."""
    return eq(x, false()) or eq(x, true())


def NOT(x: Bool) -> Bool:
    """NOT: true ↔ false."""
    if eq(x, false()):
        return true()
    return false()


def AND(x: Bool, y: Bool) -> Bool:
    """AND: true only when both operands are true."""
    if eq(x, true()) and eq(y, true()):
        return true()
    return false()


def OR(x: Bool, y: Bool) -> Bool:
    """OR: true when at least one operand is true."""
    if eq(x, true()) or eq(y, true()):
        return true()
    return false()


def NAND(x: Bool, y: Bool) -> Bool:
    """NAND: functionally complete primitive."""
    return NOT(AND(x, y))


def IMPLIES(x: Bool, y: Bool) -> Bool:
    """x → y  ≡  ¬x ∨ y."""
    return OR(NOT(x), y)


def IFF(x: Bool, y: Bool) -> Bool:
    """x ↔ y  ≡  (x → y) ∧ (y → x)."""
    return AND(IMPLIES(x, y), IMPLIES(y, x))

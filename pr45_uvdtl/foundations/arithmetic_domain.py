"""Arithmetic Domain - pr45_uvdtl/foundations/arithmetic_domain.py"""
# pr45_uvdtl/foundations/arithmetic_domain.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section I.1 — Deterministic Core Domain
#
# Canonical state reduces to:
#   - Natural numbers ℕ (inductive: Zero | Succ)
#   - Finite tuples over ℕ
#   - Finite strings over fixed alphabet
#   - Total functions only
#
# No floating-point values influence canonical state hashes.
# Rationals encoded as (p, q) ∈ ℕ × ℕ (numerator, denominator > 0).

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple


# ---------------------------------------------------------------------------
# Inductive Natural Numbers
# ---------------------------------------------------------------------------

class Natural:
    """Abstract base for inductive natural numbers."""


@dataclass(frozen=True)
class Zero(Natural):
    """Axiom P1: 0 ∈ ℕ"""


@dataclass(frozen=True)
class Succ(Natural):
    """Axiom P2: ∀n ∈ ℕ, S(n) ∈ ℕ"""
    pred: Natural


def zero() -> Natural:
    """Return the canonical zero."""
    # TODO: Expand zero() - stub detected by Yeshua Agent
    return Zero()


def successor(n: Natural) -> Natural:
    """Return the canonical successor of n."""
    # TODO: Expand successor() - stub detected by Yeshua Agent
    return Succ(n)


def to_int(n: Natural) -> int:
    """Convert inductive Natural to Python int (display only)."""
    acc = 0
    cur = n
    while isinstance(cur, Succ):
        acc += 1
        cur = cur.pred
    return acc


def from_int(k: int) -> Natural:
    """Build inductive Natural from non-negative Python int."""
    if k < 0:
        raise ValueError("Natural numbers are non-negative")
    result: Natural = Zero()
    for _ in range(k):
        result = Succ(result)
    return result


def nat_eq(a: Natural, b: Natural) -> bool:
    """Structural equality of Natural numbers."""
    if isinstance(a, Zero) and isinstance(b, Zero):
        return True
    if isinstance(a, Succ) and isinstance(b, Succ):
        return nat_eq(a.pred, b.pred)
    return False


# ---------------------------------------------------------------------------
# Finite Tuples over ℕ
# ---------------------------------------------------------------------------

FiniteTuple = Tuple[Natural, ...]


def make_tuple(*args: Natural) -> FiniteTuple:
    """Construct a finite tuple of Natural numbers."""
    # TODO: Expand make_tuple() - stub detected by Yeshua Agent
    return tuple(args)


def tuple_project(t: FiniteTuple, index: int) -> Natural:
    """
    Projection: returns the element at position `index`.
    Raises IndexError for out-of-bounds access.
    """
    return t[index]


# ---------------------------------------------------------------------------
# Finite Strings over a Fixed Alphabet
# ---------------------------------------------------------------------------

CANONICAL_ALPHABET: str = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "_-.:/"
)


def make_canonical_string(s: str) -> str:
    """
    Validate and return a canonical string (subset of CANONICAL_ALPHABET).
    Raises ValueError if any character is not in the alphabet.
    """
    for ch in s:
        if ch not in CANONICAL_ALPHABET:
            raise ValueError(f"Character {ch!r} not in canonical alphabet")
    return s


# ---------------------------------------------------------------------------
# Rational Encoding (no floats)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Rational:
    """
    Rational number encoded as (p, q) ∈ ℕ × ℕ⁺.
    p is the numerator (Python int ≥ 0).
    q is the denominator (Python int > 0).
    No float arithmetic is used or exposed.
    """
    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if self.denominator <= 0:
            raise ValueError("Rational denominator must be positive")
        if self.numerator < 0:
            raise ValueError("Rational numerator must be non-negative")

    def as_pair(self) -> Tuple[int, int]:
        """Return (numerator, denominator) — the canonical rational encoding."""
        # TODO: Expand as_pair() - stub detected by Yeshua Agent
        return (self.numerator, self.denominator)


# ---------------------------------------------------------------------------
# Total Functions
# ---------------------------------------------------------------------------

def apply_total(f: Callable[[Natural], Natural], n: Natural) -> Natural:
    """
    Apply a total function f : ℕ → ℕ.
    The function must be total (defined for all Natural inputs).
    """
    return f(n)


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "Float arithmetic (IEEE 754)": "Non-deterministic rounding; platform-dependent",
    "PR #45 Arithmetic Domain": (
        "All values in ℕ or Rational(p,q); no float literals; "
        "deterministic across all compliant platforms"
    ),
}

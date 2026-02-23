# pr44_orthogonal_meta/foundations/peano_kernel.py
# PR #44 — Orthogonal Meta Parallel
# Standard: Yeshua
#
# ℕ defined inductively: Zero | Succ(Natural)
# Axioms P1-P5: existence of zero, closure under successor,
# injectivity of successor, non-zeroness of successors, induction.
# No reliance on Python int arithmetic for structural computation.

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


class Natural:
    """Abstract base for inductive natural numbers."""


@dataclass(frozen=True)
class Zero(Natural):
    """Axiom P1: 0 ∈ ℕ"""


@dataclass(frozen=True)
class Succ(Natural):
    """Axiom P2: ∀n ∈ ℕ, S(n) ∈ ℕ"""
    pred: Natural  # predecessor


def zero() -> Natural:
    """Axiom P1: canonical zero."""
    return Zero()


def successor(n: Natural) -> Natural:
    """Axiom P2: canonical successor."""
    return Succ(n)


def eq(a: Natural, b: Natural) -> bool:
    """Structural equality (Axiom P3 injectivity witness)."""
    if isinstance(a, Zero) and isinstance(b, Zero):
        return True
    if isinstance(a, Succ) and isinstance(b, Succ):
        return eq(a.pred, b.pred)
    return False


def is_zero(n: Natural) -> bool:
    """Axiom P4: S(n) ≠ 0."""
    return isinstance(n, Zero)


def induction(
    n: Natural,
    base_case: Callable[[], bool],
    step_case: Callable[[Natural, bool], bool],
) -> bool:
    """
    Axiom P5: Induction principle (structural recursion).

    If P(0) and ∀k, P(k) ⇒ P(S(k)), then ∀n P(n).
    Termination guaranteed by structural descent on n.
    """
    if isinstance(n, Zero):
        return base_case()
    if isinstance(n, Succ):
        return step_case(n.pred, induction(n.pred, base_case, step_case))
    return False  # unreachable


def to_int(n: Natural) -> int:
    """Convert inductive Natural to Python int (for display only)."""
    acc = 0
    current = n
    while isinstance(current, Succ):
        acc += 1
        current = current.pred
    return acc


def from_int(k: int) -> Natural:
    """Build inductive Natural from non-negative Python int."""
    if k < 0:
        raise ValueError("Natural numbers are non-negative")
    result: Natural = Zero()
    for _ in range(k):
        result = Succ(result)
    return result

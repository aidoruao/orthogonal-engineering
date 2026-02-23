# pr43/foundations/primitive_recursion.py
# PR #43 — Orthogonal Parallel
# Standard: Yeshua
#
# Primitive recursive functions over ℕ.
# All recursion strictly decreases on structural predecessor.
# Termination guaranteed by structural descent.
# Zero floating point. Zero randomness. Zero external dependency.

from __future__ import annotations

from .peano_kernel import Natural, Zero, Succ, zero, successor, eq


def add(a: Natural, b: Natural) -> Natural:
    """
    Primitive recursion:
      add(a, 0)    = a
      add(a, S(b)) = S(add(a, b))
    """
    if isinstance(b, Zero):
        return a
    if isinstance(b, Succ):
        return successor(add(a, b.pred))
    raise TypeError(f"Expected Natural, got {type(b)}")


def mul(a: Natural, b: Natural) -> Natural:
    """
    Primitive recursion:
      mul(a, 0)    = 0
      mul(a, S(b)) = add(a, mul(a, b))
    """
    if isinstance(b, Zero):
        return zero()
    if isinstance(b, Succ):
        return add(a, mul(a, b.pred))
    raise TypeError(f"Expected Natural, got {type(b)}")


def leq(a: Natural, b: Natural) -> bool:
    """
    a ≤ b — defined by structural co-recursion on both arguments.
      0   ≤ b    = True
      S(a) ≤ 0   = False
      S(a) ≤ S(b) = a ≤ b
    Termination guaranteed: both arguments decrease structurally.
    """
    if isinstance(a, Zero):
        return True
    if isinstance(b, Zero):
        return False
    if isinstance(a, Succ) and isinstance(b, Succ):
        return leq(a.pred, b.pred)
    raise TypeError(f"Expected Natural, got {type(a)} or {type(b)}")


def lt(a: Natural, b: Natural) -> bool:
    """a < b  ⟺  S(a) ≤ b"""
    return leq(successor(a), b)

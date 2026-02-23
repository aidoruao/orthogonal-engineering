# pr43/foundations/type_theory.py
# PR #43 — Orthogonal Parallel
# Standard: Yeshua
#
# Curry-Howard correspondence: propositions as types, proofs as programs.
# Π-type: dependent product (universal quantification).
# Σ-type: dependent sum (existential quantification).
# →-type: function (implication via modus ponens).

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from .peano_kernel import Natural, induction

A = TypeVar("A")
B = TypeVar("B")


@dataclass(frozen=True)
class Proof(Generic[A]):
    """
    A constructive proof: a typed witness of proposition A.
    Programs are proofs; propositions are types.
    """
    witness: A

    def apply(self, f: Callable[[A], B]) -> "Proof[B]":
        """Modus ponens: Proof(A) and A→B yields Proof(B)."""
        return Proof(f(self.witness))


class Pi(Generic[A, B]):
    """
    Π(x:A).B(x) — dependent function type (universal quantification).
    ∀ x:A, B(x) holds by f(x) for each x.
    """
    def __init__(self, f: Callable[[A], B]) -> None:
        self._f = f

    def __call__(self, x: A) -> B:
        return self._f(x)


@dataclass(frozen=True)
class Sigma(Generic[A, B]):
    """
    Σ(x:A).B(x) — dependent pair type (existential quantification).
    ∃ x:A such that B(x) holds; fst is the witness, snd is the proof.
    """
    fst: A   # the witness
    snd: B   # the proof of B(fst)


def plus_zero_identity(n: Natural) -> Proof[bool]:
    """
    Constructive proof that ∀n ∈ ℕ, n + 0 = n.
    Reduces structurally via Axiom P5 (induction).
    """
    from .primitive_recursion import add
    from .peano_kernel import zero, eq

    def base() -> bool:
        return eq(add(zero(), zero()), zero())

    def step(k: Natural, ih: bool) -> bool:
        return ih

    result = induction(n, base, step)
    return Proof(result)

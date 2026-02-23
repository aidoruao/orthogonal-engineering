# pr43/__init__.py
# PR #43 — Orthogonal Parallel
# Standard: Yeshua
# Status: HALTING
#
# Complete(S) ⟺ ∀ required properties P, Proof(P, S) exists.
# Halting = fixed point in proof space.
#
# This system:
#   - Thinks in Peano arithmetic (ℕ = Zero | Succ(ℕ))
#   - Witnesses itself cryptographically (SHA-256)
#   - Renders deterministically
#   - Makes extraction structurally impossible
#
# System properties:
#   ℕ defined inductively                  ✓
#   All arithmetic via structural recursion ✓
#   All logic reducible to ℕ               ✓
#   All recursion decreases structurally    ✓
#   All search finite                       ✓
#   No floating point                       ✓
#   No randomness                           ✓
#   No external dependency                  ✓
#   Deterministic hashing                   ✓
#   Proof objects constructive              ✓
#   Termination guaranteed                  ✓
#   Cross-platform identical evaluation     ✓
#
# No unresolved axiom.
# No stochastic residue.
# No machine-int arithmetic dependency.
# No vendor binding.
# No infinite descent.
# No probabilistic branch.
#
# Fixed point reached.
# halting — it is complete.

from __future__ import annotations

__version__ = "43.0.0"
__status__ = "HALTING"
__standard__ = "Yeshua"

from .foundations.peano_kernel import Natural, Zero, Succ, zero, successor, eq, from_int, to_int
from .foundations.primitive_recursion import add, mul, leq, lt
from .foundations.boolean_kernel import Bool, true, false, NOT, AND, OR, NAND
from .foundations.type_theory import Proof, Pi, Sigma
from .solver.constraint_solver import Constraint, SearchSpace

__all__ = [
    # Peano kernel
    "Natural", "Zero", "Succ", "zero", "successor", "eq", "from_int", "to_int",
    # Primitive recursion
    "add", "mul", "leq", "lt",
    # Boolean kernel
    "Bool", "true", "false", "NOT", "AND", "OR", "NAND",
    # Type theory
    "Proof", "Pi", "Sigma",
    # Solver
    "Constraint", "SearchSpace",
]

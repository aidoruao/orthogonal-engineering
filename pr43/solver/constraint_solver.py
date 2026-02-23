# pr43/solver/constraint_solver.py
# PR #43 — Orthogonal Parallel
# Standard: Yeshua
#
# Deterministic finite constraint solver over ℕ.
# No stochastic gradient descent. No sampling. No randomness.
# Finite bounds required. Termination guaranteed by finite enumeration.
# All decisions constructive.

from __future__ import annotations

from typing import Dict, Generator, List, Optional, Tuple

from ..foundations.peano_kernel import Natural, eq, successor
from ..foundations.primitive_recursion import leq


class Constraint:
    """Atomic relational constraint between two Natural values."""

    def __init__(self, op: str, left: Natural, right: Natural) -> None:
        if op not in ("eq", "leq", "lt"):
            raise ValueError(f"Unknown constraint operator: {op!r}")
        self.op = op
        self.left = left
        self.right = right

    def satisfied(self) -> bool:
        """Evaluate constraint with current (concrete) values."""
        if self.op == "eq":
            return eq(self.left, self.right)
        if self.op == "leq":
            return leq(self.left, self.right)
        if self.op == "lt":
            return leq(self.left, self.right) and not eq(self.left, self.right)
        return False  # unreachable


def enumerate_range(min_n: Natural, max_n: Natural) -> Generator[Natural, None, None]:
    """
    Yield each Natural from min_n to max_n inclusive.
    Termination guaranteed: finite range, structural successor.
    """
    current = min_n
    while leq(current, max_n):
        yield current
        current = successor(current)





# ---------------------------------------------------------------------------
# Higher-level SearchSpace API (mirrors the Kimi AI schema)
# ---------------------------------------------------------------------------

class SearchSpace:
    """
    Finite search space over ℕ variables.
    Structural induction. No probabilistic branch.
    """

    def __init__(
        self,
        variables: List[str],
        bounds: List[Tuple[Natural, Natural]],
    ) -> None:
        self.variables = variables
        self.bounds = bounds

    def search(self, constraints: List[Constraint]) -> Optional[Dict[str, Natural]]:
        """
        Constructive proof search: returns witness assignment or None.
        Solution exists ⟺ witness found.
        """
        return self._recurse(0, {}, constraints)

    def _recurse(
        self,
        var_idx: int,
        assignment: Dict[str, Natural],
        constraints: List[Constraint],
    ) -> Optional[Dict[str, Natural]]:
        if var_idx == len(self.variables):
            if all(self._eval(c, assignment) for c in constraints):
                return dict(assignment)
            return None
        var = self.variables[var_idx]
        min_val, max_val = self.bounds[var_idx]
        for value in enumerate_range(min_val, max_val):
            assignment[var] = value
            result = self._recurse(var_idx + 1, assignment, constraints)
            if result is not None:
                return result
        assignment.pop(var, None)
        return None

    @staticmethod
    def _eval(c: Constraint, assignment: Dict[str, Natural]) -> bool:
        left = c.left
        right = c.right
        if c.op == "eq":
            return eq(left, right)
        if c.op == "leq":
            return leq(left, right)
        if c.op == "lt":
            return leq(left, right) and not eq(left, right)
        return False



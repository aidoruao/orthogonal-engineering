"""Deterministic Training - pr44_orthogonal_meta/domain_models/ai/deterministic_training.py"""
# pr44_orthogonal_meta/domain_models/ai/deterministic_training.py
# PR #44 — Orthogonal Meta Parallel
# Standard: Yeshua
#
# Replaces stochastic gradient descent (SGD) with constraint propagation.
# All outputs deterministic, hash-identical across builds.
# No floating point, no randomness, no hidden state.

from __future__ import annotations

from typing import Dict, List, Optional

from ...foundations.peano_kernel import Natural, from_int, to_int, eq
from ...foundations.primitive_recursion import add, leq


def constraint_propagate(
    variables: List[str],
    domains: Dict[str, List[Natural]],
    constraints: List[Dict],
) -> Optional[Dict[str, Natural]]:
    """
    Deterministic constraint propagation over finite Natural domains.

    Replaces SGD: instead of stochastic gradient updates, we enumerate
    the space constructively and return the first satisfying assignment.

    Termination guaranteed: finite domains, structural enumeration.
    """
    return _backtrack(variables, 0, {}, domains, constraints)


def _backtrack(
    variables: List[str],
    idx: int,
    assignment: Dict[str, Natural],
    domains: Dict[str, List[Natural]],
    constraints: List[Dict],
) -> Optional[Dict[str, Natural]]:
    if idx == len(variables):
        return dict(assignment)
    var = variables[idx]
    for value in domains[var]:
        assignment[var] = value
        if _all_satisfied(assignment, constraints):
            result = _backtrack(variables, idx + 1, assignment, domains, constraints)
            if result is not None:
                return result
    assignment.pop(var, None)
    return None


def _all_satisfied(
    assignment: Dict[str, Natural],
    constraints: List[Dict],
) -> bool:
    for c in constraints:
        op = c.get("op", "eq")
        lhs_var = c.get("lhs")
        rhs_var = c.get("rhs")
        if lhs_var not in assignment or rhs_var not in assignment:
            continue
        lhs = assignment[lhs_var]
        rhs = assignment[rhs_var]
        if op == "eq" and not eq(lhs, rhs):
            return False
        if op == "leq" and not leq(lhs, rhs):
            return False
    return True


# ---------------------------------------------------------------------------
# Comparative summary
# ---------------------------------------------------------------------------

COMPARISON: Dict[str, Dict[str, str]] = {
    "SGD (stochastic)": {
        "method": "gradient descent with noise",
        "randomness": "seeded pseudo-random or truly stochastic",
        "verifiability": "not reproducible without fixed seed",
        "output": "floating-point weights (~GBs)",
    },
    "PR #44 constraint propagation": {
        "method": "constructive enumeration over ℕ",
        "randomness": "none",
        "verifiability": "hash-verifiable, byte-identical",
        "output": "Natural number assignments (~bytes)",
    },
}

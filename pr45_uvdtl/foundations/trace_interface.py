# pr45_uvdtl/foundations/trace_interface.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section I.2 — Explainable Arithmetic Interface
#
# Every non-trivial transformation must expose:
#   trace(operation_id) → finite sequence of primitive steps
#
# Primitive steps allowed:
#   - successor
#   - zero_test
#   - bounded_recursion
#   - tuple_construction
#   - projection
#
# Traces are: finite, deterministic, recomputable.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence


# ---------------------------------------------------------------------------
# Primitive Step Types
# ---------------------------------------------------------------------------

PRIMITIVE_STEPS = frozenset([
    "successor",
    "zero_test",
    "bounded_recursion",
    "tuple_construction",
    "projection",
])


@dataclass(frozen=True)
class PrimitiveStep:
    """A single primitive computation step."""
    kind: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.kind not in PRIMITIVE_STEPS:
            raise ValueError(f"Illegal primitive step: {self.kind!r}")


# ---------------------------------------------------------------------------
# Trace
# ---------------------------------------------------------------------------

@dataclass
class Trace:
    """
    A finite, ordered sequence of primitive steps for one operation.
    Deterministic and recomputable from the same inputs.
    """
    operation_id: str
    steps: List[PrimitiveStep] = field(default_factory=list)

    def append(self, step: PrimitiveStep) -> None:
        self.steps.append(step)

    def is_finite(self) -> bool:
        """A Trace is always finite (Python list is bounded)."""
        return True

    def recompute(self) -> List[PrimitiveStep]:
        """Return a deterministic copy of the step sequence."""
        return list(self.steps)

    def length(self) -> int:
        return len(self.steps)


# ---------------------------------------------------------------------------
# Traced Operations
# ---------------------------------------------------------------------------

def trace_successor(n: int) -> Trace:
    """Trace a single successor application: n → n+1."""
    t = Trace(operation_id="successor")
    t.append(PrimitiveStep("successor", f"succ({n}) = {n + 1}"))
    return t


def trace_zero_test(n: int) -> Trace:
    """Trace a zero test: is n == 0?"""
    t = Trace(operation_id="zero_test")
    t.append(PrimitiveStep("zero_test", f"is_zero({n}) = {n == 0}"))
    return t


def trace_add(a: int, b: int) -> Trace:
    """
    Trace addition a + b via bounded recursion.
    Each step applies 'successor' once; 'bounded_recursion' frames the loop.
    """
    t = Trace(operation_id=f"add({a},{b})")
    t.append(PrimitiveStep("bounded_recursion", f"add by recursion on {b} steps"))
    acc = a
    for _ in range(b):
        t.append(PrimitiveStep("successor", f"succ({acc}) = {acc + 1}"))
        acc += 1
    return t


def trace_tuple_construction(values: Sequence[int]) -> Trace:
    """Trace construction of a finite tuple."""
    t = Trace(operation_id="tuple_construction")
    t.append(PrimitiveStep("tuple_construction", f"tuple{tuple(values)}"))
    return t


def trace_projection(values: Sequence[int], index: int) -> Trace:
    """Trace projection of element `index` from a tuple."""
    t = Trace(operation_id=f"projection[{index}]")
    t.append(PrimitiveStep("projection", f"project({list(values)}, {index}) = {values[index]}"))
    return t


# ---------------------------------------------------------------------------
# Public trace() dispatcher
# ---------------------------------------------------------------------------

def trace(operation_id: str, **kwargs: int) -> Trace:
    """
    Dispatch to the correct trace function by operation_id.

    Supported operation_ids:
      "successor"          — requires kwarg n
      "zero_test"          — requires kwarg n
      "add"                — requires kwargs a, b
      "tuple_construction" — requires kwarg values (list)
      "projection"         — requires kwargs values (list), index
    """
    if operation_id == "successor":
        return trace_successor(kwargs["n"])
    if operation_id == "zero_test":
        return trace_zero_test(kwargs["n"])
    if operation_id == "add":
        return trace_add(kwargs["a"], kwargs["b"])
    if operation_id == "tuple_construction":
        return trace_tuple_construction(kwargs["values"])
    if operation_id == "projection":
        return trace_projection(kwargs["values"], kwargs["index"])
    raise ValueError(f"Unknown operation_id: {operation_id!r}")


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "Black-box neural operation": "No trace; non-auditable computation",
    "PR #45 trace_interface": (
        "Every operation produces a finite, deterministic, recomputable "
        "step sequence using only the five permitted primitive kinds"
    ),
}

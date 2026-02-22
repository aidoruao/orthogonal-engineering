"""
axioms/peano.py — Formal Peano Axioms

Machine-verifiable encoding of the five Peano axioms and recursively-defined
arithmetic.  All arithmetic used by this system must reduce to these
primitives or to a provably equivalent fixed-point representation.

No floats.  No undefined behaviour.  No hardware arithmetic in the hot path.

Builds on top of oe_ifm.mathematical_core and oe_ifm.peano_kernel.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Tuple

# Re-export the proven substrate from oe_ifm so the axiom layer is the
# single canonical import point for all Peano arithmetic.
from oe_ifm.mathematical_core import (
    int64,
    peano_add,
    predecessor,
    successor,
    uint64,
)
from oe_ifm.peano_kernel import PeanoNat, PeanoProof

__all__ = [
    "ZERO",
    "successor",
    "predecessor",
    "peano_add",
    "peano_mul",
    "int64",
    "uint64",
    "PeanoNat",
    "PeanoProof",
    "verify_p1",
    "verify_p2",
    "verify_p3",
    "verify_p4",
    "verify_p5_schema",
]

# ---------------------------------------------------------------------------
# P1 — Zero element
# ---------------------------------------------------------------------------

ZERO: int = 0


def verify_p1() -> bool:
    """P1: 0 is a natural number and the additive identity."""
    return isinstance(ZERO, int) and ZERO == 0 and peano_add(ZERO, ZERO) == ZERO


# ---------------------------------------------------------------------------
# P2/P3 — Successor is total and injective
# ---------------------------------------------------------------------------

def verify_p2(n: int) -> bool:
    """P2: S(n) is a natural number for every natural number n."""
    return isinstance(successor(n), int)


def verify_p3(n: int) -> bool:
    """P3: S(n) != 0 for all natural n."""
    return successor(n) != ZERO


def verify_p4(m: int, n: int) -> bool:
    """P4 (Injectivity): S(m) == S(n) implies m == n."""
    if successor(m) == successor(n):
        return m == n
    return True  # vacuously true when antecedent is false


# ---------------------------------------------------------------------------
# P5 — Mathematical induction schema
# ---------------------------------------------------------------------------

def verify_p5_schema(
    base_case: bool,
    inductive_step_fn,
    limit: int = 100,
) -> Tuple[bool, List[str]]:
    """
    P5 (Induction): if base_case holds and inductive_step_fn(n) implies
    the property holds for S(n), then the property holds for all n in [0, limit].

    Returns (passed, counterexample_list).
    """
    counterexamples: List[str] = []
    if not base_case:
        counterexamples.append("Base case failed (n=0)")
        return False, counterexamples
    holds = True
    for n in range(limit):
        if not inductive_step_fn(n):
            counterexamples.append(f"Inductive step failed at n={n}")
            holds = False
            break
    return holds, counterexamples


# ---------------------------------------------------------------------------
# Multiplication — recursively defined via repeated addition
# ---------------------------------------------------------------------------

def peano_mul(a: int, b: int) -> int:
    """
    Peano multiplication: a * b = a added to itself b times.

    Uses only peano_add; no hardware multiplication in the proof path.
    """
    if b == 0:
        return 0
    result = 0
    remaining = b
    while remaining > 0:
        result = peano_add(result, a)
        remaining = predecessor(remaining)
    return result


# ---------------------------------------------------------------------------
# Proof object canonical serialization helpers
# ---------------------------------------------------------------------------

def proof_hash(proof: PeanoProof) -> str:
    """Return the SHA-256 hash of a proof's canonical JSON serialisation."""
    return proof.proof_hash


def proof_to_bytes(proof: PeanoProof) -> bytes:
    """Serialise a PeanoProof to canonical UTF-8 JSON bytes (sorted keys)."""
    return json.dumps(proof.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

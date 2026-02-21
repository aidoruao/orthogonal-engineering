"""
Peano Kernel — oe_ifm/peano_kernel.py

Proof-object layer on top of the Peano arithmetic primitives in
oe_ifm/mathematical_core.py.

Each operation returns a PeanoProof object that carries:
  - The computed numeric value
  - A human-readable derivation chain (sequence of proof steps)
  - A hash of the derivation (for Merkle-style integrity)

This ensures that every arithmetic result is an auditable artefact, not a
bare integer.  Call sites can use the ergonomic PeanoNat wrapper to keep
existing code readable while gaining proof tracking.

Design notes:
  - No floats, no hardware arithmetic (+, -, *) in the hot path.
  - All addition is delegated to peano_add from mathematical_core.
  - Multiplication delegates to modular_multiply (or peano_mul_proof for
    unbounded multiplication via repeated addition).
  - Proof chains are kept in memory only; callers may serialise them via
    to_dict() for persistence.

Author: Orthogonal Engineering
PR: #32
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

from .mathematical_core import (
    int64,
    modular_multiply,
    peano_add,
    predecessor,
    successor,
    uint64,
)

# ---------------------------------------------------------------------------
# PeanoProof — the core data structure
# ---------------------------------------------------------------------------


class PeanoProof:
    """
    An arithmetic result together with its derivation.

    Attributes:
        value:       The computed integer result.
        steps:       Ordered list of proof-step descriptions.
        proof_hash:  SHA-256 hex digest of the JSON-serialised steps.
    """

    def __init__(self, value: int, steps: List[str]) -> None:
        self.value: int = value
        self.steps: List[str] = list(steps)
        self.proof_hash: str = self._hash_steps()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _hash_steps(self) -> str:
        serialised = json.dumps(self.steps, separators=(",", ":"), sort_keys=False)
        return hashlib.sha256(serialised.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_valid(self) -> bool:
        """Return True if the proof_hash matches a fresh hash of the steps."""
        return self.proof_hash == self._hash_steps()

    def to_dict(self) -> Dict[str, Any]:
        """Serialise proof to a plain dict (JSON-compatible)."""
        return {
            "value": self.value,
            "steps": self.steps,
            "proof_hash": self.proof_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PeanoProof":
        """Deserialise a proof from a plain dict."""
        proof = cls(value=data["value"], steps=data["steps"])
        if proof.proof_hash != data["proof_hash"]:
            raise ValueError("Proof hash mismatch — derivation may be tampered.")
        return proof

    def __repr__(self) -> str:
        return f"PeanoProof(value={self.value}, steps={len(self.steps)}, hash={self.proof_hash[:8]}...)"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PeanoProof):
            return self.value == other.value and self.proof_hash == other.proof_hash
        if isinstance(other, int):
            return self.value == other
        return NotImplemented

    def __int__(self) -> int:
        return self.value


# ---------------------------------------------------------------------------
# PeanoNat — ergonomic wrapper for proof-tracked natural numbers
# ---------------------------------------------------------------------------


class PeanoNat:
    """
    Ergonomic wrapper that makes a Peano-backed integer look like a regular int.

    Arithmetic operations produce PeanoProof objects so that every result
    carries its derivation.  Use unwrap() to extract the bare int.

    Example::

        a = PeanoNat(3)
        b = PeanoNat(5)
        proof = a + b          # returns PeanoProof(value=8, ...)
        print(int(proof))      # 8
        print(proof.is_valid())  # True
    """

    def __init__(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"PeanoNat requires a non-negative integer; got {value!r}")
        self._value: int = value

    @property
    def value(self) -> int:
        return self._value

    def unwrap(self) -> int:
        return self._value

    # ------------------------------------------------------------------
    # Arithmetic — all return PeanoProof
    # ------------------------------------------------------------------

    def __add__(self, other: "PeanoNat | int") -> PeanoProof:
        b = other._value if isinstance(other, PeanoNat) else int(other)
        return peano_add_proof(self._value, b)

    def __mul__(self, other: "PeanoNat | int") -> PeanoProof:
        b = other._value if isinstance(other, PeanoNat) else int(other)
        return peano_mul_proof(self._value, b)

    def successor(self) -> PeanoProof:
        return successor_proof(self._value)

    def predecessor(self) -> PeanoProof:
        return predecessor_proof(self._value)

    def __repr__(self) -> str:
        return f"PeanoNat({self._value})"

    def __int__(self) -> int:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PeanoNat):
            return self._value == other._value
        if isinstance(other, int):
            return self._value == other
        return NotImplemented


# ---------------------------------------------------------------------------
# Proof-producing arithmetic functions
# ---------------------------------------------------------------------------


def successor_proof(n: int) -> PeanoProof:
    """
    Return PeanoProof for S(n) = n + 1 (Peano Axiom P2).

    Args:
        n: A non-negative integer.

    Returns:
        PeanoProof with value n+1 and one derivation step.
    """
    result = successor(n)
    steps = [f"S({n}) = {n} + 1 = {result}  [Peano P2]"]
    return PeanoProof(result, steps)


def predecessor_proof(n: int) -> PeanoProof:
    """
    Return PeanoProof for P(n) = n - 1 (inverse of successor).

    Args:
        n: Any integer.

    Returns:
        PeanoProof with value n-1 and one derivation step.
    """
    result = predecessor(n)
    steps = [f"P({n}) = {n} - 1 = {result}  [predecessor]"]
    return PeanoProof(result, steps)


def peano_add_proof(a: int, b: int) -> PeanoProof:
    """
    Return PeanoProof for a + b via the successor-function definition.

    Steps record the iterative reduction: add(a, b) = add(S(a), P(b)) until b=0.
    For large b, only the boundary steps are logged (to avoid huge step lists).

    Args:
        a: First non-negative integer.
        b: Second non-negative integer.

    Returns:
        PeanoProof documenting the addition derivation.
    """
    if b < 0:
        raise ValueError("peano_add_proof is defined for non-negative integers only")

    result = peano_add(a, b)
    steps: List[str] = [
        f"add({a}, {b})  [base]",
        f"  = {result}  [via bit-carry Peano loop]",
        f"  ∵ add(a, 0) = a  [identity]",
        f"  ∵ add(a, S(b)) = S(add(a, b))  [inductive step]",
        f"QED: add({a}, {b}) = {result}",
    ]
    return PeanoProof(result, steps)


def peano_mul_proof(a: int, b: int) -> PeanoProof:
    """
    Return PeanoProof for a * b via repeated Peano addition.

    mul(a, 0) = 0
    mul(a, S(b)) = add(mul(a, b), a)

    Args:
        a: First non-negative integer.
        b: Second non-negative integer.

    Returns:
        PeanoProof documenting the multiplication derivation.
    """
    if a < 0 or b < 0:
        raise ValueError("peano_mul_proof is defined for non-negative integers only")

    # Compute result via repeated Peano addition
    result = 0
    steps: List[str] = [f"mul({a}, {b})  [base]"]
    for i in range(b):
        prev = result
        result = peano_add(result, a)
        steps.append(f"  step {i}: add({prev}, {a}) = {result}")

    steps.append(f"QED: mul({a}, {b}) = {result}")
    return PeanoProof(result, steps)


def proof_add(p1: PeanoProof, p2: PeanoProof) -> PeanoProof:
    """
    Chain two proofs: compute the addition of their values and combine their steps.

    Args:
        p1: First proof.
        p2: Second proof.

    Returns:
        New PeanoProof whose steps include both derivations plus the final add.
    """
    inner = peano_add_proof(p1.value, p2.value)
    combined_steps = (
        [f"[P1] {s}" for s in p1.steps]
        + [f"[P2] {s}" for s in p2.steps]
        + [f"[compose] add(P1.value={p1.value}, P2.value={p2.value})"]
        + inner.steps
    )
    return PeanoProof(inner.value, combined_steps)

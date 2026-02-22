"""
axioms/logic.py — Propositional & First-Order Logic Core

Implements:
  - Propositional logic connectives
  - Inference rules (Modus Ponens, Universal Instantiation, Induction)
  - Proof object canonical serialisation
  - Proof hash (SHA-256)
  - Merkle root over a proof DAG

Every invariant in the repository is representable as a ProofObject.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Tuple

from oe_ifm.mathematical_core import (
    bool_and,
    bool_iff,
    bool_implies,
    bool_not,
    bool_or,
)

__all__ = [
    "ProofObject",
    "modus_ponens",
    "universal_instantiation",
    "induction_rule",
    "merkle_root_over_proofs",
]

# ---------------------------------------------------------------------------
# ProofObject — canonical proof node
# ---------------------------------------------------------------------------


class ProofObject:
    """
    A single proof node in the proof DAG.

    Attributes:
        rule:       Name of the inference rule applied.
        premises:   List of premise descriptions or sub-ProofObjects.
        conclusion: The derived conclusion (string).
        proof_hash: SHA-256 of the canonical JSON serialisation.
    """

    def __init__(
        self,
        rule: str,
        premises: List[Any],
        conclusion: str,
    ) -> None:
        self.rule = rule
        self.premises = premises
        self.conclusion = conclusion
        self.proof_hash: str = self._compute_hash()

    def _compute_hash(self) -> str:
        serialised = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialised.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        def _premise(p: Any) -> Any:
            return p.to_dict() if isinstance(p, ProofObject) else str(p)

        return {
            "rule": self.rule,
            "premises": [_premise(p) for p in self.premises],
            "conclusion": self.conclusion,
        }

    def is_valid(self) -> bool:
        """Re-compute hash and compare to stored value."""
        return self._compute_hash() == self.proof_hash

    def __repr__(self) -> str:
        return f"ProofObject(rule={self.rule!r}, conclusion={self.conclusion!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProofObject) and self.proof_hash == other.proof_hash


# ---------------------------------------------------------------------------
# Propositional logic
# ---------------------------------------------------------------------------

def prop_and(p: bool, q: bool) -> bool:
    return bool_and(p, q)


def prop_or(p: bool, q: bool) -> bool:
    return bool_or(p, q)


def prop_not(p: bool) -> bool:
    return bool_not(p)


def prop_implies(p: bool, q: bool) -> bool:
    return bool_implies(p, q)


def prop_iff(p: bool, q: bool) -> bool:
    return bool_iff(p, q)


# ---------------------------------------------------------------------------
# Inference rules
# ---------------------------------------------------------------------------

def modus_ponens(
    p: bool,
    p_implies_q: bool,
    p_label: str = "P",
    q_label: str = "Q",
) -> Tuple[bool, ProofObject]:
    """
    Modus Ponens: from P and (P -> Q), derive Q.

    Returns (conclusion_value, proof_object).
    """
    conclusion_value = p and p_implies_q
    proof = ProofObject(
        rule="ModusPonens",
        premises=[f"{p_label} is {p}", f"({p_label} -> {q_label}) is {p_implies_q}"],
        conclusion=f"{q_label} is {conclusion_value}",
    )
    return conclusion_value, proof


def universal_instantiation(
    predicate: Callable[[Any], bool],
    witness: Any,
    domain_label: str = "x",
) -> Tuple[bool, ProofObject]:
    """
    Universal Instantiation: from ∀x P(x), derive P(witness).

    Returns (result, proof_object).
    """
    result = predicate(witness)
    proof = ProofObject(
        rule="UniversalInstantiation",
        premises=[f"∀{domain_label} P({domain_label})", f"witness={witness!r}"],
        conclusion=f"P({witness!r}) = {result}",
    )
    return result, proof


def induction_rule(
    base_predicate: bool,
    inductive_fn: Callable[[int], bool],
    limit: int,
    property_label: str = "P",
) -> Tuple[bool, ProofObject]:
    """
    Mathematical Induction: verify base case and inductive step up to limit.

    Returns (all_hold, proof_object).
    """
    if not base_predicate:
        proof = ProofObject(
            rule="Induction",
            premises=[f"{property_label}(0) = False"],
            conclusion=f"Induction failed at base case",
        )
        return False, proof

    failed_at: Optional[int] = None
    for n in range(limit):
        if not inductive_fn(n):
            failed_at = n
            break

    if failed_at is not None:
        proof = ProofObject(
            rule="Induction",
            premises=[
                f"{property_label}(0) = True",
                f"Inductive step failed at n={failed_at}",
            ],
            conclusion=f"Induction failed at n={failed_at}",
        )
        return False, proof

    proof = ProofObject(
        rule="Induction",
        premises=[
            f"{property_label}(0) = True",
            f"∀n ∈ [0,{limit}): {property_label}(n) → {property_label}(S(n))",
        ],
        conclusion=f"{property_label}(n) holds for all n ∈ [0,{limit}]",
    )
    return True, proof


# ---------------------------------------------------------------------------
# Merkle root over proof DAG
# ---------------------------------------------------------------------------

def _hash_leaf(proof: ProofObject) -> bytes:
    return hashlib.sha256(b"\x00" + proof.proof_hash.encode("utf-8")).digest()


def _hash_internal(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def merkle_root_over_proofs(proofs: List[ProofObject]) -> str:
    """
    Compute a binary Merkle root over an ordered list of ProofObjects.

    Leaves are ordered by their proof_hash (deterministic).
    Returns the root hash as a hex string, or the empty-set hash if empty.
    """
    if not proofs:
        return hashlib.sha256(b"EMPTY_PROOF_SET").hexdigest()

    # Sort by hash for canonical ordering
    sorted_proofs = sorted(proofs, key=lambda p: p.proof_hash)
    layer: List[bytes] = [_hash_leaf(p) for p in sorted_proofs]

    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])  # Duplicate last leaf for odd count
        next_layer: List[bytes] = []
        for i in range(0, len(layer), 2):
            next_layer.append(_hash_internal(layer[i], layer[i + 1]))
        layer = next_layer

    return layer[0].hex()

"""
axioms/yeshua_axioms.py — Yeshua Standard Enforcement Axioms

Defines the eight invariants of the Yeshua Standard:
  1. Every truth is derivable from axioms.
  2. Every derivation is reproducible.
  3. Every mutation is re-verifiable.
  4. No authority without proof.
  5. No hidden state.
  6. No unverifiable dependency.
  7. No economic gatekeeping.
  8. Every artifact is hash-anchored.

These become the enforcement kernel.  Each claim carries:
  - Source (where the claim originates)
  - Derivation path (ProofObject chain)
  - Hash commitment (SHA-256)

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from axioms.logic import ProofObject

__all__ = [
    "YeshuaClaim",
    "YeshuaViolation",
    "verify_yeshua_standard",
    "YESHUA_AXIOMS",
]

# ---------------------------------------------------------------------------
# The eight axioms as human-readable + machine-checkable constants
# ---------------------------------------------------------------------------

YESHUA_AXIOMS: Dict[int, str] = {
    1: "Every truth is derivable from axioms.",
    2: "Every derivation is reproducible.",
    3: "Every mutation is re-verifiable.",
    4: "No authority without proof.",
    5: "No hidden state.",
    6: "No unverifiable dependency.",
    7: "No economic gatekeeping.",
    8: "Every artifact is hash-anchored.",
}


# ---------------------------------------------------------------------------
# YeshuaClaim — a claim that must satisfy all eight axioms
# ---------------------------------------------------------------------------


@dataclass
class YeshuaClaim:
    """
    A claim that participates in the Yeshua enforcement substrate.

    Attributes:
        source:          Where this claim originates (file path or module name).
        statement:       Human-readable claim text.
        derivation:      ProofObject representing the derivation.
        hash_commitment: SHA-256 of (source + statement + proof_hash).
    """

    source: str
    statement: str
    derivation: ProofObject

    def __post_init__(self) -> None:
        self.hash_commitment: str = self._compute_commitment()

    def _compute_commitment(self) -> str:
        payload = json.dumps(
            {
                "source": self.source,
                "statement": self.statement,
                "proof_hash": self.derivation.proof_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "statement": self.statement,
            "derivation": self.derivation.to_dict(),
            "hash_commitment": self.hash_commitment,
        }

    def is_reproducible(self) -> bool:
        """Axiom 2: re-derive the commitment and verify it matches."""
        return self._compute_commitment() == self.hash_commitment

    def is_hash_anchored(self) -> bool:
        """Axiom 8: commitment must be a 64-char hex SHA-256."""
        return len(self.hash_commitment) == 64 and all(
            c in "0123456789abcdef" for c in self.hash_commitment
        )


# ---------------------------------------------------------------------------
# YeshuaViolation — raised when a claim violates the standard
# ---------------------------------------------------------------------------


class YeshuaViolation(Exception):
    """Raised when a YeshuaClaim violates one of the eight Yeshua axioms."""

    def __init__(self, axiom_number: int, claim: YeshuaClaim, detail: str) -> None:
        self.axiom_number = axiom_number
        self.claim = claim
        self.detail = detail
        axiom_text = YESHUA_AXIOMS.get(axiom_number, "Unknown axiom")
        super().__init__(
            f"YeshuaViolation [Axiom {axiom_number}]: {axiom_text} — {detail}"
        )


# ---------------------------------------------------------------------------
# Enforcement kernel
# ---------------------------------------------------------------------------


def verify_yeshua_standard(claim: YeshuaClaim) -> List[YeshuaViolation]:
    """
    Verify a claim against all eight Yeshua axioms.

    Returns a (possibly empty) list of violations.
    An empty list means the claim satisfies the Yeshua Standard.
    """
    violations: List[YeshuaViolation] = []

    # Axiom 1: derivation must exist (truth derivable from axioms)
    if claim.derivation is None:
        violations.append(YeshuaViolation(1, claim, "No derivation attached"))

    # Axiom 2: derivation must be reproducible
    if not claim.is_reproducible():
        violations.append(
            YeshuaViolation(2, claim, "Hash commitment does not reproduce")
        )

    # Axiom 3: proof object must pass internal re-verification
    if claim.derivation is not None and not claim.derivation.is_valid():
        violations.append(
            YeshuaViolation(3, claim, "ProofObject hash does not verify internally")
        )

    # Axiom 4: source must be non-empty (authority must be declared)
    if not claim.source or not claim.source.strip():
        violations.append(
            YeshuaViolation(4, claim, "Source is empty — no declared authority")
        )

    # Axiom 5: statement must be non-empty (no hidden state)
    if not claim.statement or not claim.statement.strip():
        violations.append(YeshuaViolation(5, claim, "Statement is empty — hidden state"))

    # Axiom 6: derivation rule must be declared (verifiable dependency)
    if claim.derivation is not None and not claim.derivation.rule:
        violations.append(
            YeshuaViolation(6, claim, "Derivation rule is empty — unverifiable dependency")
        )

    # Axiom 7: statement must not contain economic gatekeeping keywords
    monetization_keywords = {"paywall", "subscription", "license fee", "proprietary", "paid"}
    if any(kw in claim.statement.lower() for kw in monetization_keywords):
        violations.append(
            YeshuaViolation(7, claim, "Statement contains economic gatekeeping keyword")
        )

    # Axiom 8: hash commitment must be a valid SHA-256 hex digest
    if not claim.is_hash_anchored():
        violations.append(
            YeshuaViolation(8, claim, "Hash commitment is not a valid SHA-256 digest")
        )

    return violations

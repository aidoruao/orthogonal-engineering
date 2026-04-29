"""Intent Capture - pr46_agape_witness/relational/intent_capture.py"""
# pr46_agape_witness/relational/intent_capture.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Intent capture / witness: canonicalized declarations of intent ("why").
# Human-readable and machine-verifiable.
# All entries are deterministic (sorted keys, SHA-256 hash).

from __future__ import annotations

from dataclasses import dataclass

from pr46_agape_witness.util.canonical import canonical_str
from pr46_agape_witness.util.hashing import sha256_hash


@dataclass(frozen=True)
class IntentDeclaration:
    """
    A witnessed, canonicalized declaration of intent.

    Fields:
      agent_id      — agent making the declaration.
      intent        — human-readable description of the "why".
      context       — optional machine-readable context (str).
      timestamp     — ISO-8601, injected (deterministic).
      canonical_json — canonical JSON string of the declaration.
      intent_hash   — SHA-256 of the canonical JSON.
    """
    agent_id: str
    intent: str
    context: str
    timestamp: str
    canonical_json: str
    intent_hash: str

    @classmethod
    def create(
        cls,
        agent_id: str,
        intent: str,
        context: str,
        timestamp: str,
    ) -> "IntentDeclaration":
        """
        Factory: produce a canonicalized IntentDeclaration.
        Raises ValueError if intent is empty.
        """
        if not intent:
            raise ValueError("Intent declaration requires a non-empty intent")
        doc = {
            "agent_id": agent_id,
            "context": context,
            "intent": intent,
            "timestamp": timestamp,
        }
        c_json = canonical_str(doc)
        intent_hash = sha256_hash(doc)
        return cls(
            agent_id=agent_id,
            intent=intent,
            context=context,
            timestamp=timestamp,
            canonical_json=c_json,
            intent_hash=intent_hash,
        )

    def verify(self) -> bool:
        """
        Verify that canonical_json and intent_hash are consistent.
        Raises ValueError on mismatch.
        """
        doc = {
            "agent_id": self.agent_id,
            "context": self.context,
            "intent": self.intent,
            "timestamp": self.timestamp,
        }
        expected_hash = sha256_hash(doc)
        expected_json = canonical_str(doc)
        if self.intent_hash != expected_hash:
            raise ValueError(
                f"IntentDeclaration hash mismatch: "
                f"computed={expected_hash!r} stored={self.intent_hash!r}"
            )
        if self.canonical_json != expected_json:
            raise ValueError(
                f"IntentDeclaration canonical_json mismatch"
            )
        return True

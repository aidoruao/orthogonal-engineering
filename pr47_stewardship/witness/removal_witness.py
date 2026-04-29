"""Removal Witness - pr47_stewardship/witness/removal_witness.py"""
# pr47_stewardship/witness/removal_witness.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# RemovalWitness: append-only ledger of boundary transitions.
#
# Each entry records *that* an artifact transitioned without exposing
# *what* the artifact contained.  Reason codes are opaque so that
# future readers cannot infer sensitivity categories from the log.

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import List


# Genesis constant for the removal witness chain.
REMOVAL_GENESIS_HASH: str = hashlib.sha256(b"pr47_removal_genesis").hexdigest()


@dataclass(frozen=True)
class RemovalEntry:
    """
    One entry in the removal witness ledger.

    Fields:
      content_hash  — SHA-256 of the transitioned artifact.
      reason_code   — opaque code, e.g. "R1".
      consent_hash  — SHA-256 of the authorising consent record.
      witnessed_by  — module identifier ("pr47").
      previous_hash — hash of the preceding ledger entry (chain link).
    """
    content_hash: str
    reason_code: str
    consent_hash: str
    witnessed_by: str
    previous_hash: str

    def canonical_bytes(self) -> bytes:
        """Deterministic serialisation (sorted keys, UTF-8)."""
        doc = {
            "consent_hash": self.consent_hash,
            "content_hash": self.content_hash,
            "previous_hash": self.previous_hash,
            "reason_code": self.reason_code,
            "witnessed_by": self.witnessed_by,
        }
        return json.dumps(doc, sort_keys=True, ensure_ascii=True).encode("utf-8")

    def entry_hash(self) -> str:
        """SHA-256 of the canonical entry bytes."""
        # TODO: Expand entry_hash() - stub detected by Yeshua Agent
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class RemovalWitness:
    """
    Append-only ledger recording boundary transitions.

    The chain structure mirrors PR #45 WitnessChain:
    each entry links to its predecessor, making tampering detectable.
    """

    def __init__(self) -> None:
        self._entries: List[RemovalEntry] = []
        self._chain_hash: str = REMOVAL_GENESIS_HASH

    def record_transition(
        self,
        content_hash: str,
        reason_code: str,
        consent_hash: str,
        witnessed_by: str = "pr47",
    ) -> RemovalEntry:
        """
        Append one boundary transition to the ledger.

        Parameters:
          content_hash — SHA-256 of the artifact before transition.
          reason_code  — opaque code (e.g. "R1").
          consent_hash — SHA-256 of the authorising consent record.
          witnessed_by — identifier of the witnessing module.

        Returns the immutable RemovalEntry.
        """
        entry = RemovalEntry(
            content_hash=content_hash,
            reason_code=reason_code,
            consent_hash=consent_hash,
            witnessed_by=witnessed_by,
            previous_hash=self._chain_hash,
        )
        self._entries.append(entry)
        self._chain_hash = entry.entry_hash()
        return entry

    def has_entry_for_hash(self, content_hash: str) -> bool:
        """Return True if any entry records a transition for content_hash."""
        return any(e.content_hash == content_hash for e in self._entries)

    def entry_for_hash(self, content_hash: str) -> RemovalEntry:
        """
        Return the first entry matching content_hash.
        Raises KeyError if not found.
        """
        for e in self._entries:
            if e.content_hash == content_hash:
                return e
        raise KeyError(f"No removal entry for content_hash={content_hash!r}")

    @property
    def chain_hash(self) -> str:
        """Current chain hash after all appended entries."""
        return self._chain_hash

    @property
    def length(self) -> int:
        return len(self._entries)

    def entries(self) -> List[RemovalEntry]:
        """Return a copy of all entries in append order."""
        return list(self._entries)

    def verify_integrity(self) -> bool:
        """
        Recompute the chain hash from genesis and compare to stored value.
        Raises ValueError on detected tampering.
        """
        h = REMOVAL_GENESIS_HASH
        for entry in self._entries:
            recomputed = RemovalEntry(
                content_hash=entry.content_hash,
                reason_code=entry.reason_code,
                consent_hash=entry.consent_hash,
                witnessed_by=entry.witnessed_by,
                previous_hash=h,
            ).entry_hash()
            h = recomputed
        if h != self._chain_hash:
            raise ValueError(
                f"RemovalWitness integrity violation: "
                f"recomputed={h!r} stored={self._chain_hash!r}"
            )
        return True

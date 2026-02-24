# pr47_stewardship/witness/consent_log.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# ConsentLog: append-only log of human authorisations for boundary transitions.
#
# Every transition requires explicit human consent.  Each consent record is
# hashed; the hash is threaded through every TransitionEntry and RemovalEntry
# so the audit trail links back to the human decision.

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ConsentRecord:
    """
    One human authorisation covering one or more artifact transitions.

    Fields:
      authoriser    — opaque identifier for the human who granted consent.
      scope         — list of content_hash values covered by this consent.
      action        — the approved action ("move_local", "encrypt_local", etc.).
      timestamp     — injected ISO-8601 string.
      consent_hash  — SHA-256 of the canonical consent record (self-referential
                      hash is computed *without* the consent_hash field).
    """
    authoriser: str
    scope: List[str]
    action: str
    timestamp: str
    consent_hash: str

    @classmethod
    def create(
        cls,
        authoriser: str,
        scope: List[str],
        action: str,
        timestamp: str,
    ) -> "ConsentRecord":
        """Factory: compute consent_hash from the other fields."""
        sorted_scope = sorted(scope)
        doc = {
            "action": action,
            "authoriser": authoriser,
            "scope": sorted_scope,
            "timestamp": timestamp,
        }
        consent_hash = hashlib.sha256(
            json.dumps(doc, sort_keys=True, ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        return cls(
            authoriser=authoriser,
            scope=sorted_scope,
            action=action,
            timestamp=timestamp,
            consent_hash=consent_hash,
        )

    def covers(self, content_hash: str) -> bool:
        """Return True if this consent covers content_hash."""
        return content_hash in self.scope


class ConsentLog:
    """Append-only log of ConsentRecords."""

    def __init__(self) -> None:
        self._records: List[ConsentRecord] = []

    def append(self, record: ConsentRecord) -> None:
        """Append a consent record to the log."""
        self._records.append(record)

    def records(self) -> List[ConsentRecord]:
        """Return a copy of all records in append order."""
        return list(self._records)

    def has_consent_for(self, content_hash: str) -> bool:
        """Return True if any record covers content_hash."""
        return any(r.covers(content_hash) for r in self._records)

    def consent_hash_for(self, content_hash: str) -> str:
        """
        Return the consent_hash of the first record that covers content_hash.
        Raises KeyError if no record covers content_hash.
        """
        for r in self._records:
            if r.covers(content_hash):
                return r.consent_hash
        raise KeyError(
            f"No consent record covers content_hash={content_hash!r}"
        )

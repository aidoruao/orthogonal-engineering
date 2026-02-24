# pr47_stewardship/movement/witness_mover.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# WitnessMover: moves artifacts across boundaries while recording a
# deterministic witness entry for every transition.
#
# Invariants preserved:
#   - NoSilentTransition: every move produces a WitnessEntry before returning.
#   - Provenance: content_hash computed before the move, never after.
#   - Consent: every entry references the active consent_hash.

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pr47_stewardship.movement.hash_preserver import sha256_file, sha256_bytes


@dataclass(frozen=True)
class TransitionEntry:
    """
    Witness record for one boundary transition.

    Fields:
      operation     — always "boundary_transition".
      content_hash  — SHA-256 of the artifact *before* the move.
      from_path     — source path (opaque for encrypted boundary).
      to_boundary   — destination boundary name.
      to_path       — destination path, or None for encrypted/delete.
      timestamp     — injected ISO-8601 string (never system clock).
      consent_hash  — SHA-256 of the authorising consent record.
    """
    operation: str
    content_hash: str
    from_path: Optional[str]
    to_boundary: str
    to_path: Optional[str]
    timestamp: str
    consent_hash: str

    def canonical_bytes(self) -> bytes:
        """Deterministic serialisation (sorted keys, UTF-8)."""
        doc = {
            "consent_hash": self.consent_hash,
            "content_hash": self.content_hash,
            "from_path": self.from_path,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "to_boundary": self.to_boundary,
            "to_path": self.to_path,
        }
        return json.dumps(doc, sort_keys=True, ensure_ascii=True).encode("utf-8")

    def entry_hash(self) -> str:
        """SHA-256 of the canonical entry bytes."""
        return sha256_bytes(self.canonical_bytes())


class WitnessMover:
    """
    Records boundary transitions without executing filesystem operations.

    Filesystem operations are intentionally separated so this class remains
    pure/testable and the caller controls when (and whether) files move.

    Parameters:
      consent_hash — SHA-256 of the human-signed consent document that
                     authorises the current batch of transitions.
    """

    def __init__(self, consent_hash: str) -> None:
        self._consent_hash = consent_hash
        self._entries: list[TransitionEntry] = []

    @property
    def consent_hash(self) -> str:
        return self._consent_hash

    def record_transition(
        self,
        content_hash: str,
        from_path: Optional[str],
        to_boundary: str,
        to_path: Optional[str],
        timestamp: str,
    ) -> TransitionEntry:
        """
        Record one boundary transition and append it to the internal log.

        Parameters:
          content_hash — pre-move SHA-256 of the artifact.
          from_path    — source relative path (None if already gone).
          to_boundary  — "local", "encrypted", or "delete_with_witness".
          to_path      — destination relative path, or None.
          timestamp    — injected ISO-8601 string.

        Returns the immutable TransitionEntry.
        """
        entry = TransitionEntry(
            operation="boundary_transition",
            content_hash=content_hash,
            from_path=from_path,
            to_boundary=to_boundary,
            to_path=to_path,
            timestamp=timestamp,
            consent_hash=self._consent_hash,
        )
        self._entries.append(entry)
        return entry

    def entries(self) -> list[TransitionEntry]:
        """Return a copy of all recorded transition entries in append order."""
        return list(self._entries)

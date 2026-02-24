# pr47_stewardship/witness/provenance_pointer.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# ProvenancePointer: opaque reference to the post-transition location of an
# artifact.  The pointer records *that* a file moved and a hash of its new
# location, but deliberately avoids encoding the raw destination path in any
# public log so that the public record reveals nothing about local storage
# layout.

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProvenancePointer:
    """
    Opaque reference to a post-transition artifact.

    Fields:
      content_hash      — SHA-256 of the original artifact.
      boundary          — destination boundary name ("local", "encrypted").
      location_hash     — SHA-256 of the destination path (opaque).
      timestamp         — injected ISO-8601 string.
    """
    content_hash: str
    boundary: str
    location_hash: str
    timestamp: str

    @classmethod
    def create(
        cls,
        content_hash: str,
        boundary: str,
        destination_path: Optional[str],
        timestamp: str,
    ) -> "ProvenancePointer":
        """
        Factory: derive location_hash from destination_path without
        storing the raw path in the pointer.
        """
        raw = (destination_path or "").encode("utf-8")
        location_hash = hashlib.sha256(raw).hexdigest()
        return cls(
            content_hash=content_hash,
            boundary=boundary,
            location_hash=location_hash,
            timestamp=timestamp,
        )

    def canonical_bytes(self) -> bytes:
        """Deterministic serialisation (sorted keys, UTF-8)."""
        doc = {
            "boundary": self.boundary,
            "content_hash": self.content_hash,
            "location_hash": self.location_hash,
            "timestamp": self.timestamp,
        }
        return json.dumps(doc, sort_keys=True, ensure_ascii=True).encode("utf-8")

    def pointer_hash(self) -> str:
        """SHA-256 of the canonical pointer bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

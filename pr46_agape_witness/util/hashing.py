# pr46_agape_witness/util/hashing.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Deterministic SHA-256 hashing utility.
# All hashes are computed over canonical_bytes (sorted-key, type-annotated JSON).

from __future__ import annotations

import hashlib
from typing import Any

from pr46_agape_witness.util.canonical import canonical_bytes


def sha256_hash(doc: Any) -> str:
    """
    Return the SHA-256 hex digest of the canonical encoding of doc.
    Deterministic: equal doc → equal hash.
    """
    return hashlib.sha256(canonical_bytes(doc)).hexdigest()


def sha256_raw(data: bytes) -> str:
    """Return the SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


# Genesis constant: hash of the empty agape witness chain
AGAPE_GENESIS_HASH: str = hashlib.sha256(b"agape_genesis").hexdigest()

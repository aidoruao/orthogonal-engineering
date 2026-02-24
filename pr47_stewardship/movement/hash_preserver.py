# pr47_stewardship/movement/hash_preserver.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# HashPreserver: computes deterministic SHA-256 hashes of files before
# any boundary transition so provenance is maintained even when content moves.

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: str | Path) -> str:
    """
    Return the SHA-256 hex digest of the file at path.

    Reads the file in binary mode in 64 KiB chunks to support large files
    without loading them entirely into memory.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return the SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()

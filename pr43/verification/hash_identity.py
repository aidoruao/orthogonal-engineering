# pr43/verification/hash_identity.py
# PR #43 — Orthogonal Parallel
# Standard: Yeshua
#
# Cross-platform byte identity layer.
# SHA-256 hashing of source files and directories.
# Sorted traversal ensures deterministic ordering.
# Same bytes → same hash on any platform.

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict


def sha256_bytes(data: bytes) -> str:
    """SHA-256 digest of raw bytes. Deterministic. Cross-platform."""
    return hashlib.sha256(data).hexdigest()


def sha256_str(text: str, encoding: str = "utf-8") -> str:
    """SHA-256 digest of a UTF-8 string."""
    return sha256_bytes(text.encode(encoding))


def hash_file(path: Path) -> str:
    """SHA-256 of a file's raw bytes."""
    return sha256_bytes(path.read_bytes())


def hash_directory(path: Path) -> Dict[str, str]:
    """
    Compute SHA-256 for every file under path.
    Sorted traversal guarantees deterministic ordering across platforms.
    """
    result: Dict[str, str] = {}
    for f in sorted(path.rglob("*")):
        if f.is_file():
            result[str(f.relative_to(path))] = hash_file(f)
    return result


def verify_equal(hash_a: Dict[str, str], hash_b: Dict[str, str]) -> bool:
    """
    Two hash manifests are equal iff they are structurally identical.
    Returns True iff both directories have identical content.
    """
    return hash_a == hash_b


def verify_reproducibility(
    build1: Dict[str, str],
    build2: Dict[str, str],
) -> bool:
    """
    Same source ⟹ identical build outputs.
    Raises ValueError with diff if any output differs.
    """
    if build1 == build2:
        return True
    diff = {
        k: (build1.get(k), build2.get(k))
        for k in set(build1) | set(build2)
        if build1.get(k) != build2.get(k)
    }
    raise ValueError(f"Build non-reproducible: {diff}")

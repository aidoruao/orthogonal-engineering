"""
merkle/global_merkle.py — Global Repository Merkle Root Generator

Constructs a global Merkle tree over all tracked source files and
writes the root to merkle/global_root.json.

Run as: python merkle/global_merkle.py

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).parent.parent
OUTPUT_FILE = Path(__file__).parent / "global_root.json"

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
SOURCE_EXTS = {
    ".py", ".js", ".ts", ".yaml", ".yml", ".json", ".md",
    ".txt", ".html", ".csv", ".sh",
}


def _git_ls_files() -> List[str]:
    try:
        out = subprocess.check_output(
            ["git", "ls-files"],
            cwd=REPO_ROOT, stderr=subprocess.DEVNULL, text=True,
        )
        return [ln for ln in out.splitlines() if ln.strip()]
    except Exception:
        return []


def _canonical_bytes(fpath: Path) -> bytes:
    """Read file, normalise line endings, encode as UTF-8."""
    try:
        content = fpath.read_text(encoding="utf-8", errors="replace")
        return content.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    except OSError:
        return b""


def _hash_leaf(content: bytes) -> str:
    return hashlib.sha256(b"\x00" + content).hexdigest()


def _hash_internal(left: str, right: str) -> str:
    return hashlib.sha256(b"\x01" + left.encode() + right.encode()).hexdigest()


def build_global_merkle() -> Tuple[str, int]:
    """
    Build a binary Merkle tree over all tracked source files.

    Leaves are sorted by their repo-relative path (UTF-8 lexicographic).
    Returns (root_hash, file_count).
    """
    tracked = _git_ls_files()
    leaves: List[Tuple[str, str]] = []  # (path, leaf_hash)

    for rel in sorted(tracked):
        fpath = REPO_ROOT / rel
        if not fpath.exists() or fpath.suffix not in SOURCE_EXTS:
            continue
        cb = _canonical_bytes(fpath)
        leaves.append((rel, _hash_leaf(cb)))

    if not leaves:
        return hashlib.sha256(b"EMPTY").hexdigest(), 0

    layer: List[str] = [h for _, h in leaves]

    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        next_layer: List[str] = []
        for i in range(0, len(layer), 2):
            next_layer.append(_hash_internal(layer[i], layer[i + 1]))
        layer = next_layer

    return layer[0], len(leaves)


def write_global_root() -> Dict:
    root_hash, file_count = build_global_merkle()
    depth = 0
    n = file_count
    while n > 1:
        n = (n + 1) // 2
        depth += 1

    result = {
        "file_count": file_count,
        "hash_algorithm": "SHA-256",
        "leaf_encoding": "SHA-256(0x00 || canonical_bytes)",
        "internal_encoding": "SHA-256(0x01 || left_hash_hex || right_hash_hex)",
        "tree_depth": depth,
        "root_hash": root_hash,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    return result


if __name__ == "__main__":
    result = write_global_root()
    print(json.dumps(result, indent=2, sort_keys=True))

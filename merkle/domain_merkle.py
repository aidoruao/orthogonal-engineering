"""merkle/domain_merkle.py — Per-Domain Merkle Root Generator.

For each domain in ``src/domains/``, constructs a binary Merkle tree
over all source files in that domain directory and writes the per-domain
roots to ``merkle/domain_roots.json``.

Run as: python merkle/domain_merkle.py

Standard: Yeshua / Glass-Box / Orthogonal Engineering
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = REPO_ROOT / "src" / "domains"
OUTPUT_FILE = Path(__file__).parent / "domain_roots.json"

SOURCE_EXTS = {
    ".py", ".json", ".yaml", ".yml", ".md", ".txt",
    ".html", ".csv",
}


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


def _build_merkle(leaves: List[str]) -> str:
    """Build binary Merkle tree from leaf hashes; return root hash."""
    if not leaves:
        return hashlib.sha256(b"EMPTY").hexdigest()

    layer = list(leaves)
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        next_layer: List[str] = []
        for i in range(0, len(layer), 2):
            next_layer.append(_hash_internal(layer[i], layer[i + 1]))
        layer = next_layer

    return layer[0]


def build_domain_merkle(domain_dir: Path) -> Tuple[str, int]:
    """Build a Merkle root for a single domain directory.

    Args:
        domain_dir: Path to a domain folder (e.g. ``src/domains/d_aerospace``).

    Returns:
        Tuple of (root_hash, file_count).

    Falsifies if: root_hash length is not 64 hex characters.
    """
    files = sorted(
        p
        for p in domain_dir.rglob("*")
        if p.is_file()
        and p.suffix in SOURCE_EXTS
        and "__pycache__" not in p.parts
    )
    leaf_hashes = [_hash_leaf(_canonical_bytes(f)) for f in files]
    return _build_merkle(leaf_hashes), len(files)


def build_all_domain_roots() -> Dict[str, dict]:
    """Build per-domain Merkle roots for all domains.

    Returns:
        Mapping of domain name → ``{root_hash, file_count}``.

    Falsifies if: any domain root_hash is not 64 hex characters.
    """
    results: Dict[str, dict] = {}

    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        root_hash, file_count = build_domain_merkle(domain_dir)
        results[domain_dir.name] = {
            "root_hash": root_hash,
            "file_count": file_count,
            "hash_algorithm": "SHA-256",
            "leaf_encoding": "SHA-256(0x00 || canonical_bytes)",
            "internal_encoding": "SHA-256(0x01 || left_hash_hex || right_hash_hex)",
        }

    return results


def write_domain_roots() -> Dict[str, dict]:
    """Compute and persist per-domain Merkle roots to ``merkle/domain_roots.json``.

    Returns:
        The mapping written to disk.

    Falsifies if: the output file is absent after this function returns.
    """
    results = build_all_domain_roots()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    data = write_domain_roots()
    domain_count = len(data)
    print(f"Generated Merkle roots for {domain_count} domains → {OUTPUT_FILE}")
    if "--json" in sys.argv:
        print(json.dumps(data, indent=2, sort_keys=True))

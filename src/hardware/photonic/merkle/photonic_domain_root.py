"""PHOTONIC Domain Merkle Root — Compute SHA-256 Merkle root of all files in
src/hardware/photonic/.

Category 17: Merkle Integration.

Leaf encoding: SHA-256(0x00 || canonical_bytes)
Internal encoding: SHA-256(0x01 || left_hash_hex || right_hash_hex)
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import List, Tuple

_repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from axioms.logic import ProofObject


def _sha256_leaf(data: bytes) -> str:
    """Leaf hash: SHA-256(0x00 || data)."""
    return hashlib.sha256(b"\x00" + data).hexdigest()


def _sha256_internal(left: str, right: str) -> str:
    """Internal hash: SHA-256(0x01 || left || right)."""
    payload = b"\x01" + bytes.fromhex(left) + bytes.fromhex(right)
    return hashlib.sha256(payload).hexdigest()


def _get_photonic_files() -> List[Path]:
    """Return sorted list of all files under src/hardware/photonic/."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    photonic_dir = repo_root / "src" / "hardware" / "photonic"
    files = sorted(p for p in photonic_dir.rglob("*") if p.is_file())
    return files


def _relative_path(path: Path) -> str:
    """Return path relative to repo root."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    return str(path.relative_to(repo_root))


def compute_photonic_domain_root() -> Tuple[bool, ProofObject, str, List[dict]]:
    """Compute Merkle root of the photonic domain.

    Returns (ok, proof_object, root_hash, file_records).

    Falsifies if: root_hash is not a 64-character hex string.
    falsifies_if: root_hash is not a 64-character hex string.
    """
    files = _get_photonic_files()
    leaves: List[str] = []
    records: List[dict] = []

    for path in files:
        data = path.read_bytes()
        leaf_hash = _sha256_leaf(data)
        leaves.append(leaf_hash)
        records.append(
            {
                "relative_path": str(path.relative_to(path.parent.parent.parent)),
                "size_bytes": len(data),
                "leaf_hash": leaf_hash,
            }
        )

    if not leaves:
        return False, ProofObject(
            conclusion="VIOLATION: no photonic files found",
            premises=[],
            rule="photonic_domain_root",
        ), "", []

    # Pad to power of 2
    while len(leaves) & (len(leaves) - 1) != 0:
        leaves.append(leaves[-1])

    # Build tree
    queue = list(leaves)
    while len(queue) > 1:
        next_level: List[str] = []
        for i in range(0, len(queue), 2):
            next_level.append(_sha256_internal(queue[i], queue[i + 1]))
        queue = next_level

    root = queue[0]

    ok = len(root) == 64 and all(c in "0123456789abcdef" for c in root)
    proof = ProofObject(
        conclusion=f"Photonic domain Merkle root: {root}",
        premises=[
            f"Files: {len(records)}",
            f"Root: {root}",
        ],
        rule="photonic_domain_root",
    )
    return ok, proof, root, records


def write_domain_root(output_path: Path | None = None) -> Path:
    """Write domain root JSON and return path."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    if output_path is None:
        output_path = repo_root / "merkle" / "domain_roots" / "photonic.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ok, proof, root, records = compute_photonic_domain_root()
    payload = {
        "domain": "photonic",
        "root_hash": root,
        "file_count": len(records),
        "files": records,
        "ok": ok,
        "proof": {
            "conclusion": proof.conclusion,
            "premises": proof.premises,
            "rule": proof.rule,
        },
    }
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    return output_path


def main() -> int:
    """CLI entry point."""
    output = write_domain_root()
    print(f"Photonic domain root written → {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

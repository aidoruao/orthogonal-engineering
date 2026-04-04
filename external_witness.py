"""
A-18: External Witness Engine
==============================
Provides an independent verification process that runs *outside* the primary
health-check pipeline.  Its sole job is to compute a deterministic manifest of
the repository state from first principles — walking the filesystem, hashing
every tracked file — without reusing any hash logic from
health_check_integration.py.

Key invariant (from the bi-layer epistemic spec):
    hash_internal == hash_external
    → if this fails, the system is in an epistemically inconsistent state.

The engine writes its result to ``external_manifest.json`` in the
``logs/health_checks/`` directory.  It is deliberately kept independent:
  - No imports from health_check_integration.py
  - Uses its own hash accumulation order (sorted file paths)
  - Uses SHA-256 directly, not any registry-level hash
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Directories that are runtime-generated and must NOT be included in the
# external manifest — otherwise the manifest would be invalidated by its own
# creation.
_EXCLUDED_DIRS: frozenset = frozenset(
    {
        ".git",
        "__pycache__",
        "logs",
        ".mypy_cache",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        ".tox",
        "dist",
        "build",
        "*.egg-info",
    }
)

# File extensions to include (source + config only)
_INCLUDED_EXTENSIONS: frozenset = frozenset(
    {
        ".py",
        ".json",
        ".yaml",
        ".yml",
        ".md",
        ".txt",
        ".sh",
        ".toml",
        ".cfg",
        ".ini",
    }
)


def _should_include(path: Path) -> bool:
    """Return True if this path should be hashed by the external witness."""
    for part in path.parts:
        if part in _EXCLUDED_DIRS or part.endswith(".egg-info"):
            return False
    if path.is_file():
        return path.suffix in _INCLUDED_EXTENSIONS
    return False


def compute_external_manifest(root: str | Path) -> Dict[str, Any]:
    """Walk the repository tree and compute an independent file-level manifest.

    The manifest contains:
    - ``file_hashes``: mapping of relative path → SHA-256 hex digest
    - ``tree_hash``: SHA-256 of all (path, digest) pairs in sorted order
    - ``file_count``: number of files included
    - ``computed_at``: ISO-8601 UTC timestamp
    - ``root``: resolved absolute root path
    - ``algorithm``: "sha256"

    Returns the manifest dict (does not write to disk; use write_manifest()).
    """
    root_path = Path(root).resolve()
    file_hashes: Dict[str, str] = {}

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Prune excluded dirs in-place so os.walk won't descend
        dirnames[:] = [
            d for d in sorted(dirnames)
            if d not in _EXCLUDED_DIRS and not d.endswith(".egg-info")
        ]
        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            if not _should_include(fpath):
                continue
            rel = str(fpath.relative_to(root_path))
            try:
                digest = hashlib.sha256(fpath.read_bytes()).hexdigest()
            except OSError:
                digest = "unreadable"
            file_hashes[rel] = digest

    # Tree hash: deterministic over sorted (path, digest) pairs
    tree_hasher = hashlib.sha256()
    for rel, digest in sorted(file_hashes.items()):
        tree_hasher.update(f"{rel}:{digest}\n".encode("utf-8"))
    tree_hash = tree_hasher.hexdigest()

    return {
        "schema_version": "1.0",
        "algorithm": "sha256",
        "root": str(root_path),
        "computed_at": (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        ),
        "file_count": len(file_hashes),
        "tree_hash": tree_hash,
        "file_hashes": file_hashes,
    }


def write_manifest(
    manifest: Dict[str, Any],
    output_dir: str | Path,
    filename: str = "external_manifest.json",
) -> Path:
    """Persist the manifest to ``output_dir/filename``.

    Returns the resolved path of the written file.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out_path


def load_manifest(path: str | Path) -> Optional[Dict[str, Any]]:
    """Load and return a previously written manifest, or None if missing."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


class ExternalWitness:
    """High-level facade for A-18: External Witness Engine.

    Usage::

        witness = ExternalWitness(repo_root=".", output_dir="logs/health_checks")
        result = witness.run()
        # result["tree_hash"] is the external ground truth
    """

    def __init__(
        self,
        repo_root: str | Path,
        output_dir: str | Path = "logs/health_checks",
        filename: str = "external_manifest.json",
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.output_dir = Path(output_dir)
        self.filename = filename

    def run(self) -> Dict[str, Any]:
        """Compute manifest and write to disk.  Returns the manifest dict."""
        manifest = compute_external_manifest(self.repo_root)
        self.manifest_path = write_manifest(manifest, self.output_dir, self.filename)
        return manifest

    def load_previous(self) -> Optional[Dict[str, Any]]:
        """Load the last persisted manifest without recomputing."""
        return load_manifest(self.output_dir / self.filename)

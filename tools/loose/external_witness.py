"""
A-18: External Witness Engine
==============================
Provides an independent verification process that runs *outside* the primary
health-check pipeline.  Its sole job is to compute a deterministic manifest of
the repository state from first principles — walking the filesystem, hashing
every tracked file — without reusing any hash logic from
health_check_integration.py.

Critical independence invariants (Kimi spec):
  - DIFFERENT ALGORITHM: external uses SHA-512; internal uses SHA-256.
    The hash values are never equal even for identical content — proving
    the two pipelines cannot share a result.
  - NO SHARED IMPORTS from health_check_integration.py
  - Separate output file (external_manifest.json ≠ latest_health_check.json)

Key invariant (dual-evidence spec):
    hash_internal != hash_external  (by algorithm)
    …but both refer to the SAME ground truth — proven via the correspondence
    validator (A-19) which re-hashes common files with both algorithms.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ------------------------------------------------------------------ #
# Configuration                                                       #
# ------------------------------------------------------------------ #

# Internal pipeline uses SHA-256; we use SHA-512 for true independence.
_EXTERNAL_ALGORITHM = "sha512"

# Directories that are runtime-generated and must NOT be included.
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
    }
)

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
    for part in path.parts:
        if part in _EXCLUDED_DIRS or part.endswith(".egg-info"):
            return False
    if path.is_file():
        return path.suffix in _INCLUDED_EXTENSIONS
    return False


def _hash_file(path: Path, algorithm: str = _EXTERNAL_ALGORITHM) -> str:
    """Hash a file with the specified algorithm (independent from internal SHA-256)."""
    h = hashlib.new(algorithm)
    try:
        h.update(path.read_bytes())
    except OSError:
        return "unreadable"
    return h.hexdigest()


# ------------------------------------------------------------------ #
# Core computation (no dependency on health_check_integration.py)    #
# ------------------------------------------------------------------ #

def compute_external_manifest(
    root: str | Path,
    algorithm: str = _EXTERNAL_ALGORITHM,
) -> Dict[str, Any]:
    """Walk the repository tree and compute an independent file-level manifest.

    Uses SHA-512 by default — deliberately different from the internal SHA-256
    hash — so the two pipelines cannot accidentally share a cached result.

    Returns:
        manifest dict with:
        - ``file_hashes``: relative_path → hex digest (sha-512)
        - ``tree_hash``:   sha-512 of all (path, digest) pairs sorted
        - ``file_count``:  number of included files
        - ``computed_at``: ISO-8601 UTC timestamp
        - ``algorithm``:   "sha512"
        - ``root``:        resolved absolute root path
    """
    root_path = Path(root).resolve()
    file_hashes: Dict[str, str] = {}

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [
            d for d in sorted(dirnames)
            if d not in _EXCLUDED_DIRS and not d.endswith(".egg-info")
        ]
        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            if not _should_include(fpath):
                continue
            rel = str(fpath.relative_to(root_path))
            file_hashes[rel] = _hash_file(fpath, algorithm)

    # Tree hash: deterministic over sorted (path, digest) pairs
    tree_hasher = hashlib.new(algorithm)
    for rel, digest in sorted(file_hashes.items()):
        tree_hasher.update(f"{rel}:{digest}\n".encode("utf-8"))
    tree_hash = tree_hasher.hexdigest()

    return {
        "schema_version": "1.0",
        "algorithm": algorithm,
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
        # Witness identity: unique per run, proves independent execution
        "witness_id": hashlib.sha256(
            f"{tree_hash}{os.getpid()}".encode()
        ).hexdigest()[:12],
    }


def write_manifest(
    manifest: Dict[str, Any],
    output_dir: str | Path,
    filename: str = "external_manifest.json",
) -> Path:
    """Persist the manifest to ``output_dir/filename``."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out_path


def load_manifest(path: str | Path) -> Optional[Dict[str, Any]]:
    """Load and return a previously written manifest, or None if missing/corrupt."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ------------------------------------------------------------------ #
# High-level facade                                                   #
# ------------------------------------------------------------------ #

class ExternalWitness:
    """High-level facade for A-18: External Witness Engine.

    Uses SHA-512 (not SHA-256) to ensure complete independence from the
    internal pipeline.  The ``correspondence_validator`` (A-19) bridges
    the two by re-hashing common files with both algorithms to prove
    they reference the same ground truth.

    Usage::

        witness = ExternalWitness(repo_root=".", output_dir="logs/health_checks")
        result = witness.run()
        # result["tree_hash"] is the external SHA-512 ground truth
    """

    def __init__(
        self,
        repo_root: str | Path,
        output_dir: str | Path = "logs/health_checks",
        filename: str = "external_manifest.json",
        algorithm: str = _EXTERNAL_ALGORITHM,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.output_dir = Path(output_dir)
        self.filename = filename
        self.algorithm = algorithm
        self.manifest_path: Optional[Path] = None

    def run(self) -> Dict[str, Any]:
        """Compute manifest and write to disk.  Returns the manifest dict."""
        manifest = compute_external_manifest(self.repo_root, self.algorithm)
        self.manifest_path = write_manifest(manifest, self.output_dir, self.filename)
        return manifest

    def load_previous(self) -> Optional[Dict[str, Any]]:
        """Load the last persisted manifest without recomputing."""
        return load_manifest(self.output_dir / self.filename)

    def run_testimony(
        self,
        verification_tasks: List[Any],
        thresholds: Dict[str, Any],
        out_dir: str | Path,
    ) -> Tuple[bool, Any]:
        """Run verification-as-testimony and return top-level YeshuaClaim."""
        from audit.verification_testimony import run_verifications
        from fractions import Fraction

        frac_thresholds = {
            k: Fraction(str(v)) if not isinstance(v, Fraction) else v
            for k, v in thresholds.items()
        }
        return run_verifications(verification_tasks, frac_thresholds, str(out_dir))

    @staticmethod
    def exists(output_dir: str | Path = "logs/health_checks") -> bool:
        """Return True if a previous external manifest exists on disk."""
        return (Path(output_dir) / "external_manifest.json").exists()


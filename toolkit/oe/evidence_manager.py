"""
EvidenceManager — toolkit/oe/evidence_manager.py

Hashes all repository files as Merkle tree leaves and produces a single
"Omega invariant hash" (root) for the repository state.

This module is the authoritative source for the repo-wide integrity root.
It can be run locally or in CI.

Usage (CLI)::

    python -m toolkit.oe.evidence_manager [--repo-root <path>] [--output <file>]

Usage (API)::

    from toolkit.oe.evidence_manager import EvidenceManager
    em = EvidenceManager(repo_root="/path/to/repo")
    root = em.compute_omega_root()
    print(root)  # 64-char hex SHA-256

Author: Orthogonal Engineering
PR: #32
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

from .merkle import MerkleTree, build_merkle_tree_from_files

# ---------------------------------------------------------------------------
# Default exclusions (mirrors common .gitignore patterns)
# ---------------------------------------------------------------------------

DEFAULT_EXCLUDE_DIRS = frozenset({
    ".git", "__pycache__", ".venv", "venv", "env",
    "node_modules", ".pytest_cache", ".mypy_cache",
    "dist", "build", "*.egg-info",
})

DEFAULT_EXCLUDE_SUFFIXES = frozenset({
    ".pyc", ".pyo", ".pyd",
    ".so", ".dll", ".dylib",
    ".egg", ".whl",
})


# ---------------------------------------------------------------------------
# EvidenceManager
# ---------------------------------------------------------------------------


class EvidenceManager:
    """
    Hashes all repository files and produces a Merkle root ("Omega invariant").

    The root is deterministic: same files, same content → same root, regardless
    of OS, hardware, or execution order (leaves are sorted by canonical path).

    Attributes:
        repo_root:    Absolute path to the repository root.
        exclude_dirs: Set of directory names to exclude from scanning.
        exclude_suffixes: Set of file suffixes to exclude.
    """

    def __init__(
        self,
        repo_root: Optional[str | Path] = None,
        exclude_dirs: Optional[frozenset] = None,
        exclude_suffixes: Optional[frozenset] = None,
    ) -> None:
        self.repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
        self.exclude_dirs = exclude_dirs if exclude_dirs is not None else DEFAULT_EXCLUDE_DIRS
        self.exclude_suffixes = exclude_suffixes if exclude_suffixes is not None else DEFAULT_EXCLUDE_SUFFIXES
        self._tree: Optional[MerkleTree] = None

    # ------------------------------------------------------------------
    # File discovery
    # ------------------------------------------------------------------

    def iter_files(self) -> Iterator[Path]:
        """
        Yield all repository files in deterministic order, respecting exclusions.

        Yields:
            Absolute Path objects, sorted by path string for determinism.
        """
        candidates: List[Path] = []

        for path in self.repo_root.rglob("*"):
            if not path.is_file():
                continue
            # Exclude files inside excluded directories
            if any(part in self.exclude_dirs for part in path.parts):
                continue
            # Exclude by suffix
            if path.suffix in self.exclude_suffixes:
                continue
            candidates.append(path)

        candidates.sort()
        yield from candidates

    def _canonical_path(self, file_path: Path) -> str:
        """Return the canonical relative path string (forward slashes)."""
        try:
            rel = file_path.relative_to(self.repo_root)
        except ValueError:
            rel = file_path
        return str(rel).replace("\\", "/")

    def _hash_file(self, file_path: Path) -> str:
        """Return SHA-256 hex digest of the raw file bytes."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    # ------------------------------------------------------------------
    # Merkle tree construction
    # ------------------------------------------------------------------

    def build_tree(self) -> MerkleTree:
        """
        Hash all repo files and build the Merkle tree.

        Returns:
            Built MerkleTree with the Omega root computed.
        """
        file_hashes: List[Tuple[str, str]] = []
        for path in self.iter_files():
            canon = self._canonical_path(path)
            file_hash = self._hash_file(path)
            file_hashes.append((canon, file_hash))

        tree = build_merkle_tree_from_files(file_hashes)
        self._tree = tree
        return tree

    def compute_omega_root(self) -> str:
        """
        Compute and return the Omega invariant hash (Merkle root).

        This is the single hash that represents the entire repository state.
        Calls build_tree() internally.

        Returns:
            64-character lowercase hex SHA-256 Merkle root.
        """
        tree = self.build_tree()
        return tree.root

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_report(self) -> Dict:
        """
        Generate a full integrity report dict.

        Returns:
            Dict with keys: timestamp, repo_root, omega_root,
            file_count, files (list of {path, hash}).
        """
        tree = self.build_tree()
        files_list = [{"path": p, "hash": h} for p, h in tree.leaves]

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repo_root": str(self.repo_root),
            "omega_root": tree.root,
            "file_count": len(tree.leaves),
            "files": files_list,
        }

    def get_inclusion_proof(self, relative_path: str) -> Dict:
        """
        Return the Merkle inclusion proof for a specific file.

        Args:
            relative_path: Forward-slash relative path from repo root.

        Returns:
            Proof dict (see MerkleTree.get_inclusion_proof).

        Raises:
            ValueError: If the file is not in the tree.
            RuntimeError: If compute_omega_root() has not been called yet.
        """
        if self._tree is None:
            self.build_tree()
        assert self._tree is not None
        return self._tree.get_inclusion_proof(relative_path)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evidence_manager",
        description="Compute Merkle-based Omega invariant hash for the repository.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to repository root (default: current directory)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write JSON report to this file (default: stdout)",
    )
    parser.add_argument(
        "--root-only",
        action="store_true",
        help="Print only the Omega root hash (no JSON report)",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    em = EvidenceManager(repo_root=args.repo_root)

    if args.root_only:
        root = em.compute_omega_root()
        print(root)
        return 0

    report = em.generate_report()
    report_json = json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(report_json, encoding="utf-8")
        print(f"Report written to {args.output}")
        print(f"Omega root: {report['omega_root']}")
    else:
        print(report_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())

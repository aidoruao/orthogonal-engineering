"""
Manifest module for streaming manifest.jsonl generation.

Supports checkpointing and restartable runs for large repositories.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.1.0
"""

import json
from pathlib import Path
from typing import Dict, Any, Iterator, Optional, Set

from .canonicalizer import canonical_byte_representation
from .hasher import compute_sha256


class ManifestGenerator:
    """Generator for streaming manifest.jsonl with checkpointing support."""

    def __init__(self, output_path: Path, checkpoint_path: Optional[Path] = None):
        """
        Initialize manifest generator.

        Args:
            output_path: Path to output manifest.jsonl
            checkpoint_path: Path to checkpoint file (optional)
        """
        self.output_path = Path(output_path)
        self.checkpoint_path = checkpoint_path or self.output_path.with_suffix('.checkpoint')
        self.processed_files: Set[str] = set()

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_checkpoint()

    def _load_checkpoint(self) -> None:
        """Load processed files from checkpoint."""
        if self.checkpoint_path.exists():
            with open(self.checkpoint_path, 'r') as f:
                for line in f:
                    if line.strip():
                        self.processed_files.add(line.strip())

    def _save_checkpoint(self, path: str) -> None:
        """Save a processed file path to the checkpoint."""
        with open(self.checkpoint_path, 'a') as f:
            f.write(path + '\n')

    def is_processed(self, path: str) -> bool:
        """Return True if the canonical path has already been processed."""
        return path in self.processed_files

    def add_file(self, file_path: Path, canonical_path: str) -> Optional[Dict[str, Any]]:
        """
        Add a file to the manifest.

        Args:
            file_path: Actual path to file
            canonical_path: Canonical path for manifest entry

        Returns:
            Manifest entry dict, or None if already processed
        """
        if self.is_processed(canonical_path):
            return None

        file_path = Path(file_path)
        canonical_bytes, file_type = canonical_byte_representation(file_path)
        canonical_hash = compute_sha256(canonical_bytes)
        size = len(canonical_bytes)

        entry = {
            'path': canonical_path,
            'type': file_type,
            'hash': canonical_hash,
            'size': size,
            'content_address': f"sha256:{canonical_hash}",
        }

        with open(self.output_path, 'a') as f:
            f.write(json.dumps(entry, separators=(',', ':')) + '\n')

        self._save_checkpoint(canonical_path)
        self.processed_files.add(canonical_path)
        return entry

    def process_directory(self, root_dir: Path,
                          exclude_patterns: Optional[list] = None) -> Iterator[Dict[str, Any]]:
        """
        Process all files in a directory tree.

        Args:
            root_dir: Root directory to process
            exclude_patterns: List of glob patterns to exclude

        Yields:
            Manifest entries
        """
        exclude_patterns = exclude_patterns or []

        for file_path in sorted(root_dir.rglob('*')):
            if file_path.is_dir():
                continue

            skip = any(file_path.match(p) for p in exclude_patterns)
            if skip:
                continue

            try:
                canon = str(file_path.relative_to(root_dir)).replace('\\', '/')
            except ValueError:
                canon = str(file_path).replace('\\', '/')

            entry = self.add_file(file_path, canon)
            if entry:
                yield entry

    def finalize(self) -> None:
        """Finalize the manifest and remove checkpoint."""
        if self.checkpoint_path.exists():
            self.checkpoint_path.unlink()


def load_manifest(manifest_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Load and iterate through a manifest.jsonl file.

    Args:
        manifest_path: Path to manifest file

    Yields:
        Manifest entries
    """
    with open(manifest_path, 'r') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

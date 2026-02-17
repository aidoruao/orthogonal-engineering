"""
Manifest module for orthogonal-engineering.

Generates JSONL manifest files listing canonical paths, file types, hashes,
sizes, and content-addressed references. Supports streaming large repositories
with checkpointing.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import json
import os
from pathlib import Path
from typing import Iterator, Union

from .canonicalizer import canonical_byte_representation, canonical_path, detect_file_type
from .hasher import hash_bytes


class ManifestEntry:
    """Represents a single entry in the manifest."""
    
    def __init__(self, file_path: str, canonical_path: str, file_type: str,
                 canonical_hash: str, size: int, content_ref: str = None):
        """
        Initialize manifest entry.
        
        Args:
            file_path: Original file path
            canonical_path: Canonical path representation
            file_type: File type (text, json, xml, binary)
            canonical_hash: SHA-256 hash of canonical bytes
            size: File size in bytes
            content_ref: Optional content-addressed reference
        """
        self.file_path = file_path
        self.canonical_path = canonical_path
        self.file_type = file_type
        self.canonical_hash = canonical_hash
        self.size = size
        self.content_ref = content_ref or f"sha256:{canonical_hash}"
    
    def to_dict(self) -> dict:
        """Convert entry to dictionary."""
        return {
            'file_path': self.file_path,
            'canonical_path': self.canonical_path,
            'file_type': self.file_type,
            'canonical_hash': self.canonical_hash,
            'size': self.size,
            'content_ref': self.content_ref
        }


class ManifestGenerator:
    """Generates manifest files for repositories."""
    
    def __init__(self, base_path: Union[str, Path], checkpoint_interval: int = 100):
        """
        Initialize manifest generator.
        
        Args:
            base_path: Base path for repository
            checkpoint_interval: Number of files to process before checkpointing
        """
        self.base_path = Path(base_path).resolve()
        self.checkpoint_interval = checkpoint_interval
        self.entries: list = []
        self.processed_count = 0
    
    def add_file(self, file_path: Union[str, Path]) -> ManifestEntry:
Manifest module for streaming manifest.jsonl generation.

Supports checkpointing and restartable runs for large repositories.
"""

import json
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, Set
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
        self.output_path = output_path
        self.checkpoint_path = checkpoint_path or output_path.with_suffix('.checkpoint')
        self.processed_files: Set[str] = set()
        
        # Ensure parent directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load checkpoint if exists
        self._load_checkpoint()
    
    def _load_checkpoint(self) -> None:
        """Load processed files from checkpoint."""
        if self.checkpoint_path.exists():
            with open(self.checkpoint_path, 'r') as f:
                for line in f:
                    if line.strip():
                        self.processed_files.add(line.strip())
    
    def _save_checkpoint(self, path: str) -> None:
        """
        Save a processed file to checkpoint.
        
        Args:
            path: Canonical path that was processed
        """
        with open(self.checkpoint_path, 'a') as f:
            f.write(path + '\n')
    
    def is_processed(self, path: str) -> bool:
        """
        Check if a file has already been processed.
        
        Args:
            path: Canonical path to check
            
        Returns:
            True if already processed
        """
        return path in self.processed_files
    
    def add_file(self, file_path: Path, canonical_path: str) -> Dict[str, Any]:
        """
        Add a file to the manifest.
        
        Args:
            file_path: Path to file
            
        Returns:
            ManifestEntry for the file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get canonical representation and hash
        canonical_bytes = canonical_byte_representation(file_path)
        canonical_hash = hash_bytes(canonical_bytes)
        
        # Get file info
        canon_path = canonical_path(file_path, self.base_path)
        file_type = detect_file_type(file_path)
        size = len(canonical_bytes)
        
        # Create entry
        entry = ManifestEntry(
            file_path=str(file_path),
            canonical_path=canon_path,
            file_type=file_type,
            canonical_hash=canonical_hash,
            size=size
        )
        
        self.entries.append(entry)
        self.processed_count += 1
        
        return entry
    
    def scan_directory(self, directory: Union[str, Path] = None,
                      pattern: str = None, exclude_patterns: list = None) -> Iterator[ManifestEntry]:
        """
        Scan directory and yield manifest entries.
        
        Args:
            directory: Directory to scan (defaults to base_path)
            pattern: Optional glob pattern to filter files
            exclude_patterns: Optional list of patterns to exclude
            
        Yields:
            ManifestEntry for each file
        """
        if directory is None:
            directory = self.base_path
        else:
            directory = Path(directory)
        
        exclude_patterns = exclude_patterns or ['.git', '__pycache__', '*.pyc', '.DS_Store']
        
        # Recursively find files
        if pattern:
            files = directory.rglob(pattern)
        else:
            files = directory.rglob('*')
        
        for file_path in files:
            # Skip directories
            if not file_path.is_file():
                continue
            
            # Skip excluded patterns
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if exclude_pattern in str(file_path):
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
            
            try:
                entry = self.add_file(file_path)
                yield entry
            except Exception as e:
                # Log error but continue processing
                print(f"Warning: Failed to process {file_path}: {e}")
                continue
    
    def save_manifest(self, output_path: Union[str, Path], checkpoint: bool = False):
        """
        Save manifest to JSONL file.
        
        Args:
            output_path: Path to output file
            checkpoint: If True, append to existing file (for checkpointing)
        """
        mode = 'a' if checkpoint else 'w'
        
        with open(output_path, mode, encoding='utf-8') as f:
            for entry in self.entries:
                f.write(json.dumps(entry.to_dict(), sort_keys=True) + '\n')
        
        # Clear entries after saving if checkpointing
        if checkpoint:
            self.entries.clear()
    
    def generate_streaming_manifest(self, output_path: Union[str, Path],
                                   directory: Union[str, Path] = None,
                                   pattern: str = None,
                                   exclude_patterns: list = None):
        """
        Generate manifest with streaming and checkpointing for large repos.
        
        Args:
            output_path: Path to output JSONL file
            directory: Directory to scan
            pattern: Optional glob pattern
            exclude_patterns: Optional exclusion patterns
        """
        # Clear existing file
        output_path = Path(output_path)
        if output_path.exists():
            output_path.unlink()
        
        count = 0
        for entry in self.scan_directory(directory, pattern, exclude_patterns):
            count += 1
            
            # Checkpoint at intervals
            if count % self.checkpoint_interval == 0:
                self.save_manifest(output_path, checkpoint=True)
                print(f"Checkpoint: Processed {count} files")
        
        # Save remaining entries
        if self.entries:
            self.save_manifest(output_path, checkpoint=True)
        
        print(f"Manifest complete: {count} files processed")
    
    def load_manifest(self, input_path: Union[str, Path]) -> list:
        """
        Load manifest from JSONL file.
        
        Args:
            input_path: Path to JSONL file
            
        Returns:
            List of ManifestEntry objects
        """
        entries = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    entry = ManifestEntry(**data)
                    entries.append(entry)
        return entries
            file_path: Actual path to file
            canonical_path: Canonical path for manifest
            
        Returns:
            Manifest entry
        """
        # Skip if already processed
        if self.is_processed(canonical_path):
            return None
        
        # Get canonical representation
        canonical_bytes, file_type = canonical_byte_representation(file_path)
        
        # Compute hash
        canonical_hash = compute_sha256(canonical_bytes)
        
        # Get file size
        size = len(canonical_bytes)
        
        # Create content-address reference
        content_address = f"sha256:{canonical_hash}"
        
        # Build manifest entry
        entry = {
            'path': canonical_path,
            'type': file_type,
            'hash': canonical_hash,
            'size': size,
            'content_address': content_address
        }
        
        # Write to manifest
        with open(self.output_path, 'a') as f:
            f.write(json.dumps(entry, separators=(',', ':')) + '\n')
        
        # Update checkpoint
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
        
        # Walk directory tree
        for file_path in sorted(root_dir.rglob('*')):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Check exclusion patterns
            skip = False
            for pattern in exclude_patterns:
                if file_path.match(pattern):
                    skip = True
                    break
            
            if skip:
                continue
            
            # Get canonical path (relative to root)
            try:
                canonical_path = str(file_path.relative_to(root_dir))
            except ValueError:
                # File is not relative to root
                canonical_path = str(file_path)
            
            # Normalize path separators to forward slash
            canonical_path = canonical_path.replace('\\', '/')
            
            # Add to manifest
            entry = self.add_file(file_path, canonical_path)
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

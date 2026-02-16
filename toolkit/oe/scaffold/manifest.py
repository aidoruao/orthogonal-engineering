"""
Manifest Module

Provides streamed JSONL manifest generation with:
- Canonical path listing
- File type detection
- Canonical hash computation
- File size tracking
- Content-address reference
- Checkpointing for large repositories
"""

import json
from pathlib import Path
from typing import Union, List, Optional, Iterator
import time

from .canonicalizer import canonical_byte_representation, detect_file_type
from .hasher import compute_hash


class ManifestEntry:
    """Represents a single entry in the manifest."""
    
    def __init__(self, canonical_path: str, file_type: str, canonical_hash: str, 
                 size: int, content_address: str):
        self.canonical_path = canonical_path
        self.file_type = file_type
        self.canonical_hash = canonical_hash
        self.size = size
        self.content_address = content_address
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "canonical_path": self.canonical_path,
            "file_type": self.file_type,
            "canonical_hash": self.canonical_hash,
            "size": self.size,
            "content_address": self.content_address
        }


class ManifestGenerator:
    """Streamed manifest generator with checkpointing."""
    
    def __init__(self, output_path: Union[str, Path], checkpoint_interval: int = 100):
        """
        Initialize manifest generator.
        
        Args:
            output_path: Path to output manifest.jsonl file
            checkpoint_interval: Number of entries between checkpoints
        """
        self.output_path = Path(output_path)
        self.checkpoint_interval = checkpoint_interval
        self.entries_written = 0
        self.checkpoint_path = self.output_path.with_suffix(".checkpoint")
        
        # Clear existing manifest
        if self.output_path.exists():
            self.output_path.unlink()
    
    def add_entry(self, entry: ManifestEntry) -> None:
        """
        Add entry to manifest.
        
        Args:
            entry: ManifestEntry to add
        """
        # Append to JSONL file
        with open(self.output_path, "a", encoding="utf-8") as f:
            json.dump(entry.to_dict(), f, ensure_ascii=False)
            f.write("\n")
        
        self.entries_written += 1
        
        # Create checkpoint if needed
        if self.entries_written % self.checkpoint_interval == 0:
            self._create_checkpoint()
    
    def _create_checkpoint(self) -> None:
        """Create checkpoint file."""
        checkpoint_data = {
            "entries_written": self.entries_written,
            "timestamp": time.time(),
            "manifest_path": str(self.output_path)
        }
        
        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2)
    
    def finalize(self) -> None:
        """Finalize manifest generation."""
        # Final checkpoint
        self._create_checkpoint()
        
        # Write summary
        summary_path = self.output_path.with_suffix(".summary.json")
        summary = {
            "total_entries": self.entries_written,
            "manifest_path": str(self.output_path),
            "completed": time.time()
        }
        
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)


def create_manifest_entry(file_path: Union[str, Path], 
                         base_path: Optional[Union[str, Path]] = None) -> ManifestEntry:
    """
    Create manifest entry for a file.
    
    Args:
        file_path: Path to the file
        base_path: Optional base path for computing relative canonical path
        
    Returns:
        ManifestEntry object
    """
    file_path = Path(file_path)
    
    # Compute canonical path (relative to base_path if provided)
    if base_path:
        base_path = Path(base_path)
        try:
            canonical_path = str(file_path.relative_to(base_path))
        except ValueError:
            # If not relative, use absolute path
            canonical_path = str(file_path.resolve())
    else:
        canonical_path = str(file_path.resolve())
    
    # Normalize path separators to forward slashes for cross-platform consistency
    canonical_path = canonical_path.replace("\\", "/")
    
    # Detect file type
    file_type = detect_file_type(file_path)
    
    # Compute canonical hash
    canonical_bytes = canonical_byte_representation(file_path)
    canonical_hash = compute_hash(canonical_bytes)
    
    # Get size
    size = len(canonical_bytes)
    
    # Create content address (same as hash in this implementation)
    content_address = f"sha256:{canonical_hash}"
    
    return ManifestEntry(canonical_path, file_type, canonical_hash, size, content_address)


def generate_manifest(file_paths: List[Union[str, Path]], 
                     output_path: Union[str, Path],
                     base_path: Optional[Union[str, Path]] = None,
                     checkpoint_interval: int = 100) -> int:
    """
    Generate manifest for a list of files.
    
    Args:
        file_paths: List of file paths to include
        output_path: Path to output manifest.jsonl
        base_path: Optional base path for relative paths
        checkpoint_interval: Entries between checkpoints
        
    Returns:
        Number of entries written
    """
    generator = ManifestGenerator(output_path, checkpoint_interval)
    
    for file_path in file_paths:
        try:
            entry = create_manifest_entry(file_path, base_path)
            generator.add_entry(entry)
        except Exception as e:
            # Log error but continue processing
            print(f"Warning: Failed to process {file_path}: {e}")
    
    generator.finalize()
    return generator.entries_written


def iterate_manifest(manifest_path: Union[str, Path]) -> Iterator[dict]:
    """
    Iterate over entries in a manifest file.
    
    Args:
        manifest_path: Path to manifest.jsonl file
        
    Yields:
        Dictionary for each manifest entry
    """
    manifest_path = Path(manifest_path)
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

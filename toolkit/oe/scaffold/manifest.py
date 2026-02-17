"""
<<<<<<< HEAD
Streaming JSONL manifest builder with checkpointing support.

Generates manifest.jsonl with:
- canonical_path: UTF-8 normalized path
- file_type: Detected file type
- canonical_hash: SHA-256 of canonical bytes
- size: File size in bytes
- content_address: Content-addressable reference

Supports checkpointing for large repos and restartable runs.
"""

import json
import mimetypes
from pathlib import Path
from typing import Union, Optional, Set, Iterator
from dataclasses import dataclass, asdict

from .canonicalizer import canonical_byte_representation
from .hasher import hash_file


@dataclass
class ManifestEntry:
    """Single entry in the manifest."""
    canonical_path: str
    file_type: str
    canonical_hash: str
    size: int
    content_address: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class ManifestBuilder:
    """
    Streaming manifest builder with checkpointing.
    
    Features:
    - Streaming JSONL output
    - Checkpointing for large repositories
    - Restartable runs
    - Deterministic ordering
    """
    
    def __init__(self, output_path: Union[str, Path] = "manifest.jsonl",
                 checkpoint_path: Optional[Union[str, Path]] = None):
        """
        Initialize manifest builder.
        
        Args:
            output_path: Path to output manifest.jsonl
            checkpoint_path: Optional path to checkpoint file
        """
        self.output_path = Path(output_path)
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self.processed_files: Set[str] = set()
        
        # Load checkpoint if exists
        if self.checkpoint_path and self.checkpoint_path.exists():
            self._load_checkpoint()
    
    def _load_checkpoint(self) -> None:
        """Load processed files from checkpoint."""
        if not self.checkpoint_path:
            return
        
        try:
            with open(self.checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)
                self.processed_files = set(checkpoint_data.get('processed_files', []))
        except Exception as e:
            print(f"Warning: Failed to load checkpoint: {e}")
    
    def _save_checkpoint(self) -> None:
        """Save current progress to checkpoint."""
        if not self.checkpoint_path:
            return
        
        try:
            checkpoint_data = {
                'processed_files': list(self.processed_files),
                'total_processed': len(self.processed_files)
            }
            with open(self.checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save checkpoint: {e}")
    
    def _detect_file_type(self, file_path: Path) -> str:
        """
        Detect file type from extension and MIME type.
        
        Args:
            file_path: Path to file
            
        Returns:
            File type string
        """
        # Try MIME type first
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        if mime_type:
            return mime_type
        
        # Fall back to extension
        suffix = file_path.suffix.lower()
        
        # Common types
        type_map = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.yaml': 'application/x-yaml',
            '.yml': 'application/x-yaml',
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.meta': 'application/xml',
        }
        
        return type_map.get(suffix, 'application/octet-stream')
    
    def add_file(self, file_path: Union[str, Path], 
                 canonical_path: Optional[str] = None) -> Optional[ManifestEntry]:
        """
        Add a file to the manifest.
        
        Args:
            file_path: Path to file
            canonical_path: Optional canonical path (defaults to relative path)
            
        Returns:
            ManifestEntry or None if already processed
        """
        path = Path(file_path)
        
        if not path.exists() or not path.is_file():
            return None
        
        # Use canonical path or convert to string
        if canonical_path is None:
            canonical_path = str(path)
        
        # Skip if already processed
        if canonical_path in self.processed_files:
            return None
        
        # Compute hash and size
        try:
            canonical_hash = hash_file(path, canonical=True)
            size = path.stat().st_size
            file_type = self._detect_file_type(path)
            
            # Content-addressable reference (hash-based)
            content_address = f"sha256:{canonical_hash}"
            
            entry = ManifestEntry(
                canonical_path=canonical_path,
                file_type=file_type,
                canonical_hash=canonical_hash,
                size=size,
                content_address=content_address
            )
            
            # Write to manifest
            with open(self.output_path, 'a') as f:
                f.write(json.dumps(entry.to_dict()) + '\n')
            
            # Mark as processed
            self.processed_files.add(canonical_path)
            
            # Save checkpoint periodically (every 100 files)
            if len(self.processed_files) % 100 == 0:
                self._save_checkpoint()
            
            return entry
            
        except Exception as e:
            print(f"Error processing {canonical_path}: {e}")
            return None
    
    def add_directory(self, dir_path: Union[str, Path], 
                     pattern: str = "**/*",
                     relative_to: Optional[Path] = None) -> Iterator[ManifestEntry]:
        """
        Add all files in a directory to the manifest.
        
        Args:
            dir_path: Path to directory
            pattern: Glob pattern for file matching
            relative_to: Optional base path for computing relative paths
            
        Yields:
            ManifestEntry for each file
        """
        dir_path = Path(dir_path)
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")
        
        if relative_to is None:
            relative_to = dir_path
        
        # Sort for deterministic ordering
        for file_path in sorted(dir_path.glob(pattern)):
            if file_path.is_file():
                # Compute canonical path (relative to base)
                try:
                    canonical_path = str(file_path.relative_to(relative_to))
                except ValueError:
                    canonical_path = str(file_path)
                
                entry = self.add_file(file_path, canonical_path)
                if entry:
                    yield entry
        
        # Final checkpoint save
        self._save_checkpoint()
    
    def finalize(self) -> None:
        """Finalize the manifest and save final checkpoint."""
        self._save_checkpoint()


# Unit tests and examples
def _test_manifest_builder():
    """Test manifest builder."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "a.txt").write_text("File A content")
        (tmpdir / "b.json").write_text('{"key": "value"}')
        
        # Build manifest
        manifest_path = tmpdir / "manifest.jsonl"
        builder = ManifestBuilder(output_path=manifest_path)
        
        entries = list(builder.add_directory(tmpdir, pattern="*.txt"))
        assert len(entries) >= 1
        
        # Verify manifest file exists
        assert manifest_path.exists()
        
        # Read and verify entries
        with open(manifest_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) >= 1
            
            for line in lines:
                entry = json.loads(line)
                assert 'canonical_path' in entry
                assert 'canonical_hash' in entry
                assert 'size' in entry
        
        print("✓ Manifest builder tests passed")


if __name__ == "__main__":
    _test_manifest_builder()
    print("\n✓ All manifest tests passed")
=======
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
>>>>>>> copilot/add-deterministic-auditable-scaffold

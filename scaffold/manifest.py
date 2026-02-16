"""
Manifest Module

Streams manifest.jsonl listing:
- canonical_path: Canonical path (UTF-8)
- file_type: Detected file type
- canonical_hash: SHA-256 hash of canonical bytes
- size: File size in bytes
- content_address: Content-addressable reference

Supports checkpointing for large repositories.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union

from .canonicalizer import canonical_byte_representation, get_file_type
from .hasher import compute_hash


class ManifestEntry:
    """Represents a single entry in the manifest."""
    
    def __init__(self, 
                 canonical_path: str,
                 file_type: str,
                 canonical_hash: str,
                 size: int,
                 content_address: Optional[str] = None):
        """
        Initialize manifest entry.
        
        Args:
            canonical_path: Canonical file path
            file_type: Detected file type
            canonical_hash: SHA-256 hash of canonical bytes
            size: File size in bytes
            content_address: Optional content-addressable reference
        """
        self.canonical_path = canonical_path
        self.file_type = file_type
        self.canonical_hash = canonical_hash
        self.size = size
        self.content_address = content_address or f"sha256:{canonical_hash}"
    
    def to_dict(self) -> dict:
        """Convert entry to dictionary."""
        return {
            "canonical_path": self.canonical_path,
            "file_type": self.file_type,
            "canonical_hash": self.canonical_hash,
            "size": self.size,
            "content_address": self.content_address
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ManifestEntry':
        """Create entry from dictionary."""
        return cls(
            canonical_path=data["canonical_path"],
            file_type=data["file_type"],
            canonical_hash=data["canonical_hash"],
            size=data["size"],
            content_address=data.get("content_address")
        )


class ManifestCheckpoint:
    """Manages checkpointing for large repository processing."""
    
    def __init__(self, checkpoint_file: Path):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_file: Path to checkpoint file
        """
        self.checkpoint_file = checkpoint_file
        self.processed_files: set = set()
        
        # Load existing checkpoint if present
        if checkpoint_file.exists():
            self._load()
    
    def _load(self):
        """Load checkpoint from file."""
        with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.processed_files = set(data.get("processed_files", []))
    
    def save(self, processed_files: set):
        """
        Save checkpoint.
        
        Args:
            processed_files: Set of processed file paths
        """
        self.processed_files = processed_files
        
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processed_count": len(processed_files),
            "processed_files": list(processed_files)
        }
        
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def is_processed(self, file_path: str) -> bool:
        """Check if file has been processed."""
        return file_path in self.processed_files
    
    def mark_processed(self, file_path: str):
        """Mark file as processed."""
        self.processed_files.add(file_path)
    
    def clear(self):
        """Clear checkpoint."""
        self.processed_files.clear()
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()


class ManifestGenerator:
    """
    Generates manifest.jsonl for repository files.
    
    Supports streaming and checkpointing for large repositories.
    """
    
    def __init__(self, 
                 repo_path: Union[str, Path],
                 output_path: Optional[Union[str, Path]] = None,
                 checkpoint_interval: int = 100):
        """
        Initialize manifest generator.
        
        Args:
            repo_path: Path to repository root
            output_path: Path to output manifest.jsonl (default: repo_path/manifest.jsonl)
            checkpoint_interval: Save checkpoint every N files
        """
        self.repo_path = Path(repo_path)
        self.output_path = Path(output_path) if output_path else self.repo_path / "manifest.jsonl"
        self.checkpoint_interval = checkpoint_interval
        
        # Checkpoint file
        checkpoint_file = self.output_path.parent / f".{self.output_path.name}.checkpoint"
        self.checkpoint = ManifestCheckpoint(checkpoint_file)
        
        # Statistics
        self.total_files = 0
        self.processed_files = 0
        self.skipped_files = 0
        self.errors = 0
    
    def _should_include(self, file_path: Path) -> bool:
        """
        Determine if file should be included in manifest.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file should be included
        """
        # Skip hidden files and directories
        if file_path.name.startswith('.'):
            return False
        
        # Skip common build/dependency directories
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                       'dist', 'build', '.pytest_cache', '.mypy_cache'}
        
        for part in file_path.parts:
            if part in exclude_dirs:
                return False
        
        return True
    
    def _generate_entry(self, file_path: Path) -> Optional[ManifestEntry]:
        """
        Generate manifest entry for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            ManifestEntry or None if file should be skipped
        """
        try:
            # Get canonical path (relative to repo)
            canonical_path = str(file_path.relative_to(self.repo_path))
            
            # Get file type
            file_type = get_file_type(file_path)
            
            # Get canonical bytes and compute hash
            canonical_bytes = canonical_byte_representation(file_path)
            canonical_hash = compute_hash(canonical_bytes)
            
            # Get file size
            size = file_path.stat().st_size
            
            # Create entry
            return ManifestEntry(
                canonical_path=canonical_path,
                file_type=file_type,
                canonical_hash=canonical_hash,
                size=size
            )
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            self.errors += 1
            return None
    
    def generate(self, resume: bool = True) -> int:
        """
        Generate manifest for all files in repository.
        
        Args:
            resume: If True, resume from checkpoint if present
            
        Returns:
            Number of files processed
        """
        # Clear checkpoint if not resuming
        if not resume:
            self.checkpoint.clear()
        
        # Collect all files
        all_files = []
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file() and self._should_include(file_path):
                all_files.append(file_path)
        
        self.total_files = len(all_files)
        
        # Open output file
        mode = 'a' if resume else 'w'
        with open(self.output_path, mode, encoding='utf-8') as f:
            for i, file_path in enumerate(all_files):
                canonical_path = str(file_path.relative_to(self.repo_path))
                
                # Skip if already processed (checkpoint)
                if resume and self.checkpoint.is_processed(canonical_path):
                    self.skipped_files += 1
                    continue
                
                # Generate entry
                entry = self._generate_entry(file_path)
                
                if entry:
                    # Write to manifest
                    f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + '\n')
                    f.flush()  # Ensure write for streaming
                    
                    # Mark as processed
                    self.checkpoint.mark_processed(canonical_path)
                    self.processed_files += 1
                    
                    # Save checkpoint periodically
                    if self.processed_files % self.checkpoint_interval == 0:
                        self.checkpoint.save(self.checkpoint.processed_files)
                        print(f"Checkpoint: {self.processed_files}/{self.total_files} files")
        
        # Final checkpoint
        self.checkpoint.save(self.checkpoint.processed_files)
        
        # Clear checkpoint after successful completion
        if self.errors == 0:
            self.checkpoint.clear()
        
        return self.processed_files
    
    def iter_entries(self) -> Iterator[ManifestEntry]:
        """
        Iterate over manifest entries.
        
        Yields:
            ManifestEntry objects
        """
        if not self.output_path.exists():
            return
        
        with open(self.output_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    yield ManifestEntry.from_dict(json.loads(line))
    
    def get_statistics(self) -> dict:
        """
        Get generation statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "skipped_files": self.skipped_files,
            "errors": self.errors
        }
    
    def verify_manifest(self) -> List[str]:
        """
        Verify manifest against current repository state.
        
        Returns:
            List of verification errors (empty if all OK)
        """
        errors = []
        
        for entry in self.iter_entries():
            file_path = self.repo_path / entry.canonical_path
            
            # Check if file exists
            if not file_path.exists():
                errors.append(f"Missing file: {entry.canonical_path}")
                continue
            
            # Verify hash
            try:
                canonical_bytes = canonical_byte_representation(file_path)
                current_hash = compute_hash(canonical_bytes)
                
                if current_hash != entry.canonical_hash:
                    errors.append(
                        f"Hash mismatch for {entry.canonical_path}: "
                        f"expected {entry.canonical_hash}, got {current_hash}"
                    )
            except Exception as e:
                errors.append(f"Error verifying {entry.canonical_path}: {e}")
        
        return errors

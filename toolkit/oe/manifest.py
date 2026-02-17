"""
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

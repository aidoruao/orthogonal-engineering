"""
Manifest file handling for content-addressable storage.

Provides manifest creation, validation, and management for CAS operations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from hasher import hash_file
from merkle import MerkleTree


class Manifest:
    """Manifest for tracking content in CAS."""
    
    def __init__(self, name: str = "manifest", metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize manifest.
        
        Args:
            name: Manifest name
            metadata: Optional metadata dictionary
        """
        self.name = name
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.metadata = metadata or {}
        self.entries: List[Dict[str, Any]] = []
    
    def add_entry(self, filepath: Union[str, Path], hash_value: Optional[str] = None, **kwargs):
        """
        Add file entry to manifest.
        
        Args:
            filepath: Path to file
            hash_value: Pre-computed hash (will compute if None)
            **kwargs: Additional metadata for this entry
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Compute hash if not provided
        if hash_value is None:
            hash_value = hash_file(filepath)
        
        entry = {
            "path": str(filepath),
            "name": filepath.name,
            "hash": hash_value,
            "size": filepath.stat().st_size,
            "added_at": datetime.utcnow().isoformat() + "Z",
            **kwargs
        }
        
        self.entries.append(entry)
    
    def get_merkle_root(self) -> Optional[str]:
        """
        Compute Merkle root of all entries.
        
        Returns:
            Merkle root hash, or None if no entries
        """
        if not self.entries:
            return None
        
        hashes = [entry["hash"] for entry in self.entries]
        tree = MerkleTree(hashes)
        return tree.get_root_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert manifest to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "entries": self.entries,
            "merkle_root": self.get_merkle_root(),
            "entry_count": len(self.entries)
        }
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert manifest to JSON string.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save(self, filepath: Union[str, Path]):
        """
        Save manifest to file.
        
        Args:
            filepath: Where to save manifest
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Manifest':
        """
        Create manifest from dictionary.
        
        Args:
            data: Dictionary with manifest data
            
        Returns:
            Manifest instance
        """
        manifest = cls(
            name=data.get("name", "manifest"),
            metadata=data.get("metadata", {})
        )
        manifest.created_at = data.get("created_at", manifest.created_at)
        manifest.entries = data.get("entries", [])
        return manifest
    
    @classmethod
    def load(cls, filepath: Union[str, Path]) -> 'Manifest':
        """
        Load manifest from file.
        
        Args:
            filepath: Path to manifest file
            
        Returns:
            Manifest instance
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Manifest not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def verify(self) -> Dict[str, Any]:
        """
        Verify all entries in manifest.
        
        Returns:
            Verification report with status and details
        """
        results = {
            "verified": True,
            "total": len(self.entries),
            "valid": 0,
            "invalid": 0,
            "missing": 0,
            "details": []
        }
        
        for entry in self.entries:
            filepath = Path(entry["path"])
            
            if not filepath.exists():
                results["verified"] = False
                results["missing"] += 1
                results["details"].append({
                    "path": entry["path"],
                    "status": "missing"
                })
                continue
            
            # Verify hash
            actual_hash = hash_file(filepath)
            if actual_hash == entry["hash"]:
                results["valid"] += 1
                results["details"].append({
                    "path": entry["path"],
                    "status": "valid"
                })
            else:
                results["verified"] = False
                results["invalid"] += 1
                results["details"].append({
                    "path": entry["path"],
                    "status": "invalid",
                    "expected_hash": entry["hash"],
                    "actual_hash": actual_hash
                })
        
        return results
Manifest module for streamed manifest.jsonl generation.

This module provides functionality to create a manifest of files with:
- Canonical path
- Canonical hash
- File size
- File type
- Content-address reference

Supports checkpointing for restartable runs on large repositories.

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import json
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Set

from canonicalizer import canonicalize
from hasher import sha256_hex
from utils import CheckpointManager, deterministic_sort_paths, relative_path


def detect_file_type(file_path: Path) -> str:
    """
    Detect file type based on extension and content.
    
    Args:
        file_path: Path to file
        
    Returns:
        File type string ('json', 'xml', 'text', 'binary')
    """
    suffix = file_path.suffix.lower()
    
    # Check by extension
    if suffix in ['.json', '.jsonl']:
        return 'json'
    elif suffix in ['.xml', '.xsd', '.xsl']:
        return 'xml'
    elif suffix in ['.txt', '.md', '.py', '.js', '.ts', '.css', '.html', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
        return 'text'
    
    # Use mimetypes as fallback
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type:
        if 'json' in mime_type:
            return 'json'
        elif 'xml' in mime_type:
            return 'xml'
        elif mime_type.startswith('text/'):
            return 'text'
    
    # Default to binary
    return 'binary'


class ManifestGenerator:
    """Generate streamed manifest.jsonl with checkpointing support."""
    
    def __init__(
        self,
        output_path: Path,
        checkpoint_path: Optional[Path] = None,
        base_dir: Optional[Path] = None
    ):
        """
        Initialize manifest generator.
        
        Args:
            output_path: Path to output manifest.jsonl
            checkpoint_path: Optional path to checkpoint file
            base_dir: Base directory for relative paths (defaults to cwd)
        """
        self.output_path = output_path
        self.base_dir = base_dir or Path.cwd()
        
        # Initialize checkpoint manager
        if checkpoint_path is None:
            checkpoint_path = output_path.parent / f"{output_path.stem}.checkpoint.json"
        self.checkpoint = CheckpointManager(checkpoint_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open manifest file for appending
        self.manifest_file = open(output_path, 'a')
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close manifest file."""
        if hasattr(self, 'manifest_file') and self.manifest_file:
            self.manifest_file.close()
    
    def add_file(self, file_path: Path, skip_if_processed: bool = True) -> Optional[Dict]:
        """
        Add a file to the manifest.
        
        Args:
            file_path: Path to file
            skip_if_processed: Skip if already in checkpoint
            
        Returns:
            Manifest entry dictionary or None if skipped
        """
        # Convert to absolute path
        abs_path = file_path.absolute()
        path_str = str(abs_path)
        
        # Check checkpoint
        if skip_if_processed and self.checkpoint.is_processed(path_str):
            return None
        
        # Skip if not a file
        if not abs_path.is_file():
            return None
        
        try:
            # Detect file type
            file_type = detect_file_type(abs_path)
            
            # Read file content
            with open(abs_path, 'rb') as f:
                content = f.read()
            
            # Canonicalize content
            try:
                canonical_bytes = canonicalize(content, file_type)
            except Exception:
                # If canonicalization fails, treat as binary
                file_type = 'binary'
                canonical_bytes = content
            
            # Compute canonical hash
            canonical_hash = sha256_hex(canonical_bytes)
            
            # Get relative path
            canonical_path = relative_path(abs_path, self.base_dir)
            
            # Create manifest entry
            entry = {
                'canonical_path': canonical_path,
                'canonical_hash': canonical_hash,
                'size_bytes': len(content),
                'file_type': file_type,
                'content_address': f"sha256:{canonical_hash}"
            }
            
            # Write to manifest
            self.manifest_file.write(json.dumps(entry) + '\n')
            self.manifest_file.flush()
            
            # Update checkpoint
            self.checkpoint.mark_processed(path_str)
            self.checkpoint.save()
            
            return entry
            
        except Exception as e:
            # Log error but continue
            print(f"Error processing {file_path}: {e}")
            return None
    
    def scan_directory(
        self,
        directory: Path,
        patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        progress_callback: Optional[callable] = None
    ) -> int:
        """
        Scan directory and add all matching files to manifest.
        
        Args:
            directory: Directory to scan
            patterns: Optional glob patterns to include
            exclude_patterns: Optional glob patterns to exclude
            progress_callback: Optional callback(processed, total)
            
        Returns:
            Number of files added
        """
        # Collect all files
        if patterns:
            files = []
            for pattern in patterns:
                files.extend(directory.rglob(pattern))
        else:
            files = list(directory.rglob('*'))
        
        # Filter out directories and excluded patterns
        files = [f for f in files if f.is_file()]
        
        if exclude_patterns:
            excluded_files = set()
            for pattern in exclude_patterns:
                excluded_files.update(directory.rglob(pattern))
            files = [f for f in files if f not in excluded_files]
        
        # Sort deterministically
        file_paths = deterministic_sort_paths([str(f) for f in files])
        files = [Path(p) for p in file_paths]
        
        # Process files
        added = 0
        total = len(files)
        
        for i, file_path in enumerate(files):
            entry = self.add_file(file_path)
            if entry:
                added += 1
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return added
    
    def finalize(self) -> Dict:
        """
        Finalize manifest and return summary.
        
        Returns:
            Summary dictionary with stats
        """
        self.close()
        
        # Read manifest to compute stats
        stats = {
            'total_files': 0,
            'total_bytes': 0,
            'file_types': {}
        }
        
        with open(self.output_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                stats['total_files'] += 1
                stats['total_bytes'] += entry['size_bytes']
                
                file_type = entry['file_type']
                if file_type not in stats['file_types']:
                    stats['file_types'][file_type] = 0
                stats['file_types'][file_type] += 1
        
        # Clear checkpoint on successful completion
        self.checkpoint.clear()
        
        return stats


def generate_manifest(
    repo_path: Path,
    output_path: Path,
    patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None
) -> Dict:
    """
    Convenience function to generate a complete manifest.
    
    Args:
        repo_path: Repository path to scan
        output_path: Output manifest.jsonl path
        patterns: Optional include patterns
        exclude_patterns: Optional exclude patterns
        
    Returns:
        Summary dictionary
    """
    with ManifestGenerator(output_path, base_dir=repo_path) as generator:
        generator.scan_directory(repo_path, patterns, exclude_patterns)
        return generator.finalize()

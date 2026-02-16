"""
Manifest Generator Module

Streams manifest.jsonl listing:
- canonical_path: UTF-8 canonical file path
- file_type: text, json, xml, or binary
- canonical_hash: SHA-256 of canonical bytes
- size: File size in bytes
- content_addressed_ref: Content-addressed reference

Supports checkpointing for large repositories.
"""

import json
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Set, Union

from .canonicalizer import Canonicalizer, canonical_byte_representation
from .hasher import Hasher


class ManifestGenerator:
    """
    Generates JSONL manifest files for repository contents.
    """
    
    def __init__(self, checkpoint_interval: int = 100):
        """
        Initialize manifest generator.
        
        Args:
            checkpoint_interval: Number of files to process before checkpointing
        """
        self.checkpoint_interval = checkpoint_interval
        self.processed_count = 0
        self.checkpoint_path: Optional[Path] = None
    
    @staticmethod
    def _get_canonical_path(file_path: Path, repo_root: Path) -> str:
        """
        Get canonical path relative to repository root.
        
        Args:
            file_path: Absolute file path
            repo_root: Repository root path
            
        Returns:
            Canonical relative path (UTF-8 with forward slashes)
        """
        try:
            rel_path = file_path.relative_to(repo_root)
        except ValueError:
            # File is not relative to repo root
            rel_path = file_path
        
        # Convert to forward slashes and ensure UTF-8
        return str(rel_path).replace('\\', '/')
    
    @staticmethod
    def _get_content_addressed_ref(canonical_hash: str) -> str:
        """
        Generate content-addressed reference from hash.
        
        Uses format: sha256:<hash>
        
        Args:
            canonical_hash: SHA-256 hash
            
        Returns:
            Content-addressed reference
        """
        return f"sha256:{canonical_hash}"
    
    def _should_exclude(self, file_path: Path, exclude_patterns: Set[str]) -> bool:
        """
        Check if file should be excluded based on patterns.
        
        Args:
            file_path: Path to file
            exclude_patterns: Set of patterns to exclude
            
        Returns:
            True if file should be excluded
        """
        file_str = str(file_path)
        
        for pattern in exclude_patterns:
            if pattern in file_str:
                return True
            
            # Handle wildcards
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(file_str, pattern):
                    return True
        
        return False
    
    def generate_manifest_entry(self, file_path: Path, repo_root: Path) -> Dict:
        """
        Generate a single manifest entry for a file.
        
        Args:
            file_path: Path to file
            repo_root: Repository root path
            
        Returns:
            Manifest entry dictionary
        """
        # Get canonical path
        canonical_path = self._get_canonical_path(file_path, repo_root)
        
        # Detect file type
        file_type = Canonicalizer.detect_file_type(file_path)
        
        # Get canonical bytes and hash
        canonical_bytes = canonical_byte_representation(file_path)
        canonical_hash = Hasher.hash_bytes(canonical_bytes)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Generate content-addressed reference
        content_ref = self._get_content_addressed_ref(canonical_hash)
        
        return {
            "canonical_path": canonical_path,
            "file_type": file_type,
            "canonical_hash": canonical_hash,
            "size": file_size,
            "content_addressed_ref": content_ref
        }
    
    def generate_manifest_stream(
        self,
        repo_root: Union[str, Path],
        exclude_patterns: Optional[Set[str]] = None
    ) -> Generator[Dict, None, None]:
        """
        Generate manifest entries as a stream (generator).
        
        Args:
            repo_root: Repository root path
            exclude_patterns: Patterns to exclude (e.g., {'.git', '__pycache__', '*.pyc'})
            
        Yields:
            Manifest entry dictionaries
        """
        repo_root = Path(repo_root)
        
        if exclude_patterns is None:
            exclude_patterns = {'.git', '__pycache__', 'node_modules', '.DS_Store'}
        
        # Walk repository
        for file_path in sorted(repo_root.rglob('*')):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Skip excluded files
            if self._should_exclude(file_path, exclude_patterns):
                continue
            
            try:
                entry = self.generate_manifest_entry(file_path, repo_root)
                self.processed_count += 1
                yield entry
            except Exception as e:
                # Log error but continue processing
                yield {
                    "canonical_path": self._get_canonical_path(file_path, repo_root),
                    "error": str(e),
                    "file_type": "error",
                    "canonical_hash": "",
                    "size": 0,
                    "content_addressed_ref": ""
                }
    
    def write_manifest(
        self,
        repo_root: Union[str, Path],
        output_path: Union[str, Path],
        exclude_patterns: Optional[Set[str]] = None,
        enable_checkpoints: bool = True
    ) -> int:
        """
        Write manifest to JSONL file with optional checkpointing.
        
        Args:
            repo_root: Repository root path
            output_path: Output JSONL file path
            exclude_patterns: Patterns to exclude
            enable_checkpoints: Whether to enable checkpointing
            
        Returns:
            Number of files processed
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up checkpoint path
        if enable_checkpoints:
            self.checkpoint_path = output_path.parent / f"{output_path.stem}_checkpoint.jsonl"
        
        self.processed_count = 0
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in self.generate_manifest_stream(repo_root, exclude_patterns):
                # Write entry
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                
                # Checkpoint if needed
                if (enable_checkpoints and 
                    self.checkpoint_path and 
                    self.processed_count % self.checkpoint_interval == 0):
                    
                    # Write checkpoint metadata
                    checkpoint_data = {
                        "processed_count": self.processed_count,
                        "last_file": entry.get("canonical_path", ""),
                    }
                    
                    with open(self.checkpoint_path, 'w', encoding='utf-8') as cp:
                        json.dump(checkpoint_data, cp, indent=2)
        
        # Remove checkpoint file on completion
        if enable_checkpoints and self.checkpoint_path and self.checkpoint_path.exists():
            self.checkpoint_path.unlink()
        
        return self.processed_count
    
    @staticmethod
    def load_manifest(manifest_path: Union[str, Path]) -> Generator[Dict, None, None]:
        """
        Load and parse a manifest JSONL file.
        
        Args:
            manifest_path: Path to manifest JSONL file
            
        Yields:
            Manifest entry dictionaries
        """
        manifest_path = Path(manifest_path)
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
    
    @staticmethod
    def verify_manifest(
        manifest_path: Union[str, Path],
        repo_root: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Verify that files match their manifest entries.
        
        Args:
            manifest_path: Path to manifest JSONL file
            repo_root: Repository root path
            
        Returns:
            Verification results dictionary
        """
        repo_root = Path(repo_root)
        results = {
            "total": 0,
            "verified": 0,
            "mismatched": 0,
            "missing": 0,
            "errors": []
        }
        
        for entry in ManifestGenerator.load_manifest(manifest_path):
            results["total"] += 1
            
            canonical_path = entry.get("canonical_path", "")
            expected_hash = entry.get("canonical_hash", "")
            
            if not canonical_path or not expected_hash:
                continue
            
            file_path = repo_root / canonical_path
            
            if not file_path.exists():
                results["missing"] += 1
                results["errors"].append({
                    "file": canonical_path,
                    "error": "File not found"
                })
                continue
            
            try:
                actual_hash = Hasher.hash_file(file_path)
                
                if actual_hash == expected_hash:
                    results["verified"] += 1
                else:
                    results["mismatched"] += 1
                    results["errors"].append({
                        "file": canonical_path,
                        "error": "Hash mismatch",
                        "expected": expected_hash,
                        "actual": actual_hash
                    })
            except Exception as e:
                results["errors"].append({
                    "file": canonical_path,
                    "error": str(e)
                })
        
        return results


# Convenience function
def generate_manifest(
    repo_root: Union[str, Path],
    output_path: Union[str, Path],
    exclude_patterns: Optional[Set[str]] = None
) -> int:
    """
    Generate manifest file for repository.
    
    Args:
        repo_root: Repository root path
        output_path: Output JSONL file path
        exclude_patterns: Patterns to exclude
        
    Returns:
        Number of files processed
    """
    generator = ManifestGenerator()
    return generator.write_manifest(repo_root, output_path, exclude_patterns)

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

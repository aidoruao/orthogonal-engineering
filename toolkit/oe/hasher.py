"""
Hasher module for orthogonal-engineering.

Provides SHA-256 hashing of canonical byte representations for deterministic
file hashing and Merkle tree construction.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import hashlib
from pathlib import Path
from typing import Union

from .canonicalizer import canonical_byte_representation


def hash_bytes(data: bytes) -> str:
    """
    Compute SHA-256 hash of bytes.
    
    Args:
        data: Bytes to hash
        
    Returns:
        Lowercase hexadecimal SHA-256 hash
    """
    return hashlib.sha256(data).hexdigest()


def hash_file(file_path: Union[str, Path]) -> str:
    """
    Compute SHA-256 hash of file's canonical representation.
    
    Args:
        file_path: Path to file
        
    Returns:
        Lowercase hexadecimal SHA-256 hash of canonical bytes
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file cannot be canonicalized
    """
    canonical_bytes = canonical_byte_representation(file_path)
    return hash_bytes(canonical_bytes)


def hash_vehicle_entry(vehicle_data: dict) -> str:
    """
    Compute hash for a vehicle entry from handling.meta.
    
    This provides a hook for per-vehicle hashing in the handling pipeline.
    
    Args:
        vehicle_data: Dictionary containing vehicle element data
        
    Returns:
        Lowercase hexadecimal SHA-256 hash
    """
    # Serialize vehicle data in canonical form (sorted keys)
    import json
    canonical_json = json.dumps(vehicle_data, sort_keys=True, separators=(',', ':'))
    return hash_bytes(canonical_json.encode('utf-8'))

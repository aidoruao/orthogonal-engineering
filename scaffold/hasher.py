"""
SHA-256 Hashing Module

Provides SHA-256 hashing of canonical bytes with hex lowercase output.
Supports both file-level and per-vehicle hashing hooks.
"""

import hashlib
from pathlib import Path
from typing import Union

from .canonicalizer import canonical_byte_representation


def compute_hash(data: bytes) -> str:
    """
    Compute SHA-256 hash of bytes.
    
    Args:
        data: Bytes to hash
        
    Returns:
        Hex lowercase SHA-256 hash
    """
    return hashlib.sha256(data).hexdigest()


def compute_file_hash(file_path: Union[str, Path], use_canonical: bool = True) -> str:
    """
    Compute SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        use_canonical: If True, use canonical byte representation.
                      If False, hash raw file bytes.
        
    Returns:
        Hex lowercase SHA-256 hash
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if use_canonical:
        # Use canonical representation
        canonical_bytes = canonical_byte_representation(path)
        return compute_hash(canonical_bytes)
    else:
        # Hash raw file bytes
        with open(path, 'rb') as f:
            return compute_hash(f.read())


def compute_incremental_hash(file_path: Union[str, Path], 
                            chunk_size: int = 65536) -> str:
    """
    Compute SHA-256 hash of a file incrementally (for large files).
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read (default: 64KB)
        
    Returns:
        Hex lowercase SHA-256 hash
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    sha256_hash = hashlib.sha256()
    
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()


class VehicleHasher:
    """
    Per-vehicle hashing hooks for specialized content.
    
    This class provides hooks for custom hashing logic for specific
    file types or content patterns (e.g., GTA handling.meta vehicles).
    """
    
    def __init__(self):
        """Initialize vehicle hasher."""
        self.custom_hashers = {}
    
    def register_hasher(self, vehicle_type: str, hasher_func):
        """
        Register a custom hasher for a vehicle type.
        
        Args:
            vehicle_type: Type identifier (e.g., 'gta_handling_vehicle')
            hasher_func: Function that takes bytes and returns hash string
        """
        self.custom_hashers[vehicle_type] = hasher_func
    
    def hash_vehicle(self, vehicle_type: str, data: bytes) -> str:
        """
        Hash vehicle data using custom hasher if registered.
        
        Args:
            vehicle_type: Type identifier
            data: Vehicle data bytes
            
        Returns:
            Hex lowercase SHA-256 hash
        """
        if vehicle_type in self.custom_hashers:
            return self.custom_hashers[vehicle_type](data)
        else:
            # Default to standard SHA-256
            return compute_hash(data)

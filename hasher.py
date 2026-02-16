"""
SHA-256 hashing utilities for content-addressable storage.

Provides secure hashing for files and data with verification support.
"""

import hashlib
from pathlib import Path
from typing import Union


def hash_file(filepath: Union[str, Path]) -> str:
    """
    Compute SHA-256 hash of a file.
    
    Args:
        filepath: Path to file to hash
        
    Returns:
        Hexadecimal SHA-256 hash string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in chunks for memory efficiency
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def hash_data(data: Union[str, bytes]) -> str:
    """
    Compute SHA-256 hash of data.
    
    Args:
        data: String or bytes to hash
        
    Returns:
        Hexadecimal SHA-256 hash string
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()


def verify_hash(filepath: Union[str, Path], expected_hash: str) -> bool:
    """
    Verify file hash matches expected value.
    
    Args:
        filepath: Path to file to verify
        expected_hash: Expected SHA-256 hash
        
    Returns:
        True if hash matches, False otherwise
    """
    try:
        actual_hash = hash_file(filepath)
        return actual_hash.lower() == expected_hash.lower()
    except FileNotFoundError:
        return False

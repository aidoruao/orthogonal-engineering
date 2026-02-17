"""
Hasher module for deterministic SHA-256 hashing.

Provides file-level hashing functions with optional HMAC support.
"""

import hashlib
import hmac
from pathlib import Path
from typing import Optional


def compute_sha256(data: bytes, hmac_key: Optional[bytes] = None) -> str:
    """
    Compute SHA-256 hash of data as hex lowercase.
    
    Args:
        data: Bytes to hash
        hmac_key: Optional HMAC key for authenticated hashing
        
    Returns:
        Hex lowercase SHA-256 hash string
    """
    if hmac_key is not None:
        h = hmac.new(hmac_key, data, hashlib.sha256)
        return h.hexdigest()
    else:
        return hashlib.sha256(data).hexdigest()


def hash_file(file_path: Path, hmac_key: Optional[bytes] = None) -> str:
    """
    Compute SHA-256 hash of a file.
    
    Args:
        file_path: Path to file to hash
        hmac_key: Optional HMAC key for authenticated hashing
        
    Returns:
        Hex lowercase SHA-256 hash string
    """
    with open(file_path, 'rb') as f:
        data = f.read()
    return compute_sha256(data, hmac_key)


def hash_bytes_chunked(file_path: Path, chunk_size: int = 65536, 
                       hmac_key: Optional[bytes] = None) -> str:
    """
    Compute SHA-256 hash of a file in chunks (memory efficient).
    
    Args:
        file_path: Path to file to hash
        chunk_size: Size of chunks to read (default 64KB)
        hmac_key: Optional HMAC key for authenticated hashing
        
    Returns:
        Hex lowercase SHA-256 hash string
    """
    if hmac_key is not None:
        h = hmac.new(hmac_key, b'', hashlib.sha256)
    else:
        h = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    
    return h.hexdigest()

"""
Hasher module for orthogonal-engineering.

Provides SHA-256 hashing of byte data and files for deterministic
hashing and Merkle tree construction.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.1.0
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
    return hashlib.sha256(data).hexdigest()


# Alias for backward compatibility
def hash_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of bytes (alias for compute_sha256)."""
    return compute_sha256(data)


def hash_file(file_path: Path, hmac_key: Optional[bytes] = None) -> str:
    """
    Compute SHA-256 hash of a file (raw bytes).

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


def hash_vehicle_entry(vehicle_data: dict) -> str:
    """
    Compute hash for a vehicle entry from handling.meta.

    Args:
        vehicle_data: Dictionary containing vehicle element data

    Returns:
        Lowercase hexadecimal SHA-256 hash
    """
    import json
    canonical_json = json.dumps(vehicle_data, sort_keys=True, separators=(',', ':'))
    return compute_sha256(canonical_json.encode('utf-8'))

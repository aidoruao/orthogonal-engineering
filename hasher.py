"""
Hasher module providing SHA-256 and HMAC-SHA256 utilities.

This module provides helpers to compute deterministic cryptographic hashes
for the deterministic pipeline scaffold.

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import hashlib
import hmac
from typing import Optional


def sha256_hex(data: bytes) -> str:
    """
    Compute SHA-256 hex digest of the given bytes.
    
    Args:
        data: Bytes to hash
        
    Returns:
        Hexadecimal string representation of the SHA-256 hash
    """
    return hashlib.sha256(data).hexdigest()


def hmac_sha256_hex(data: bytes, key: bytes) -> str:
    """
    Compute HMAC-SHA256 hex digest with the given key.
    
    Args:
        data: Bytes to hash
        key: Secret key for HMAC
        
    Returns:
        Hexadecimal string representation of the HMAC-SHA256
    """
    return hmac.new(key, data, hashlib.sha256).hexdigest()


def compute_hash(data: bytes, key: Optional[bytes] = None) -> str:
    """
    Compute hash with optional HMAC mode.
    
    If key is provided, returns HMAC-SHA256, otherwise returns SHA-256.
    
    Args:
        data: Bytes to hash
        key: Optional secret key for HMAC mode
        
    Returns:
        Hexadecimal string representation of the hash
    """
    if key is not None:
        return hmac_sha256_hex(data, key)
    return sha256_hex(data)

"""
Hashing Module

Provides SHA-256 hashing of canonical byte representations.
All hashes are returned as lowercase hexadecimal strings.
"""

import hashlib
from pathlib import Path
from typing import Union

from .canonicalizer import canonical_byte_representation


def compute_hash(data: bytes) -> str:
    """
    Compute SHA-256 hash of byte data.
    
    Args:
        data: Bytes to hash
        
    Returns:
        Lowercase hexadecimal SHA-256 hash
    """
    return hashlib.sha256(data).hexdigest()


def compute_file_hash(file_path: Union[str, Path]) -> str:
    """
    Compute SHA-256 hash of a file's canonical representation.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Lowercase hexadecimal SHA-256 hash
        
    Raises:
        FileNotFoundError: If file does not exist
    """
    canonical_bytes = canonical_byte_representation(file_path)
    return compute_hash(canonical_bytes)


def compute_per_vehicle_hash(file_path: Union[str, Path], vehicle_id: str) -> str:
    """
    Compute SHA-256 hash with vehicle-specific identifier.
    
    This is useful for GTA handling.meta processing where each vehicle
    has unique handling data.
    
    Args:
        file_path: Path to the file
        vehicle_id: Vehicle identifier to include in hash
        
    Returns:
        Lowercase hexadecimal SHA-256 hash
    """
    canonical_bytes = canonical_byte_representation(file_path)
    # Include vehicle ID in hash for unique identification
    vehicle_bytes = vehicle_id.encode("utf-8")
    combined = vehicle_bytes + b"|" + canonical_bytes
    return compute_hash(combined)

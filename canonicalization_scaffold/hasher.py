"""
SHA-256 Hasher Module

Provides SHA-256 hashing of canonical bytes with hex lowercase output.
Includes file-level and per-vehicle hashing hooks.
"""

import hashlib
from pathlib import Path
from typing import Union

from .canonicalizer import canonical_byte_representation


class Hasher:
    """
    SHA-256 hasher for canonical bytes.
    """
    
    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """
        Compute SHA-256 hash of bytes.
        
        Args:
            data: Input bytes
            
        Returns:
            Hex lowercase SHA-256 hash
        """
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def hash_file(file_path: Union[str, Path]) -> str:
        """
        Compute SHA-256 hash of file's canonical representation.
        
        This is the main entry point for file hashing.
        
        Process:
        1. Get canonical byte representation
        2. Compute SHA-256 hash
        3. Return hex lowercase
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex lowercase SHA-256 hash
        """
        canonical_bytes = canonical_byte_representation(file_path)
        return Hasher.hash_bytes(canonical_bytes)
    
    @staticmethod
    def hash_file_raw(file_path: Union[str, Path]) -> str:
        """
        Compute SHA-256 hash of raw file bytes (without canonicalization).
        
        Useful for comparison or verification purposes.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex lowercase SHA-256 hash of raw bytes
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read in chunks for large files
            while chunk := f.read(65536):  # 64KB chunks
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    @staticmethod
    def hash_vehicle(vehicle_data: dict) -> str:
        """
        Compute SHA-256 hash of vehicle data structure.
        
        This is a specialized hook for GTA handling.meta vehicle hashing.
        The dict is serialized in a canonical way before hashing.
        
        Args:
            vehicle_data: Vehicle data dictionary
            
        Returns:
            Hex lowercase SHA-256 hash
        """
        # Import here to avoid circular dependency
        from .canonicalizer import Canonicalizer
        
        # Canonicalize as JSON for deterministic hashing
        canonical_bytes = Canonicalizer.canonicalize_json(vehicle_data)
        return Hasher.hash_bytes(canonical_bytes)
    
    @staticmethod
    def verify_hash(file_path: Union[str, Path], expected_hash: str) -> bool:
        """
        Verify that a file's hash matches the expected hash.
        
        Args:
            file_path: Path to file
            expected_hash: Expected hex lowercase SHA-256 hash
            
        Returns:
            True if hashes match, False otherwise
        """
        try:
            actual_hash = Hasher.hash_file(file_path)
            return actual_hash.lower() == expected_hash.lower()
        except Exception:
            return False


# Convenience functions
def hash_file(file_path: Union[str, Path]) -> str:
    """
    Compute SHA-256 hash of file's canonical representation.
    
    Args:
        file_path: Path to file
        
    Returns:
        Hex lowercase SHA-256 hash
    """
    return Hasher.hash_file(file_path)


def hash_bytes(data: bytes) -> str:
    """
    Compute SHA-256 hash of bytes.
    
    Args:
        data: Input bytes
        
    Returns:
        Hex lowercase SHA-256 hash
    """
    return Hasher.hash_bytes(data)


def verify_hash(file_path: Union[str, Path], expected_hash: str) -> bool:
    """
    Verify that a file's hash matches the expected hash.
    
    Args:
        file_path: Path to file
        expected_hash: Expected hex lowercase SHA-256 hash
        
    Returns:
        True if hashes match, False otherwise
    """
    return Hasher.verify_hash(file_path, expected_hash)

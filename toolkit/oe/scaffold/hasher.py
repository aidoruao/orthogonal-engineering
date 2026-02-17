"""
<<<<<<< HEAD
SHA-256 hashing of canonical bytes.

Provides file-level and optional per-vehicle hashing hooks.
All hashes are hex lowercase for consistency.
=======
Hashing Module

Provides SHA-256 hashing of canonical byte representations.
All hashes are returned as lowercase hexadecimal strings.
>>>>>>> copilot/add-deterministic-auditable-scaffold
"""

import hashlib
from pathlib import Path
<<<<<<< HEAD
from typing import Union, Optional, Callable
=======
from typing import Union
>>>>>>> copilot/add-deterministic-auditable-scaffold

from .canonicalizer import canonical_byte_representation


<<<<<<< HEAD
def hash_bytes(data: bytes) -> str:
    """
    Hash bytes with SHA-256, return hex lowercase.
=======
def compute_hash(data: bytes) -> str:
    """
    Compute SHA-256 hash of byte data.
>>>>>>> copilot/add-deterministic-auditable-scaffold
    
    Args:
        data: Bytes to hash
        
    Returns:
<<<<<<< HEAD
        Lowercase hex SHA-256 hash
        
    Examples:
        >>> hash_bytes(b"Hello, World!")
        'dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f'
    """
    return hashlib.sha256(data).hexdigest().lower()


def hash_file(file_path: Union[str, Path], 
              canonical: bool = True,
              hook: Optional[Callable[[bytes], bytes]] = None) -> str:
    """
    Hash a file using SHA-256.
    
    Args:
        file_path: Path to file
        canonical: If True, use canonical byte representation
        hook: Optional transformation hook applied before hashing
        
    Returns:
        Lowercase hex SHA-256 hash
        
    Examples:
        >>> hash_file("config.json")
        'a1b2c3d4...'
        
        >>> # With custom hook
        >>> hash_file("data.txt", hook=lambda b: b.upper())
        'e5f6g7h8...'
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get bytes
    if canonical:
        data = canonical_byte_representation(path)
    else:
        data = path.read_bytes()
    
    # Apply hook if provided
    if hook is not None:
        data = hook(data)
    
    # Hash
    return hash_bytes(data)


def hash_directory_tree(dir_path: Union[str, Path],
                       canonical: bool = True,
                       pattern: str = "*") -> dict:
    """
    Hash all files in a directory tree.
    
    Args:
        dir_path: Path to directory
        canonical: If True, use canonical byte representation
        pattern: Glob pattern for file matching
        
    Returns:
        Dictionary mapping relative paths to hashes
        
    Examples:
        >>> hash_directory_tree("src/")
        {'main.py': 'abc123...', 'utils.py': 'def456...'}
    """
    dir_path = Path(dir_path)
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")
    
    hashes = {}
    
    for file_path in sorted(dir_path.rglob(pattern)):
        if file_path.is_file():
            rel_path = file_path.relative_to(dir_path)
            try:
                hashes[str(rel_path)] = hash_file(file_path, canonical=canonical)
            except Exception as e:
                # Log but continue
                hashes[str(rel_path)] = f"ERROR: {e}"
    
    return hashes


# Per-vehicle hashing hooks for custom transformations
class HashingHooks:
    """
    Collection of optional hashing hooks for custom transformations.
    """
    
    @staticmethod
    def uppercase_hook(data: bytes) -> bytes:
        """Convert to uppercase before hashing."""
        return data.upper()
    
    @staticmethod
    def lowercase_hook(data: bytes) -> bytes:
        """Convert to lowercase before hashing."""
        return data.lower()
    
    @staticmethod
    def strip_whitespace_hook(data: bytes) -> bytes:
        """Strip all whitespace before hashing."""
        return b''.join(data.split())


# Unit tests and examples
def _test_hash_bytes():
    """Test basic byte hashing."""
    # Known SHA-256 hash
    data = b"Hello, World!"
    expected = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
    assert hash_bytes(data) == expected
    
    # Empty string
    assert hash_bytes(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    
    print("✓ hash_bytes tests passed")


def _test_hooks():
    """Test hashing hooks."""
    data = b"TeSt DaTa"
    
    # Uppercase hook
    upper_hash = hash_bytes(HashingHooks.uppercase_hook(data))
    expected_upper = hash_bytes(b"TEST DATA")
    assert upper_hash == expected_upper
    
    # Lowercase hook
    lower_hash = hash_bytes(HashingHooks.lowercase_hook(data))
    expected_lower = hash_bytes(b"test data")
    assert lower_hash == expected_lower
    
    print("✓ Hashing hooks tests passed")


if __name__ == "__main__":
    _test_hash_bytes()
    _test_hooks()
    print("\n✓ All hasher tests passed")
=======
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
>>>>>>> copilot/add-deterministic-auditable-scaffold

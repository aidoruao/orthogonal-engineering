"""
Unit tests for hasher module.
"""

import tempfile
from pathlib import Path
import pytest
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from toolkit.oe.hasher import (
    compute_sha256,
    hash_file,
    hash_bytes_chunked,
)


def test_compute_sha256_basic():
    """Test basic SHA-256 computation."""
    data = b"Hello, World!"
    hash_result = compute_sha256(data)
    
    # Should be hex lowercase
    assert len(hash_result) == 64
    assert hash_result == hash_result.lower()
    
    # Verify it's deterministic
    hash_result2 = compute_sha256(data)
    assert hash_result == hash_result2


def test_compute_sha256_empty():
    """Test SHA-256 of empty data."""
    hash_result = compute_sha256(b"")
    
    # Known SHA-256 of empty string
    expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert hash_result == expected


def test_compute_sha256_with_hmac():
    """Test SHA-256 with HMAC key."""
    data = b"Hello, World!"
    key = b"secret_key"
    
    hash_result = compute_sha256(data, hmac_key=key)
    
    # Should be hex lowercase
    assert len(hash_result) == 64
    assert hash_result == hash_result.lower()
    
    # Should be different from non-HMAC hash
    normal_hash = compute_sha256(data)
    assert hash_result != normal_hash


def test_hash_file():
    """Test hashing a file."""
    data = b"Test file content"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(data)
        f.flush()
        temp_path = Path(f.name)
    
    try:
        hash_result = hash_file(temp_path)
        
        # Should match direct hash of data
        expected = compute_sha256(data)
        assert hash_result == expected
    finally:
        temp_path.unlink()


def test_hash_file_with_hmac():
    """Test hashing a file with HMAC."""
    data = b"Test file content"
    key = b"secret_key"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(data)
        f.flush()
        temp_path = Path(f.name)
    
    try:
        hash_result = hash_file(temp_path, hmac_key=key)
        
        # Should match HMAC hash of data
        expected = compute_sha256(data, hmac_key=key)
        assert hash_result == expected
    finally:
        temp_path.unlink()


def test_hash_bytes_chunked():
    """Test chunked hashing."""
    data = b"A" * 100000  # 100KB
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(data)
        f.flush()
        temp_path = Path(f.name)
    
    try:
        # Hash with small chunk size
        hash_result = hash_bytes_chunked(temp_path, chunk_size=1024)
        
        # Should match non-chunked hash
        expected = compute_sha256(data)
        assert hash_result == expected
    finally:
        temp_path.unlink()


def test_hash_bytes_chunked_with_hmac():
    """Test chunked hashing with HMAC."""
    data = b"B" * 100000  # 100KB
    key = b"secret_key"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(data)
        f.flush()
        temp_path = Path(f.name)
    
    try:
        hash_result = hash_bytes_chunked(temp_path, chunk_size=1024, hmac_key=key)
        
        # Should match HMAC hash
        expected = compute_sha256(data, hmac_key=key)
        assert hash_result == expected
    finally:
        temp_path.unlink()


def test_deterministic_hashing():
    """Test that hashing is deterministic."""
    data = b"Deterministic test"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(data)
        f.flush()
        temp_path = Path(f.name)
    
    try:
        hash1 = hash_file(temp_path)
        hash2 = hash_file(temp_path)
        hash3 = hash_bytes_chunked(temp_path)
        
        # All should be identical
        assert hash1 == hash2 == hash3
    finally:
        temp_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

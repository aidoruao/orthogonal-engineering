"""
Unit tests for hasher module.
"""

import tempfile
import pytest
from pathlib import Path

from toolkit.oe.scaffold.hasher import (
    hash_bytes,
    hash_file,
    hash_directory_tree,
    HashingHooks
)


def test_hash_bytes_known_value():
    """Test hashing with known SHA-256 value."""
    # Known SHA-256 hash for "Hello, World!"
    data = b"Hello, World!"
    expected = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
    
    assert hash_bytes(data) == expected


def test_hash_bytes_empty():
    """Test hashing empty bytes."""
    # Known SHA-256 for empty string
    expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    
    assert hash_bytes(b"") == expected


def test_hash_bytes_lowercase():
    """Test hash output is lowercase."""
    result = hash_bytes(b"test")
    
    assert result == result.lower()
    assert len(result) == 64  # SHA-256 hex length


def test_hash_file_canonical():
    """Test hashing file with canonical representation."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content\r\n")
        temp_path = f.name
    
    try:
        # Canonical should normalize line endings
        result = hash_file(temp_path, canonical=True)
        
        # Hash of "Test content\n" (LF normalized)
        expected = hash_bytes(b"Test content\n")
        assert result == expected
    finally:
        Path(temp_path).unlink()


def test_hash_file_non_canonical():
    """Test hashing file without canonicalization."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
        data = b"Test\r\ncontent"
        f.write(data)
        temp_path = f.name
    
    try:
        # Non-canonical should preserve exact bytes
        result = hash_file(temp_path, canonical=False)
        expected = hash_bytes(data)
        
        assert result == expected
    finally:
        Path(temp_path).unlink()


def test_hash_file_with_hook():
    """Test hashing with transformation hook."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("TeSt")
        temp_path = f.name
    
    try:
        # Hash with uppercase hook
        result = hash_file(temp_path, canonical=False, hook=lambda b: b.upper())
        expected = hash_bytes(b"TEST")
        
        assert result == expected
    finally:
        Path(temp_path).unlink()


def test_hash_file_not_found():
    """Test FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        hash_file("/nonexistent/file.txt")


def test_hash_directory_tree():
    """Test hashing directory tree."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "a.txt").write_text("File A")
        (tmpdir / "b.txt").write_text("File B")
        (tmpdir / "subdir").mkdir()
        (tmpdir / "subdir" / "c.txt").write_text("File C")
        
        # Hash directory
        result = hash_directory_tree(tmpdir, pattern="**/*.txt")
        
        assert "a.txt" in result
        assert "b.txt" in result
        assert "subdir/c.txt" in result or "subdir\\c.txt" in result
        
        # Verify hashes are valid
        for path, file_hash in result.items():
            assert len(file_hash) == 64 or file_hash.startswith("ERROR:")


def test_hashing_hooks_uppercase():
    """Test uppercase hook."""
    data = b"TeSt DaTa"
    result = HashingHooks.uppercase_hook(data)
    
    assert result == b"TEST DATA"


def test_hashing_hooks_lowercase():
    """Test lowercase hook."""
    data = b"TeSt DaTa"
    result = HashingHooks.lowercase_hook(data)
    
    assert result == b"test data"


def test_hashing_hooks_strip_whitespace():
    """Test whitespace stripping hook."""
    data = b"  Test  \n Data  \t"
    result = HashingHooks.strip_whitespace_hook(data)
    
    assert result == b"TestData"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

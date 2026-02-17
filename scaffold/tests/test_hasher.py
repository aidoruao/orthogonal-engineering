"""
Unit tests for hasher module.

Tests SHA-256 hashing functionality.
"""

import tempfile
import unittest
from pathlib import Path

from scaffold.hasher import (
    VehicleHasher,
    compute_file_hash,
    compute_hash,
    compute_incremental_hash,
)


class TestHasher(unittest.TestCase):
    """Test cases for hasher module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_compute_hash(self):
        """Test basic hash computation."""
        data = b"Hello World"
        hash_value = compute_hash(data)
        
        # Should be 64 character hex string
        self.assertEqual(len(hash_value), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash_value))
        
        # Should be deterministic
        self.assertEqual(compute_hash(data), hash_value)
        
        # Known hash for "Hello World"
        expected = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
        self.assertEqual(hash_value, expected)
    
    def test_compute_file_hash_canonical(self):
        """Test file hash with canonical representation."""
        # Create text file with CRLF
        text_file = self.test_path / "test.txt"
        text_file.write_text('Line1\r\nLine2', encoding='utf-8')
        
        hash_canonical = compute_file_hash(text_file, use_canonical=True)
        
        # Create same file with LF only
        text_file2 = self.test_path / "test2.txt"
        text_file2.write_text('Line1\nLine2', encoding='utf-8')
        
        hash_canonical2 = compute_file_hash(text_file2, use_canonical=True)
        
        # Canonical hashes should match (normalized line endings)
        self.assertEqual(hash_canonical, hash_canonical2)
    
    def test_compute_file_hash_raw(self):
        """Test file hash without canonicalization."""
        text_file = self.test_path / "test.txt"
        text_file.write_text('Line1\r\nLine2', encoding='utf-8')
        
        hash_raw = compute_file_hash(text_file, use_canonical=False)
        
        # Should be different from canonical
        hash_canonical = compute_file_hash(text_file, use_canonical=True)
        self.assertNotEqual(hash_raw, hash_canonical)
    
    def test_compute_incremental_hash(self):
        """Test incremental hashing for large files."""
        # Create a larger file
        large_file = self.test_path / "large.txt"
        data = b"A" * 100000  # 100KB
        large_file.write_bytes(data)
        
        hash_incremental = compute_incremental_hash(large_file, chunk_size=1024)
        hash_direct = compute_hash(data)
        
        # Should match direct hash
        self.assertEqual(hash_incremental, hash_direct)
    
    def test_file_not_found(self):
        """Test handling of non-existent files."""
        with self.assertRaises(FileNotFoundError):
            compute_file_hash(self.test_path / "nonexistent.txt")
    
    def test_vehicle_hasher(self):
        """Test vehicle hasher with custom hashers."""
        hasher = VehicleHasher()
        
        # Test default hasher
        data = b"test data"
        hash1 = hasher.hash_vehicle("unknown_type", data)
        self.assertEqual(hash1, compute_hash(data))
        
        # Register custom hasher
        def custom_hasher(data):
            return "custom_" + compute_hash(data)
        
        hasher.register_hasher("custom_type", custom_hasher)
        
        # Test custom hasher
        hash2 = hasher.hash_vehicle("custom_type", data)
        self.assertTrue(hash2.startswith("custom_"))
        self.assertNotEqual(hash1, hash2)


if __name__ == '__main__':
    unittest.main()

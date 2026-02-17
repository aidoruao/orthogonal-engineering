"""
Unit tests for hasher module
"""

import tempfile
import unittest
from pathlib import Path

from canonicalization_scaffold.hasher import (
    Hasher,
    hash_bytes,
    hash_file,
    verify_hash,
)


class TestHasher(unittest.TestCase):
    """Test cases for Hasher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_hash_bytes(self):
        """Test SHA-256 hashing of bytes."""
        data = b"Hello, World!"
        result = Hasher.hash_bytes(data)
        
        # Should be hex lowercase
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)  # SHA-256 is 64 hex chars
        self.assertTrue(all(c in '0123456789abcdef' for c in result))
        
        # Known hash for "Hello, World!"
        import hashlib
        expected = hashlib.sha256(data).hexdigest()
        self.assertEqual(result, expected)
    
    def test_hash_bytes_empty(self):
        """Test hashing of empty bytes."""
        data = b""
        result = Hasher.hash_bytes(data)
        
        # Known SHA-256 of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(result, expected)
    
    def test_hash_file(self):
        """Test SHA-256 hashing of file."""
        # Create test file
        test_file = self.temp_path / "test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Hello\nWorld")
        
        result = hash_file(test_file)
        
        # Should be hex lowercase
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)
        
        # Should match canonical representation
        from canonicalization_scaffold.canonicalizer import canonical_byte_representation
        import hashlib
        
        canonical_bytes = canonical_byte_representation(test_file)
        expected = hashlib.sha256(canonical_bytes).hexdigest()
        self.assertEqual(result, expected)
    
    def test_hash_file_raw(self):
        """Test raw file hashing (without canonicalization)."""
        # Create test file with CRLF
        test_file = self.temp_path / "test.txt"
        with open(test_file, 'wb') as f:
            f.write(b"Hello\r\nWorld")
        
        result = Hasher.hash_file_raw(test_file)
        
        # Should hash raw bytes (with CRLF)
        import hashlib
        expected = hashlib.sha256(b"Hello\r\nWorld").hexdigest()
        self.assertEqual(result, expected)
    
    def test_hash_file_vs_raw(self):
        """Test difference between canonical and raw hashing."""
        # Create test file with CRLF
        test_file = self.temp_path / "test.txt"
        with open(test_file, 'wb') as f:
            f.write(b"Hello\r\nWorld")
        
        canonical_hash = hash_file(test_file)
        raw_hash = Hasher.hash_file_raw(test_file)
        
        # Should be different (canonical normalizes to LF)
        self.assertNotEqual(canonical_hash, raw_hash)
    
    def test_hash_file_nonexistent(self):
        """Test hashing non-existent file."""
        test_file = self.temp_path / "nonexistent.txt"
        
        with self.assertRaises(FileNotFoundError):
            hash_file(test_file)
    
    def test_hash_vehicle(self):
        """Test vehicle data hashing."""
        vehicle_data = {
            "handlingName": "ADDER",
            "fMass": 1600.0,
            "fInitialDragCoeff": 10.5
        }
        
        result = Hasher.hash_vehicle(vehicle_data)
        
        # Should be deterministic
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)
        
        # Hashing again should give same result
        result2 = Hasher.hash_vehicle(vehicle_data)
        self.assertEqual(result, result2)
    
    def test_hash_vehicle_key_order(self):
        """Test that vehicle hash is independent of key order."""
        vehicle1 = {"z": 1, "a": 2, "m": 3}
        vehicle2 = {"a": 2, "m": 3, "z": 1}
        
        hash1 = Hasher.hash_vehicle(vehicle1)
        hash2 = Hasher.hash_vehicle(vehicle2)
        
        # Should be same (keys are sorted during canonicalization)
        self.assertEqual(hash1, hash2)
    
    def test_verify_hash_valid(self):
        """Test hash verification for valid file."""
        # Create test file
        test_file = self.temp_path / "test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Hello")
        
        # Get hash
        expected_hash = hash_file(test_file)
        
        # Verify
        self.assertTrue(verify_hash(test_file, expected_hash))
    
    def test_verify_hash_invalid(self):
        """Test hash verification for invalid hash."""
        # Create test file
        test_file = self.temp_path / "test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Hello")
        
        # Wrong hash
        wrong_hash = "0" * 64
        
        # Verify should fail
        self.assertFalse(verify_hash(test_file, wrong_hash))
    
    def test_verify_hash_case_insensitive(self):
        """Test hash verification is case-insensitive."""
        # Create test file
        test_file = self.temp_path / "test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Hello")
        
        # Get hash
        expected_hash = hash_file(test_file)
        
        # Verify with uppercase
        self.assertTrue(verify_hash(test_file, expected_hash.upper()))
    
    def test_verify_hash_nonexistent(self):
        """Test hash verification for non-existent file."""
        test_file = self.temp_path / "nonexistent.txt"
        
        # Should return False (not raise exception)
        self.assertFalse(verify_hash(test_file, "0" * 64))
    
    def test_hash_consistency(self):
        """Test that hashing is consistent across multiple calls."""
        # Create test file
        test_file = self.temp_path / "test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Consistency test")
        
        # Hash multiple times
        hash1 = hash_file(test_file)
        hash2 = hash_file(test_file)
        hash3 = hash_file(test_file)
        
        # All should be identical
        self.assertEqual(hash1, hash2)
        self.assertEqual(hash2, hash3)


if __name__ == '__main__':
    unittest.main()

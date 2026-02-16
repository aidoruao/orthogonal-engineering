"""
Test module for hasher.py

Tests SHA-256 hashing of canonical byte representations.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from toolkit.oe.hasher import hash_bytes, hash_file, hash_vehicle_entry


class TestHasher(unittest.TestCase):
    """Test cases for hasher module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_hash_bytes_sha256(self):
        """Test hash_bytes produces SHA-256 hash."""
        data = b"Hello, World!"
        result = hash_bytes(data)
        
        # Verify it's a valid SHA-256 hash (64 hex characters)
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))
        
        # Verify it matches expected SHA-256
        expected = hashlib.sha256(data).hexdigest()
        self.assertEqual(result, expected)
    
    def test_hash_bytes_lowercase(self):
        """Test hash_bytes returns lowercase hex."""
        data = b"Test"
        result = hash_bytes(data)
        
        # Should be lowercase
        self.assertEqual(result, result.lower())
    
    def test_hash_file_text(self):
        """Test hash_file with text file."""
        file_path = self.test_path / 'test.txt'
        
        # Write text with CRLF
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("line1\r\nline2\r\n")
        
        result = hash_file(file_path)
        
        # Should hash canonical form (LF normalized)
        canonical_bytes = b"line1\nline2\n"
        expected = hashlib.sha256(canonical_bytes).hexdigest()
        self.assertEqual(result, expected)
    
    def test_hash_file_json(self):
        """Test hash_file with JSON file."""
        file_path = self.test_path / 'test.json'
        
        # Write unsorted JSON
        data = {'z': 3, 'a': 1, 'b': 2}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        result = hash_file(file_path)
        
        # Should hash canonical form (sorted, compact)
        canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        canonical_bytes = canonical_json.encode('utf-8')
        expected = hashlib.sha256(canonical_bytes).hexdigest()
        self.assertEqual(result, expected)
    
    def test_hash_file_deterministic(self):
        """Test hash_file is deterministic."""
        file_path = self.test_path / 'test.txt'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("test content")
        
        # Hash multiple times
        hash1 = hash_file(file_path)
        hash2 = hash_file(file_path)
        
        self.assertEqual(hash1, hash2)
    
    def test_hash_file_not_found(self):
        """Test hash_file raises FileNotFoundError."""
        file_path = self.test_path / 'nonexistent.txt'
        
        with self.assertRaises(FileNotFoundError):
            hash_file(file_path)
    
    def test_hash_vehicle_entry(self):
        """Test hash_vehicle_entry with vehicle data."""
        vehicle_data = {
            'handlingName': 'ADDER',
            'fMass': '1500.0',
            'fInitialDragCoeff': '10.0'
        }
        
        result = hash_vehicle_entry(vehicle_data)
        
        # Should be valid SHA-256 hash
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))
    
    def test_hash_vehicle_entry_deterministic(self):
        """Test hash_vehicle_entry is deterministic."""
        vehicle_data = {
            'handlingName': 'ADDER',
            'fMass': '1500.0',
            'fInitialDragCoeff': '10.0'
        }
        
        hash1 = hash_vehicle_entry(vehicle_data)
        hash2 = hash_vehicle_entry(vehicle_data)
        
        self.assertEqual(hash1, hash2)
    
    def test_hash_vehicle_entry_order_independent(self):
        """Test hash_vehicle_entry is independent of insertion order."""
        vehicle_data1 = {
            'handlingName': 'ADDER',
            'fMass': '1500.0',
            'fInitialDragCoeff': '10.0'
        }
        
        vehicle_data2 = {
            'fInitialDragCoeff': '10.0',
            'fMass': '1500.0',
            'handlingName': 'ADDER'
        }
        
        hash1 = hash_vehicle_entry(vehicle_data1)
        hash2 = hash_vehicle_entry(vehicle_data2)
        
        # Should be identical despite different insertion order
        self.assertEqual(hash1, hash2)
    
    def test_different_content_different_hash(self):
        """Test that different content produces different hashes."""
        file_path1 = self.test_path / 'test1.txt'
        file_path2 = self.test_path / 'test2.txt'
        
        with open(file_path1, 'w', encoding='utf-8') as f:
            f.write("content1")
        
        with open(file_path2, 'w', encoding='utf-8') as f:
            f.write("content2")
        
        hash1 = hash_file(file_path1)
        hash2 = hash_file(file_path2)
        
        self.assertNotEqual(hash1, hash2)


if __name__ == '__main__':
    unittest.main()

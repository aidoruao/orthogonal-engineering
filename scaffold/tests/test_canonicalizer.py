"""
Unit tests for canonicalizer module.

Tests canonical byte representation for text, JSON, XML, and binary files.
"""

import json
import tempfile
import unittest
from pathlib import Path

from scaffold.canonicalizer import (
    FileType,
    canonical_byte_representation,
    canonicalize_json,
    canonicalize_xml,
    detect_file_type,
    get_file_type,
    normalize_text,
)


class TestCanonicalizer(unittest.TestCase):
    """Test cases for canonicalizer module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_normalize_text(self):
        """Test text normalization."""
        # Test BOM removal
        text_with_bom = '\ufeffHello World'
        self.assertEqual(normalize_text(text_with_bom), 'Hello World')
        
        # Test line ending normalization
        text_crlf = 'Line1\r\nLine2\r\nLine3'
        normalized = normalize_text(text_crlf)
        self.assertEqual(normalized, 'Line1\nLine2\nLine3')
        
        # Test CR normalization
        text_cr = 'Line1\rLine2\rLine3'
        normalized = normalize_text(text_cr)
        self.assertEqual(normalized, 'Line1\nLine2\nLine3')
    
    def test_canonicalize_json(self):
        """Test JSON canonicalization."""
        # Test dict with unsorted keys
        data = {"z": 1, "a": 2, "m": 3}
        canonical = canonicalize_json(data)
        
        # Keys should be sorted
        self.assertEqual(canonical, b'{"a":2,"m":3,"z":1}')
        
        # Test nested objects
        nested = {"b": {"y": 1, "x": 2}, "a": 3}
        canonical = canonicalize_json(nested)
        self.assertIn(b'"a":3', canonical)
        self.assertIn(b'"b":{"x":2,"y":1}', canonical)
    
    def test_canonicalize_xml(self):
        """Test XML canonicalization."""
        xml_data = b'<root attr2="b" attr1="a"><child>text</child></root>'
        canonical = canonicalize_xml(xml_data)
        
        # Should be valid XML
        self.assertIn(b'<root', canonical)
        self.assertIn(b'</root>', canonical)
    
    def test_detect_file_type(self):
        """Test file type detection."""
        # Test JSON file
        json_file = self.test_path / "test.json"
        json_file.write_text('{"key": "value"}')
        self.assertEqual(detect_file_type(json_file), FileType.JSON)
        
        # Test text file
        text_file = self.test_path / "test.txt"
        text_file.write_text('Hello World')
        self.assertEqual(detect_file_type(text_file), FileType.TEXT)
        
        # Test Python file
        py_file = self.test_path / "test.py"
        py_file.write_text('print("hello")')
        self.assertEqual(detect_file_type(py_file), FileType.TEXT)
        
        # Test binary file
        bin_file = self.test_path / "test.bin"
        bin_file.write_bytes(b'\x00\x01\x02\x03\xff')
        self.assertEqual(detect_file_type(bin_file), FileType.BINARY)
    
    def test_canonical_byte_representation_text(self):
        """Test canonical representation for text files."""
        # Create text file with CRLF
        text_file = self.test_path / "test.txt"
        text_file.write_text('Line1\r\nLine2\r\n', encoding='utf-8')
        
        canonical = canonical_byte_representation(text_file)
        
        # Should have LF only
        self.assertEqual(canonical, b'Line1\nLine2\n')
    
    def test_canonical_byte_representation_json(self):
        """Test canonical representation for JSON files."""
        # Create JSON file with unsorted keys
        json_file = self.test_path / "test.json"
        data = {"z": 1, "a": 2}
        json_file.write_text(json.dumps(data))
        
        canonical = canonical_byte_representation(json_file)
        
        # Keys should be sorted
        self.assertEqual(canonical, b'{"a":2,"z":1}')
    
    def test_canonical_byte_representation_xml(self):
        """Test canonical representation for XML files."""
        xml_file = self.test_path / "test.xml"
        xml_file.write_text('<root><child>text</child></root>')
        
        canonical = canonical_byte_representation(xml_file)
        
        # Should be valid XML
        self.assertIn(b'<root>', canonical)
        self.assertIn(b'<child>text</child>', canonical)
    
    def test_canonical_byte_representation_binary(self):
        """Test canonical representation for binary files."""
        bin_file = self.test_path / "test.bin"
        data = b'\x00\x01\x02\x03\xff'
        bin_file.write_bytes(data)
        
        canonical = canonical_byte_representation(bin_file)
        
        # Binary should be unchanged
        self.assertEqual(canonical, data)
    
    def test_file_not_found(self):
        """Test handling of non-existent files."""
        with self.assertRaises(FileNotFoundError):
            canonical_byte_representation(self.test_path / "nonexistent.txt")
    
    def test_get_file_type(self):
        """Test get_file_type function."""
        json_file = self.test_path / "test.json"
        json_file.write_text('{}')
        
        self.assertEqual(get_file_type(json_file), FileType.JSON)


if __name__ == '__main__':
    unittest.main()

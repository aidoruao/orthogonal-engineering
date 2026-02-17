"""
Unit tests for canonicalizer module
"""

import json
import tempfile
import unittest
from pathlib import Path

from canonicalization_scaffold.canonicalizer import (
    Canonicalizer,
    canonical_byte_representation,
)


class TestCanonicalizer(unittest.TestCase):
    """Test cases for Canonicalizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_normalize_unicode(self):
        """Test Unicode NFC normalization."""
        # Test combining characters
        input_text = "café"  # May be composed or decomposed
        result = Canonicalizer._normalize_unicode(input_text)
        
        # Should be in NFC form
        import unicodedata
        self.assertEqual(result, unicodedata.normalize('NFC', input_text))
    
    def test_normalize_line_endings(self):
        """Test line ending normalization to LF."""
        # Test CRLF
        self.assertEqual(
            Canonicalizer._normalize_line_endings("line1\r\nline2"),
            "line1\nline2"
        )
        
        # Test CR
        self.assertEqual(
            Canonicalizer._normalize_line_endings("line1\rline2"),
            "line1\nline2"
        )
        
        # Test LF (should remain unchanged)
        self.assertEqual(
            Canonicalizer._normalize_line_endings("line1\nline2"),
            "line1\nline2"
        )
    
    def test_strip_bom(self):
        """Test BOM removal."""
        # UTF-8 BOM
        data_with_bom = b'\xef\xbb\xbfHello'
        self.assertEqual(
            Canonicalizer._strip_bom(data_with_bom),
            b'Hello'
        )
        
        # No BOM
        data_no_bom = b'Hello'
        self.assertEqual(
            Canonicalizer._strip_bom(data_no_bom),
            b'Hello'
        )
    
    def test_canonicalize_text(self):
        """Test text canonicalization."""
        # Test with CRLF and Unicode
        input_text = "Hello\r\nWorld\r\ncafé"
        result = Canonicalizer.canonicalize_text(input_text)
        
        # Should be UTF-8, LF, NFC
        expected = "Hello\nWorld\ncafé".encode('utf-8')
        self.assertEqual(result, expected)
    
    def test_canonicalize_json(self):
        """Test JSON canonicalization."""
        # Test dict with unsorted keys
        data = {"z": 1, "a": 2, "m": 3}
        result = Canonicalizer.canonicalize_json(data)
        
        # Should be sorted keys, compact format
        expected = b'{"a":2,"m":3,"z":1}'
        self.assertEqual(result, expected)
        
        # Test from string
        json_str = '{"z": 1, "a": 2}'
        result = Canonicalizer.canonicalize_json(json_str)
        expected = b'{"a":2,"z":1}'
        self.assertEqual(result, expected)
    
    def test_canonicalize_json_nested(self):
        """Test JSON canonicalization with nested objects."""
        data = {
            "outer": {
                "z": 1,
                "a": 2
            },
            "array": [3, 2, 1]
        }
        result = Canonicalizer.canonicalize_json(data)
        
        # Should sort keys recursively
        result_dict = json.loads(result.decode('utf-8'))
        self.assertEqual(list(result_dict.keys()), ["array", "outer"])
        self.assertEqual(list(result_dict["outer"].keys()), ["a", "z"])
    
    def test_canonicalize_xml(self):
        """Test XML canonicalization."""
        xml_str = '<root><child attr="value">Text</child></root>'
        result = Canonicalizer.canonicalize_xml(xml_str)
        
        # Should be valid UTF-8
        self.assertIsInstance(result, bytes)
        result_str = result.decode('utf-8')
        
        # Should contain the elements (order may vary)
        self.assertIn('root', result_str)
        self.assertIn('child', result_str)
    
    def test_canonicalize_binary(self):
        """Test binary canonicalization (should be identity)."""
        data = b'\x00\x01\x02\x03'
        result = Canonicalizer.canonicalize_binary(data)
        self.assertEqual(result, data)
    
    def test_detect_file_type(self):
        """Test file type detection."""
        # JSON
        self.assertEqual(
            Canonicalizer.detect_file_type(Path("test.json")),
            "json"
        )
        self.assertEqual(
            Canonicalizer.detect_file_type(Path("test.jsonl")),
            "json"
        )
        
        # XML
        self.assertEqual(
            Canonicalizer.detect_file_type(Path("test.xml")),
            "xml"
        )
        
        # Text
        self.assertEqual(
            Canonicalizer.detect_file_type(Path("test.py")),
            "text"
        )
        self.assertEqual(
            Canonicalizer.detect_file_type(Path("test.md")),
            "text"
        )
        
        # Binary (default)
        self.assertEqual(
            Canonicalizer.detect_file_type(Path("test.bin")),
            "binary"
        )
    
    def test_canonical_byte_representation_text(self):
        """Test canonical byte representation for text files."""
        # Create test file
        test_file = self.temp_path / "test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Hello\r\nWorld")
        
        result = canonical_byte_representation(test_file)
        expected = b"Hello\nWorld"
        self.assertEqual(result, expected)
    
    def test_canonical_byte_representation_json(self):
        """Test canonical byte representation for JSON files."""
        # Create test file
        test_file = self.temp_path / "test.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump({"z": 1, "a": 2}, f)
        
        result = canonical_byte_representation(test_file)
        expected = b'{"a":2,"z":1}'
        self.assertEqual(result, expected)
    
    def test_canonical_byte_representation_jsonl(self):
        """Test canonical byte representation for JSONL files."""
        # Create test file
        test_file = self.temp_path / "test.jsonl"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('{"z": 1}\n')
            f.write('{"a": 2}\n')
        
        result = canonical_byte_representation(test_file)
        # Each line should be canonicalized
        lines = result.decode('utf-8').split('\n')
        self.assertEqual(lines[0], '{"z":1}')
        self.assertEqual(lines[1], '{"a":2}')
    
    def test_canonical_byte_representation_binary(self):
        """Test canonical byte representation for binary files."""
        # Create test file
        test_file = self.temp_path / "test.bin"
        with open(test_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03')
        
        result = canonical_byte_representation(test_file)
        expected = b'\x00\x01\x02\x03'
        self.assertEqual(result, expected)
    
    def test_canonical_byte_representation_nonexistent(self):
        """Test canonical byte representation for non-existent file."""
        test_file = self.temp_path / "nonexistent.txt"
        
        with self.assertRaises(FileNotFoundError):
            canonical_byte_representation(test_file)
    
    def test_canonical_byte_representation_with_bom(self):
        """Test canonical byte representation removes BOM."""
        # Create test file with BOM
        test_file = self.temp_path / "test_bom.txt"
        with open(test_file, 'wb') as f:
            f.write(b'\xef\xbb\xbfHello')
        
        result = canonical_byte_representation(test_file)
        # BOM should be stripped
        self.assertEqual(result, b'Hello')


if __name__ == '__main__':
    unittest.main()

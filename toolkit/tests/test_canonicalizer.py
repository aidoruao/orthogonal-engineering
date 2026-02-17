"""
Test module for canonicalizer.py

Tests canonical byte representation for text, JSON, XML, and binary files.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from toolkit.oe.canonicalizer import (
    CanonicalFileType,
    canonical_byte_representation,
    canonical_path,
    detect_file_type,
)


class TestCanonicalizer(unittest.TestCase):
    """Test cases for canonicalizer module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_detect_file_type_json(self):
        """Test JSON file type detection."""
        file_path = self.test_path / 'test.json'
        file_path.touch()
        self.assertEqual(detect_file_type(file_path), CanonicalFileType.JSON)
    
    def test_detect_file_type_xml(self):
        """Test XML file type detection."""
        file_path = self.test_path / 'test.xml'
        file_path.touch()
        self.assertEqual(detect_file_type(file_path), CanonicalFileType.XML)
    
    def test_detect_file_type_text(self):
        """Test text file type detection."""
        for ext in ['.txt', '.md', '.py', '.js']:
            file_path = self.test_path / f'test{ext}'
            file_path.touch()
            self.assertEqual(detect_file_type(file_path), CanonicalFileType.TEXT)
    
    def test_detect_file_type_binary(self):
        """Test binary file type detection."""
        file_path = self.test_path / 'test.bin'
        file_path.touch()
        self.assertEqual(detect_file_type(file_path), CanonicalFileType.BINARY)
    
    def test_canonicalize_text_lf_normalization(self):
        """Test text canonicalization with line ending normalization."""
        file_path = self.test_path / 'test.txt'
        
        # Write with CRLF
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("line1\r\nline2\r\nline3")
        
        canonical = canonical_byte_representation(file_path)
        
        # Should be normalized to LF
        self.assertEqual(canonical, b"line1\nline2\nline3")
    
    def test_canonicalize_text_utf8_no_bom(self):
        """Test text canonicalization ensures UTF-8 without BOM."""
        file_path = self.test_path / 'test.txt'
        
        # Write UTF-8 content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Hello, 世界!")
        
        canonical = canonical_byte_representation(file_path)
        
        # Should not start with BOM
        self.assertNotEqual(canonical[:3], b'\xef\xbb\xbf')
        
        # Should be valid UTF-8
        self.assertEqual(canonical.decode('utf-8'), "Hello, 世界!")
    
    def test_canonicalize_json_sorted_keys(self):
        """Test JSON canonicalization with sorted keys."""
        file_path = self.test_path / 'test.json'
        
        # Write unsorted JSON
        data = {'z': 3, 'a': 1, 'b': 2}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        canonical = canonical_byte_representation(file_path)
        
        # Should have sorted keys
        expected = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        self.assertEqual(canonical, expected.encode('utf-8'))
    
    def test_canonicalize_json_compact(self):
        """Test JSON canonicalization is compact (no whitespace)."""
        file_path = self.test_path / 'test.json'
        
        # Write formatted JSON
        data = {'key': 'value', 'nested': {'a': 1}}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        canonical = canonical_byte_representation(file_path)
        
        # Should be compact
        self.assertNotIn(b'\n', canonical)
        self.assertNotIn(b'  ', canonical)
    
    def test_canonicalize_xml_c14n(self):
        """Test XML canonicalization using C14N."""
        file_path = self.test_path / 'test.xml'
        
        # Write XML with comments and formatting
        xml_content = """<?xml version="1.0"?>
<!-- This is a comment -->
<root>
    <child attr="value">text</child>
</root>"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        canonical = canonical_byte_representation(file_path)
        
        # Should be valid XML
        self.assertIn(b'<root>', canonical)
        self.assertIn(b'<child', canonical)
        
        # Comments should be removed
        self.assertNotIn(b'<!-- This is a comment -->', canonical)
    
    def test_canonicalize_binary(self):
        """Test binary file canonicalization (raw bytes)."""
        file_path = self.test_path / 'test.bin'
        
        # Write binary data
        test_bytes = b'\x00\x01\x02\xff\xfe\xfd'
        with open(file_path, 'wb') as f:
            f.write(test_bytes)
        
        canonical = canonical_byte_representation(file_path)
        
        # Should be identical to original
        self.assertEqual(canonical, test_bytes)
    
    def test_canonical_path_relative(self):
        """Test canonical path with relative path."""
        file_path = self.test_path / 'subdir' / 'file.txt'
        file_path.parent.mkdir(exist_ok=True)
        file_path.touch()
        
        canon = canonical_path(file_path, self.test_path)
        
        # Should be relative and use forward slashes
        self.assertEqual(canon, 'subdir/file.txt')
    
    def test_canonical_path_forward_slashes(self):
        """Test canonical path uses forward slashes."""
        file_path = self.test_path / 'test.txt'
        file_path.touch()
        
        canon = canonical_path(file_path)
        
        # Should not contain backslashes
        self.assertNotIn('\\', canon)
    
    def test_file_not_found_error(self):
        """Test FileNotFoundError for non-existent file."""
        file_path = self.test_path / 'nonexistent.txt'
        
        with self.assertRaises(FileNotFoundError):
            canonical_byte_representation(file_path)
    
    def test_deterministic_output(self):
        """Test that canonicalization is deterministic."""
        file_path = self.test_path / 'test.json'
        
        data = {'z': 3, 'a': 1, 'b': 2, 'nested': {'x': 10, 'y': 20}}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        # Get canonical representation multiple times
        canonical1 = canonical_byte_representation(file_path)
        canonical2 = canonical_byte_representation(file_path)
        
        # Should be identical
        self.assertEqual(canonical1, canonical2)


if __name__ == '__main__':
    unittest.main()

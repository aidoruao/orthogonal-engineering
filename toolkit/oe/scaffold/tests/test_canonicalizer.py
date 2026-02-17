"""
Unit tests for canonicalizer module.
"""

import tempfile
import json
import pytest
from pathlib import Path

from toolkit.oe.scaffold.canonicalizer import (
    normalize_text,
    canonical_json_bytes,
    canonical_xml_bytes,
    canonical_byte_representation
)


def test_normalize_text_line_endings():
    """Test text normalization handles different line endings."""
    # CRLF -> LF
    assert normalize_text("line1\r\nline2\r\nline3") == "line1\nline2\nline3"
    
    # CR -> LF
    assert normalize_text("line1\rline2\rline3") == "line1\nline2\nline3"
    
    # Mixed
    assert normalize_text("line1\r\nline2\rline3\n") == "line1\nline2\nline3\n"


def test_normalize_text_unicode():
    """Test Unicode NFC normalization."""
    import unicodedata
    
    text = "café"
    normalized = normalize_text(text)
    assert normalized == unicodedata.normalize('NFC', text)


def test_canonical_json_bytes_key_ordering():
    """Test JSON canonical form orders keys lexicographically."""
    data = {"z": 1, "a": 2, "m": 3}
    result = canonical_json_bytes(data)
    
    # Keys should be sorted alphabetically
    assert result == b'{"a":2,"m":3,"z":1}'


def test_canonical_json_bytes_nested():
    """Test nested JSON objects are canonicalized."""
    data = {"outer": {"z": 1, "a": 2}, "inner": [3, 2, 1]}
    result = canonical_json_bytes(data)
    
    # Keys sorted at all levels
    assert b'"inner":[3,2,1]' in result
    assert b'"outer":{"a":2,"z":1}' in result


def test_canonical_json_bytes_from_string():
    """Test parsing JSON from string."""
    json_str = '{"z": 1, "a": 2}'
    result = canonical_json_bytes(json_str)
    
    assert result == b'{"a":2,"z":1}'


def test_canonical_byte_representation_text():
    """Test canonical representation of text files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Line 1\r\nLine 2\rLine 3\n")
        temp_path = f.name
    
    try:
        result = canonical_byte_representation(temp_path)
        assert result == b"Line 1\nLine 2\nLine 3\n"
    finally:
        Path(temp_path).unlink()


def test_canonical_byte_representation_json():
    """Test canonical representation of JSON files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"z": 1, "a": 2}, f)
        temp_path = f.name
    
    try:
        result = canonical_byte_representation(temp_path)
        assert result == b'{"a":2,"z":1}'
    finally:
        Path(temp_path).unlink()


def test_canonical_byte_representation_binary():
    """Test binary files returned unchanged."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
        data = b'\x00\x01\x02\x03'
        f.write(data)
        temp_path = f.name
    
    try:
        result = canonical_byte_representation(temp_path)
        assert result == data
    finally:
        Path(temp_path).unlink()


def test_canonical_byte_representation_python():
    """Test Python files are treated as text."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def hello():\r\n    print('world')\r\n")
        temp_path = f.name
    
    try:
        result = canonical_byte_representation(temp_path)
        assert result == b"def hello():\n    print('world')\n"
    finally:
        Path(temp_path).unlink()


def test_canonical_byte_representation_file_not_found():
    """Test FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError):
        canonical_byte_representation("/nonexistent/file.txt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

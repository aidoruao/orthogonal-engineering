"""
Unit tests for canonicalizer module.
"""

import tempfile
import json
from pathlib import Path
import pytest
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from toolkit.oe.canonicalizer import (
    detect_file_type,
    normalize_text,
    canonical_text,
    canonical_json,
    canonical_xml,
    canonical_binary,
    canonical_byte_representation,
)


def test_detect_file_type_json():
    """Test JSON file type detection."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        f.write(b'{"key": "value"}')
        f.flush()
        temp_path = Path(f.name)
    
    try:
        assert detect_file_type(temp_path) == 'json'
    finally:
        temp_path.unlink()


def test_detect_file_type_xml():
    """Test XML file type detection."""
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as f:
        f.write(b'<root></root>')
        f.flush()
        temp_path = Path(f.name)
    
    try:
        assert detect_file_type(temp_path) == 'xml'
    finally:
        temp_path.unlink()


def test_detect_file_type_text():
    """Test text file type detection."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b'Hello, world!')
        f.flush()
        temp_path = Path(f.name)
    
    try:
        assert detect_file_type(temp_path) == 'text'
    finally:
        temp_path.unlink()


def test_detect_file_type_binary():
    """Test binary file type detection."""
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
        f.write(b'\x00\x01\x02\x03')
        f.flush()
        temp_path = Path(f.name)
    
    try:
        assert detect_file_type(temp_path) == 'binary'
    finally:
        temp_path.unlink()


def test_normalize_text_crlf():
    """Test CRLF to LF normalization."""
    text = "line1\r\nline2\r\nline3"
    normalized = normalize_text(text)
    assert normalized == "line1\nline2\nline3"


def test_normalize_text_cr():
    """Test CR to LF normalization."""
    text = "line1\rline2\rline3"
    normalized = normalize_text(text)
    assert normalized == "line1\nline2\nline3"


def test_normalize_text_nfc():
    """Test NFC Unicode normalization."""
    # Using combining characters that should be normalized
    text = "café"  # e with combining accent
    normalized = normalize_text(text)
    # Should be normalized to precomposed form
    assert len(normalized) <= len(text)


def test_canonical_text_utf8_no_bom():
    """Test canonical text removes BOM and uses UTF-8."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
        # Write UTF-8 with BOM
        f.write(b'\xef\xbb\xbfHello')
        f.flush()
        temp_path = Path(f.name)
    
    try:
        canonical = canonical_text(temp_path)
        # Should not have BOM
        assert not canonical.startswith(b'\xef\xbb\xbf')
        assert canonical == b'Hello'
    finally:
        temp_path.unlink()


def test_canonical_text_lf_endings():
    """Test canonical text uses LF line endings."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("line1\r\nline2\r\n")
        f.flush()
        temp_path = Path(f.name)
    
    try:
        canonical = canonical_text(temp_path)
        assert canonical == b'line1\nline2\n'
    finally:
        temp_path.unlink()


def test_canonical_json_sorted_keys():
    """Test canonical JSON has sorted keys."""
    data = {"z": 1, "a": 2, "m": 3}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        f.flush()
        temp_path = Path(f.name)
    
    try:
        canonical = canonical_json(temp_path)
        # Decode and check order
        canonical_str = canonical.decode('utf-8')
        # Should be {"a":2,"m":3,"z":1} (compact, sorted)
        assert canonical_str == '{"a":2,"m":3,"z":1}'
    finally:
        temp_path.unlink()


def test_canonical_json_compact():
    """Test canonical JSON is compact (no extra whitespace)."""
    data = {"key": "value"}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f, indent=2)
        f.flush()
        temp_path = Path(f.name)
    
    try:
        canonical = canonical_json(temp_path)
        canonical_str = canonical.decode('utf-8')
        # Should have no spaces
        assert ' ' not in canonical_str
        assert canonical_str == '{"key":"value"}'
    finally:
        temp_path.unlink()


def test_canonical_xml_basic():
    """Test canonical XML parsing."""
    xml_content = '<root><child attr="value">text</child></root>'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_content)
        f.flush()
        temp_path = Path(f.name)
    
    try:
        canonical = canonical_xml(temp_path)
        # Should be valid UTF-8 XML
        assert canonical.startswith(b'<root>')
    finally:
        temp_path.unlink()


def test_canonical_binary_raw():
    """Test canonical binary returns raw bytes."""
    data = b'\x00\x01\x02\x03\xff\xfe'
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
        f.write(data)
        f.flush()
        temp_path = Path(f.name)
    
    try:
        canonical = canonical_binary(temp_path)
        assert canonical == data
    finally:
        temp_path.unlink()


def test_canonical_byte_representation_returns_type():
    """Test canonical_byte_representation returns both bytes and type."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test")
        f.flush()
        temp_path = Path(f.name)
    
    try:
        canonical, file_type = canonical_byte_representation(temp_path)
        assert isinstance(canonical, bytes)
        assert file_type == 'text'
    finally:
        temp_path.unlink()


def test_canonical_byte_representation_deterministic():
    """Test canonical_byte_representation is deterministic."""
    data = {"z": 1, "a": 2}
    
    # Create two files with same data but different formatting
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f1:
        json.dump(data, f1, indent=2)
        f1.flush()
        temp_path1 = Path(f1.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
        json.dump(data, f2)
        f2.flush()
        temp_path2 = Path(f2.name)
    
    try:
        canonical1, _ = canonical_byte_representation(temp_path1)
        canonical2, _ = canonical_byte_representation(temp_path2)
        
        # Should be identical despite different source formatting
        assert canonical1 == canonical2
    finally:
        temp_path1.unlink()
        temp_path2.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

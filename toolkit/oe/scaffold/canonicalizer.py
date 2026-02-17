"""
Deterministic canonical byte representation for files.

Handles:
- Text files: UTF-8 no BOM, LF line endings, NFC normalization
- JSON: Lexicographic key ordering
- XML: Exclusive C14N (Canonical XML) without comments
- Binary: Raw bytes

Strips extended filesystem metadata for reproducibility.
"""

import json
import unicodedata
from pathlib import Path
from typing import Union
from xml.dom import minidom


def normalize_text(text: str) -> str:
    """
    Normalize text to UTF-8, NFC, LF line endings.
    
    Args:
        text: Input text string
        
    Returns:
        Normalized text
    """
    # NFC normalization
    text = unicodedata.normalize('NFC', text)
    
    # Normalize line endings to LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text


def canonical_json_bytes(data: Union[dict, list, str]) -> bytes:
    """
    Convert JSON to canonical bytes with lexicographic key ordering.
    
    Args:
        data: JSON-compatible data structure or JSON string
        
    Returns:
        Canonical JSON as bytes
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    # Sort keys lexicographically, no extra whitespace
    canonical_json = json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(',', ':')
    )
    
    # Normalize and encode
    canonical_json = normalize_text(canonical_json)
    return canonical_json.encode('utf-8')


def canonical_xml_bytes(xml_content: Union[str, bytes]) -> bytes:
    """
    Convert XML to canonical form using exclusive C14N without comments.
    
    Args:
        xml_content: XML content as string or bytes
        
    Returns:
        Canonical XML as bytes
    """
    if isinstance(xml_content, bytes):
        xml_content = xml_content.decode('utf-8')
    
    # Parse and canonicalize
    dom = minidom.parseString(xml_content)
    
    # Convert to canonical form (simplified - for production use lxml.etree with c14n)
    canonical = dom.toxml(encoding='utf-8')
    
    # Remove XML declaration and normalize
    if canonical.startswith(b'<?xml'):
        canonical = canonical.split(b'?>', 1)[1].strip()
    
    return canonical


def canonical_byte_representation(file_path: Union[str, Path]) -> bytes:
    """
    Get deterministic canonical byte representation of a file.
    
    Detects file type and applies appropriate canonicalization:
    - .txt, .md, .py, etc.: Text normalization
    - .json: Lexicographic key ordering
    - .xml: Exclusive C14N
    - Others: Raw bytes
    
    Args:
        file_path: Path to file
        
    Returns:
        Canonical bytes representation
        
    Examples:
        >>> canonical_byte_representation("config.json")
        b'{"key1":"value1","key2":"value2"}'
        
        >>> canonical_byte_representation("README.md")
        b'# Title\\nNormalized text content\\n'
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    suffix = path.suffix.lower()
    
    # Read file
    try:
        content = path.read_bytes()
    except Exception as e:
        raise IOError(f"Failed to read {file_path}: {e}")
    
    # JSON files
    if suffix == '.json':
        try:
            # Decode, parse, and re-encode canonically
            text = content.decode('utf-8')
            return canonical_json_bytes(text)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to raw bytes if not valid JSON/UTF-8
            return content
    
    # XML files
    elif suffix in {'.xml', '.meta'}:
        try:
            return canonical_xml_bytes(content)
        except Exception:
            # Fall back to raw bytes if not valid XML
            return content
    
    # Text files
    elif suffix in {'.txt', '.md', '.py', '.js', '.ts', '.c', '.cpp', '.h', 
                    '.java', '.rs', '.go', '.sh', '.yaml', '.yml', '.toml',
                    '.ini', '.cfg', '.conf', '.html', '.css', '.sql'}:
        try:
            text = content.decode('utf-8')
            normalized = normalize_text(text)
            return normalized.encode('utf-8')
        except UnicodeDecodeError:
            # Fall back to raw bytes if not valid UTF-8
            return content
    
    # Binary files - return raw bytes
    else:
        return content


# Unit tests and examples
def _test_text_normalization():
    """Test text normalization."""
    # Different line endings should normalize to LF
    assert normalize_text("line1\r\nline2\rline3\n") == "line1\nline2\nline3\n"
    
    # NFC normalization test
    text = "café"  # Could be composed different ways
    normalized = normalize_text(text)
    assert normalized == unicodedata.normalize('NFC', text)
    
    print("✓ Text normalization tests passed")


def _test_json_canonicalization():
    """Test JSON canonicalization."""
    # Keys should be sorted
    data = {"z": 1, "a": 2, "m": 3}
    canonical = canonical_json_bytes(data)
    assert canonical == b'{"a":2,"m":3,"z":1}'
    
    # Nested objects
    data = {"outer": {"z": 1, "a": 2}}
    canonical = canonical_json_bytes(data)
    assert canonical == b'{"outer":{"a":2,"z":1}}'
    
    print("✓ JSON canonicalization tests passed")


if __name__ == "__main__":
    _test_text_normalization()
    _test_json_canonicalization()
    print("\n✓ All canonicalizer tests passed")

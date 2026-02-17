"""
<<<<<<< HEAD
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
=======
Canonicalization Module

Provides deterministic canonical byte representation for various file types:
- Text files: UTF-8 no BOM, LF line endings, NFC normalization
- JSON: Lexicographic key ordering, compact representation
- XML: Exclusive C14N without comments
- Binary: Raw bytes

Strips extended filesystem metadata for deterministic hashing.
"""

import hashlib
import json
import os
import unicodedata
from pathlib import Path
from typing import Union


class FileType:
    """File type enumeration."""
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"


def detect_file_type(file_path: Union[str, Path]) -> str:
    """
    Detect file type based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File type as string (text, json, xml, binary)
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    
    if ext == ".json":
        return FileType.JSON
    elif ext in [".xml", ".xsd", ".xslt"]:
        return FileType.XML
    elif ext in [".txt", ".md", ".py", ".js", ".ts", ".c", ".cpp", ".h", ".java", 
                 ".go", ".rs", ".sh", ".bat", ".ps1", ".yaml", ".yml", ".toml", 
                 ".ini", ".cfg", ".conf", ".log", ".csv", ".html", ".css", ".sql"]:
        return FileType.TEXT
    else:
        # Default to binary for unknown extensions
        return FileType.BINARY


def normalize_text(content: str) -> str:
    """
    Normalize text content for deterministic representation.
    
    - Apply NFC Unicode normalization
    - Convert to LF line endings
    - Strip trailing whitespace from lines
    - Ensure single trailing newline
    
    Args:
        content: Text content to normalize
        
    Returns:
        Normalized text content
    """
    # Apply NFC normalization
    content = unicodedata.normalize("NFC", content)
    
    # Convert all line endings to LF
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    
    # Strip trailing whitespace from each line
    lines = content.split("\n")
    lines = [line.rstrip() for line in lines]
    
    # Join with LF and ensure single trailing newline
    content = "\n".join(lines)
    if content and not content.endswith("\n"):
        content += "\n"
    
    return content


def canonicalize_json(content: str) -> str:
    """
    Canonicalize JSON content with lexicographic key ordering.
    
    Args:
        content: JSON string to canonicalize
        
    Returns:
        Canonicalized JSON string
        
    Raises:
        ValueError: If content is not valid JSON
    """
    try:
        # Parse JSON
        data = json.loads(content)
        
        # Serialize with sorted keys, no extra whitespace
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        
        return canonical
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e}")


def canonicalize_xml(content: str) -> str:
    """
    Canonicalize XML using Exclusive C14N without comments.
    
    Note: This is a simplified implementation. For full C14N compliance,
    consider using lxml or xml.etree with proper C14N support.
    
    Args:
        content: XML string to canonicalize
        
    Returns:
        Canonicalized XML string
    """
    try:
        import xml.etree.ElementTree as ET
        
        # Parse XML
        root = ET.fromstring(content)
        
        # Canonicalize using ET.canonicalize (Python 3.8+)
        # This provides basic C14N support
        try:
            canonical = ET.canonicalize(content, strip_text=True)
            return canonical
        except AttributeError:
            # Fallback for older Python versions
            # Just normalize whitespace and return
            return ET.tostring(root, encoding="unicode", method="xml")
            
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")
>>>>>>> copilot/add-deterministic-auditable-scaffold


def canonical_byte_representation(file_path: Union[str, Path]) -> bytes:
    """
<<<<<<< HEAD
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
=======
    Generate deterministic canonical byte representation of a file.
    
    This function:
    1. Detects file type based on extension
    2. Reads file content
    3. Applies appropriate canonicalization
    4. Returns canonical bytes
    
    Strips extended filesystem metadata (timestamps, permissions, etc.)
    for deterministic hashing across different systems.
    
    Args:
        file_path: Path to the file to canonicalize
        
    Returns:
        Canonical byte representation
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file content cannot be canonicalized
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Detect file type
    file_type = detect_file_type(file_path)
    
    if file_type == FileType.BINARY:
        # Binary files: return raw bytes
        with open(file_path, "rb") as f:
            return f.read()
    
    # Text-based files: read as UTF-8
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # If UTF-8 fails, treat as binary
        with open(file_path, "rb") as f:
            return f.read()
    
    # Apply type-specific canonicalization
    if file_type == FileType.JSON:
        canonical = canonicalize_json(content)
    elif file_type == FileType.XML:
        canonical = canonicalize_xml(content)
    else:  # FileType.TEXT
        canonical = normalize_text(content)
    
    # Convert to UTF-8 bytes without BOM
    return canonical.encode("utf-8")


def get_file_info(file_path: Union[str, Path]) -> dict:
    """
    Get file information for manifest generation.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_type = detect_file_type(file_path)
    canonical_bytes = canonical_byte_representation(file_path)
    
    return {
        "path": str(file_path),
        "type": file_type,
        "size": len(canonical_bytes),
        "canonical_size": len(canonical_bytes),
    }
>>>>>>> copilot/add-deterministic-auditable-scaffold

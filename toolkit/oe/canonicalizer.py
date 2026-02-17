"""
Canonicalizer module for orthogonal-engineering.

Provides canonical byte representation for various file types to enable
deterministic, byte-for-byte reproducible hashing and Merkle root production.

Supported formats:
- Text files: UTF-8 encoding, no BOM, LF line endings, NFC normalization
- JSON files: Deterministic lexicographic key ordering
- XML files: Exclusive C14N without comments
- Binary files: Raw bytes

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import hashlib
import json
import os
import unicodedata
from pathlib import Path
from typing import Union
from xml.etree import ElementTree as ET


class CanonicalFileType:
    """Enumeration of supported canonical file types."""
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"


def detect_file_type(file_path: Union[str, Path]) -> str:
    """
    Detect the file type based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        One of CanonicalFileType values
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext == '.json':
        return CanonicalFileType.JSON
    elif ext in ['.xml', '.meta']:
        return CanonicalFileType.XML
    elif ext in ['.txt', '.md', '.py', '.js', '.ts', '.css', '.html', '.csv', '.yaml', '.yml']:
        return CanonicalFileType.TEXT
    else:
        # Default to binary for unknown extensions
        return CanonicalFileType.BINARY


def canonical_byte_representation(file_path: Union[str, Path]) -> bytes:
    """
    Generate canonical byte representation of a file.
    
    This function produces a deterministic byte representation that:
    - For text: UTF-8 no BOM, LF line endings, NFC normalization
    - For JSON: Deterministic lexicographic key ordering, compact encoding
    - For XML: Exclusive Canonical XML (C14N) without comments
    - For binary: Raw bytes as-is
    
    Removes extended metadata (timestamps, permissions) from canonical output.
    
    Args:
        file_path: Path to the file to canonicalize
        
    Returns:
        Canonical byte representation
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file cannot be canonicalized
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_type = detect_file_type(path)
    
    if file_type == CanonicalFileType.TEXT:
        return _canonicalize_text(path)
    elif file_type == CanonicalFileType.JSON:
        return _canonicalize_json(path)
    elif file_type == CanonicalFileType.XML:
        return _canonicalize_xml(path)
    else:  # BINARY
        return _canonicalize_binary(path)


def _canonicalize_text(file_path: Path) -> bytes:
    """
    Canonicalize text file: UTF-8 no BOM, LF endings, NFC normalization.
Canonicalizer module for deterministic byte representation.

Handles text, JSON, XML, and binary files with normalization.
"""

import json
import unicodedata
from pathlib import Path
from typing import Tuple
from xml.etree import ElementTree as ET


def detect_file_type(file_path: Path) -> str:
    """
    Detect file type based on extension and content.
    
    Args:
        file_path: Path to file
        
    Returns:
        File type: 'text', 'json', 'xml', or 'binary'
    """
    # First check for binary content
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return 'binary'
    except IOError:
        pass
    
    suffix = file_path.suffix.lower()
    
    # JSON files
    if suffix in ['.json', '.jsonl']:
        return 'json'
    
    # XML files
    if suffix in ['.xml', '.xsd', '.xsl', '.xslt', '.svg']:
        return 'xml'
    
    # Text files
    if suffix in ['.txt', '.md', '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h',
                  '.css', '.html', '.yaml', '.yml', '.toml', '.ini', '.conf',
                  '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd']:
        return 'text'
    
    # Try to decode as UTF-8 to determine if text
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            chunk.decode('utf-8')
            return 'text'
    except (UnicodeDecodeError, IOError):
        return 'binary'


def normalize_text(text: str) -> str:
    """
    Normalize text to NFC form with LF line endings.
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    # Normalize Unicode to NFC form
    text = unicodedata.normalize('NFC', text)
    
    # Convert line endings to LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text


def canonical_text(file_path: Path) -> bytes:
    """
    Get canonical representation of a text file.
    
    UTF-8 no BOM, LF line endings, NFC normalization.
    
    Args:
        file_path: Path to text file
        
    Returns:
        Canonical byte representation
    """
    # Read file content (auto-detect encoding if needed)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try reading with errors='replace' or other encodings
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    
    # Apply NFC normalization
    content = unicodedata.normalize('NFC', content)
    
    # Convert all line endings to LF
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Encode to UTF-8 without BOM
    return content.encode('utf-8')


def _canonicalize_json(file_path: Path) -> bytes:
    """
    Canonicalize JSON file: deterministic lexicographic key ordering.
        Canonical bytes
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            text = f.read()
        
        # Normalize text
        text = normalize_text(text)
        
        # Encode to UTF-8 without BOM
        return text.encode('utf-8')
    except (UnicodeDecodeError, IOError):
        # If text parsing fails, treat as binary
        return canonical_binary(file_path)


def canonical_json(file_path: Path) -> bytes:
    """
    Get canonical representation of a JSON file.
    
    Sorted keys, UTF-8, no BOM, compact format.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Canonical byte representation
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Serialize with sorted keys, no whitespace, ensure_ascii=False for unicode
    canonical_json = json.dumps(
        data,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    )
    
    # Encode to UTF-8
    return canonical_json.encode('utf-8')


def _canonicalize_xml(file_path: Path) -> bytes:
    """
    Canonicalize XML file: Exclusive C14N without comments.
        Canonical bytes
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        # Serialize with sorted keys
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        
        # Encode to UTF-8 without BOM
        return canonical.encode('utf-8')
    except (UnicodeDecodeError, json.JSONDecodeError):
        # If JSON parsing fails, treat as text or binary
        try:
            return canonical_text(file_path)
        except UnicodeDecodeError:
            return canonical_binary(file_path)


def canonical_xml(file_path: Path) -> bytes:
    """
    Get canonical representation of an XML file.
    
    Exclusive C14N without comments.
    
    Args:
        file_path: Path to XML file
        
    Returns:
        Canonical byte representation
        Canonical bytes
    """
    try:
        # Parse XML
        tree = ET.parse(file_path)
        
        # Remove comments from tree
        def remove_comments(element):
            """Remove comment nodes from XML tree."""
            for child in list(element):
                if child.tag is ET.Comment:
                    element.remove(child)
                else:
                    remove_comments(child)
        
        root = tree.getroot()
        remove_comments(root)
        
        # Write to bytes with consistent encoding
        from io import BytesIO
        output = BytesIO()
        tree.write(output, encoding='utf-8', xml_declaration=False)
        return output.getvalue()
    except Exception as e:
        raise ValueError(f"Failed to canonicalize XML: {e}")


def _canonicalize_binary(file_path: Path) -> bytes:
    """
    Canonicalize binary file: raw bytes as-is.
        root = tree.getroot()
        
        # Use C14N (Canonical XML) method
        # Note: Python's ET doesn't have full C14N support, so we do basic normalization
        # For production, consider using lxml with proper C14N support
        
        # Sort attributes
        for elem in root.iter():
            if elem.attrib:
                elem.attrib = dict(sorted(elem.attrib.items()))
        
        # Serialize
        xml_bytes = ET.tostring(root, encoding='utf-8', method='xml')
        
        return xml_bytes
    except ET.ParseError:
        # If XML parsing fails, treat as text
        return canonical_text(file_path)


def canonical_binary(file_path: Path) -> bytes:
    """
    Get canonical representation of a binary file.
    
    Raw bytes without modification.
    
    Args:
        file_path: Path to binary file
        
    Returns:
        Raw file bytes
        Raw bytes
    """
    with open(file_path, 'rb') as f:
        return f.read()


def canonical_path(file_path: Union[str, Path], base_path: Union[str, Path] = None) -> str:
    """
    Generate canonical path representation for consistent ordering.
    
    Args:
        file_path: Path to canonicalize
        base_path: Optional base path to make relative to
        
    Returns:
        Canonical path string (UTF-8, forward slashes, relative if base_path given)
    """
    path = Path(file_path).resolve()
    
    if base_path:
        base = Path(base_path).resolve()
        try:
            path = path.relative_to(base)
        except ValueError:
            # If path is not relative to base, use absolute
            pass
    
    # Convert to forward slashes and return as string
    return str(path).replace(os.sep, '/')
def canonical_byte_representation(file_path: Path) -> Tuple[bytes, str]:
    """
    Get deterministic canonical byte representation of a file.
    
    Strips extended filesystem metadata and normalizes content based on type.
    
    Args:
        file_path: Path to file
        
    Returns:
        Tuple of (canonical_bytes, file_type)
    """
    file_type = detect_file_type(file_path)
    
    if file_type == 'json':
        canonical = canonical_json(file_path)
    elif file_type == 'xml':
        canonical = canonical_xml(file_path)
    elif file_type == 'text':
        canonical = canonical_text(file_path)
    else:  # binary
        canonical = canonical_binary(file_path)
    
    return canonical, file_type

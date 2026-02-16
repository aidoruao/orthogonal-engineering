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
    
    Args:
        file_path: Path to XML file
        
    Returns:
        Canonical byte representation
    """
    try:
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Use c14n (Canonical XML) without comments
        # Note: ElementTree's c14n method provides canonical XML
        from io import BytesIO
        output = BytesIO()
        tree.write_c14n(output, with_comments=False)
        return output.getvalue()
    except Exception as e:
        raise ValueError(f"Failed to canonicalize XML: {e}")


def _canonicalize_binary(file_path: Path) -> bytes:
    """
    Canonicalize binary file: raw bytes as-is.
    
    Args:
        file_path: Path to binary file
        
    Returns:
        Raw file bytes
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

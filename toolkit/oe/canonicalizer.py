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
Version: 1.1.0
"""

import json
import os
import unicodedata
from pathlib import Path
from typing import Tuple, Union
from xml.etree import ElementTree as ET


class CanonicalFileType:
    """Enumeration of supported canonical file types."""
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"


def detect_file_type(file_path: Union[str, Path]) -> str:
    """
    Detect file type based on extension and content.

    Args:
        file_path: Path to file

    Returns:
        File type: 'text', 'json', 'xml', or 'binary'
    """
    file_path = Path(file_path)

    # First check for binary content (null bytes)
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            if b'\x00' in chunk:
                return 'binary'
    except IOError:
        pass

    suffix = file_path.suffix.lower()

    if suffix in ['.json', '.jsonl']:
        return 'json'
    if suffix in ['.xml', '.xsd', '.xsl', '.xslt', '.svg', '.meta']:
        return 'xml'
    if suffix in ['.txt', '.md', '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h',
                  '.css', '.html', '.yaml', '.yml', '.toml', '.ini', '.conf',
                  '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd', '.csv']:
        return 'text'

    # Try to decode as UTF-8 to determine if text
    try:
        with open(file_path, 'rb') as f:
            f.read(8192).decode('utf-8')
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
    text = unicodedata.normalize('NFC', text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text


def canonical_text(file_path: Union[str, Path]) -> bytes:
    """
    Get canonical representation of a text file.

    UTF-8 no BOM, LF line endings, NFC normalization.

    Args:
        file_path: Path to text file

    Returns:
        Canonical byte representation
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

    content = unicodedata.normalize('NFC', content)
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    return content.encode('utf-8')


def canonical_json(file_path: Union[str, Path]) -> bytes:
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

    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return canonical.encode('utf-8')


def canonical_xml(file_path: Union[str, Path]) -> bytes:
    """
    Get canonical representation of an XML file.

    Exclusive C14N without comments.

    Args:
        file_path: Path to XML file

    Returns:
        Canonical byte representation
    """
    try:
        tree = ET.parse(file_path)

        def remove_comments(element):
            for child in list(element):
                if child.tag is ET.Comment:
                    element.remove(child)
                else:
                    remove_comments(child)

        root = tree.getroot()
        remove_comments(root)

        from io import BytesIO
        output = BytesIO()
        tree.write(output, encoding='utf-8', xml_declaration=False)
        return output.getvalue()
    except ET.ParseError as exc:
        raise ValueError(f"Failed to canonicalize XML: {exc}")


def canonical_binary(file_path: Union[str, Path]) -> bytes:
    """
    Get canonical representation of a binary file.

    Raw bytes without modification.

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
            pass

    return str(path).replace(os.sep, '/')


def canonical_byte_representation(file_path: Union[str, Path]) -> Tuple[bytes, str]:
    """
    Get deterministic canonical byte representation of a file.

    Args:
        file_path: Path to file

    Returns:
        Tuple of (canonical_bytes, file_type)
    """
    file_type = detect_file_type(file_path)

    if file_type == 'json':
        data = canonical_json(file_path)
    elif file_type == 'xml':
        data = canonical_xml(file_path)
    elif file_type == 'text':
        data = canonical_text(file_path)
    else:
        data = canonical_binary(file_path)

    return data, file_type

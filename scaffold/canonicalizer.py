"""
Canonical Byte Representation Module

Provides deterministic canonical byte representation for various file types:
- Text: UTF-8 no BOM, LF line endings, NFC normalization
- JSON: Deterministic lexicographic key ordering
- XML: Exclusive C14N without comments
- Binary: Raw bytes

Strips extended filesystem metadata for reproducibility.
"""

import hashlib
import json
import os
import unicodedata
from pathlib import Path
from typing import Union
from xml.etree import ElementTree as ET


class FileType:
    """File type constants."""
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"


def detect_file_type(file_path: Union[str, Path]) -> str:
    """
    Detect file type based on extension and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File type string (text, json, xml, binary)
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    # Check by extension
    if suffix in ['.json', '.jsonl']:
        return FileType.JSON
    elif suffix in ['.xml', '.xsd', '.xsl', '.xslt', '.svg']:
        return FileType.XML
    elif suffix in ['.txt', '.md', '.py', '.js', '.java', '.c', '.cpp', '.h', 
                    '.cs', '.go', '.rs', '.sh', '.bat', '.yaml', '.yml', 
                    '.toml', '.ini', '.cfg', '.conf']:
        return FileType.TEXT
    
    # Try to detect by content
    try:
        with open(path, 'rb') as f:
            header = f.read(512)
        
        # Check for null bytes (binary)
        if b'\x00' in header:
            return FileType.BINARY
            
        # Try to decode as text
        try:
            header.decode('utf-8')
            # Check if it's JSON
            if path.suffix.lower() in ['.json', '.jsonl'] or header.strip().startswith(b'{'):
                return FileType.JSON
            # Check if it's XML
            if header.strip().startswith(b'<?xml') or header.strip().startswith(b'<'):
                return FileType.XML
            return FileType.TEXT
        except UnicodeDecodeError:
            return FileType.BINARY
            
    except Exception:
        return FileType.BINARY


def normalize_text(text: str) -> str:
    """
    Normalize text to canonical form.
    
    - Convert to NFC (Canonical Decomposition, followed by Canonical Composition)
    - Normalize line endings to LF
    - Remove BOM if present
    
    Args:
        text: Input text string
        
    Returns:
        Normalized text string
    """
    # Remove BOM if present
    if text.startswith('\ufeff'):
        text = text[1:]
    
    # Normalize to NFC
    text = unicodedata.normalize('NFC', text)
    
    # Normalize line endings to LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text


def canonicalize_json(data: Union[str, bytes, dict]) -> bytes:
    """
    Canonicalize JSON with deterministic key ordering.
    
    Args:
        data: JSON string, bytes, or dict
        
    Returns:
        Canonical JSON bytes (UTF-8 encoded, sorted keys, compact)
    """
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    
    if isinstance(data, str):
        data = json.loads(data)
    
    # Serialize with sorted keys, no extra whitespace
    canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    
    # Encode to UTF-8
    return canonical_json.encode('utf-8')


def canonicalize_xml(xml_data: Union[str, bytes]) -> bytes:
    """
    Canonicalize XML using Exclusive C14N without comments.
    
    Note: This is a simplified implementation. For full C14N support,
    use lxml with c14n method.
    
    Args:
        xml_data: XML string or bytes
        
    Returns:
        Canonical XML bytes
    """
    if isinstance(xml_data, str):
        xml_data = xml_data.encode('utf-8')
    
    # Parse XML
    root = ET.fromstring(xml_data)
    
    # Sort attributes for deterministic output
    def sort_attributes(elem):
        """Sort attributes in element."""
        if elem.attrib:
            elem.attrib = dict(sorted(elem.attrib.items()))
        for child in elem:
            sort_attributes(child)
    
    sort_attributes(root)
    
    # Convert back to bytes with UTF-8 encoding
    # ElementTree.tostring produces deterministic output
    return ET.tostring(root, encoding='utf-8', method='xml')


def canonical_byte_representation(file_path: Union[str, Path]) -> bytes:
    """
    Generate canonical byte representation of a file.
    
    This function provides deterministic, reproducible byte sequences for files
    by normalizing content according to file type.
    
    Supported file types:
    - Text: UTF-8 no BOM, LF line endings, NFC normalization
    - JSON: Deterministic lexicographic key ordering
    - XML: Exclusive C14N without comments
    - Binary: Raw bytes (no transformation)
    
    Args:
        file_path: Path to the file
        
    Returns:
        Canonical byte representation
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type is unsupported or content is invalid
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    
    # Detect file type
    file_type = detect_file_type(path)
    
    # Read file
    with open(path, 'rb') as f:
        content = f.read()
    
    # Process based on type
    if file_type == FileType.JSON:
        try:
            return canonicalize_json(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
            
    elif file_type == FileType.XML:
        try:
            return canonicalize_xml(content)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML in {file_path}: {e}")
            
    elif file_type == FileType.TEXT:
        try:
            text = content.decode('utf-8')
            normalized = normalize_text(text)
            return normalized.encode('utf-8')
        except UnicodeDecodeError as e:
            # Fall back to binary if can't decode as UTF-8
            return content
            
    else:  # BINARY
        return content


def get_file_type(file_path: Union[str, Path]) -> str:
    """
    Get the detected file type for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File type string
    """
    return detect_file_type(file_path)

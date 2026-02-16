"""
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
    
    # Try to detect if binary
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return 'binary'
            # Try to decode as UTF-8
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
        Canonical bytes
    """
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        text = f.read()
    
    # Normalize text
    text = normalize_text(text)
    
    # Encode to UTF-8 without BOM
    return text.encode('utf-8')


def canonical_json(file_path: Path) -> bytes:
    """
    Get canonical representation of a JSON file.
    
    Sorted keys, UTF-8, no BOM, compact format.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Canonical bytes
    """
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    # Serialize with sorted keys
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    
    # Encode to UTF-8 without BOM
    return canonical.encode('utf-8')


def canonical_xml(file_path: Path) -> bytes:
    """
    Get canonical representation of an XML file.
    
    Exclusive C14N without comments.
    
    Args:
        file_path: Path to XML file
        
    Returns:
        Canonical bytes
    """
    try:
        # Parse XML
        tree = ET.parse(file_path)
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
        Raw bytes
    """
    with open(file_path, 'rb') as f:
        return f.read()


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

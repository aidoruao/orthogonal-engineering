"""
Content canonicalization for consistent hashing.

Ensures content is normalized before hashing to maintain integrity.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union


def canonicalize_text(text: str) -> str:
    """
    Canonicalize text content.
    
    Normalizes line endings and trailing whitespace for consistent hashing.
    
    Args:
        text: Input text
        
    Returns:
        Canonicalized text
    """
    # Normalize line endings to LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove trailing whitespace from lines but preserve structure
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    
    # Join with consistent line ending
    return '\n'.join(lines)


def canonicalize_json(data: Union[Dict, str, Path]) -> str:
    """
    Canonicalize JSON data for consistent hashing.
    
    Args:
        data: Dictionary, JSON string, or path to JSON file
        
    Returns:
        Canonicalized JSON string
    """
    if isinstance(data, (str, Path)):
        # Load from file or parse string
        if Path(data).exists():
            with open(data, 'r', encoding='utf-8') as f:
                obj = json.load(f)
        else:
            obj = json.loads(str(data))
    else:
        obj = data
    
    # Serialize with sorted keys and consistent formatting
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False)


def canonicalize_file(filepath: Union[str, Path]) -> bytes:
    """
    Canonicalize file content based on type.
    
    Args:
        filepath: Path to file
        
    Returns:
        Canonicalized content as bytes
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    suffix = filepath.suffix.lower()
    
    # Text-based files
    if suffix in ['.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.sh', '.ps1', '.bat']:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return canonicalize_text(content).encode('utf-8')
    
    # JSON files
    elif suffix == '.json' or suffix == '.jsonl':
        with open(filepath, 'r', encoding='utf-8') as f:
            if suffix == '.jsonl':
                # For JSONL, canonicalize each line
                lines = []
                for line in f:
                    line = line.strip()
                    if line:
                        obj = json.loads(line)
                        lines.append(json.dumps(obj, sort_keys=True, ensure_ascii=False))
                return '\n'.join(lines).encode('utf-8')
            else:
                data = json.load(f)
        return canonicalize_json(data).encode('utf-8')
    
    # Binary files - return as-is
    else:
        with open(filepath, 'rb') as f:
            return f.read()


def is_text_file(filepath: Union[str, Path]) -> bool:
    """
    Check if file is text-based.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if file is text-based
    """
    filepath = Path(filepath)
    suffix = filepath.suffix.lower()
    
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx', 
        '.html', '.css', '.json', '.jsonl', '.xml', '.yaml', '.yml',
        '.sh', '.bash', '.ps1', '.bat', '.cmd',
        '.c', '.cpp', '.h', '.hpp', '.java', '.cs', '.go', '.rs',
        '.rb', '.php', '.swift', '.kt', '.sql'
    }
    
    return suffix in text_extensions
Canonicalizer module for deterministic file canonicalization.

This module provides deterministic canonicalization utilities for various file types:
- JSON: sorted keys, consistent separators
- XML: exclusive canonicalization (C14N) without comments
- Text: NFC normalization, LF line endings
- Binary: returned as-is

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import json
import unicodedata
from typing import Union
from xml.etree import ElementTree as ET


def canonicalize_json(data: Union[str, bytes, dict]) -> bytes:
    """
    Canonicalize JSON data with sorted keys and consistent separators.
    
    Args:
        data: JSON data as string, bytes, or dict
        
    Returns:
        Canonicalized JSON as UTF-8 encoded bytes
    """
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    if isinstance(data, str):
        data = json.loads(data)
    
    # Use sorted keys and consistent separators (no spaces)
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return canonical.encode('utf-8')


def canonicalize_xml(data: Union[str, bytes]) -> bytes:
    """
    Canonicalize XML using exclusive canonicalization (C14N) without comments.
    
    Args:
        data: XML data as string or bytes
        
    Returns:
        Canonicalized XML as UTF-8 encoded bytes
    """
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    
    # Parse XML
    root = ET.fromstring(data)
    
    # Convert to C14N (canonical XML)
    # Note: Python's ET.canonicalize requires Python 3.8+
    try:
        from xml.etree.ElementTree import canonicalize
        canonical = canonicalize(ET.tostring(root, encoding='unicode'), strip_text=True)
        return canonical.encode('utf-8')
    except ImportError:
        # Fallback: use lxml if available
        try:
            from lxml import etree
            canonical = etree.tostring(root, method='c14n', exclusive=True, with_comments=False)
            return canonical
        except ImportError:
            # Final fallback: simple serialization
            return ET.tostring(root, encoding='utf-8', method='xml')


def canonicalize_text(data: Union[str, bytes]) -> bytes:
    """
    Canonicalize text with NFC normalization and LF line endings.
    
    Args:
        data: Text data as string or bytes
        
    Returns:
        Canonicalized text as UTF-8 encoded bytes
    """
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    
    # Normalize to NFC (canonical composition)
    normalized = unicodedata.normalize('NFC', data)
    
    # Normalize line endings to LF
    normalized = normalized.replace('\r\n', '\n').replace('\r', '\n')
    
    return normalized.encode('utf-8')


def canonicalize_binary(data: bytes) -> bytes:
    """
    Return binary data as-is (no canonicalization).
    
    Args:
        data: Binary data
        
    Returns:
        The same binary data
    """
    return data


def canonicalize(data: Union[str, bytes, dict], file_type: str) -> bytes:
    """
    Canonicalize data based on file type.
    
    Args:
        data: Data to canonicalize
        file_type: Type of file ('json', 'xml', 'text', 'binary')
        
    Returns:
        Canonicalized data as bytes
        
    Raises:
        ValueError: If file_type is not supported
    """
    file_type = file_type.lower()
    
    if file_type == 'json':
        return canonicalize_json(data)
    elif file_type == 'xml':
        return canonicalize_xml(data)
    elif file_type == 'text':
        return canonicalize_text(data)
    elif file_type == 'binary':
        if isinstance(data, (str, dict)):
            raise ValueError("Binary data must be bytes")
        return canonicalize_binary(data)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

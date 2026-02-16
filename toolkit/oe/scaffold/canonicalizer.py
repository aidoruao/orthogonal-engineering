"""
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


def canonical_byte_representation(file_path: Union[str, Path]) -> bytes:
    """
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

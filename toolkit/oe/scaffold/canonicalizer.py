"""
Canonicalization Module

Provides deterministic canonical byte representation for various file types:
- Text files: UTF-8 no BOM, LF line endings, NFC normalization
- JSON: Lexicographic key ordering, compact representation
- XML: Exclusive C14N without comments
- Binary: Raw bytes

Strips extended filesystem metadata for deterministic hashing.
"""

import json
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
        return FileType.BINARY


def normalize_text(content: str) -> str:
    """
    Normalize text content for deterministic representation.

    - Apply NFC Unicode normalization
    - Convert to LF line endings
    - Strip trailing whitespace from lines

    Args:
        content: Text content to normalize

    Returns:
        Normalized text content
    """
    content = unicodedata.normalize("NFC", content)
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    lines = content.split("\n")
    lines = [line.rstrip() for line in lines]
    return "\n".join(lines)


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
        data = json.loads(content)
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON content: {exc}")


def canonicalize_xml(content: str) -> str:
    """
    Canonicalize XML using Exclusive C14N without comments.

    Args:
        content: XML string to canonicalize

    Returns:
        Canonicalized XML string
    """
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
        try:
            return ET.canonicalize(content, strip_text=True)
        except AttributeError:
            return ET.tostring(root, encoding="unicode", method="xml")
    except Exception as exc:
        raise ValueError(f"Invalid XML content: {exc}")


def canonical_byte_representation(file_path: Union[str, Path]) -> bytes:
    """
    Generate deterministic canonical byte representation of a file.

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

    file_type = detect_file_type(file_path)

    if file_type == FileType.BINARY:
        with open(file_path, "rb") as f:
            return f.read()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, "rb") as f:
            return f.read()

    if file_type == FileType.JSON:
        canonical = canonicalize_json(content)
    elif file_type == FileType.XML:
        canonical = canonicalize_xml(content)
    else:
        canonical = normalize_text(content)

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

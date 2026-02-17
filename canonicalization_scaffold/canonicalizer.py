"""
Canonicalizer Module

Provides canonical byte representation for different file types:
- Text files: UTF-8 no BOM, LF line endings, NFC normalization
- JSON: Deterministic lexicographic key ordering
- XML: Exclusive C14N without comments
- Binary: Raw bytes

Strips extended metadata for deterministic hashing.
"""

import json
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import BinaryIO, Union
from xml.dom import minidom


class Canonicalizer:
    """
    Canonicalizes files for deterministic hashing.
    """
    
    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """
        Normalize Unicode text to NFC (Canonical Composition).
        
        Args:
            text: Input text
            
        Returns:
            NFC-normalized text
        """
        return unicodedata.normalize('NFC', text)
    
    @staticmethod
    def _normalize_line_endings(text: str) -> str:
        """
        Normalize line endings to LF (Unix-style).
        
        Args:
            text: Input text
            
        Returns:
            Text with LF line endings
        """
        # Replace CRLF and CR with LF
        return text.replace('\r\n', '\n').replace('\r', '\n')
    
    @staticmethod
    def _strip_bom(data: bytes) -> bytes:
        """
        Strip UTF-8 BOM if present.
        
        Args:
            data: Input bytes
            
        Returns:
            Bytes without BOM
        """
        if data.startswith(b'\xef\xbb\xbf'):
            return data[3:]
        return data
    
    @staticmethod
    def canonicalize_text(content: str) -> bytes:
        """
        Canonicalize text content.
        
        Process:
        1. Normalize Unicode to NFC
        2. Normalize line endings to LF
        3. Encode to UTF-8 without BOM
        
        Args:
            content: Text content
            
        Returns:
            Canonical bytes
        """
        # Normalize Unicode
        normalized = Canonicalizer._normalize_unicode(content)
        
        # Normalize line endings
        normalized = Canonicalizer._normalize_line_endings(normalized)
        
        # Encode to UTF-8 (no BOM)
        return normalized.encode('utf-8')
    
    @staticmethod
    def canonicalize_json(content: Union[str, dict]) -> bytes:
        """
        Canonicalize JSON content with deterministic key ordering.
        
        Process:
        1. Parse JSON if string
        2. Sort keys lexicographically
        3. Serialize with compact formatting
        4. Encode to UTF-8
        
        Args:
            content: JSON string or dict
            
        Returns:
            Canonical bytes
        """
        # Parse if string
        if isinstance(content, str):
            data = json.loads(content)
        else:
            data = content
        
        # Serialize with sorted keys, compact formatting
        canonical_json = json.dumps(
            data,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=False
        )
        
        # Encode to UTF-8
        return canonical_json.encode('utf-8')
    
    @staticmethod
    def canonicalize_xml(content: str) -> bytes:
        """
        Canonicalize XML using Exclusive C14N without comments.
        
        Note: This is a simplified implementation. For production use,
        consider using lxml with proper C14N support.
        
        Args:
            content: XML content string
            
        Returns:
            Canonical bytes
        """
        try:
            # Parse XML
            root = ET.fromstring(content)
            
            # Sort attributes and elements for deterministic output
            def sort_element(elem):
                # Sort attributes
                if elem.attrib:
                    elem.attrib = dict(sorted(elem.attrib.items()))
                # Recursively sort children
                for child in elem:
                    sort_element(child)
                # Sort children by tag name
                elem[:] = sorted(elem, key=lambda e: (e.tag, ET.tostring(e)))
            
            sort_element(root)
            
            # Convert back to string (without XML declaration)
            xml_str = ET.tostring(root, encoding='unicode', method='xml')
            
            # Remove comments (simplified approach)
            xml_str = '\n'.join(line for line in xml_str.split('\n') 
                               if '<!--' not in line and '-->' not in line)
            
            # Normalize whitespace between tags
            xml_str = ' '.join(xml_str.split())
            
            return xml_str.encode('utf-8')
            
        except ET.ParseError as e:
            # If XML parsing fails, treat as text
            return Canonicalizer.canonicalize_text(content)
    
    @staticmethod
    def canonicalize_binary(data: bytes) -> bytes:
        """
        Canonicalize binary data (returns as-is).
        
        Args:
            data: Binary data
            
        Returns:
            Same binary data
        """
        return data
    
    @staticmethod
    def detect_file_type(file_path: Path) -> str:
        """
        Detect file type based on extension.
        
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
        if suffix in ['.txt', '.md', '.rst', '.py', '.js', '.ts', '.java', 
                      '.c', '.cpp', '.h', '.hpp', '.css', '.html', '.yaml', 
                      '.yml', '.toml', '.ini', '.cfg', '.conf', '.sh', '.bat',
                      '.ps1', '.rb', '.go', '.rs', '.swift', '.kt', '.scala']:
            return 'text'
        
        # Default to binary
        return 'binary'
    
    @staticmethod
    def canonical_byte_representation(file_path: Union[str, Path]) -> bytes:
        """
        Get canonical byte representation of a file.
        
        This is the main entry point for canonicalization.
        
        Process:
        1. Detect file type
        2. Read file content
        3. Apply appropriate canonicalization
        4. Return canonical bytes
        
        Args:
            file_path: Path to file
            
        Returns:
            Canonical bytes representation
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect file type
        file_type = Canonicalizer.detect_file_type(file_path)
        
        # Read file
        if file_type == 'binary':
            with open(file_path, 'rb') as f:
                data = f.read()
            return Canonicalizer.canonicalize_binary(data)
        
        else:
            # Read as text with UTF-8, handle BOM
            with open(file_path, 'rb') as f:
                data = f.read()
            data = Canonicalizer._strip_bom(data)
            
            try:
                content = data.decode('utf-8')
            except UnicodeDecodeError:
                # If UTF-8 decode fails, treat as binary
                return Canonicalizer.canonicalize_binary(data)
            
            # Apply type-specific canonicalization
            if file_type == 'json':
                # For JSONL, process line by line
                if file_path.suffix.lower() == '.jsonl':
                    lines = content.strip().split('\n')
                    canonical_lines = []
                    for line in lines:
                        if line.strip():
                            canonical_lines.append(
                                Canonicalizer.canonicalize_json(line).decode('utf-8')
                            )
                    return '\n'.join(canonical_lines).encode('utf-8')
                else:
                    return Canonicalizer.canonicalize_json(content)
            
            elif file_type == 'xml':
                return Canonicalizer.canonicalize_xml(content)
            
            else:  # text
                return Canonicalizer.canonicalize_text(content)


# Convenience function
def canonical_byte_representation(file_path: Union[str, Path]) -> bytes:
    """
    Get canonical byte representation of a file.
    
    This is a convenience function that wraps Canonicalizer.canonical_byte_representation.
    
    Args:
        file_path: Path to file
        
    Returns:
        Canonical bytes representation
    """
    return Canonicalizer.canonical_byte_representation(file_path)

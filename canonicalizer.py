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

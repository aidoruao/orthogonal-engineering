"""
Utility functions for CAS operations.

Provides common helpers for file operations, path handling, and validation.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Union


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(name: str) -> str:
    """
    Convert string to safe filename.
    
    Args:
        name: Original name
        
    Returns:
        Safe filename string
    """
    # Replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    safe_name = name
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip('. ')
    
    return safe_name or "unnamed"


def copy_file(src: Union[str, Path], dst: Union[str, Path], preserve_metadata: bool = True) -> Path:
    """
    Copy file with optional metadata preservation.
    
    Args:
        src: Source file path
        dst: Destination file path
        preserve_metadata: Whether to preserve file metadata
        
    Returns:
        Path to destination file
        
    Raises:
        FileNotFoundError: If source doesn't exist
    """
    src = Path(src)
    dst = Path(dst)
    
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    
    # Ensure destination directory exists
    ensure_dir(dst.parent)
    
    if preserve_metadata:
        shutil.copy2(src, dst)
    else:
        shutil.copy(src, dst)
    
    return dst


def list_files(directory: Union[str, Path], pattern: str = "*", recursive: bool = False) -> List[Path]:
    """
    List files in directory matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (default: "*")
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    
    if not directory.exists():
        return []
    
    if recursive:
        return sorted([p for p in directory.rglob(pattern) if p.is_file()])
    else:
        return sorted([p for p in directory.glob(pattern) if p.is_file()])


def get_file_size(filepath: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in bytes
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    return filepath.stat().st_size


def format_size(size_bytes: int) -> str:
    """
    Format byte size as human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def is_safe_path(base_dir: Union[str, Path], path: Union[str, Path]) -> bool:
    """
    Check if path is within base directory (prevent directory traversal).
    
    Args:
        base_dir: Base directory
        path: Path to check
        
    Returns:
        True if path is safe, False otherwise
    """
    base_dir = Path(base_dir).resolve()
    path = Path(path).resolve()
    
    try:
        path.relative_to(base_dir)
        return True
    except ValueError:
        return False

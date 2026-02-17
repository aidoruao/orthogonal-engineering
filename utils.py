"""
Utility functions for CAS operations.

Provides common helpers for file operations, path handling, and validation.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Union


def ensure_dir(path: Union[str, Path]) -> Path:
Utility module providing IO helpers, sorting, concurrency, and checkpoint functions.

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, TypeVar


T = TypeVar('T')


def ensure_dir(path: Path) -> None:
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
        path: Path to directory
    """
    path.mkdir(parents=True, exist_ok=True)


def safe_read_file(path: Path, binary: bool = False) -> Optional[Any]:
    """
    Safely read a file, returning None on error.
    
    Args:
        path: Path to file
        binary: If True, read as binary
        
    Returns:
        File contents or None on error
    """
    try:
        mode = 'rb' if binary else 'r'
        with open(path, mode) as f:
            return f.read()
    except Exception:
        return None


def safe_write_file(path: Path, content: Any, binary: bool = False) -> bool:
    """
    Safely write to a file, returning success status.
    
    Args:
        path: Path to file
        content: Content to write
        binary: If True, write as binary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        ensure_dir(path.parent)
        mode = 'wb' if binary else 'w'
        with open(path, mode) as f:
            f.write(content)
        return True
    except Exception:
        return False


def deterministic_sort_paths(paths: List[str]) -> List[str]:
    """
    Sort paths deterministically using UTF-8 lexicographic order.
    
    Args:
        paths: List of path strings
        
    Returns:
        Sorted list of paths
    """
    # Sort by UTF-8 byte representation for deterministic ordering
    return sorted(paths, key=lambda p: p.encode('utf-8'))


def deterministic_sort_dict_keys(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sort dictionary keys deterministically.
    
    Args:
        d: Dictionary to sort
        
    Returns:
        New dictionary with sorted keys
    """
    return {k: d[k] for k in sorted(d.keys())}


def parallel_map(
    func: Callable[[T], Any],
    items: Iterable[T],
    max_workers: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[Any]:
    """
    Apply function to items in parallel using ThreadPoolExecutor.
    
    Args:
        func: Function to apply to each item
        items: Iterable of items to process
        max_workers: Maximum number of worker threads
        progress_callback: Optional callback(completed, total)
        
    Returns:
        List of results in the same order as items
    """
    items_list = list(items)
    total = len(items_list)
    results = [None] * total
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks with their indices
        future_to_index = {
            executor.submit(func, item): i
            for i, item in enumerate(items_list)
        }
        
        completed = 0
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            results[index] = future.result()
            completed += 1
            
            if progress_callback:
                progress_callback(completed, total)
    
    return results


class CheckpointManager:
    """Manage checkpoint files for restartable operations."""
    
    def __init__(self, checkpoint_path: Path):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_path: Path to checkpoint file
        """
        self.checkpoint_path = checkpoint_path
        self._data: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load checkpoint from file if it exists."""
        if self.checkpoint_path.exists():
            try:
                with open(self.checkpoint_path, 'r') as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}
    
    def save(self) -> None:
        """Save checkpoint to file."""
        ensure_dir(self.checkpoint_path.parent)
        with open(self.checkpoint_path, 'w') as f:
            json.dump(self._data, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from checkpoint."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in checkpoint."""
        self._data[key] = value
    
    def mark_processed(self, item_id: str) -> None:
        """Mark an item as processed."""
        if 'processed' not in self._data:
            self._data['processed'] = []
        if item_id not in self._data['processed']:
            self._data['processed'].append(item_id)
    
    def is_processed(self, item_id: str) -> bool:
        """Check if an item has been processed."""
        return item_id in self._data.get('processed', [])
    
    def clear(self) -> None:
        """Clear all checkpoint data."""
        self._data = {}
        if self.checkpoint_path.exists():
            self.checkpoint_path.unlink()


def get_file_size(path: Path) -> int:
    """
    Get file size in bytes.
    
    Args:
        path: Path to file
        
    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    try:
        return path.stat().st_size
    except Exception:
        return 0


def relative_path(path: Path, base: Path) -> str:
    """
    Get relative path from base, using forward slashes.
    
    Args:
        path: Absolute path
        base: Base directory
        
    Returns:
        Relative path string with forward slashes
    """
    try:
        rel = path.relative_to(base)
        return str(rel).replace(os.sep, '/')
    except ValueError:
        # If path is not relative to base, return absolute
        return str(path).replace(os.sep, '/')

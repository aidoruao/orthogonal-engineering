#!/usr/bin/env python3
"""
OE-DFM Utility Functions

Common utilities for the Deterministic Fractal Model.

Author: Orthogonal Engineering
Standard: Yeshua  
Version: 1.0.0
"""

import hashlib
import struct
from pathlib import Path
from typing import Any, Dict, Tuple

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML required. Run: pip install pyyaml")


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load and validate configuration file.
    
    Args:
        config_path: Path to YAML configuration
        
    Returns:
        Configuration dictionary
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate required fields
    required_fields = ['root_seed', 'topology', 'fractal', 'training']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    return config


def derive_seed(parent_seed: str, *components: Any) -> str:
    """
    Deterministically derive a child seed from parent seed and components.
    
    Args:
        parent_seed: Parent seed string
        *components: Additional components to mix into derivation
        
    Returns:
        Hex-encoded SHA256 hash
    """
    data = parent_seed
    for component in components:
        data += str(component)
    
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def seed_to_bytes(seed: str, num_bytes: int) -> bytes:
    """
    Expand a seed string into a deterministic byte sequence.
    
    Uses iterative hashing to generate arbitrary length byte sequences.
    
    Args:
        seed: Seed string
        num_bytes: Number of bytes to generate
        
    Returns:
        Deterministic byte sequence
    """
    result = b''
    counter = 0
    
    while len(result) < num_bytes:
        # Hash seed with counter
        chunk_seed = f"{seed}_{counter}"
        chunk_hash = hashlib.sha256(chunk_seed.encode('utf-8')).digest()
        result += chunk_hash
        counter += 1
    
    return result[:num_bytes]


def bytes_to_floats(data: bytes, num_floats: int, dtype: str = 'float32') -> list:
    """
    Convert bytes to float array.
    
    Args:
        data: Byte sequence
        num_floats: Number of floats to extract
        dtype: Float precision ('float32' or 'float64')
        
    Returns:
        List of floats
    """
    if dtype == 'float32':
        fmt = 'f'
        bytes_per_float = 4
    elif dtype == 'float64':
        fmt = 'd'
        bytes_per_float = 8
    else:
        raise ValueError(f"Unsupported dtype: {dtype}")
    
    floats = []
    for i in range(num_floats):
        start = i * bytes_per_float
        end = start + bytes_per_float
        
        if end > len(data):
            # Wrap around if needed
            start = start % len(data)
            end = start + bytes_per_float
            if end > len(data):
                end = len(data)
                start = end - bytes_per_float
        
        chunk = data[start:end]
        if len(chunk) == bytes_per_float:
            value = struct.unpack(fmt, chunk)[0]
            floats.append(value)
    
    return floats


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA256 hash of a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Hex-encoded SHA256 hash
    """
    hasher = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def validate_tensor_hash(tensor_bytes: bytes, expected_hash: str) -> bool:
    """
    Validate tensor hash matches expected value.
    
    Args:
        tensor_bytes: Tensor data as bytes
        expected_hash: Expected SHA256 hash
        
    Returns:
        True if hash matches
    """
    actual_hash = hashlib.sha256(tensor_bytes).hexdigest()
    return actual_hash == expected_hash

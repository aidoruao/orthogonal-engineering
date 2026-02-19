#!/usr/bin/env python3
"""
OE-IFM Utilities

Cross-machine guarantee enforcement and helper functions.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import hashlib
import platform
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML required. Run: pip install pyyaml")

try:
    import torch
except ImportError:
    raise ImportError("PyTorch required. Run: pip install torch")


class CrossMachineGuarantee:
    """Enforces cross-machine determinism guarantees."""
    
    @staticmethod
    def enforce_deterministic_environment():
        """
        Enforce all conditions required for cross-machine determinism.
        
        Raises:
            RuntimeError: If any condition fails
        """
        # 1. Python version check (require 3.x)
        version_info = sys.version_info
        if version_info.major < 3:
            raise RuntimeError(
                f"Python 3.x required for determinism. Current: {sys.version}"
            )
        
        # 2. Endianness check (require little-endian for consistency)
        if sys.byteorder != 'little':
            raise RuntimeError(
                f"Little-endian system required. Current: {sys.byteorder}"
            )
        
        # 3. Disable multithreading
        torch.set_num_threads(1)
        
        # 4. Disable MKL parallel
        import os
        os.environ['MKL_NUM_THREADS'] = '1'
        os.environ['OMP_NUM_THREADS'] = '1'
        os.environ['NUMEXPR_NUM_THREADS'] = '1'
        
        # 5. CPU only - no CUDA
        if torch.cuda.is_available():
            # Just warn, don't fail - user may have CUDA but we'll use CPU
            print("WARNING: CUDA available but will use CPU only for determinism")
        
        # 6. Set deterministic algorithms
        torch.use_deterministic_algorithms(True, warn_only=False)
        
        print("✓ Cross-machine determinism environment enforced")
        print(f"  Python: {sys.version}")
        print(f"  Platform: {platform.platform()}")
        print(f"  Endianness: {sys.byteorder}")
        print(f"  Torch threads: 1")
        print(f"  Device: CPU only")
    
    @staticmethod
    def check_device_cpu_only(device):
        """Verify device is CPU only."""
        if str(device) != 'cpu':
            raise RuntimeError(f"CPU-only execution required. Got device: {device}")


def load_config(config_path: Path = None) -> Dict[str, Any]:
    """
    Load PR26 configuration.
    
    Args:
        config_path: Path to config file (default: pr26_root.yaml)
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path(__file__).parent / "pr26_root.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def deterministic_hash(data: bytes) -> str:
    """
    Compute SHA256 hash of data.
    
    Args:
        data: Bytes to hash
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(data).hexdigest()


def deterministic_expand(seed_bytes: bytes, required_bytes: int) -> bytes:
    """
    Deterministically expand seed to required number of bytes.
    
    Uses iterative SHA256 hashing to expand seed.
    
    Args:
        seed_bytes: Initial seed
        required_bytes: Number of bytes to generate
        
    Returns:
        Expanded bytes
    """
    result = b''
    counter = 0
    
    while len(result) < required_bytes:
        # Hash seed + counter
        hash_input = seed_bytes + counter.to_bytes(8, byteorder='little')
        chunk = hashlib.sha256(hash_input).digest()
        result += chunk
        counter += 1
    
    return result[:required_bytes]


def bytes_to_int64_tensor(data: bytes, shape: tuple) -> torch.Tensor:
    """
    Convert bytes to int64 tensor.
    
    Args:
        data: Raw bytes
        shape: Desired tensor shape
        
    Returns:
        Int64 tensor
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("NumPy required. Run: pip install numpy")
    
    # Calculate required number of int64 values
    num_elements = 1
    for dim in shape:
        num_elements *= dim
    
    # Each int64 is 8 bytes
    required_bytes = num_elements * 8
    
    # Ensure we have enough bytes
    if len(data) < required_bytes:
        raise ValueError(
            f"Insufficient bytes: need {required_bytes}, got {len(data)}"
        )
    
    # Convert to int64 array
    int64_array = np.frombuffer(data[:required_bytes], dtype=np.int64)
    
    # Make a copy to ensure writable tensor
    int64_array = int64_array.copy()
    
    # Reshape and convert to torch tensor
    tensor = torch.from_numpy(int64_array.reshape(shape))
    
    return tensor


def int64_mod(x: torch.Tensor) -> torch.Tensor:
    """
    Explicit modulo 2^64 for documentation clarity.
    
    PyTorch int64 naturally wraps at 2^64 due to two's complement
    representation, so this function returns the input unchanged.
    It exists solely for code clarity and documentation.
    
    Args:
        x: Int64 tensor
        
    Returns:
        Same tensor (int64 wraps automatically)
    """
    # Verification: ensure input is int64
    assert x.dtype == torch.int64, f"Expected int64, got {x.dtype}"
    # int64 naturally wraps at 2^64 in two's complement
    return x


def compute_tensor_hash(tensor: torch.Tensor) -> str:
    """
    Compute hash of tensor bytes.
    
    Args:
        tensor: Tensor to hash
        
    Returns:
        SHA256 hash as hexadecimal string
    """
    # Convert to numpy and get raw bytes
    tensor_bytes = tensor.cpu().numpy().tobytes()
    return deterministic_hash(tensor_bytes)

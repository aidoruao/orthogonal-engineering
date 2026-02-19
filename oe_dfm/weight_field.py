#!/usr/bin/env python3
"""
OE-DFM Weight Field Generator

Deterministic tensor initialization via cryptographic hash expansion.
No random initialization. No Xavier. No Kaiming.
Pure deterministic field generation.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import hashlib
import math
import struct
from pathlib import Path
from typing import Tuple, List

try:
    import torch
except ImportError:
    raise ImportError("PyTorch required. Run: pip install torch")

from .utils import derive_seed, seed_to_bytes


class WeightFieldGenerator:
    """Generates deterministic tensor fields from root seed."""
    
    def __init__(self, root_seed: str, float_precision: str = 'float32'):
        """
        Initialize weight field generator.
        
        Args:
            root_seed: Root seed string
            float_precision: Float precision ('float32' or 'float64')
        """
        self.root_seed = root_seed
        self.float_precision = float_precision
        self.dtype = torch.float32 if float_precision == 'float32' else torch.float64
        
    def generate_tensor(self, shape: Tuple[int, ...], name: str, 
                       normalize: bool = True) -> torch.Tensor:
        """
        Generate a deterministic tensor from seed and name.
        
        Args:
            shape: Tensor shape tuple
            name: Tensor name for seed derivation
            normalize: Whether to normalize using variance scaling
            
        Returns:
            Deterministic tensor
        """
        # Derive tensor-specific seed
        tensor_seed = derive_seed(self.root_seed, name)
        
        # Calculate total elements
        num_elements = 1
        for dim in shape:
            num_elements *= dim
        
        # Generate bytes
        bytes_per_element = 4 if self.float_precision == 'float32' else 8
        total_bytes = num_elements * bytes_per_element
        tensor_bytes = seed_to_bytes(tensor_seed, total_bytes)
        
        # Convert bytes to floats
        values = []
        fmt = 'f' if self.float_precision == 'float32' else 'd'
        
        for i in range(num_elements):
            start = i * bytes_per_element
            end = start + bytes_per_element
            chunk = tensor_bytes[start:end]
            value = struct.unpack(fmt, chunk)[0]
            
            # Handle NaN/Inf by wrapping to valid range
            if not math.isfinite(value):
                # Use hash of position to get deterministic replacement
                pos_hash = hashlib.sha256(f"{tensor_seed}_{i}".encode()).digest()
                value = struct.unpack(fmt, pos_hash[:bytes_per_element])[0]
                if not math.isfinite(value):
                    value = 0.0
            
            values.append(value)
        
        # Create tensor
        tensor = torch.tensor(values, dtype=self.dtype).reshape(shape)
        
        # Normalize if requested
        if normalize:
            tensor = self._variance_scale_normalize(tensor, shape)
        
        return tensor
    
    def _variance_scale_normalize(self, tensor: torch.Tensor, 
                                   shape: Tuple[int, ...]) -> torch.Tensor:
        """
        Apply variance scaling normalization.
        
        Ensures consistent activation variance across layers.
        
        Args:
            tensor: Input tensor
            shape: Tensor shape
            
        Returns:
            Normalized tensor
        """
        # Compute fan-in (input dimension)
        if len(shape) == 1:
            fan_in = shape[0]
        elif len(shape) == 2:
            fan_in = shape[1]  # [out, in]
        else:
            # For higher dimensional tensors, use product of all but first dim
            fan_in = 1
            for dim in shape[1:]:
                fan_in *= dim
        
        # Calculate standard deviation for variance scaling
        # Using 1/sqrt(fan_in) as in common initialization schemes
        std = 1.0 / math.sqrt(fan_in)
        
        # Standardize tensor to mean=0, std=1
        mean = tensor.mean()
        current_std = tensor.std()
        
        if current_std > 0:
            tensor = (tensor - mean) / current_std
        
        # Scale to target std
        tensor = tensor * std
        
        return tensor
    
    def generate_model_weights(self, config: dict) -> dict:
        """
        Generate all model weights from configuration.
        
        Args:
            config: Model configuration dictionary
            
        Returns:
            Dictionary of named tensors
        """
        topology = config['topology']
        layers = topology['layers']
        hidden_dim = topology['hidden_dim']
        attention_heads = topology['attention_heads']
        vocab_size = topology['vocab_size']
        max_seq_len = topology['max_seq_len']
        
        weights = {}
        
        # Token embedding
        weights['token_embedding'] = self.generate_tensor(
            (vocab_size, hidden_dim), 
            'token_embedding',
            normalize=True
        )
        
        # Positional encoding (for RoPE, we store sin/cos tables)
        weights['rope_sin'] = self.generate_tensor(
            (max_seq_len, hidden_dim // attention_heads // 2),
            'rope_sin',
            normalize=False
        )
        weights['rope_cos'] = self.generate_tensor(
            (max_seq_len, hidden_dim // attention_heads // 2),
            'rope_cos',
            normalize=False
        )
        
        # Transformer layers
        for layer_idx in range(layers):
            prefix = f'layer_{layer_idx}'
            
            # Attention
            weights[f'{prefix}.attn.q_proj'] = self.generate_tensor(
                (hidden_dim, hidden_dim),
                f'{prefix}.attn.q_proj',
                normalize=True
            )
            weights[f'{prefix}.attn.k_proj'] = self.generate_tensor(
                (hidden_dim, hidden_dim),
                f'{prefix}.attn.k_proj',
                normalize=True
            )
            weights[f'{prefix}.attn.v_proj'] = self.generate_tensor(
                (hidden_dim, hidden_dim),
                f'{prefix}.attn.v_proj',
                normalize=True
            )
            weights[f'{prefix}.attn.o_proj'] = self.generate_tensor(
                (hidden_dim, hidden_dim),
                f'{prefix}.attn.o_proj',
                normalize=True
            )
            
            # Attention layer norm
            weights[f'{prefix}.attn_norm.weight'] = self.generate_tensor(
                (hidden_dim,),
                f'{prefix}.attn_norm.weight',
                normalize=False
            )
            
            # MLP
            mlp_dim = hidden_dim * 4  # Standard expansion factor
            weights[f'{prefix}.mlp.gate_proj'] = self.generate_tensor(
                (hidden_dim, mlp_dim),
                f'{prefix}.mlp.gate_proj',
                normalize=True
            )
            weights[f'{prefix}.mlp.up_proj'] = self.generate_tensor(
                (hidden_dim, mlp_dim),
                f'{prefix}.mlp.up_proj',
                normalize=True
            )
            weights[f'{prefix}.mlp.down_proj'] = self.generate_tensor(
                (mlp_dim, hidden_dim),
                f'{prefix}.mlp.down_proj',
                normalize=True
            )
            
            # MLP layer norm
            weights[f'{prefix}.mlp_norm.weight'] = self.generate_tensor(
                (hidden_dim,),
                f'{prefix}.mlp_norm.weight',
                normalize=False
            )
        
        # Final layer norm
        weights['final_norm.weight'] = self.generate_tensor(
            (hidden_dim,),
            'final_norm.weight',
            normalize=False
        )
        
        # Output projection (to vocabulary)
        weights['output_proj'] = self.generate_tensor(
            (hidden_dim, vocab_size),
            'output_proj',
            normalize=True
        )
        
        return weights

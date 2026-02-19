#!/usr/bin/env python3
"""
OE-IFM Weight Field Generation

Deterministic integer weight generation from seed.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import hashlib
from typing import Tuple

try:
    import torch
except ImportError:
    raise ImportError("PyTorch required. Run: pip install torch")

from .utils import deterministic_expand, bytes_to_int64_tensor, int64_mod


class WeightField:
    """Deterministic integer weight field generator."""
    
    def __init__(self, root_seed: str):
        """
        Initialize weight field.
        
        Args:
            root_seed: Root seed string
        """
        self.root_seed = root_seed
        self.root_seed_bytes = root_seed.encode('utf-8')
    
    def generate_tensor(self, tensor_name: str, shape: Tuple[int, ...]) -> torch.Tensor:
        """
        Generate deterministic int64 tensor from seed and name.
        
        Process:
        1. seed_T = sha256(root_seed + tensor_name)
        2. bytes = deterministic_expand(seed_T, required_bytes)
        3. tensor = reinterpret_as_int64(bytes)
        
        No normalization, no scaling, no float conversion.
        Weights are raw 64-bit integers.
        
        Args:
            tensor_name: Name of tensor to generate
            shape: Tensor shape
            
        Returns:
            Int64 tensor with deterministic weights
        """
        # Create seed for this specific tensor
        seed_input = self.root_seed_bytes + tensor_name.encode('utf-8')
        seed_T = hashlib.sha256(seed_input).digest()
        
        # Calculate required bytes (8 bytes per int64)
        num_elements = 1
        for dim in shape:
            num_elements *= dim
        required_bytes = num_elements * 8
        
        # Expand seed to required bytes
        expanded_bytes = deterministic_expand(seed_T, required_bytes)
        
        # Convert to int64 tensor
        tensor = bytes_to_int64_tensor(expanded_bytes, shape)
        
        # Explicit modulo 2^64 (though int64 naturally wraps)
        tensor = int64_mod(tensor)
        
        return tensor
    
    def generate_model_weights(self, config: dict) -> dict:
        """
        Generate all model weights from config.
        
        Args:
            config: Model configuration dictionary
            
        Returns:
            Dictionary of {tensor_name: tensor}
        """
        arch = config['architecture']
        
        num_layers = arch['layers']
        hidden_dim = arch['hidden_dim']
        num_heads = arch['heads']
        vocab_size = arch['vocab_size']

        # Validate attention head configuration: hidden_dim must be divisible by num_heads
        assert num_heads > 0 and hidden_dim % num_heads == 0, (
            f"Invalid architecture config: hidden_dim ({hidden_dim}) must be divisible "
            f"by num_heads ({num_heads}), and num_heads must be positive."
        )
        
        weights = {}
        
        # Token embedding
        weights['token_embedding'] = self.generate_tensor(
            'token_embedding',
            (vocab_size, hidden_dim)
        )
        
        # Transformer layers
        for layer_idx in range(num_layers):
            prefix = f'layer_{layer_idx}'
            
            # Attention projections
            weights[f'{prefix}_q_proj'] = self.generate_tensor(
                f'{prefix}_q_proj',
                (hidden_dim, hidden_dim)
            )
            weights[f'{prefix}_k_proj'] = self.generate_tensor(
                f'{prefix}_k_proj',
                (hidden_dim, hidden_dim)
            )
            weights[f'{prefix}_v_proj'] = self.generate_tensor(
                f'{prefix}_v_proj',
                (hidden_dim, hidden_dim)
            )
            weights[f'{prefix}_o_proj'] = self.generate_tensor(
                f'{prefix}_o_proj',
                (hidden_dim, hidden_dim)
            )
            
            # MLP projections
            mlp_dim = hidden_dim * 4
            weights[f'{prefix}_mlp_w1'] = self.generate_tensor(
                f'{prefix}_mlp_w1',
                (hidden_dim, mlp_dim)
            )
            weights[f'{prefix}_mlp_w2'] = self.generate_tensor(
                f'{prefix}_mlp_w2',
                (mlp_dim, hidden_dim)
            )
            
            # Polynomial activation coefficient
            weights[f'{prefix}_poly_a'] = self.generate_tensor(
                f'{prefix}_poly_a',
                (1,)
            )
        
        # Output projection
        weights['output_proj'] = self.generate_tensor(
            'output_proj',
            (hidden_dim, vocab_size)
        )
        
        return weights

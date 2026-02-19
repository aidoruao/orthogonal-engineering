#!/usr/bin/env python3
"""
OE-IFM Integer Architecture

Pure integer transformer architecture.
No floating point operations anywhere.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from typing import Dict, Optional

try:
    import torch
    import torch.nn as nn
except ImportError:
    raise ImportError("PyTorch required. Run: pip install torch")

from .utils import int64_mod


class IntegerAttention(nn.Module):
    """Integer-only attention mechanism."""
    
    def __init__(self, hidden_dim: int, num_heads: int):
        """
        Initialize integer attention.
        
        Args:
            hidden_dim: Hidden dimension
            num_heads: Number of attention heads
        """
        super().__init__()
        assert hidden_dim % num_heads == 0
        
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        # Note: No nn.Linear layers - weights are loaded externally
        # This is just the computation graph
    
    def forward(
        self,
        x: torch.Tensor,
        q_weight: torch.Tensor,
        k_weight: torch.Tensor,
        v_weight: torch.Tensor,
        o_weight: torch.Tensor,
    ) -> torch.Tensor:
        """
        Integer attention forward pass.
        
        Replaces softmax attention with modular dot product.
        No normalization, no softmax, no floating ops.
        
        Args:
            x: Input tensor [batch, seq_len, hidden_dim] int64
            q_weight: Query projection weight [hidden_dim, hidden_dim] int64
            k_weight: Key projection weight [hidden_dim, hidden_dim] int64
            v_weight: Value projection weight [hidden_dim, hidden_dim] int64
            o_weight: Output projection weight [hidden_dim, hidden_dim] int64
            
        Returns:
            Output tensor [batch, seq_len, hidden_dim] int64
        """
        batch_size, seq_len, _ = x.shape
        
        # Project to Q, K, V using integer matrix multiply
        # q = x @ q_weight (mod 2^64)
        q = int64_mod(torch.matmul(x, q_weight))
        k = int64_mod(torch.matmul(x, k_weight))
        v = int64_mod(torch.matmul(x, v_weight))
        
        # Reshape for multi-head
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim)
        k = k.view(batch_size, seq_len, self.num_heads, self.head_dim)
        v = v.view(batch_size, seq_len, self.num_heads, self.head_dim)
        
        # Transpose for attention computation
        q = q.transpose(1, 2)  # [batch, num_heads, seq_len, head_dim]
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        
        # Compute attention scores: score = Q @ K^T (mod 2^64)
        # No scaling, no softmax
        scores = int64_mod(torch.matmul(q, k.transpose(-2, -1)))
        
        # Apply scores to values: out = scores @ V (mod 2^64)
        out = int64_mod(torch.matmul(scores, v))
        
        # Reshape back
        out = out.transpose(1, 2).contiguous()
        out = out.view(batch_size, seq_len, self.hidden_dim)
        
        # Output projection
        out = int64_mod(torch.matmul(out, o_weight))
        
        return out


class IntegerMLP(nn.Module):
    """Integer-only MLP with polynomial activation."""
    
    def __init__(self, hidden_dim: int, mlp_dim: int):
        """
        Initialize integer MLP.
        
        Args:
            hidden_dim: Hidden dimension
            mlp_dim: MLP intermediate dimension
        """
        super().__init__()
        self.hidden_dim = hidden_dim
        self.mlp_dim = mlp_dim
    
    def polynomial_activation(self, x: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
        """
        Polynomial activation: f(x) = x^3 + a*x (mod 2^64)
        
        No transcendental functions, no floating ops.
        
        Args:
            x: Input tensor int64
            a: Coefficient tensor int64
            
        Returns:
            Activated tensor int64
        """
        x_cubed = int64_mod(x * x * x)
        ax = int64_mod(a * x)
        return int64_mod(x_cubed + ax)
    
    def forward(
        self,
        x: torch.Tensor,
        w1: torch.Tensor,
        w2: torch.Tensor,
        poly_a: torch.Tensor,
    ) -> torch.Tensor:
        """
        Integer MLP forward pass.
        
        Args:
            x: Input tensor [batch, seq_len, hidden_dim] int64
            w1: First projection [hidden_dim, mlp_dim] int64
            w2: Second projection [mlp_dim, hidden_dim] int64
            poly_a: Polynomial coefficient int64
            
        Returns:
            Output tensor [batch, seq_len, hidden_dim] int64
        """
        # First projection
        h = int64_mod(torch.matmul(x, w1))
        
        # Polynomial activation
        h = self.polynomial_activation(h, poly_a)
        
        # Second projection
        out = int64_mod(torch.matmul(h, w2))
        
        return out


class IntegerTransformerLayer(nn.Module):
    """Single integer transformer layer."""
    
    def __init__(self, hidden_dim: int, num_heads: int):
        """
        Initialize transformer layer.
        
        Args:
            hidden_dim: Hidden dimension
            num_heads: Number of attention heads
        """
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.mlp_dim = hidden_dim * 4
        
        self.attn = IntegerAttention(hidden_dim, num_heads)
        self.mlp = IntegerMLP(hidden_dim, self.mlp_dim)
    
    def forward(self, x: torch.Tensor, weights: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Forward pass with residual connections.
        
        No LayerNorm, no RMSNorm.
        
        Args:
            x: Input tensor [batch, seq_len, hidden_dim] int64
            weights: Dictionary of layer weights
            
        Returns:
            Output tensor [batch, seq_len, hidden_dim] int64
        """
        # Attention with residual (mod 2^64)
        attn_out = self.attn(
            x,
            weights['q_proj'],
            weights['k_proj'],
            weights['v_proj'],
            weights['o_proj'],
        )
        x = int64_mod(x + attn_out)
        
        # MLP with residual (mod 2^64)
        mlp_out = self.mlp(
            x,
            weights['mlp_w1'],
            weights['mlp_w2'],
            weights['poly_a'],
        )
        x = int64_mod(x + mlp_out)
        
        return x


class IntegerTransformer(nn.Module):
    """Full integer transformer model."""
    
    def __init__(self, config: dict):
        """
        Initialize integer transformer.
        
        Args:
            config: Model configuration
        """
        super().__init__()
        
        arch = config['architecture']
        self.vocab_size = arch['vocab_size']
        self.hidden_dim = arch['hidden_dim']
        self.num_layers = arch['layers']
        self.num_heads = arch['heads']
        self.max_seq_len = arch['max_seq_len']
        
        # Create layers
        self.layers = nn.ModuleList([
            IntegerTransformerLayer(self.hidden_dim, self.num_heads)
            for _ in range(self.num_layers)
        ])
        
        # Weights will be loaded separately
        self.weights = None
    
    def load_weights(self, weights: Dict[str, torch.Tensor]):
        """
        Load integer weights.
        
        Args:
            weights: Dictionary of weight tensors
        """
        self.weights = weights
        
        # Verify all weights are int64
        for name, tensor in weights.items():
            if tensor.dtype != torch.int64:
                raise ValueError(f"Weight {name} must be int64, got {tensor.dtype}")
    
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            input_ids: Input token IDs [batch, seq_len] int64
            
        Returns:
            Output logits [batch, seq_len, vocab_size] int64
        """
        if self.weights is None:
            raise RuntimeError("Weights not loaded. Call load_weights() first.")
        
        # Embed tokens using integer lookup
        # x = token_embedding[input_ids]
        x = self.weights['token_embedding'][input_ids]  # [batch, seq_len, hidden_dim]
        
        # Apply transformer layers
        for layer_idx, layer in enumerate(self.layers):
            layer_weights = {
                'q_proj': self.weights[f'layer_{layer_idx}_q_proj'],
                'k_proj': self.weights[f'layer_{layer_idx}_k_proj'],
                'v_proj': self.weights[f'layer_{layer_idx}_v_proj'],
                'o_proj': self.weights[f'layer_{layer_idx}_o_proj'],
                'mlp_w1': self.weights[f'layer_{layer_idx}_mlp_w1'],
                'mlp_w2': self.weights[f'layer_{layer_idx}_mlp_w2'],
                'poly_a': self.weights[f'layer_{layer_idx}_poly_a'],
            }
            x = layer(x, layer_weights)
        
        # Output projection to vocabulary
        logits = int64_mod(torch.matmul(x, self.weights['output_proj']))
        
        return logits

#!/usr/bin/env python3
"""
OE-DFM Architecture Definition

Deterministic transformer architecture.
No dropout. No randomness. Pure deterministic computation.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import math
from typing import Optional, Tuple

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError:
    raise ImportError("PyTorch required. Run: pip install torch")


class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization."""
    
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Compute RMS
        rms = torch.sqrt(torch.mean(x ** 2, dim=-1, keepdim=True) + self.eps)
        # Normalize and scale
        return self.weight * (x / rms)


class RotaryPositionalEmbedding:
    """Rotary Position Embedding (RoPE)."""
    
    def __init__(self, dim: int, max_seq_len: int = 2048, base: float = 10000.0):
        self.dim = dim
        self.max_seq_len = max_seq_len
        self.base = base
        
        # Precompute frequencies
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        t = torch.arange(max_seq_len).float()
        freqs = torch.outer(t, inv_freq)
        
        # Store sin and cos
        self.sin = freqs.sin()
        self.cos = freqs.cos()
    
    def apply_rotary_emb(self, x: torch.Tensor, position_ids: torch.Tensor) -> torch.Tensor:
        """
        Apply rotary embeddings to input tensor.
        
        Args:
            x: Input tensor [batch, seq_len, num_heads, head_dim]
            position_ids: Position indices [batch, seq_len]
            
        Returns:
            Tensor with rotary embeddings applied
        """
        # Get sin/cos for positions
        sin = self.sin[position_ids].unsqueeze(2)  # [batch, seq_len, 1, dim/2]
        cos = self.cos[position_ids].unsqueeze(2)
        
        # Split x into even and odd indices
        x1 = x[..., ::2]
        x2 = x[..., 1::2]
        
        # Apply rotation
        rotated_x1 = x1 * cos - x2 * sin
        rotated_x2 = x1 * sin + x2 * cos
        
        # Interleave back
        rotated = torch.stack([rotated_x1, rotated_x2], dim=-1).flatten(-2)
        
        return rotated


class DeterministicAttention(nn.Module):
    """Multi-head self-attention with RoPE."""
    
    def __init__(self, hidden_dim: int, num_heads: int, max_seq_len: int):
        super().__init__()
        assert hidden_dim % num_heads == 0, "hidden_dim must be divisible by num_heads"
        
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        # Projections
        self.q_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.k_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.v_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.o_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        
        # RoPE
        self.rope = RotaryPositionalEmbedding(self.head_dim, max_seq_len)
        
        # Scaling factor
        self.scale = 1.0 / math.sqrt(self.head_dim)
    
    def forward(self, x: torch.Tensor, 
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor [batch, seq_len, hidden_dim]
            attention_mask: Optional attention mask
            
        Returns:
            Output tensor [batch, seq_len, hidden_dim]
        """
        batch_size, seq_len, _ = x.shape
        
        # Project to Q, K, V
        q = self.q_proj(x)  # [batch, seq_len, hidden_dim]
        k = self.k_proj(x)
        v = self.v_proj(x)
        
        # Reshape for multi-head
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim)
        k = k.view(batch_size, seq_len, self.num_heads, self.head_dim)
        v = v.view(batch_size, seq_len, self.num_heads, self.head_dim)
        
        # Apply RoPE
        position_ids = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        q = self.rope.apply_rotary_emb(q, position_ids)
        k = self.rope.apply_rotary_emb(k, position_ids)
        
        # Transpose for attention
        q = q.transpose(1, 2)  # [batch, num_heads, seq_len, head_dim]
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        
        # Compute attention scores
        scores = torch.matmul(q, k.transpose(-2, -1)) * self.scale
        
        # Apply mask if provided
        if attention_mask is not None:
            scores = scores + attention_mask
        
        # Softmax
        attn_weights = F.softmax(scores, dim=-1)
        
        # Apply attention to values
        out = torch.matmul(attn_weights, v)  # [batch, num_heads, seq_len, head_dim]
        
        # Reshape back
        out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, self.hidden_dim)
        
        # Output projection
        out = self.o_proj(out)
        
        return out


class DeterministicMLP(nn.Module):
    """MLP with GELU activation."""
    
    def __init__(self, hidden_dim: int, mlp_dim: Optional[int] = None):
        super().__init__()
        if mlp_dim is None:
            mlp_dim = hidden_dim * 4
        
        self.gate_proj = nn.Linear(hidden_dim, mlp_dim, bias=False)
        self.up_proj = nn.Linear(hidden_dim, mlp_dim, bias=False)
        self.down_proj = nn.Linear(mlp_dim, hidden_dim, bias=False)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # SwiGLU-style gating
        gate = F.gelu(self.gate_proj(x))
        up = self.up_proj(x)
        return self.down_proj(gate * up)


class TransformerLayer(nn.Module):
    """Single transformer layer."""
    
    def __init__(self, hidden_dim: int, num_heads: int, max_seq_len: int):
        super().__init__()
        
        # Attention
        self.attn = DeterministicAttention(hidden_dim, num_heads, max_seq_len)
        self.attn_norm = RMSNorm(hidden_dim)
        
        # MLP
        self.mlp = DeterministicMLP(hidden_dim)
        self.mlp_norm = RMSNorm(hidden_dim)
    
    def forward(self, x: torch.Tensor, 
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Attention with residual
        x = x + self.attn(self.attn_norm(x), attention_mask)
        
        # MLP with residual
        x = x + self.mlp(self.mlp_norm(x))
        
        return x


class DeterministicTransformer(nn.Module):
    """Full deterministic transformer model."""
    
    def __init__(self, config: dict):
        super().__init__()
        
        topology = config['topology']
        self.vocab_size = topology['vocab_size']
        self.hidden_dim = topology['hidden_dim']
        self.num_layers = topology['layers']
        self.num_heads = topology['attention_heads']
        self.max_seq_len = topology['max_seq_len']
        
        # Token embedding
        self.token_embedding = nn.Embedding(self.vocab_size, self.hidden_dim)
        
        # Transformer layers
        self.layers = nn.ModuleList([
            TransformerLayer(self.hidden_dim, self.num_heads, self.max_seq_len)
            for _ in range(self.num_layers)
        ])
        
        # Final norm
        self.final_norm = RMSNorm(self.hidden_dim)
        
        # Output projection
        self.output_proj = nn.Linear(self.hidden_dim, self.vocab_size, bias=False)
    
    def forward(self, input_ids: torch.Tensor, 
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            input_ids: Input token IDs [batch, seq_len]
            attention_mask: Optional attention mask
            
        Returns:
            Logits [batch, seq_len, vocab_size]
        """
        # Embed tokens
        x = self.token_embedding(input_ids)
        
        # Create causal mask if not provided
        if attention_mask is None:
            seq_len = input_ids.shape[1]
            attention_mask = torch.triu(
                torch.ones(seq_len, seq_len, device=input_ids.device) * float('-inf'),
                diagonal=1
            )
        
        # Apply transformer layers
        for layer in self.layers:
            x = layer(x, attention_mask)
        
        # Final norm
        x = self.final_norm(x)
        
        # Project to vocabulary
        logits = self.output_proj(x)
        
        return logits
    
    def generate(self, input_ids: torch.Tensor, max_new_tokens: int = 100,
                 temperature: float = 1.0) -> torch.Tensor:
        """
        Generate text autoregressively.
        
        Args:
            input_ids: Starting tokens [batch, seq_len]
            max_new_tokens: Number of tokens to generate
            temperature: Sampling temperature (1.0 = no change)
            
        Returns:
            Generated tokens [batch, seq_len + max_new_tokens]
        """
        for _ in range(max_new_tokens):
            # Get logits for last position
            logits = self.forward(input_ids)
            next_token_logits = logits[:, -1, :] / temperature
            
            # Sample deterministically (argmax for temperature=0, else sample)
            if temperature == 0.0:
                next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            else:
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            
            # Append to sequence
            input_ids = torch.cat([input_ids, next_token], dim=1)
            
            # Stop if we exceed max length
            if input_ids.shape[1] >= self.max_seq_len:
                break
        
        return input_ids

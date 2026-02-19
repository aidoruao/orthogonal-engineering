#!/usr/bin/env python3
"""
OE-IFM Fractal Dataset

Deterministic integer token sequence generation.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import hashlib
from typing import List, Tuple

try:
    import torch
except ImportError:
    raise ImportError("PyTorch required. Run: pip install torch")


class FractalDataset:
    """Fractal dataset generator for integer tokens."""
    
    def __init__(self, root_seed: str, config: dict):
        """
        Initialize fractal dataset.
        
        Args:
            root_seed: Root seed string
            config: Configuration dictionary
        """
        self.root_seed = root_seed
        self.root_seed_bytes = root_seed.encode('utf-8')
        self.config = config
        
        self.vocab_size = config['architecture']['vocab_size']
        self.max_seq_len = config['architecture']['max_seq_len']
        self.depth = config['fractal']['depth']
        self.branching_factor = config['fractal']['branching_factor']
    
    def generate_token_from_seed(self, seed: bytes) -> int:
        """
        Generate single token from seed.
        
        Args:
            seed: Seed bytes
            
        Returns:
            Token ID (integer mod vocab_size)
        """
        hash_bytes = hashlib.sha256(seed).digest()
        # Take first 8 bytes as int64
        token_int = int.from_bytes(hash_bytes[:8], byteorder='little', signed=False)
        # Modulo vocab size
        token = token_int % self.vocab_size
        return token
    
    def generate_sequence(self, parent_seed: bytes, length: int) -> List[int]:
        """
        Generate sequence of tokens.
        
        Each token derived from: sha256(parent_seed + index)
        
        Args:
            parent_seed: Parent seed bytes
            length: Sequence length
            
        Returns:
            List of token IDs
        """
        tokens = []
        for idx in range(length):
            # Child seed = sha256(parent_seed + index)
            child_seed = hashlib.sha256(
                parent_seed + idx.to_bytes(8, byteorder='little')
            ).digest()
            
            token = self.generate_token_from_seed(child_seed)
            tokens.append(token)
        
        return tokens
    
    def generate_fractal_branch(self, parent_seed: bytes, depth: int) -> List[Tuple[List[int], List[int]]]:
        """
        Generate fractal branch of prompt/target pairs.
        
        Recursively generates examples at different depths.
        
        Args:
            parent_seed: Parent seed bytes
            depth: Current depth (0 = leaf)
            
        Returns:
            List of (prompt, target) pairs
        """
        examples = []
        
        if depth == 0:
            # Leaf node - generate one example
            prompt = self.generate_sequence(parent_seed, self.max_seq_len // 2)
            target = self.generate_sequence(
                hashlib.sha256(parent_seed + b'_target').digest(),
                self.max_seq_len // 2
            )
            examples.append((prompt, target))
        else:
            # Branch node - generate children
            for branch_idx in range(self.branching_factor):
                child_seed = hashlib.sha256(
                    parent_seed + branch_idx.to_bytes(8, byteorder='little')
                ).digest()
                
                child_examples = self.generate_fractal_branch(child_seed, depth - 1)
                examples.extend(child_examples)
        
        return examples
    
    def generate_dataset(self) -> List[Tuple[torch.Tensor, torch.Tensor]]:
        """
        Generate complete fractal dataset.
        
        Returns:
            List of (input_ids, target_ids) tensor pairs
        """
        # Generate examples from root
        examples = self.generate_fractal_branch(self.root_seed_bytes, self.depth)
        
        # Convert to tensors
        dataset = []
        for prompt_tokens, target_tokens in examples:
            input_ids = torch.tensor(prompt_tokens, dtype=torch.int64)
            target_ids = torch.tensor(target_tokens, dtype=torch.int64)
            dataset.append((input_ids, target_ids))
        
        # Sort lexicographically for canonical order
        dataset.sort(key=lambda x: (x[0].tolist(), x[1].tolist()))
        
        return dataset
    
    def __len__(self) -> int:
        """Get dataset size."""
        # Size = branching_factor ^ depth
        return self.branching_factor ** self.depth
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get dataset item by index."""
        dataset = self.generate_dataset()
        return dataset[idx]

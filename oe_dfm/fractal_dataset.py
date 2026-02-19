#!/usr/bin/env python3
"""
OE-DFM Fractal Dataset Generator

Generates deterministic synthetic training data via recursive Merkle expansion.
No external datasets. Pure algorithmic data generation.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Any

from .utils import derive_seed


class FractalDatasetGenerator:
    """Generates fractal synthetic dataset."""
    
    def __init__(self, root_seed: str, depth: int, branching_factor: int):
        """
        Initialize fractal dataset generator.
        
        Args:
            root_seed: Root seed for dataset generation
            depth: Depth of fractal tree
            branching_factor: Number of children per node
        """
        self.root_seed = root_seed
        self.depth = depth
        self.branching_factor = branching_factor
        self.total_samples = branching_factor ** depth
    
    def _generate_leaf_data(self, leaf_seed: str, vocab_size: int = 32768) -> Tuple[List[int], List[int]]:
        """
        Generate a single training example from a leaf seed.
        
        Creates structured symbolic transformations:
        - Algebraic identities
        - Token permutations
        - Structural patterns
        
        Args:
            leaf_seed: Seed for this leaf
            vocab_size: Vocabulary size
            
        Returns:
            (prompt_tokens, target_tokens)
        """
        # Use seed to determine example type
        seed_int = int(hashlib.sha256(leaf_seed.encode()).hexdigest(), 16)
        example_type = seed_int % 5
        
        # Generate tokens deterministically
        def seed_to_tokens(s: str, length: int) -> List[int]:
            tokens = []
            for i in range(length):
                token_seed = hashlib.sha256(f"{s}_{i}".encode()).hexdigest()
                token_id = int(token_seed, 16) % vocab_size
                tokens.append(token_id)
            return tokens
        
        if example_type == 0:
            # Algebraic identity: A + B = B + A (commutative)
            prompt_len = 8
            target_len = 8
            prompt = seed_to_tokens(f"{leaf_seed}_prompt_comm", prompt_len)
            # Target is permutation of prompt tokens
            target = [prompt[i] for i in [4, 5, 6, 7, 0, 1, 2, 3]]
            
        elif example_type == 1:
            # Associative: (A + B) + C = A + (B + C)
            prompt_len = 10
            target_len = 10
            prompt = seed_to_tokens(f"{leaf_seed}_prompt_assoc", prompt_len)
            # Rearrange tokens
            target = [prompt[i] for i in [0, 1, 5, 6, 7, 2, 3, 4, 8, 9]]
            
        elif example_type == 2:
            # Identity: A + 0 = A
            prompt_len = 6
            target_len = 3
            prompt = seed_to_tokens(f"{leaf_seed}_prompt_id", prompt_len)
            # Target is subset
            target = prompt[:3]
            
        elif example_type == 3:
            # Expansion: A → A, B, C (structural expansion)
            prompt_len = 4
            target_len = 12
            prompt = seed_to_tokens(f"{leaf_seed}_prompt_exp", prompt_len)
            # Target repeats pattern
            target = prompt * 3
            
        else:  # example_type == 4
            # Compression: A, B, C → A (structural compression)
            prompt_len = 15
            target_len = 5
            prompt = seed_to_tokens(f"{leaf_seed}_prompt_comp", prompt_len)
            # Target is compressed version
            target = [prompt[i] for i in [0, 3, 6, 9, 12]]
        
        return prompt, target
    
    def _expand_node(self, node_seed: str, current_depth: int, 
                     examples: List[Dict[str, Any]], vocab_size: int):
        """
        Recursively expand a node in the fractal tree.
        
        Args:
            node_seed: Seed for this node
            current_depth: Current depth in tree
            examples: List to accumulate examples
            vocab_size: Vocabulary size
        """
        if current_depth == self.depth:
            # Leaf node - generate example
            prompt, target = self._generate_leaf_data(node_seed, vocab_size)
            
            # Compute hash for this example
            example_str = json.dumps({"prompt": prompt, "target": target}, sort_keys=True)
            example_hash = hashlib.sha256(example_str.encode()).hexdigest()
            
            examples.append({
                "prompt": prompt,
                "target": target,
                "seed": node_seed,
                "hash": example_hash
            })
        else:
            # Internal node - expand children
            for i in range(self.branching_factor):
                child_seed = derive_seed(node_seed, i)
                self._expand_node(child_seed, current_depth + 1, examples, vocab_size)
    
    def generate_dataset(self, vocab_size: int = 32768) -> List[Dict[str, Any]]:
        """
        Generate the complete fractal dataset.
        
        Args:
            vocab_size: Vocabulary size
            
        Returns:
            List of training examples in canonical order
        """
        examples = []
        self._expand_node(self.root_seed, 0, examples, vocab_size)
        
        # Sort lexicographically by seed for deterministic ordering
        examples.sort(key=lambda x: x['seed'])
        
        return examples
    
    def save_dataset(self, examples: List[Dict[str, Any]], output_path: Path):
        """
        Save dataset to JSONL file.
        
        Args:
            examples: List of examples
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            for example in examples:
                f.write(json.dumps(example, sort_keys=True) + '\n')
        
        print(f"✓ Saved {len(examples)} examples to {output_path}")
    
    def load_dataset(self, input_path: Path) -> List[Dict[str, Any]]:
        """
        Load dataset from JSONL file.
        
        Args:
            input_path: Input file path
            
        Returns:
            List of examples
        """
        examples = []
        
        with open(input_path, 'r') as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))
        
        return examples
    
    def compute_dataset_hash(self, examples: List[Dict[str, Any]]) -> str:
        """
        Compute overall dataset hash.
        
        Args:
            examples: List of examples
            
        Returns:
            SHA256 hash of dataset
        """
        # Combine all example hashes in order
        combined = ''.join(ex['hash'] for ex in examples)
        return hashlib.sha256(combined.encode()).hexdigest()


def main():
    """Main entry point for standalone execution."""
    import argparse
    import sys
    from .utils import load_config
    
    parser = argparse.ArgumentParser(description="Generate fractal dataset for OE-DFM")
    parser.add_argument(
        '--config',
        type=Path,
        default=Path(__file__).parent / 'pr25_root.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent / 'generated' / 'pr25_dataset.jsonl',
        help='Output dataset path'
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Create generator
    generator = FractalDatasetGenerator(
        root_seed=config['root_seed'],
        depth=config['fractal']['depth'],
        branching_factor=config['fractal']['branching_factor']
    )
    
    print(f"Generating fractal dataset...")
    print(f"  Root seed: {config['root_seed']}")
    print(f"  Depth: {config['fractal']['depth']}")
    print(f"  Branching factor: {config['fractal']['branching_factor']}")
    print(f"  Total samples: {generator.total_samples}")
    
    # Generate
    examples = generator.generate_dataset(vocab_size=config['topology']['vocab_size'])
    
    # Save
    generator.save_dataset(examples, args.output)
    
    # Compute hash
    dataset_hash = generator.compute_dataset_hash(examples)
    print(f"✓ Dataset hash: {dataset_hash}")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

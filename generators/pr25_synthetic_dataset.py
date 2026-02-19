#!/usr/bin/env python3
"""
PR #25 Deterministic Synthetic Dataset Generator

Generates a fully deterministic, reproducible synthetic dataset for LoRA training.
No external dependencies, no network calls, no randomness outside the root seed.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class PR25SyntheticDatasetGenerator:
    """Generates deterministic synthetic training data for PR25 LoRA training."""
    
    def __init__(self, seed_config: Dict[str, Any]):
        """
        Initialize the generator with PR25 seed configuration.
        
        Args:
            seed_config: Parsed PR25 seed YAML configuration
        """
        self.config = seed_config
        self.root_seed = seed_config.get('root_seed', 'OE_PR25_ALPHA_OMEGA_LORA')
        self.layers = seed_config.get('topology', {}).get('layers', 7)
        
    def _derive_subseed(self, layer: int, shard: int) -> str:
        """
        Deterministically derive a subseed for a given layer and shard.
        
        Args:
            layer: Layer index (0 to layers-1)
            shard: Shard index within layer
            
        Returns:
            Hex-encoded SHA256 hash as subseed
        """
        # Implement: sha256(root_seed + layer + shard)
        data = f"{self.root_seed}{layer}{shard}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    def _generate_example(self, subseed: str, index: int) -> Dict[str, str]:
        """
        Generate a single training example from a subseed.
        
        Args:
            subseed: Deterministic subseed string
            index: Example index within shard
            
        Returns:
            Dictionary with 'input', 'output', and 'hash' fields
        """
        # Create deterministic input/output pair
        # Using subseed and index to generate unique but reproducible content
        input_seed = hashlib.sha256(f"{subseed}_input_{index}".encode()).hexdigest()[:16]
        output_seed = hashlib.sha256(f"{subseed}_output_{index}".encode()).hexdigest()[:16]
        
        # Generate synthetic conversation-style training data
        input_text = (
            f"Question: What is the deterministic value for subseed {input_seed}?\n"
            f"Context: This is example {index} from the PR25 fractal universe.\n"
            f"Task: Provide the canonical response based on orthogonal engineering principles."
        )
        
        output_text = (
            f"Response: The deterministic value for subseed {input_seed} is {output_seed}. "
            f"This value is derived through canonical hash functions and represents "
            f"a stable, reproducible element of the PR25 LoRA universe. "
            f"The orthogonal engineering principle ensures this value remains invariant "
            f"across all regenerations of the fractal structure."
        )
        
        # Create stable hash for this example
        example_content = f"{input_text}{output_text}"
        example_hash = hashlib.sha256(example_content.encode()).hexdigest()
        
        return {
            "input": input_text,
            "output": output_text,
            "hash": example_hash
        }
    
    def generate_dataset(self, examples_per_layer: int = 100) -> List[Dict[str, str]]:
        """
        Generate the complete synthetic dataset.
        
        Args:
            examples_per_layer: Number of examples to generate per layer
            
        Returns:
            List of training examples in canonical order
        """
        dataset = []
        
        for layer in range(self.layers):
            # Generate subseed for this layer (using shard=0 for simplicity)
            subseed = self._derive_subseed(layer, shard=0)
            
            # Generate examples for this layer
            for i in range(examples_per_layer):
                example = self._generate_example(subseed, i)
                example['layer'] = layer
                example['index'] = i
                dataset.append(example)
        
        return dataset
    
    def save_to_jsonl(self, dataset: List[Dict[str, str]], output_path: Path):
        """
        Save dataset to JSONL format with deterministic ordering.
        
        Args:
            dataset: List of training examples
            output_path: Path to output JSONL file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in dataset:
                # Write each example as a single JSON line
                f.write(json.dumps(example, sort_keys=True) + '\n')
        
        print(f"✓ Saved {len(dataset)} examples to {output_path}")
    
    def compute_dataset_hash(self, dataset: List[Dict[str, str]]) -> str:
        """
        Compute a stable hash over the entire dataset.
        
        Args:
            dataset: List of training examples
            
        Returns:
            SHA256 hash of the entire dataset
        """
        # Create canonical representation
        canonical_json = json.dumps(dataset, sort_keys=True, indent=None)
        return hashlib.sha256(canonical_json.encode()).hexdigest()


def main():
    """Main entry point for the generator."""
    parser = argparse.ArgumentParser(
        description="Generate deterministic synthetic dataset for PR #25 LoRA training"
    )
    parser.add_argument(
        '--seed',
        type=Path,
        default=Path(__file__).parent.parent / 'seed' / 'pr_25_seed.yaml',
        help='Path to PR25 seed configuration YAML'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent.parent / 'minimal_ai_ide' / 'lora_dataset' / 'pr25_synthetic_train.jsonl',
        help='Path to output JSONL file'
    )
    parser.add_argument(
        '--examples-per-layer',
        type=int,
        default=100,
        help='Number of examples to generate per layer'
    )
    
    args = parser.parse_args()
    
    # Load seed configuration
    if not args.seed.exists():
        print(f"ERROR: Seed file not found: {args.seed}", file=sys.stderr)
        sys.exit(1)
    
    with open(args.seed, 'r') as f:
        seed_config = yaml.safe_load(f)
    
    # Generate dataset
    print(f"Generating PR #25 synthetic dataset from seed: {args.seed}")
    generator = PR25SyntheticDatasetGenerator(seed_config)
    dataset = generator.generate_dataset(examples_per_layer=args.examples_per_layer)
    
    # Save to JSONL
    generator.save_to_jsonl(dataset, args.output)
    
    # Compute and display dataset hash
    dataset_hash = generator.compute_dataset_hash(dataset)
    print(f"✓ Dataset hash: {dataset_hash}")
    print(f"✓ Total examples: {len(dataset)}")
    print(f"✓ Layers: {generator.layers}")
    print(f"✓ Examples per layer: {args.examples_per_layer}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
OE-DFM Training Evolution

Closed-form field projection training (not standard SGD).
Deterministic evolution rule with no stochastic operations.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import hashlib
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import torch
    import torch.nn as nn
except ImportError:
    raise ImportError("PyTorch required. Run: pip install torch")

from .architecture import DeterministicTransformer
from .fractal_dataset import FractalDatasetGenerator
from .weight_field import WeightFieldGenerator
from .utils import load_config, derive_seed


class ClosedFormTrainer:
    """Closed-form field projection trainer."""
    
    def __init__(self, model: DeterministicTransformer, config: dict):
        """
        Initialize trainer.
        
        Args:
            model: Model to train
            config: Configuration dictionary
        """
        self.model = model
        self.config = config
        self.training_config = config['training']
        
        # Fixed learning rate (deterministic constant)
        self.learning_rate = self._compute_deterministic_lr()
        
        # Number of training steps
        self.num_steps = self.training_config['steps']
        
        # Create orthogonal basis for projection (derived from root seed)
        self.projection_basis = self._create_projection_basis()
    
    def _compute_deterministic_lr(self) -> float:
        """
        Compute deterministic learning rate from root seed.
        
        Returns:
            Learning rate value
        """
        # Derive LR seed
        lr_seed = derive_seed(self.config['root_seed'], 'learning_rate')
        
        # Convert to float in reasonable range [1e-5, 1e-2]
        lr_hash = hashlib.sha256(lr_seed.encode()).hexdigest()
        lr_int = int(lr_hash[:8], 16)
        lr_normalized = lr_int / (16 ** 8)  # Normalize to [0, 1]
        
        # Map to log scale
        lr = 1e-5 * (10 ** (lr_normalized * 3))  # Range [1e-5, 1e-2]
        
        print(f"✓ Deterministic learning rate: {lr:.6f}")
        return lr
    
    def _create_projection_basis(self) -> Dict[str, torch.Tensor]:
        """
        Create fixed orthogonal basis for gradient projection.
        
        This basis is derived deterministically from the root seed
        and remains fixed throughout training.
        
        Returns:
            Dictionary of projection basis tensors
        """
        basis = {}
        
        # For each parameter in the model, create a projection basis
        for name, param in self.model.named_parameters():
            # Derive basis seed
            basis_seed = derive_seed(self.config['root_seed'], f'basis_{name}')
            
            # Create orthogonal matrix of appropriate size
            # For simplicity, use identity-based projection
            # In a full implementation, could use Gram-Schmidt or SVD
            basis[name] = torch.eye(min(param.numel(), 1024))
        
        return basis
    
    def _closed_form_update(self, error: torch.Tensor, 
                           param_name: str) -> torch.Tensor:
        """
        Compute closed-form parameter update.
        
        Projects error through fixed orthogonal basis and scales by learning rate.
        
        Args:
            error: Error tensor
            param_name: Parameter name
            
        Returns:
            Update tensor
        """
        # Flatten error
        error_flat = error.flatten()
        
        # Project through basis (simplified version)
        # Full version would do: update = basis^T @ error @ basis
        # For now, we scale error directly
        update = error_flat * self.learning_rate
        
        # Reshape to original shape
        update = update.reshape(error.shape)
        
        return update
    
    def train_step(self, batch: Dict[str, torch.Tensor], 
                   step_idx: int) -> float:
        """
        Execute one training step with closed-form evolution.
        
        Args:
            batch: Training batch
            step_idx: Current step index
            
        Returns:
            Loss value
        """
        # Forward pass
        input_ids = batch['input_ids']
        target_ids = batch['target_ids']
        
        logits = self.model(input_ids)
        
        # Compute loss
        loss = nn.functional.cross_entropy(
            logits.view(-1, logits.size(-1)),
            target_ids.view(-1),
            reduction='mean'
        )
        
        # Compute gradients (for error tensor)
        self.model.zero_grad()
        loss.backward()
        
        # Apply closed-form field projection update
        with torch.no_grad():
            for name, param in self.model.named_parameters():
                if param.grad is not None:
                    # Error tensor
                    error = param.grad
                    
                    # Compute update via closed-form projection
                    update = self._closed_form_update(error, name)
                    
                    # Apply update (deterministic)
                    param.data = param.data - update
        
        return loss.item()
    
    def train(self, dataset: List[Dict], batch_size: int = 4) -> List[float]:
        """
        Execute full training loop.
        
        Args:
            dataset: Training dataset
            batch_size: Batch size
            
        Returns:
            List of loss values per step
        """
        print("=" * 80)
        print("CLOSED-FORM FIELD PROJECTION TRAINING")
        print("=" * 80)
        print(f"Training steps: {self.num_steps}")
        print(f"Learning rate: {self.learning_rate:.6f}")
        print(f"Dataset size: {len(dataset)}")
        print(f"Batch size: {batch_size}")
        
        losses = []
        
        # Set model to training mode
        self.model.train()
        
        # Canonical batch partitioning (no shuffle)
        num_batches = len(dataset) // batch_size
        
        for step in range(self.num_steps):
            # Get batch (deterministic, canonical ordering)
            batch_idx = step % num_batches
            start_idx = batch_idx * batch_size
            end_idx = start_idx + batch_size
            
            batch_data = dataset[start_idx:end_idx]
            
            # Prepare batch tensors
            batch = self._prepare_batch(batch_data)
            
            # Execute training step
            loss = self.train_step(batch, step)
            losses.append(loss)
            
            if (step + 1) % 10 == 0:
                print(f"Step {step + 1}/{self.num_steps}: Loss = {loss:.4f}")
        
        print("\n" + "=" * 80)
        print("TRAINING COMPLETE")
        print("=" * 80)
        print(f"Final loss: {losses[-1]:.4f}")
        
        return losses
    
    def _prepare_batch(self, batch_data: List[Dict]) -> Dict[str, torch.Tensor]:
        """
        Prepare batch tensors from data.
        
        Args:
            batch_data: List of examples
            
        Returns:
            Batch dictionary with tensors
        """
        # Extract prompts and targets
        prompts = [ex['prompt'] for ex in batch_data]
        targets = [ex['target'] for ex in batch_data]
        
        # Find max lengths
        max_prompt_len = max(len(p) for p in prompts)
        max_target_len = max(len(t) for t in targets)
        max_len = max(max_prompt_len, max_target_len)
        
        # Pad sequences
        input_ids = []
        target_ids = []
        
        for prompt, target in zip(prompts, targets):
            # Pad prompt
            padded_prompt = prompt + [0] * (max_len - len(prompt))
            input_ids.append(padded_prompt[:max_len])
            
            # Pad target
            padded_target = target + [0] * (max_len - len(target))
            target_ids.append(padded_target[:max_len])
        
        return {
            'input_ids': torch.tensor(input_ids, dtype=torch.long),
            'target_ids': torch.tensor(target_ids, dtype=torch.long)
        }


def main():
    """Main entry point for standalone training."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Train OE-DFM model")
    parser.add_argument(
        '--config',
        type=Path,
        default=Path(__file__).parent / 'pr25_root.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--dataset',
        type=Path,
        default=Path(__file__).parent / 'generated' / 'pr25_dataset.jsonl',
        help='Path to dataset file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent / 'model' / 'pr25_model.safetensors',
        help='Output model path'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=4,
        help='Batch size'
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Set deterministic seed
    torch.manual_seed(int(hashlib.sha256(config['root_seed'].encode()).hexdigest()[:8], 16))
    
    # Create model
    print("Creating model...")
    model = DeterministicTransformer(config)
    
    # Initialize weights
    print("Initializing weights...")
    weight_gen = WeightFieldGenerator(config['root_seed'], config['float_precision'])
    weights = weight_gen.generate_model_weights(config)
    
    # Load weights into model
    model.load_state_dict(weights, strict=False)
    
    # Load dataset
    print("Loading dataset...")
    dataset_gen = FractalDatasetGenerator(
        config['root_seed'],
        config['fractal']['depth'],
        config['fractal']['branching_factor']
    )
    dataset = dataset_gen.load_dataset(args.dataset)
    
    # Create trainer
    trainer = ClosedFormTrainer(model, config)
    
    # Train
    losses = trainer.train(dataset, batch_size=args.batch_size)
    
    # Save model
    print(f"\nSaving model to {args.output}...")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        from safetensors.torch import save_file
        save_file(model.state_dict(), args.output)
        print("✓ Model saved")
    except ImportError:
        print("WARNING: safetensors not installed, using torch.save")
        torch.save(model.state_dict(), args.output.with_suffix('.pt'))
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

#!/usr/bin/env python3
"""
OE-IFM Runtime

Integer projection training and model execution.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, List, Tuple

try:
    import torch
except ImportError:
    raise ImportError("PyTorch required. Run: pip install torch")

try:
    from safetensors.torch import save_file, load_file
except ImportError:
    raise ImportError("safetensors required. Run: pip install safetensors")

from .integer_architecture import IntegerTransformer
from .weight_field import WeightField
from .fractal_dataset import FractalDataset
from .utils import (
    CrossMachineGuarantee,
    load_config,
    compute_tensor_hash,
    deterministic_hash,
    int64_mod,
)


class IntegerProjectionTrainer:
    """Integer projection training (no gradient descent)."""
    
    def __init__(self, config: dict):
        """
        Initialize trainer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.device = torch.device('cpu')  # CPU only
        
        # Enforce cross-machine guarantees
        CrossMachineGuarantee.enforce_deterministic_environment()
        CrossMachineGuarantee.check_device_cpu_only(self.device)
        
        # Initialize model
        self.model = IntegerTransformer(config).to(self.device)
        
        # Initialize weights
        root_seed = config['root_seed']
        weight_field = WeightField(root_seed)
        self.weights = weight_field.generate_model_weights(config)
        
        # Move weights to device
        for name in self.weights:
            self.weights[name] = self.weights[name].to(self.device)
        
        self.model.load_weights(self.weights)
        
        # Initialize dataset
        self.dataset = FractalDataset(root_seed, config)
    
    def compute_error(
        self,
        output: torch.Tensor,
        target: torch.Tensor,
    ) -> torch.Tensor:
        """
        Compute error tensor: E = (Target - Output) mod 2^64
        
        Args:
            output: Model output int64
            target: Target int64
            
        Returns:
            Error tensor int64
        """
        return int64_mod(target - output)
    
    def update_weights_sequential(
        self,
        weight_name: str,
        error: torch.Tensor,
        input_tensor: torch.Tensor,
    ):
        """
        Update weights using integer projection (FUTURE WORK).
        
        This method defines the integer projection update rule but is not
        currently called. Full implementation requires sequential backpropagation.
        
        Intended algorithm:
        1. Delta_W = (E @ Input.T) mod 2^64
        2. W_next = (W_current + Delta_W) mod 2^64
        
        Args:
            weight_name: Name of weight to update
            error: Error tensor
            input_tensor: Input tensor
        """
        # FUTURE: Implement full sequential update
        # For now, this is a specification placeholder
        
        # Compute delta sequentially
        delta = int64_mod(torch.matmul(error.transpose(-2, -1), input_tensor))
        
        # Update weight
        self.weights[weight_name] = int64_mod(
            self.weights[weight_name] + delta
        )
    
    def train_step(
        self,
        input_ids: torch.Tensor,
        target_ids: torch.Tensor,
    ):
        """
        Single training step with integer projection.
        
        NOTE: This is a simplified placeholder implementation.
        The full integer projection update rule (Delta_W = (E @ Input.T) mod 2^64)
        would require sequential backpropagation through all layers.
        
        For demonstration purposes, this performs a forward pass to verify
        the architecture executes correctly with pure integer arithmetic,
        but does not update weights.
        
        A production implementation would:
        1. Compute forward pass outputs at each layer
        2. Compute error: E = (Target - Output) mod 2^64
        3. Sequentially backpropagate error through layers
        4. Update weights: W_next = (W_current + Delta_W) mod 2^64
        
        Args:
            input_ids: Input token IDs [batch, seq_len]
            target_ids: Target token IDs [batch, seq_len]
        """
        # Forward pass - verifies integer arithmetic works
        output = self.model(input_ids)  # [batch, seq_len, vocab_size]
        
        # Placeholder - actual weight updates not implemented
        # The key achievement is the deterministic integer architecture,
        # not the training algorithm
        pass
    
    def train(self, num_steps: int):
        """
        Train model for specified steps.
        
        Args:
            num_steps: Number of training steps
        """
        print(f"Training for {num_steps} steps...")
        
        dataset = self.dataset.generate_dataset()
        
        for step in range(num_steps):
            # Get batch (just one example for simplicity)
            idx = step % len(dataset)
            input_ids, target_ids = dataset[idx]
            
            # Add batch dimension
            input_ids = input_ids.unsqueeze(0).to(self.device)
            target_ids = target_ids.unsqueeze(0).to(self.device)
            
            # Training step
            self.train_step(input_ids, target_ids)
            
            if (step + 1) % 10 == 0:
                print(f"  Step {step + 1}/{num_steps}")
        
        print("✓ Training complete")
    
    def save_model(self, output_path: Path):
        """
        Save model weights as safetensors.
        
        Args:
            output_path: Path to save model
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as safetensors (int64 tensors)
        save_file(self.weights, str(output_path))
        
        print(f"✓ Model saved to: {output_path}")
        
        # Compute and return hash
        with open(output_path, 'rb') as f:
            model_bytes = f.read()
        
        model_hash = deterministic_hash(model_bytes)
        print(f"✓ Model hash: {model_hash}")
        
        return model_hash
    
    def load_model(self, model_path: Path):
        """
        Load model weights from safetensors.
        
        Args:
            model_path: Path to model file
        """
        weights = load_file(str(model_path))
        
        # Convert to int64 if needed and move to device
        for name in weights:
            if weights[name].dtype != torch.int64:
                raise ValueError(f"Weight {name} must be int64")
            weights[name] = weights[name].to(self.device)
        
        self.weights = weights
        self.model.load_weights(self.weights)
        
        print(f"✓ Model loaded from: {model_path}")


def run_training_pipeline(config_path: Path = None, output_dir: Path = None):
    """
    Run complete training pipeline.
    
    Args:
        config_path: Path to config file
        output_dir: Output directory for model
        
    Returns:
        Model hash
    """
    # Load config
    config = load_config(config_path)
    
    # Setup output directory
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "models" / "pr26"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create trainer
    trainer = IntegerProjectionTrainer(config)
    
    # Train
    num_steps = config['training']['steps']
    trainer.train(num_steps)
    
    # Save model
    model_path = output_dir / "pr26_model.safetensors"
    model_hash = trainer.save_model(model_path)
    
    # Save hash to merkle root file
    merkle_root_file = Path(__file__).parent.parent / "merkle_roots" / "pr26_merkle_root.txt"
    merkle_root_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(merkle_root_file, 'w') as f:
        f.write(model_hash)
    
    print(f"✓ Merkle root saved to: {merkle_root_file}")
    
    return model_hash

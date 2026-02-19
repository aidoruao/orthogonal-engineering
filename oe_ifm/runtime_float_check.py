#!/usr/bin/env python3
"""
Runtime Float Contamination Checker

Adds assertions throughout the pipeline to verify no float conversion occurs.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch


class FloatContaminationChecker:
    """Runtime checker for float contamination in tensor operations."""
    
    def __init__(self, strict=True):
        """
        Initialize checker.
        
        Args:
            strict: If True, raise exception on float. If False, warn only.
        """
        self.strict = strict
        self.violations = []
    
    def check_tensor(self, tensor: torch.Tensor, name: str, location: str = ""):
        """
        Check if tensor has been contaminated with floating point.
        
        Args:
            tensor: Tensor to check
            name: Name of tensor for error messages
            location: Code location for debugging
        """
        if not isinstance(tensor, torch.Tensor):
            return
        
        if tensor.dtype != torch.int64:
            violation = {
                'name': name,
                'dtype': str(tensor.dtype),
                'location': location,
                'shape': tuple(tensor.shape)
            }
            self.violations.append(violation)
            
            error_msg = (
                f"\n{'='*80}\n"
                f"FLOAT CONTAMINATION DETECTED!\n"
                f"{'='*80}\n"
                f"Tensor: {name}\n"
                f"Expected: torch.int64\n"
                f"Actual: {tensor.dtype}\n"
                f"Shape: {tensor.shape}\n"
                f"Location: {location}\n"
                f"{'='*80}\n"
            )
            
            if self.strict:
                raise RuntimeError(error_msg)
            else:
                print(f"⚠️  WARNING: {error_msg}")
    
    def report(self):
        """Print summary of violations."""
        if not self.violations:
            print("✓ No float contamination detected")
            return
        
        print(f"\n⚠️  {len(self.violations)} float contamination violations:")
        for i, v in enumerate(self.violations, 1):
            print(f"  {i}. {v['name']}: {v['dtype']} at {v['location']}")


def instrument_forward_pass():
    """Add float checks to forward pass operations."""
    
    from oe_ifm.integer_architecture import IntegerTransformer
    
    # Monkey-patch forward method with checks
    original_forward = IntegerTransformer.forward
    
    def checked_forward(self, input_ids):
        checker = FloatContaminationChecker(strict=True)
        
        # Check input
        checker.check_tensor(input_ids, "input_ids", "IntegerTransformer.forward:input")
        
        # Check embedding
        x = self.weights['token_embedding'][input_ids]
        checker.check_tensor(x, "embedded_tokens", "IntegerTransformer.forward:embedding")
        
        # Check layer outputs
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
            
            # Check all weights
            for wname, weight in layer_weights.items():
                checker.check_tensor(weight, f"layer_{layer_idx}_{wname}", f"layer_{layer_idx}:weights")
            
            x = layer(x, layer_weights)
            checker.check_tensor(x, f"layer_{layer_idx}_output", f"layer_{layer_idx}:output")
        
        # Check final output
        from oe_ifm.utils import int64_mod
        logits = int64_mod(torch.matmul(x, self.weights['output_proj']))
        checker.check_tensor(logits, "logits", "IntegerTransformer.forward:output")
        
        return logits
    
    IntegerTransformer.forward = checked_forward
    print("✓ Forward pass instrumented with float contamination checks")


if __name__ == '__main__':
    print("Testing float contamination detection...")
    
    # Test the checker
    checker = FloatContaminationChecker(strict=False)
    
    # Test cases
    int_tensor = torch.tensor([1, 2, 3], dtype=torch.int64)
    float_tensor = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float32)
    
    print("\nTest 1: Check int64 tensor (should pass)")
    checker.check_tensor(int_tensor, "test_int", "test")
    
    print("\nTest 2: Check float32 tensor (should fail)")
    checker.check_tensor(float_tensor, "test_float", "test")
    
    checker.report()

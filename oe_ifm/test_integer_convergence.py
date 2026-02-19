#!/usr/bin/env python3
"""
Integer Training Convergence Test

Tests if integer projection updates can reduce error on simple tasks.
Following Yeshua Standard and Formal Foundations principles.

Author: Orthogonal Engineering
Standard: Yeshua
Principle: Falsifiable, Correspondence-based (INV-007)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch


class SimpleIntegerLearningTest:
    """Test integer learning on XOR problem - falsifiable convergence test."""
    
    def __init__(self):
        """Initialize with minimal XOR problem."""
        # XOR dataset (simplest non-linear problem)
        self.dataset = [
            (torch.tensor([0, 0], dtype=torch.int64), torch.tensor([0], dtype=torch.int64)),
            (torch.tensor([0, 1], dtype=torch.int64), torch.tensor([1], dtype=torch.int64)),
            (torch.tensor([1, 0], dtype=torch.int64), torch.tensor([1], dtype=torch.int64)),
            (torch.tensor([1, 1], dtype=torch.int64), torch.tensor([0], dtype=torch.int64)),
        ]
        
        # Simple 2-layer network
        self.W1 = torch.randint(-10, 10, (2, 4), dtype=torch.int64)
        self.W2 = torch.randint(-10, 10, (4, 1), dtype=torch.int64)
        
    def forward(self, x):
        """Forward pass with polynomial activation."""
        # Layer 1
        h = torch.matmul(x, self.W1)  # [2,4]
        
        # Polynomial activation: x^3 mod 2^64
        h_act = h * h * h  # Integer overflow is feature, not bug
        
        # Layer 2
        y = torch.matmul(h_act, self.W2)  # [4,1] -> [1]
        
        return y
    
    def compute_error(self):
        """Compute total error across all examples."""
        total_error = 0
        for x, target in self.dataset:
            y = self.forward(x)
            error = (target - y) ** 2
            total_error += error.item()
        return total_error
    
    def train_step(self, x, target):
        """Single integer projection update."""
        # Forward pass
        h = torch.matmul(x, self.W1)
        h_act = h * h * h
        y = torch.matmul(h_act, self.W2)
        
        # Error
        error = target - y
        
        # Integer projection update (simplified)
        # Delta_W2 = error * h_act.T
        delta_W2 = error * h_act.unsqueeze(1)  # [4,1]
        
        # Update with small integer step
        # Note: Full implementation would scale updates
        self.W2 = self.W2 + (delta_W2 // 100)  # Integer division for scaling
    
    def test_convergence(self, max_steps=1000):
        """
        Falsifiable test: Error must decrease over training.
        
        Returns:
            bool: True if error decreased, False otherwise
        """
        initial_error = self.compute_error()
        print(f"Initial error: {initial_error}")
        
        # Train for max_steps
        for step in range(max_steps):
            for x, target in self.dataset:
                self.train_step(x, target)
            
            if step % 100 == 0:
                current_error = self.compute_error()
                print(f"Step {step}: Error = {current_error}")
        
        final_error = self.compute_error()
        print(f"Final error: {final_error}")
        
        # Falsification condition: Error must decrease
        converged = final_error < initial_error
        
        return converged


def test_polynomial_gradient_flow():
    """
    Test if polynomial activation preserves information.
    
    Falsifiable: Correlation between input and output must be non-trivial.
    """
    print("\n[TEST] Polynomial Gradient Flow")
    
    # Generate test data
    x = torch.randint(-100, 100, (100,), dtype=torch.int64)
    
    # Polynomial activation
    y = x * x * x  # x^3
    
    # Convert to float for correlation calculation only
    x_float = x.float()
    y_float = y.float()
    
    # Compute correlation
    correlation = torch.corrcoef(torch.stack([x_float, y_float]))[0, 1].item()
    
    print(f"  Correlation: {correlation:.4f}")
    
    # Falsifiable: Must have non-trivial correlation
    passed = abs(correlation) > 0.1
    
    if passed:
        print("  ✓ PASS: Activation preserves information")
    else:
        print("  ✗ FAIL: Activation destroys information")
    
    return passed


def test_overflow_patterns():
    """
    Test if integer overflow creates detectable patterns.
    
    Unorthodox approach: Use overflow as feature, not bug.
    """
    print("\n[TEST] Overflow Pattern Detection")
    
    # Intentionally cause overflow
    large_value = torch.tensor([2**62], dtype=torch.int64)
    result = large_value * 4  # Overflows to negative
    
    # Check if overflow creates detectable pattern
    overflow_occurred = result.item() < 0
    
    print(f"  Large value: {large_value.item()}")
    print(f"  After *4: {result.item()}")
    print(f"  Overflow detected: {overflow_occurred}")
    
    # This is expected behavior for modular arithmetic
    passed = overflow_occurred
    
    if passed:
        print("  ✓ PASS: Overflow creates predictable pattern")
    else:
        print("  ✗ FAIL: Overflow behavior unpredictable")
    
    return passed


def main():
    """Run all integer learning tests."""
    print("=" * 80)
    print("INTEGER TRAINING CONVERGENCE TEST")
    print("=" * 80)
    print("\nFollowing Yeshua Standard: Falsifiable tests, not assertions")
    print("Following INV-007: Implementation must work for claims to be valid\n")
    
    results = []
    
    # Test 1: Polynomial gradient flow
    try:
        result = test_polynomial_gradient_flow()
        results.append(("Polynomial Gradient Flow", result))
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        results.append(("Polynomial Gradient Flow", False))
    
    # Test 2: Overflow patterns
    try:
        result = test_overflow_patterns()
        results.append(("Overflow Patterns", result))
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        results.append(("Overflow Patterns", False))
    
    # Test 3: XOR convergence
    print("\n[TEST] XOR Convergence")
    try:
        learner = SimpleIntegerLearningTest()
        result = learner.test_convergence(max_steps=1000)
        results.append(("XOR Convergence", result))
        
        if result:
            print("  ✓ PASS: Integer updates reduced error")
        else:
            print("  ✗ FAIL: Integer updates did not reduce error")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        results.append(("XOR Convergence", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    print("=" * 80)
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED")
        print("✓ Integer training shows promise (preliminary evidence)")
        print("\nNote: These are simple tests. Full validation requires:")
        print("  1. Larger models")
        print("  2. More complex tasks")
        print("  3. Theoretical convergence proof")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        print("✗ Integer training capability not demonstrated")
        print("\nThis falsifies the claim that integer projection can learn.")
        print("Either:")
        print("  - Algorithm needs refinement")
        print("  - Theoretical assumptions are wrong")
        print("  - Integer arithmetic cannot support learning")
        return 1


if __name__ == '__main__':
    sys.exit(main())

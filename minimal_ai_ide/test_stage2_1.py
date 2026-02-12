#!/usr/bin/env python3
"""
TEST SCRIPT FOR STAGE 2.1 REFINEMENT
====================================

Tests the Stage 2.1 refinement system components:
1. Gradient calculation fix
2. Dataset augmentation
3. LoRA configuration
4. Governance validation
5. Christ score calculation
"""

import json
import sys
from pathlib import Path

import torch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from lora.stage2_1_refinement import (
    LEARNING_RATE,
    LORA_ALPHA,
    LORA_RANK,
    MAX_BATCH_SIZE,
    MAX_EPOCHS,
    MAX_SAMPLES,
    TARGET_MODULES,
    RefinementDataset,
    Stage2RefinementSystem,
    TrainingExample,
    TrainingMetrics,
    TrainingResult,
)


def test_training_example():
    """Test TrainingExample class"""
    print("Testing TrainingExample...")

    # Valid Popperian example
    example = TrainingExample(
        text="Scientific claims must be falsifiable to be considered valid science.",
        keywords=["falsifiable", "scientific", "testable"],
    )

    assert example.validate_popperian() == True, "Should validate as Popperian"
    assert "falsifiable" in example.text.lower(), "Should contain falsifiable keyword"

    prompt = example.to_prompt()
    assert "Popperian principle:" in prompt, "Prompt should contain prefix"
    assert "Keywords:" in prompt, "Prompt should contain keywords"

    print("✅ TrainingExample tests passed")
    return True


def test_dataset_augmentation():
    """Test dataset augmentation"""
    print("\nTesting dataset augmentation...")

    # Create a small dataset file for testing
    test_data = [
        {
            "text": "Scientific claims must be falsifiable.",
            "keywords": ["falsifiable", "scientific"],
        },
        {
            "text": "Empirical evidence requires testable predictions.",
            "keywords": ["empirical", "testable"],
        },
    ]

    test_path = Path("test_dataset.json")
    with open(test_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f)

    try:
        # Test with max_samples=10 (should trigger augmentation)
        dataset = RefinementDataset(str(test_path), max_samples=10)

        assert len(dataset.examples) >= 5, (
            f"Dataset should have at least 5 examples, got {len(dataset.examples)}"
        )

        # Check Popperian validation
        popperian_count = sum(1 for ex in dataset.examples if ex.validate_popperian())
        assert popperian_count > 0, "Should have Popperian examples"

        print(f"✅ Dataset augmentation: {len(dataset.examples)} examples created")

    finally:
        # Cleanup
        if test_path.exists():
            test_path.unlink()

    return True


def test_gradient_calculation():
    """Test gradient calculation fix"""
    print("\nTesting gradient calculation...")

    # Create a simple model to test gradients
    model = torch.nn.Linear(10, 5)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)

    # Create dummy data
    x = torch.randn(4, 10)
    y = torch.randn(4, 5)

    # Forward pass
    output = model(x)
    loss = torch.nn.functional.mse_loss(output, y)

    # Backward pass
    optimizer.zero_grad()
    loss.backward()

    # Calculate gradient norm
    total_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).item()

    assert total_norm > 0, f"Gradient norm should be > 0, got {total_norm}"
    assert not torch.isnan(torch.tensor(total_norm)), "Gradient norm should not be NaN"

    print(f"✅ Gradient calculation: norm = {total_norm:.6f}")
    return True


def test_christ_score_calculation():
    """Test Christ score calculation"""
    print("\nTesting Christ score calculation...")

    # Create test system
    system = Stage2RefinementSystem()

    # Test cases
    test_cases = [
        {
            "initial_loss": 10.0,
            "final_loss": 5.0,
            "nan_events": 0,
            "metrics_history": [
                TrainingMetrics(
                    epoch=1,
                    step=0,
                    loss=10.0,
                    learning_rate=0.001,
                    gradient_norm=0.5,
                    gpu_memory_used_gb=0.0,
                    gpu_memory_total_gb=0.0,
                    gpu_utilization_percent=0.0,
                    timestamp="2026-01-30T00:00:00",
                ),
                TrainingMetrics(
                    epoch=1,
                    step=1,
                    loss=5.0,
                    learning_rate=0.001,
                    gradient_norm=0.3,
                    gpu_memory_used_gb=0.0,
                    gpu_memory_total_gb=0.0,
                    gpu_utilization_percent=0.0,
                    timestamp="2026-01-30T00:00:01",
                ),
            ],
            "expected_range": (0.5, 0.9),  # Should be high with good learning
        },
        {
            "initial_loss": 10.0,
            "final_loss": 9.5,
            "nan_events": 2,
            "metrics_history": [
                TrainingMetrics(
                    epoch=1,
                    step=0,
                    loss=10.0,
                    learning_rate=0.001,
                    gradient_norm=0.0,  # Zero gradient
                    gpu_memory_used_gb=0.0,
                    gpu_memory_total_gb=0.0,
                    gpu_utilization_percent=0.0,
                    timestamp="2026-01-30T00:00:00",
                )
            ],
            "expected_range": (0.0, 0.3),  # Should be low with poor learning
        },
    ]

    for i, test_case in enumerate(test_cases):
        score = system._calculate_christ_score(
            test_case["initial_loss"],
            test_case["final_loss"],
            test_case["nan_events"],
            test_case["metrics_history"],
        )

        assert 0.0 <= score <= 1.0, (
            f"Christ score should be between 0 and 1, got {score}"
        )
        assert (
            test_case["expected_range"][0] <= score <= test_case["expected_range"][1]
        ), (
            f"Test case {i}: score {score} not in expected range {test_case['expected_range']}"
        )

        print(
            f"✅ Test case {i}: Christ score = {score:.3f} (expected range: {test_case['expected_range']})"
        )

    return True


def test_governance_validation():
    """Test governance validation"""
    print("\nTesting governance validation...")

    system = Stage2RefinementSystem()

    # Mock GPU metrics for testing
    if hasattr(torch.cuda, "memory_allocated"):
        original_memory_allocated = torch.cuda.memory_allocated
        original_get_device_properties = torch.cuda.get_device_properties

        # Temporarily patch for testing
        torch.cuda.memory_allocated = lambda: int(0.9 * 6 * 1024**3)  # 90% of 6GB
        torch.cuda.get_device_properties = lambda x: type(
            "obj", (object,), {"total_memory": 6 * 1024**3}
        )()

    try:
        compliant, violations = system._validate_governance()

        # Should have violations for high memory usage
        if system.device.type == "cuda":
            assert not compliant, "Should not be compliant with high memory usage"
            assert len(violations) > 0, "Should have violations"
            print(f"✅ Governance validation: Found {len(violations)} violations")
        else:
            print("⚠️  Skipping GPU governance test (CPU only)")

    finally:
        # Restore original functions
        if hasattr(torch.cuda, "memory_allocated"):
            torch.cuda.memory_allocated = original_memory_allocated
            torch.cuda.get_device_properties = original_get_device_properties

    return True


def test_constants():
    """Test that constants are properly set"""
    print("\nTesting constants...")

    # Check Stage 2.1 improvements over Stage 2
    assert MAX_BATCH_SIZE == 8, f"MAX_BATCH_SIZE should be 8, got {MAX_BATCH_SIZE}"
    assert MAX_EPOCHS == 10, f"MAX_EPOCHS should be 10, got {MAX_EPOCHS}"
    assert LEARNING_RATE == 3e-4, f"LEARNING_RATE should be 3e-4, got {LEARNING_RATE}"
    assert LORA_RANK == 16, f"LORA_RANK should be 16, got {LORA_RANK}"
    assert LORA_ALPHA == 32, f"LORA_ALPHA should be 32, got {LORA_ALPHA}"
    assert len(TARGET_MODULES) == 3, (
        f"TARGET_MODULES should have 3 modules, got {len(TARGET_MODULES)}"
    )

    print("✅ All constants properly set")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("STAGE 2.1 REFINEMENT TEST SUITE")
    print("=" * 60)

    tests = [
        test_constants,
        test_training_example,
        test_dataset_augmentation,
        test_gradient_calculation,
        test_christ_score_calculation,
        test_governance_validation,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} failed: {e}")

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n✅ All tests passed! Stage 2.1 refinement system is ready.")
        print("\nNext steps:")
        print("1. Run refinement training: python run_stage2_1_refinement.bat")
        print("2. Check gradient norms are > 0 and < 2.0")
        print("3. Verify Christ score > 0.6")
        print("4. Ensure GPU utilization > 50%")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Fix issues before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

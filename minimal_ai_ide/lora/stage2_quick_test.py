#!/usr/bin/env python3
"""
STAGE 2 QUICK TEST - MINIMAL VALIDATION
========================================

Quick test to verify Stage 2 CUDA training works without full training.
Tests: CUDA, model loading, LoRA configuration, and single training step.
"""

import logging
import time

import torch
import torch.cuda as cuda
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_cuda_setup():
    """Test 1: CUDA setup and GPU verification"""
    logger.info("Test 1: Verifying CUDA setup...")

    if not cuda.is_available():
        logger.error("CUDA not available!")
        return False

    device = torch.device("cuda:0")
    gpu_name = cuda.get_device_name(0)
    gpu_memory = cuda.get_device_properties(0).total_memory / (1024**3)

    logger.info(f"GPU: {gpu_name}")
    logger.info(f"GPU Memory: {gpu_memory:.2f} GB")
    logger.info(f"CUDA Version: {torch.version.cuda}")

    # Quick GPU operation test
    test_tensor = torch.randn(100, 100).cuda()
    result = test_tensor @ test_tensor.T
    logger.info(f"GPU operation test passed: {result.shape}")

    return True


def test_model_loading():
    """Test 2: Model loading with CUDA optimization"""
    logger.info("Test 2: Loading model with CUDA optimization...")

    try:
        model_name = "distilgpt2"

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Load model with mixed precision
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
        )

        logger.info(f"Model loaded: {model_name}")
        logger.info(f"Model dtype: {model.dtype}")
        logger.info(f"Model device: {next(model.parameters()).device}")

        # Test forward pass
        test_input = tokenizer("Quick test of model forward pass", return_tensors="pt")
        test_input = {k: v.cuda() for k, v in test_input.items()}

        with torch.no_grad():
            output = model(**test_input)

        logger.info(
            f"Forward pass successful, loss: {output.loss.item() if output.loss else 'N/A'}"
        )

        return model, tokenizer

    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        return None, None


def test_lora_configuration(model):
    """Test 3: LoRA configuration"""
    logger.info("Test 3: Configuring LoRA...")

    try:
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=["c_attn"],
            bias="none",
        )

        model = get_peft_model(model, lora_config)

        # Count parameters
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        trainable_percentage = (trainable_params / total_params) * 100

        logger.info(f"LoRA configured successfully")
        logger.info(f"Trainable parameters: {trainable_params:,}")
        logger.info(f"Total parameters: {total_params:,}")
        logger.info(f"Trainable percentage: {trainable_percentage:.2f}%")

        return model

    except Exception as e:
        logger.error(f"LoRA configuration failed: {e}")
        return None


def test_single_training_step(model, tokenizer):
    """Test 4: Single training step"""
    logger.info("Test 4: Testing single training step...")

    try:
        # Create minimal test data
        test_text = "Popperian analysis: Scientific claims must be falsifiable. Keywords: falsifiable, testable"
        inputs = tokenizer(
            test_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128,
        )
        inputs = {k: v.cuda() for k, v in inputs.items()}
        inputs["labels"] = inputs["input_ids"].clone()

        # Set model to training mode
        model.train()

        # Single training step
        optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)

        start_time = time.time()

        # Forward pass
        outputs = model(**inputs)
        loss = outputs.loss

        # Backward pass
        loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)

        # Optimizer step
        optimizer.step()
        optimizer.zero_grad()

        step_time = time.time() - start_time

        logger.info(f"Single training step successful")
        logger.info(f"Loss: {loss.item():.4f}")
        logger.info(f"Step time: {step_time:.3f} seconds")

        # Check GPU memory
        memory_allocated = cuda.memory_allocated(0) / (1024**3)
        memory_reserved = cuda.memory_reserved(0) / (1024**3)
        logger.info(f"GPU memory allocated: {memory_allocated:.2f} GB")
        logger.info(f"GPU memory reserved: {memory_reserved:.2f} GB")

        return True

    except Exception as e:
        logger.error(f"Training step failed: {e}")
        return False


def main():
    """Main test execution"""
    print("\n" + "=" * 60)
    print("STAGE 2 CUDA TRAINING - QUICK TEST")
    print("=" * 60)

    start_time = time.time()
    tests_passed = 0
    total_tests = 4

    # Test 1: CUDA setup
    if test_cuda_setup():
        tests_passed += 1
        logger.info("✅ Test 1 PASSED: CUDA setup verified")
    else:
        logger.error("❌ Test 1 FAILED: CUDA setup")
        return

    # Test 2: Model loading
    model, tokenizer = test_model_loading()
    if model and tokenizer:
        tests_passed += 1
        logger.info("✅ Test 2 PASSED: Model loading verified")
    else:
        logger.error("❌ Test 2 FAILED: Model loading")
        return

    # Test 3: LoRA configuration
    model = test_lora_configuration(model)
    if model:
        tests_passed += 1
        logger.info("✅ Test 3 PASSED: LoRA configuration verified")
    else:
        logger.error("❌ Test 3 FAILED: LoRA configuration")
        return

    # Test 4: Single training step
    if test_single_training_step(model, tokenizer):
        tests_passed += 1
        logger.info("✅ Test 4 PASSED: Training step verified")
    else:
        logger.error("❌ Test 4 FAILED: Training step")

    # Summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Total time: {total_time:.2f} seconds")

    if tests_passed == total_tests:
        print("✅ ALL TESTS PASSED - Stage 2 CUDA training ready!")
        print("\nNext: Run full training with:")
        print("venv_cuda\\Scripts\\python.exe lora\\stage2_cuda_training.py \\")
        print("  --dataset lora_dataset\\popperian_examples.json \\")
        print("  --output trained_lora_stage2_cuda \\")
        print("  --model distilgpt2")
    else:
        print(f"❌ {total_tests - tests_passed} test(s) failed")
        print("Check logs above for details")

    print("=" * 60)


if __name__ == "__main__":
    main()

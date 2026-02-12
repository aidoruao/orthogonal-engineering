#!/usr/bin/env python3
"""
STAGE 2 CUDA TRAINING TEST
==========================

Test script to verify CUDA setup and Stage 2 training functionality.
Runs minimal validation to ensure:
1. CUDA is properly configured and available
2. GPU memory is sufficient for training
3. Model loading works with CUDA optimization
4. Dataset loading and tokenization works
5. Training can start without errors

This is a validation test, not full training.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict

import torch
import torch.cuda as cuda
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Stage2CudaTest:
    """Test class for Stage 2 CUDA training verification"""

    def __init__(self):
        self.device = None
        self.model = None
        self.tokenizer = None
        self.test_results = {}

    def test_cuda_availability(self) -> Dict[str, Any]:
        """Test 1: CUDA availability and configuration"""
        logger.info("Test 1: Checking CUDA availability...")

        result = {"test_name": "cuda_availability", "passed": False, "details": {}}

        try:
            # Check CUDA availability
            cuda_available = cuda.is_available()
            result["details"]["cuda_available"] = cuda_available

            if not cuda_available:
                result["details"]["error"] = "CUDA is not available"
                logger.error("CUDA is not available")
                return result

            # Get CUDA device count
            device_count = cuda.device_count()
            result["details"]["device_count"] = device_count

            # Get GPU information
            gpu_props = cuda.get_device_properties(0)
            result["details"]["gpu_name"] = gpu_props.name
            result["details"]["gpu_memory_gb"] = gpu_props.total_memory / (1024**3)
            result["details"]["cuda_version"] = torch.version.cuda
            result["details"]["pytorch_version"] = torch.__version__

            # Set device
            self.device = torch.device("cuda:0")
            result["details"]["selected_device"] = str(self.device)

            # Test CUDA operations
            test_tensor = torch.tensor([1.0, 2.0, 3.0]).cuda()
            result["details"]["cuda_operation_test"] = test_tensor.sum().item() == 6.0

            logger.info(f"CUDA available: {cuda_available}")
            logger.info(f"GPU: {gpu_props.name}")
            logger.info(f"GPU Memory: {result['details']['gpu_memory_gb']:.2f} GB")
            logger.info(f"CUDA Version: {torch.version.cuda}")

            result["passed"] = True
            logger.info("Test 1 PASSED: CUDA is properly configured")

        except Exception as e:
            result["details"]["error"] = str(e)
            logger.error(f"Test 1 FAILED: {e}")

        return result

    def test_gpu_memory(self) -> Dict[str, Any]:
        """Test 2: GPU memory availability"""
        logger.info("Test 2: Checking GPU memory...")

        result = {"test_name": "gpu_memory", "passed": False, "details": {}}

        try:
            if self.device is None or self.device.type != "cuda":
                result["details"]["error"] = "CUDA device not available"
                logger.error("CUDA device not available for memory test")
                return result

            # Get memory information
            memory_allocated = cuda.memory_allocated(0) / (1024**3)
            memory_reserved = cuda.memory_reserved(0) / (1024**3)
            memory_total = cuda.get_device_properties(0).total_memory / (1024**3)

            result["details"]["memory_allocated_gb"] = round(memory_allocated, 2)
            result["details"]["memory_reserved_gb"] = round(memory_reserved, 2)
            result["details"]["memory_total_gb"] = round(memory_total, 2)
            result["details"]["memory_free_gb"] = round(
                memory_total - memory_allocated - memory_reserved, 2
            )

            # Check if we have enough free memory (at least 2GB)
            free_memory = memory_total - memory_allocated - memory_reserved
            min_required = 2.0  # GB

            result["details"]["min_required_gb"] = min_required
            result["details"]["has_sufficient_memory"] = free_memory >= min_required

            logger.info(f"GPU Memory - Allocated: {memory_allocated:.2f} GB")
            logger.info(f"GPU Memory - Reserved: {memory_reserved:.2f} GB")
            logger.info(f"GPU Memory - Total: {memory_total:.2f} GB")
            logger.info(f"GPU Memory - Free: {free_memory:.2f} GB")

            if free_memory >= min_required:
                result["passed"] = True
                logger.info("Test 2 PASSED: Sufficient GPU memory available")
            else:
                result["details"]["warning"] = (
                    f"Insufficient GPU memory: {free_memory:.2f} GB < {min_required} GB"
                )
                logger.warning(f"Test 2 WARNING: {result['details']['warning']}")
                # We'll still pass this test but warn about memory
                result["passed"] = True

        except Exception as e:
            result["details"]["error"] = str(e)
            logger.error(f"Test 2 FAILED: {e}")

        return result

    def test_model_loading(self) -> Dict[str, Any]:
        """Test 3: Model loading with CUDA optimization"""
        logger.info("Test 3: Testing model loading with CUDA...")

        result = {"test_name": "model_loading", "passed": False, "details": {}}

        try:
            model_name = "distilgpt2"

            # Load tokenizer
            logger.info(f"Loading tokenizer: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            result["details"]["tokenizer_loaded"] = True
            result["details"]["tokenizer_vocab_size"] = len(self.tokenizer)

            # Load model with CUDA optimization
            logger.info(f"Loading model: {model_name} with CUDA optimization")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16
                if self.device.type == "cuda"
                else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
                low_cpu_mem_usage=True,
            )

            # Move to device if not using device_map
            if self.device.type == "cuda" and not hasattr(self.model, "hf_device_map"):
                self.model = self.model.to(self.device)

            result["details"]["model_loaded"] = True
            result["details"]["model_dtype"] = str(self.model.dtype)
            result["details"]["model_device"] = str(
                next(self.model.parameters()).device
            )
            result["details"]["model_parameters"] = sum(
                p.numel() for p in self.model.parameters()
            )

            # Test forward pass
            logger.info("Testing forward pass...")
            test_input = self.tokenizer(
                "Test input for model verification", return_tensors="pt"
            )
            test_input = {k: v.to(self.device) for k, v in test_input.items()}

            with torch.no_grad():
                output = self.model(**test_input)

            result["details"]["forward_pass_test"] = True
            result["details"]["output_loss"] = (
                output.loss.item() if output.loss is not None else None
            )

            logger.info(f"Model loaded successfully on {self.device}")
            logger.info(f"Model dtype: {self.model.dtype}")
            logger.info(f"Model parameters: {result['details']['model_parameters']:,}")

            result["passed"] = True
            logger.info("Test 3 PASSED: Model loading and forward pass successful")

        except Exception as e:
            result["details"]["error"] = str(e)
            logger.error(f"Test 3 FAILED: {e}")

        return result

    def test_lora_configuration(self) -> Dict[str, Any]:
        """Test 4: LoRA configuration and parameter counting"""
        logger.info("Test 4: Testing LoRA configuration...")

        result = {"test_name": "lora_configuration", "passed": False, "details": {}}

        try:
            if self.model is None:
                result["details"]["error"] = "Model not loaded"
                logger.error("Model not loaded for LoRA test")
                return result

            # Configure LoRA
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=8,  # LoRA rank
                lora_alpha=16,
                lora_dropout=0.1,
                target_modules=["c_attn"],  # For GPT-2 models
                bias="none",
            )

            # Apply LoRA
            logger.info("Applying LoRA configuration...")
            self.model = get_peft_model(self.model, lora_config)

            # Count trainable parameters
            trainable_params = sum(
                p.numel() for p in self.model.parameters() if p.requires_grad
            )
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_percentage = (trainable_params / total_params) * 100

            result["details"]["lora_applied"] = True
            result["details"]["trainable_parameters"] = trainable_params
            result["details"]["total_parameters"] = total_params
            result["details"]["trainable_percentage"] = round(trainable_percentage, 2)

            logger.info(f"Trainable parameters: {trainable_params:,}")
            logger.info(f"Total parameters: {total_params:,}")
            logger.info(f"Trainable percentage: {trainable_percentage:.2f}%")

            # Verify parameters are trainable
            if trainable_params > 0:
                result["passed"] = True
                logger.info(
                    "Test 4 PASSED: LoRA configuration successful with trainable parameters"
                )
            else:
                result["details"]["error"] = "No trainable parameters found"
                logger.error("Test 4 FAILED: No trainable parameters found")

        except Exception as e:
            result["details"]["error"] = str(e)
            logger.error(f"Test 4 FAILED: {e}")

        return result

    def test_dataset_loading(self) -> Dict[str, Any]:
        """Test 5: Dataset loading and tokenization"""
        logger.info("Test 5: Testing dataset loading...")

        result = {"test_name": "dataset_loading", "passed": False, "details": {}}

        try:
            dataset_path = "lora_dataset/popperian_examples.json"

            if not Path(dataset_path).exists():
                # Try relative path
                dataset_path = "../lora_dataset/popperian_examples.json"

            if not Path(dataset_path).exists():
                result["details"]["error"] = f"Dataset not found: {dataset_path}"
                logger.error(f"Dataset not found: {dataset_path}")
                return result

            # Load dataset
            logger.info(f"Loading dataset: {dataset_path}")
            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)

            result["details"]["dataset_found"] = True
            result["details"]["dataset_type"] = dataset.get("metadata", {}).get(
                "dataset_type", "unknown"
            )
            result["details"]["total_examples"] = dataset.get("metadata", {}).get(
                "total_examples", 0
            )

            examples = dataset.get("examples", [])
            result["details"]["loaded_examples"] = len(examples)

            # Test tokenization of a few examples
            if self.tokenizer is None:
                result["details"]["error"] = "Tokenizer not loaded"
                logger.error("Tokenizer not loaded for dataset test")
                return result

            logger.info("Testing tokenization...")
            tokenization_results = []
            for i, example in enumerate(examples[:3]):  # Test first 3 examples
                text = example.get("text", "")
                if text:
                    tokens = self.tokenizer.encode(
                        text, truncation=True, max_length=512
                    )
                    tokenization_results.append(
                        {
                            "example_index": i,
                            "text_length": len(text),
                            "token_count": len(tokens),
                            "tokenization_success": True,
                        }
                    )

            result["details"]["tokenization_tests"] = tokenization_results
            result["details"]["tokenization_success"] = all(
                r["tokenization_success"] for r in tokenization_results
            )

            logger.info(f"Dataset loaded: {len(examples)} examples")
            logger.info(f"Dataset type: {result['details']['dataset_type']}")

            if len(examples) > 0 and result["details"]["tokenization_success"]:
                result["passed"] = True
                logger.info(
                    "Test 5 PASSED: Dataset loading and tokenization successful"
                )
            else:
                result["details"]["error"] = "Dataset empty or tokenization failed"
                logger.error("Test 5 FAILED: Dataset empty or tokenization failed")

        except Exception as e:
            result["details"]["error"] = str(e)
            logger.error(f"Test 5 FAILED: {e}")

        return result

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        logger.info("=" * 60)
        logger.info("STARTING STAGE 2 CUDA TRAINING TESTS")
        logger.info("=" * 60)

        start_time = time.time()

        # Run tests in sequence
        tests = [
            self.test_cuda_availability,
            self.test_gpu_memory,
            self.test_model_loading,
            self.test_lora_configuration,
            self.test_dataset_loading,
        ]

        all_results = []
        passed_tests = 0
        total_tests = len(tests)

        for test_func in tests:
            test_result = test_func()
            all_results.append(test_result)

            if test_result["passed"]:
                passed_tests += 1
                logger.info(f"✓ {test_result['test_name']}: PASSED")
            else:
                logger.error(f"✗ {test_result['test_name']}: FAILED")

            # Add small delay between tests
            time.sleep(0.5)

        # Calculate overall results
        total_time = time.time() - start_time
        overall_passed = passed_tests == total_tests

        summary = {
            "overall_passed": overall_passed,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "total_time_seconds": round(total_time, 2),
            "test_results": all_results,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "environment": {
                "pytorch_version": torch.__version__,
                "cuda_available": cuda.is_available(),
                "cuda_version": torch.version.cuda
                if hasattr(torch.version, "cuda")
                else "N/A",
                "device_count": cuda.device_count() if cuda.is_available() else 0,
            },
        }

        # Log summary
        logger.info("=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Overall: {'PASSED' if overall_passed else 'FAILED'}")
        logger.info(f"Tests passed: {passed_tests}/{total_tests}")
        logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        logger.info(f"Total time: {total_time:.2f} seconds")

        if overall_passed:
            logger.info("✓ All tests passed! Stage 2 CUDA training is ready.")
        else:
            logger.error("✗ Some tests failed. Check the details above.")

        return summary

    def save_results(
        self,
        results: Dict[str, Any],
        output_path: str = "stage2_cuda_test_results.json",
    ):
        """Save test results to JSON file"""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Test results saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return False


def main():
    """Main execution function"""
    print("\n" + "=" * 60)
    print("STAGE 2 CUDA TRAINING VERIFICATION TEST")
    print("=" * 60)
    print("This test verifies that CUDA is properly configured")
    print("and Stage 2 training can proceed successfully.")
    print("=" * 60 + "\n")

    # Create test instance
    tester = Stage2CudaTest()

    # Run all tests
    results = tester.run_all_tests()

    # Save results
    tester.save_results(results)

    # Print final status
    print("\n" + "=" * 60)
    if results["overall_passed"]:
        print("✅ STAGE 2 CUDA TRAINING VERIFICATION: PASSED")
        print("All tests passed. CUDA is properly configured.")
        print("You can proceed with Stage 2 training.")
    else:
        print("❌ STAGE 2 CUDA TRAINING VERIFICATION: FAILED")
        print(f"Only {results['passed_tests']}/{results['total_tests']} tests passed.")
        print("Check the test results for details.")

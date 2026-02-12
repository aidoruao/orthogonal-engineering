#!/usr/bin/env python3
"""
Test Script for Quantized LoRA Training Setup
==============================================

This script validates that the training environment is properly configured
for quantized LoRA training with Llama 3.2 models.

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Comments state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all operations
4. EXPLICIT BOUNDS: MAX_TEST_TIME=60s, MAX_MEMORY_GB=8
5. TYPE SAFETY: mypy --strict compliance mandatory
6. ZERO TRUST: Verify before asserting
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Test imports to verify dependencies
try:
    import accelerate
    import bitsandbytes
    import datasets
    import peft
    import safetensors
    import torch
    import transformers

    print("✅ Core dependencies imported successfully")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    sys.exit(1)


class TrainingSetupValidator:
    """Validate training setup for quantized LoRA training"""

    def __init__(self, model_name: str = "meta-llama/Llama-3.2-1B"):
        self.model_name = model_name
        self.violations: List[str] = []
        self.start_time = time.time()

    def validate_environment(self) -> Tuple[bool, str]:
        """Validate Python and CUDA environment"""
        print("\n1. VALIDATING ENVIRONMENT")
        print("-" * 40)

        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            self.violations.append(
                f"Python version {python_version.major}.{python_version.minor} < 3.8"
            )
            return False, "Python 3.8+ required"
        print(
            f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        # Check PyTorch
        print(f"   ✅ PyTorch {torch.__version__}")

        # Check CUDA availability
        if torch.cuda.is_available():
            print(f"   ✅ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"   ✅ CUDA version: {torch.version.cuda}")
            print(
                f"   ✅ GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f}GB"
            )
        else:
            print("   ⚠️  CUDA not available - training will be slow on CPU")

        # Check other dependencies
        deps = {
            "transformers": transformers.__version__,
            "peft": peft.__version__,
            "datasets": datasets.__version__,
            "accelerate": accelerate.__version__,
            "bitsandbytes": bitsandbytes.__version__,
        }

        for dep, version in deps.items():
            print(f"   ✅ {dep}: {version}")

        return True, "Environment validated"

    def validate_dataset(self, dataset_path: str) -> Tuple[bool, str]:
        """Validate training dataset"""
        print("\n2. VALIDATING DATASET")
        print("-" * 40)

        if not os.path.exists(dataset_path):
            self.violations.append(f"Dataset path does not exist: {dataset_path}")
            return False, f"Dataset not found: {dataset_path}"

        print(f"   ✅ Dataset path exists: {dataset_path}")

        # Check file size
        file_size_mb = os.path.getsize(dataset_path) / (1024 * 1024)
        print(f"   ✅ Dataset size: {file_size_mb:.2f}MB")

        # Check file format (JSONL)
        if not dataset_path.endswith(".jsonl"):
            print(f"   ⚠️  Dataset is not JSONL format: {dataset_path}")

        # Try to read first few lines
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 5:  # Read first 5 lines
                        break
                    lines.append(line.strip())

                if not lines:
                    self.violations.append(f"Dataset is empty: {dataset_path}")
                    return False, "Dataset is empty"

                # Parse JSONL
                for i, line in enumerate(lines):
                    try:
                        data = json.loads(line)
                        required_fields = ["instruction", "output"]
                        for field in required_fields:
                            if field not in data:
                                self.violations.append(
                                    f"Line {i + 1}: Missing field '{field}'"
                                )
                                return (
                                    False,
                                    f"Invalid dataset format: missing '{field}'",
                                )
                    except json.JSONDecodeError as e:
                        self.violations.append(f"Line {i + 1}: Invalid JSON: {str(e)}")
                        return False, f"Invalid JSONL format at line {i + 1}"

                print(f"   ✅ Dataset format valid: {len(lines)} samples checked")
                print(
                    f"   ✅ Sample structure: {json.dumps({k: type(v).__name__ for k, v in data.items()}, indent=6)}"
                )

        except Exception as e:
            self.violations.append(f"Failed to read dataset: {str(e)}")
            return False, f"Failed to read dataset: {str(e)}"

        return True, "Dataset validated"

    def validate_model_access(self) -> Tuple[bool, str]:
        """Validate model can be accessed (without downloading)"""
        print("\n3. VALIDATING MODEL ACCESS")
        print("-" * 40)

        from transformers import AutoConfig

        try:
            # Try to get model config without downloading
            config = AutoConfig.from_pretrained(
                self.model_name, trust_remote_code=False
            )
            print(f"   ✅ Model config accessible: {self.model_name}")
            print(f"   ✅ Model type: {config.model_type}")
            print(f"   ✅ Hidden size: {config.hidden_size}")
            print(f"   ✅ Attention heads: {config.num_attention_heads}")
            print(f"   ✅ Layers: {config.num_hidden_layers}")

            # Estimate parameter count
            if (
                hasattr(config, "vocab_size")
                and hasattr(config, "hidden_size")
                and hasattr(config, "num_hidden_layers")
            ):
                # Rough estimate: embedding + transformer layers + output layer
                vocab_size = config.vocab_size
                hidden_size = config.hidden_size
                num_layers = config.num_hidden_layers

                # Embedding: vocab_size * hidden_size
                # Transformer layers: 12 * hidden_size^2 per layer (approx)
                # Output layer: hidden_size * vocab_size
                param_estimate = (
                    vocab_size * hidden_size  # embeddings
                    + num_layers * 12 * hidden_size * hidden_size  # transformer layers
                    + hidden_size * vocab_size  # output layer
                )

                param_estimate_billion = param_estimate / 1e9
                print(f"   ✅ Estimated parameters: {param_estimate_billion:.2f}B")

                # Check if model is too large for available memory
                if torch.cuda.is_available():
                    gpu_memory_gb = (
                        torch.cuda.get_device_properties(0).total_memory / 1e9
                    )
                    # Rough memory estimate: 2 bytes per parameter for 16-bit, plus overhead
                    memory_estimate_gb = param_estimate * 2 / 1e9 * 1.5  # 1.5x overhead

                    if memory_estimate_gb > gpu_memory_gb:
                        print(
                            f"   ⚠️  Model may not fit in GPU memory: {memory_estimate_gb:.2f}GB > {gpu_memory_gb:.2f}GB"
                        )
                        print(f"   ⚠️  Consider using quantization or smaller model")
                    else:
                        print(
                            f"   ✅ Model should fit in GPU memory: {memory_estimate_gb:.2f}GB <= {gpu_memory_gb:.2f}GB"
                        )

            return True, "Model access validated"

        except Exception as e:
            self.violations.append(f"Failed to access model: {str(e)}")
            return False, f"Model access failed: {str(e)}"

    def validate_quantization_support(self) -> Tuple[bool, str]:
        """Validate quantization support"""
        print("\n4. VALIDATING QUANTIZATION SUPPORT")
        print("-" * 40)

        try:
            # Check bitsandbytes availability
            import bitsandbytes as bnb

            # Check if CUDA is available for quantization
            if not torch.cuda.is_available():
                print("   ⚠️  CUDA not available - quantization requires GPU")
                return False, "Quantization requires CUDA"

            # Check if model supports quantization
            from transformers import AutoConfig

            config = AutoConfig.from_pretrained(
                self.model_name, trust_remote_code=False
            )

            # Most transformer models support quantization
            supported_model_types = [
                "llama",
                "mistral",
                "gemma",
                "phi",
                "qwen",
                "bloom",
                "gpt2",
                "gpt_neox",
            ]

            model_type = config.model_type.lower()
            if any(supported in model_type for supported in supported_model_types):
                print(f"   ✅ Model type '{model_type}' supports quantization")
            else:
                print(f"   ⚠️  Model type '{model_type}' may not support quantization")

            # Test bitsandbytes operations
            linear = bnb.nn.Linear4bit(
                1024, 1024, bias=False, compute_dtype=torch.float16
            )
            print(f"   ✅ 4-bit linear layer created successfully")

            linear8 = bnb.nn.Linear8bitLt(
                1024, 1024, bias=False, has_fp16_weights=False
            )
            print(f"   ✅ 8-bit linear layer created successfully")

            return True, "Quantization support validated"

        except Exception as e:
            self.violations.append(f"Quantization validation failed: {str(e)}")
            return False, f"Quantization support check failed: {str(e)}"

    def validate_output_directory(self, output_dir: str) -> Tuple[bool, str]:
        """Validate output directory"""
        print("\n5. VALIDATING OUTPUT DIRECTORY")
        print("-" * 40)

        output_path = Path(output_dir)

        # Check if directory exists
        if output_path.exists():
            if output_path.is_file():
                self.violations.append(
                    f"Output path is a file, not directory: {output_dir}"
                )
                return False, "Output path is a file"

            # Check if directory is empty
            contents = list(output_path.iterdir())
            if contents:
                print(f"   ⚠️  Output directory is not empty: {len(contents)} items")
                print(f"   ⚠️  Existing files may be overwritten")
            else:
                print(f"   ✅ Output directory exists and is empty")
        else:
            # Try to create directory
            try:
                output_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Output directory created: {output_dir}")
            except Exception as e:
                self.violations.append(f"Failed to create output directory: {str(e)}")
                return False, f"Failed to create output directory: {str(e)}"

        # Check write permissions
        test_file = output_path / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print(f"   ✅ Write permissions verified")
        except Exception as e:
            self.violations.append(f"No write permission in output directory: {str(e)}")
            return False, f"No write permission: {str(e)}"

        return True, "Output directory validated"

    def run_all_checks(
        self, dataset_path: str, output_dir: str, max_test_time: int = 60
    ) -> bool:
        """Run all validation checks"""
        print("=" * 70)
        print("QUANTIZED LoRA TRAINING SETUP VALIDATION")
        print("=" * 70)
        print(f"Model: {self.model_name}")
        print(f"Dataset: {dataset_path}")
        print(f"Output: {output_dir}")
        print(f"Max test time: {max_test_time}s")
        print()

        checks = [
            ("Environment", self.validate_environment),
            ("Dataset", lambda: self.validate_dataset(dataset_path)),
            ("Model Access", self.validate_model_access),
            ("Quantization", self.validate_quantization_support),
            ("Output Directory", lambda: self.validate_output_directory(output_dir)),
        ]

        all_passed = True

        for check_name, check_func in checks:
            # Check time limit
            elapsed = time.time() - self.start_time
            if elapsed > max_test_time:
                self.violations.append(
                    f"Validation exceeded time limit: {elapsed:.1f}s > {max_test_time}s"
                )
                print(f"\n❌ VALIDATION TIMEOUT")
                all_passed = False
                break

            try:
                passed, message = check_func()
                if passed:
                    print(f"   ✅ {check_name}: {message}")
                else:
                    print(f"   ❌ {check_name}: {message}")
                    all_passed = False
            except Exception as e:
                self.violations.append(f"{check_name} check failed: {str(e)}")
                print(f"   ❌ {check_name}: Check failed - {str(e)}")
                all_passed = False

        # Print summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        total_time = time.time() - self.start_time
        print(f"Total validation time: {total_time:.2f}s")
        print(f"All checks passed: {'✅ YES' if all_passed else '❌ NO'}")

        if self.violations:
            print(f"\nViolations found ({len(self.violations)}):")
            for i, violation in enumerate(self.violations, 1):
                print(f"  {i}. {violation}")

        # Recommendations
        print("\n" + "=" * 70)
        if all_passed:
            print("✅ SETUP VALIDATION PASSED")
            print("=" * 70)
            print("\nReady for training. Suggested command:")
            print(f"python train_quantized_lora.py \\")
            print(f"  --model {self.model_name} \\")
            print(f"  --dataset {dataset_path} \\")
            print(f"  --output {output_dir} \\")
            print(f"  --quantization 4bit \\")
            print(f"  --epochs 3 \\")
            print(f"  --batch-size 4")
        else:
            print("❌ SETUP VALIDATION FAILED")
            print("=" * 70)
            print("\nPlease fix the issues above before training.")

        return all_passed


def main():
    """Main CLI for setup validation"""
    parser = argparse.ArgumentParser(
        description="Validate setup for quantized LoRA training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Validate setup for 1B model
  python test_training_setup.py \\
    --model meta-llama/Llama-3.2-1B \\
    --dataset lora_dataset/lora_dataset_train.jsonl \\
    --output trained_lora_test

  # Validate setup for 3B model
  python test_training_setup.py \\
    --model meta-llama/Llama-3.2-3B \\
    --dataset lora_dataset/lora_dataset_train.jsonl \\
    --output trained_lora_test_3b
""",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="meta-llama/Llama-3.2-1B",
        help="Base model identifier (default: meta-llama/Llama-3.2-1B)",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="lora_dataset/lora_dataset_train.jsonl",
        help="Path to training dataset (default: lora_dataset/lora_dataset_train.jsonl)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="trained_lora_test",
        help="Output directory for trained LoRA (default: trained_lora_test)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Maximum validation time in seconds (default: 60)",
    )

    args = parser.parse_args()

    validator = TrainingSetupValidator(model_name=args.model)
    success = validator.run_all_checks(
        dataset_path=args.dataset,
        output_dir=args.output,
        max_test_time=args.timeout,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simplified Setup Validation for Quantized LoRA Training
=======================================================

Validates basic requirements for training quantized LoRA models.
Avoids problematic imports like bitsandbytes that may have compatibility issues.

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Comments state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all operations
4. EXPLICIT BOUNDS: MAX_TEST_TIME=30s
5. TYPE SAFETY: Basic type checking
6. ZERO TRUST: Verify before asserting
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


class SimpleSetupValidator:
    """Simple validation for training setup"""

    def __init__(self, model_name: str = "meta-llama/Llama-3.2-1B"):
        self.model_name = model_name
        self.violations: List[str] = []
        self.start_time = time.time()

    def validate_python_environment(self) -> Tuple[bool, str]:
        """Validate Python environment"""
        print("\n1. VALIDATING PYTHON ENVIRONMENT")
        print("-" * 40)

        # Check Python version
        python_version = sys.version_info
        print(
            f"   Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        if python_version.major < 3 or python_version.minor < 8:
            self.violations.append(
                f"Python {python_version.major}.{python_version.minor} < 3.8"
            )
            return False, "Python 3.8+ required"

        return (
            True,
            f"Python {python_version.major}.{python_version.minor}.{python_version.micro} OK",
        )

    def validate_basic_imports(self) -> Tuple[bool, str]:
        """Validate basic imports without problematic dependencies"""
        print("\n2. VALIDATING BASIC IMPORTS")
        print("-" * 40)

        # Try basic imports
        imports_to_test = [
            ("torch", "PyTorch"),
            ("transformers", "Transformers"),
            ("datasets", "Datasets"),
            ("peft", "PEFT"),
        ]

        all_imported = True
        for module_name, display_name in imports_to_test:
            try:
                __import__(module_name)
                print(f"   [OK] {display_name} import successful")
            except ImportError as e:
                self.violations.append(f"Failed to import {module_name}: {str(e)}")
                print(f"   [FAIL] {display_name} import failed: {str(e)}")
                all_imported = False

        if not all_imported:
            return False, "Some imports failed"

        # Get versions if imports succeeded
        try:
            import datasets
            import peft
            import torch
            import transformers

            print(f"   PyTorch version: {torch.__version__}")
            print(f"   Transformers version: {transformers.__version__}")
            print(f"   Datasets version: {datasets.__version__}")
            print(f"   PEFT version: {peft.__version__}")

            # Check CUDA
            if torch.cuda.is_available():
                print(f"   [OK] CUDA available: {torch.cuda.get_device_name(0)}")
                print(
                    f"   GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f}GB"
                )
            else:
                print("   ⚠️  CUDA not available - training will be slow on CPU")

        except Exception as e:
            self.violations.append(f"Version check failed: {str(e)}")
            return False, f"Version check failed: {str(e)}"

        return True, "Basic imports validated"

    def validate_dataset(self, dataset_path: str) -> Tuple[bool, str]:
        """Validate training dataset"""
        print("\n3. VALIDATING DATASET")
        print("-" * 40)

        if not os.path.exists(dataset_path):
            self.violations.append(f"Dataset path does not exist: {dataset_path}")
            return False, f"Dataset not found: {dataset_path}"

        print(f"   [OK] Dataset path exists: {dataset_path}")

        # Check file size
        try:
            file_size_mb = os.path.getsize(dataset_path) / (1024 * 1024)
            print(f"   Dataset size: {file_size_mb:.2f}MB")

            if file_size_mb < 0.1:
                self.violations.append(f"Dataset too small: {file_size_mb:.2f}MB")
                return False, "Dataset too small (< 0.1MB)"

        except Exception as e:
            self.violations.append(f"Failed to get dataset size: {str(e)}")
            return False, f"Failed to get dataset size: {str(e)}"

        # Check file format
        if not dataset_path.endswith(".jsonl"):
            print(f"   ⚠️  Dataset is not JSONL format: {dataset_path}")

        # Try to read and parse first line
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()

                if not first_line:
                    self.violations.append("Dataset is empty")
                    return False, "Dataset is empty"

                # Parse JSON
                data = json.loads(first_line)

                # Check required fields
                required_fields = ["instruction", "output"]
                missing_fields = []

                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)

                if missing_fields:
                    self.violations.append(
                        f"Missing fields in dataset: {missing_fields}"
                    )
                    return False, f"Missing fields: {missing_fields}"

                print(f"   [OK] Dataset format valid")
                print(f"   Sample fields: {list(data.keys())}")

        except json.JSONDecodeError as e:
            self.violations.append(f"Invalid JSON in dataset: {str(e)}")
            return False, f"Invalid JSON format: {str(e)}"
        except Exception as e:
            self.violations.append(f"Failed to read dataset: {str(e)}")
            return False, f"Failed to read dataset: {str(e)}"

        return True, "Dataset validated"

    def validate_output_directory(self, output_dir: str) -> Tuple[bool, str]:
        """Validate output directory"""
        print("\n4. VALIDATING OUTPUT DIRECTORY")
        print("-" * 40)

        output_path = Path(output_dir)

        # Check if directory exists
        if output_path.exists():
            if output_path.is_file():
                self.violations.append(f"Output path is a file: {output_dir}")
                return False, "Output path is a file"

            # Check contents
            try:
                contents = list(output_path.iterdir())
                if contents:
                    print(f"   ⚠️  Output directory not empty: {len(contents)} items")
                else:
                    print(f"   [OK] Output directory exists and is empty")
            except Exception as e:
                self.violations.append(f"Failed to list directory contents: {str(e)}")
                return False, f"Failed to list contents: {str(e)}"
        else:
            # Try to create directory
            try:
                output_path.mkdir(parents=True, exist_ok=True)
                print(f"   [OK] Output directory created: {output_dir}")
            except Exception as e:
                self.violations.append(f"Failed to create directory: {str(e)}")
                return False, f"Failed to create directory: {str(e)}"

        # Check write permissions
        test_file = output_path / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print(f"   [OK] Write permissions verified")
        except Exception as e:
            self.violations.append(f"No write permission: {str(e)}")
            return False, f"No write permission: {str(e)}"

        return True, "Output directory validated"

    def validate_model_name(self) -> Tuple[bool, str]:
        """Validate model name format"""
        print("\n5. VALIDATING MODEL NAME")
        print("-" * 40)

        print(f"   Model: {self.model_name}")

        # Check if it's a known Llama 3.2 model
        known_models = [
            "meta-llama/Llama-3.2-1B",
            "meta-llama/Llama-3.2-3B",
            "meta-llama/Llama-3.2-7B",
            "meta-llama/Llama-3.2-11B",
            "distilgpt2",  # For testing
        ]

        if self.model_name in known_models:
            print(f"   [OK] Known model identifier")
        else:
            print(f"   ⚠️  Unknown model identifier - may require authentication")

        # Check Hugging Face format
        if "/" in self.model_name:
            org, model = self.model_name.split("/", 1)
            print(f"   Organization: {org}")
            print(f"   Model: {model}")

        return True, "Model name validated"

    def run_all_checks(
        self, dataset_path: str, output_dir: str, max_time: int = 30
    ) -> bool:
        """Run all validation checks"""
        print("=" * 70)
        print("SIMPLIFIED SETUP VALIDATION")
        print("=" * 70)
        print(f"Model: {self.model_name}")
        print(f"Dataset: {dataset_path}")
        print(f"Output: {output_dir}")
        print(f"Max time: {max_time}s")
        print()

        checks = [
            ("Python Environment", self.validate_python_environment),
            ("Basic Imports", self.validate_basic_imports),
            ("Dataset", lambda: self.validate_dataset(dataset_path)),
            ("Output Directory", lambda: self.validate_output_directory(output_dir)),
            ("Model Name", self.validate_model_name),
        ]

        all_passed = True

        for check_name, check_func in checks:
            # Check time limit
            elapsed = time.time() - self.start_time
            if elapsed > max_time:
                self.violations.append(f"Validation timeout: {elapsed:.1f}s")
                print(f"\n❌ VALIDATION TIMEOUT")
                all_passed = False
                break

            try:
                passed, message = check_func()
                if passed:
                    print(f"   [OK] {check_name}: OK")
                else:
                    print(f"   [FAIL] {check_name}: {message}")
                    all_passed = False
            except Exception as e:
                self.violations.append(f"{check_name} failed: {str(e)}")
                print(f"   [FAIL] {check_name}: Failed - {str(e)}")
                all_passed = False

        # Print summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        total_time = time.time() - self.start_time
        print(f"Total time: {total_time:.2f}s")
        print(f"All checks passed: {'[OK] YES' if all_passed else '[FAIL] NO'}")

        if self.violations:
            print(f"\nIssues found ({len(self.violations)}):")
            for i, violation in enumerate(self.violations, 1):
                print(f"  {i}. {violation}")

        # Recommendations
        print("\n" + "=" * 70)
        if all_passed:
            print("[OK] SETUP VALIDATION PASSED")
            print("=" * 70)
            print("\nReady for training. Next steps:")
            print("1. Install bitsandbytes for quantization (optional):")
            print("   pip install bitsandbytes")
            print("\n2. Run training with:")
            print(f"   python train_quantized_lora.py \\")
            print(f"     --model {self.model_name} \\")
            print(f"     --dataset {dataset_path} \\")
            print(f"     --output {output_dir} \\")
            print(f"     --epochs 3 \\")
            print(f"     --batch-size 2")
        else:
            print("[FAIL] SETUP VALIDATION FAILED")
            print("=" * 70)
            print("\nPlease fix the issues above.")
            print("\nCommon solutions:")
            print("1. Install missing packages:")
            print("   pip install torch transformers datasets peft")
            print("\n2. Check dataset path and format")
            print("\n3. Ensure output directory is writable")

        return all_passed


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Validate setup for LoRA training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Validate setup for 1B model
  python validate_setup.py --model meta-llama/Llama-3.2-1B

  # Validate setup for 3B model
  python validate_setup.py --model meta-llama/Llama-3.2-3B

  # Custom dataset and output
  python validate_setup.py \
    --model meta-llama/Llama-3.2-1B \
    --dataset lora_dataset/lora_dataset_augmented.jsonl \
    --output trained_model
""",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="meta-llama/Llama-3.2-1B",
        help="Model identifier (default: meta-llama/Llama-3.2-1B)",
    )

    parser.add_argument(
        "--dataset",
        type=str,
        default="lora_dataset/lora_dataset_augmented.jsonl",
        help="Dataset path (default: lora_dataset/lora_dataset_augmented.jsonl)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="trained_lora",
        help="Output directory (default: trained_lora)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Maximum validation time in seconds (default: 30)",
    )

    args = parser.parse_args()

    validator = SimpleSetupValidator(model_name=args.model)
    success = validator.run_all_checks(
        dataset_path=args.dataset,
        output_dir=args.output,
        max_time=args.timeout,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

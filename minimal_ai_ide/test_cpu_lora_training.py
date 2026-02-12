#!/usr/bin/env python3
"""
Simple CPU LoRA Test Training Script
=====================================

Tests the LoRA training pipeline on CPU with the augmented dataset.
Uses a small model (distilgpt2) to verify the training infrastructure works.

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Comments state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all operations
4. EXPLICIT BOUNDS: MAX_TEST_TIME=30min, MAX_MODEL_SIZE=1GB
5. TYPE SAFETY: Basic type checking
6. ZERO TRUST: Verify before asserting
"""

import sys

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import torch

    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"PyTorch import error: {e}")
    sys.exit(1)

try:
    from datasets import Dataset, load_dataset

    print("Datasets imported successfully")
except ImportError as e:
    print(f"Datasets import error: {e}")
    sys.exit(1)

try:
    from peft import LoraConfig, TaskType, get_peft_model

    print("PEFT imported successfully")
except ImportError as e:
    print(f"PEFT import error: {e}")
    sys.exit(1)

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        PreTrainedModel,
        PreTrainedTokenizer,
        Trainer,
        TrainingArguments,
    )

    print("Transformers imported successfully")
except ImportError as e:
    print(f"Transformers import error: {e}")
    sys.exit(1)

# ============================================================================
# GOVERNANCE CONSTANTS - UNCHANGEABLE BOUNDS
# ============================================================================

MAX_TEST_TIME_MINUTES: int = 30
MAX_MODEL_SIZE_GB: int = 1
MAX_DATASET_SIZE_MB: int = 1024
MAX_LORA_RANK: int = 16
MAX_BATCH_SIZE: int = 2
MAX_EPOCHS: int = 1
MAX_GRAD_NORM: float = 1.0
MAX_LEARNING_RATE: float = 5e-5
MIN_LEARNING_RATE: float = 1e-6


# ============================================================================
# GOVERNANCE DATA STRUCTURES - TYPE SAFE
# ============================================================================


@dataclass(frozen=True)
class GovernanceThreshold:
    """Governance threshold with explicit bounds"""

    name: str
    min_value: float
    max_value: float
    unit: str


@dataclass(frozen=True)
class TestReport:
    """Test report with governance compliance"""

    model_name: str
    dataset_path: str
    test_successful: bool
    governance_compliant: bool
    violations: Tuple[str, ...]
    test_duration_minutes: float
    model_size_gb: float
    timestamp: str

    def __bool__(self) -> bool:
        """Test successful only if both functional and governance compliant"""
        return self.test_successful and self.governance_compliant


# ============================================================================
# GOVERNANCE VALIDATORS - BOUNDED OPERATIONS
# ============================================================================


def validate_dataset_path(dataset_path: str) -> Tuple[bool, str]:
    """Validate dataset path exists and is accessible"""
    path = Path(dataset_path)
    if not path.exists():
        return False, f"Dataset path does not exist: {dataset_path}"

    if not path.is_file():
        return False, f"Dataset path is not a file: {dataset_path}"

    # Check file size
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_DATASET_SIZE_MB:
        return (
            False,
            f"Dataset size {file_size_mb:.2f}MB exceeds maximum {MAX_DATASET_SIZE_MB}MB",
        )

    return True, f"Dataset valid: {file_size_mb:.2f}MB"


def validate_output_directory(output_dir: str) -> Tuple[bool, str]:
    """Validate output directory is writable"""
    path = Path(output_dir)

    # Create directory if it doesn't exist
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Cannot create output directory: {e}"

    # Test write permission
    test_file = path / ".write_test"
    try:
        test_file.write_text("test")
        test_file.unlink()
    except Exception as e:
        return False, f"Output directory not writable: {e}"

    return True, "Output directory writable"


def validate_model_name(model_name: str) -> Tuple[bool, str]:
    """Validate model name is reasonable"""
    if not model_name:
        return False, "Model name cannot be empty"

    if len(model_name) > 100:
        return False, f"Model name too long: {len(model_name)} characters"

    # Check for known small models suitable for CPU testing
    small_models = [
        "distilgpt2",
        "gpt2",
        "gpt2-medium",
        "microsoft/phi-2",
        "facebook/opt-125m",
    ]
    if model_name not in small_models:
        print(f"⚠️  Warning: {model_name} may be too large for CPU testing")

    return True, f"Model name valid: {model_name}"


# ============================================================================
# DATASET PROCESSING
# ============================================================================


def load_and_prepare_dataset(
    dataset_path: str, tokenizer: PreTrainedTokenizer, max_length: int = 512
) -> Dataset:
    """Load and prepare dataset for training"""

    # Load dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")

    # Tokenization function
    def tokenize_function(examples):
        # Combine instruction, input, and output
        texts = []
        for i in range(len(examples["instruction"])):
            instruction = examples["instruction"][i]
            input_text = examples["input"][i]
            output_text = examples["output"][i]

            # Format for causal language modeling
            text = f"Instruction: {instruction}\nInput: {input_text}\nOutput: {output_text}\n\n"
            texts.append(text)

        # Tokenize
        tokenized = tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt",
        )

        # For causal LM, labels are the same as input_ids
        tokenized["labels"] = tokenized["input_ids"].clone()

        return tokenized

    # Tokenize dataset
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names,
    )

    return tokenized_dataset


# ============================================================================
# MODEL PREPARATION
# ============================================================================


def prepare_model_for_lora(
    model_name: str,
    device: str = "cpu",
    lora_rank: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.1,
) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Prepare model with LoRA configuration"""

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Set padding token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,  # Use float32 for CPU
        device_map=device,
    )

    # Configure LoRA
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=lora_rank,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=["c_attn", "c_proj", "c_fc"],  # Common GPT-2 modules
        bias="none",
    )

    # Apply LoRA
    model = get_peft_model(model, lora_config)

    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable %: {100 * trainable_params / total_params:.2f}%")

    return model, tokenizer


# ============================================================================
# TRAINING
# ============================================================================


def run_test_training(
    model_name: str,
    dataset_path: str,
    output_dir: str,
    epochs: int = 1,
    batch_size: int = 2,
    learning_rate: float = 5e-5,
    max_steps: int = 10,  # Small for testing
) -> TestReport:
    """Run test training with governance validation"""

    violations: List[str] = []
    start_time = time.time()

    print("=" * 80)
    print("CPU LORA TEST TRAINING")
    print("=" * 80)

    # Validate inputs
    print("\n1. VALIDATING INPUTS")
    print("-" * 40)

    # Validate dataset
    dataset_valid, dataset_msg = validate_dataset_path(dataset_path)
    print(f"Dataset: {dataset_msg}")
    if not dataset_valid:
        violations.append(f"Dataset validation failed: {dataset_msg}")

    # Validate output directory
    output_valid, output_msg = validate_output_directory(output_dir)
    print(f"Output directory: {output_msg}")
    if not output_valid:
        violations.append(f"Output directory validation failed: {output_msg}")

    # Validate model name
    model_valid, model_msg = validate_model_name(model_name)
    print(f"Model: {model_msg}")
    if not model_valid:
        violations.append(f"Model validation failed: {model_msg}")

    # Validate hyperparameters
    if epochs > MAX_EPOCHS:
        violations.append(f"Epochs {epochs} exceeds maximum {MAX_EPOCHS}")
    if batch_size > MAX_BATCH_SIZE:
        violations.append(f"Batch size {batch_size} exceeds maximum {MAX_BATCH_SIZE}")
    if learning_rate > MAX_LEARNING_RATE:
        violations.append(
            f"Learning rate {learning_rate} exceeds maximum {MAX_LEARNING_RATE}"
        )

    if violations:
        print(f"\n❌ Validation failed with {len(violations)} violations:")
        for v in violations:
            print(f"  - {v}")
        return TestReport(
            model_name=model_name,
            dataset_path=dataset_path,
            test_successful=False,
            governance_compliant=False,
            violations=tuple(violations),
            test_duration_minutes=0,
            model_size_gb=0,
            timestamp=datetime.now().isoformat(),
        )

    print("\n✅ All validations passed")

    # Prepare model and tokenizer
    print("\n2. PREPARING MODEL")
    print("-" * 40)
    print(f"Model name: {model_name}")
    print(f"Device: cpu")

    try:
        model, tokenizer = prepare_model_for_lora(
            model_name=model_name,
            device="cpu",
            lora_rank=8,
        )
        print("✅ Model prepared successfully")
        print(f"Model type: {type(model)}")
        print(f"Tokenizer type: {type(tokenizer)}")
    except Exception as e:
        error_msg = f"Model preparation failed: {e}"
        print(f"❌ {error_msg}")
        import traceback

        traceback.print_exc()
        violations.append(error_msg)
        return TestReport(
            model_name=model_name,
            dataset_path=dataset_path,
            test_successful=False,
            governance_compliant=False,
            violations=tuple(violations),
            test_duration_minutes=0,
            model_size_gb=0,
            timestamp=datetime.now().isoformat(),
        )

    # Load and prepare dataset
    print("\n3. LOADING DATASET")
    print("-" * 40)
    print(f"Dataset path: {dataset_path}")

    try:
        dataset = load_and_prepare_dataset(dataset_path, tokenizer)
        print(f"✅ Dataset loaded: {len(dataset)} examples")
        print(f"Dataset type: {type(dataset)}")
        if hasattr(dataset, "column_names"):
            print(f"Dataset columns: {dataset.column_names}")
    except Exception as e:
        error_msg = f"Dataset loading failed: {e}"
        print(f"❌ {error_msg}")
        import traceback

        traceback.print_exc()
        violations.append(error_msg)
        return TestReport(
            model_name=model_name,
            dataset_path=dataset_path,
            test_successful=False,
            governance_compliant=False,
            violations=tuple(violations),
            test_duration_minutes=0,
            model_size_gb=0,
            timestamp=datetime.now().isoformat(),
        )

    # Configure training
    print("\n4. CONFIGURING TRAINING")
    print("-" * 40)
    print(f"Output directory: {output_dir}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    print(f"Learning rate: {learning_rate}")
    print(f"Max steps: {max_steps}")

    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=1,
        learning_rate=learning_rate,
        weight_decay=0.01,
        warmup_steps=10,
        logging_steps=5,
        save_steps=50,
        eval_steps=50,
        save_total_limit=2,
        load_best_model_at_end=False,
        metric_for_best_model="loss",
        greater_is_better=False,
        fp16=False,  # Disable for CPU
        report_to="none",  # Disable wandb/tensorboard
        max_steps=max_steps,  # Limit for testing
        gradient_checkpointing=False,  # Disable for CPU testing
    )

    # Create trainer
    print("Creating Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )
    print("Trainer created successfully")

    # Run training
    print("\n5. RUNNING TRAINING")
    print("-" * 40)

    try:
        print(f"Starting training for {max_steps} steps...")
        print(f"Trainer state: {trainer.state}")
        trainer.train()
        print("✅ Training completed successfully")
        print(f"Training state: {trainer.state}")

        # Save model
        print(f"Saving model to {output_dir}...")
        trainer.save_model()
        tokenizer.save_pretrained(output_dir)
        print("✅ Model saved")

        # Calculate model size
        model_size_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
        model_size_gb = model_size_bytes / (1024**3)
        print(f"Model size: {model_size_bytes:,} bytes = {model_size_gb:.2f} GB")

        if model_size_gb > MAX_MODEL_SIZE_GB:
            violations.append(
                f"Model size {model_size_gb:.2f}GB exceeds maximum {MAX_MODEL_SIZE_GB}GB"
            )

    except Exception as e:
        error_msg = f"Training failed: {e}"
        print(f"❌ {error_msg}")
        import traceback

        traceback.print_exc()
        violations.append(error_msg)
        model_size_gb = 0

    # Calculate duration
    end_time = time.time()
    duration_minutes = (end_time - start_time) / 60

    if duration_minutes > MAX_TEST_TIME_MINUTES:
        violations.append(
            f"Test duration {duration_minutes:.1f} minutes exceeds maximum {MAX_TEST_TIME_MINUTES} minutes"
        )

    # Generate report
    test_successful = len(violations) == 0
    governance_compliant = test_successful

    report = TestReport(
        model_name=model_name,
        dataset_path=dataset_path,
        test_successful=test_successful,
        governance_compliant=governance_compliant,
        violations=tuple(violations),
        test_duration_minutes=duration_minutes,
        model_size_gb=model_size_gb,
        timestamp=datetime.now().isoformat(),
    )

    print("\n" + "=" * 80)
    print("TEST REPORT")
    print("=" * 80)
    print(f"Model: {report.model_name}")
    print(f"Dataset: {report.dataset_path}")
    print(f"Test successful: {'✅' if report.test_successful else '❌'}")
    print(f"Governance compliant: {'✅' if report.governance_compliant else '❌'}")
    print(f"Duration: {report.test_duration_minutes:.1f} minutes")
    print(f"Model size: {report.model_size_gb:.2f} GB")

    if report.violations:
        print(f"\nViolations ({len(report.violations)}):")
        for v in report.violations:
            print(f"  - {v}")

    print(f"\nTimestamp: {report.timestamp}")
    print("=" * 80)

    return report


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="CPU LoRA Test Training Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Test with distilgpt2 and augmented dataset
  python test_cpu_lora_training.py \\
    --model distilgpt2 \\
    --dataset lora_dataset/lora_dataset_augmented.jsonl \\
    --output trained_lora_test_cpu

  # Test with small batch size and few steps
  python test_cpu_lora_training.py \\
    --model distilgpt2 \\
    --dataset lora_dataset/lora_dataset_augmented.jsonl \\
    --output trained_lora_test_small \\
    --batch-size 1 \\
    --max-steps 5
""",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="distilgpt2",
        help="Model name (default: distilgpt2)",
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
        default="trained_lora_test_cpu",
        help="Output directory (default: trained_lora_test_cpu)",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=1,
        help=f"Number of epochs (max: {MAX_EPOCHS}, default: 1)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help=f"Batch size (max: {MAX_BATCH_SIZE}, default: 2)",
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=5e-5,
        help=f"Learning rate (max: {MAX_LEARNING_RATE}, default: 5e-5)",
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=10,
        help="Maximum training steps (default: 10)",
    )

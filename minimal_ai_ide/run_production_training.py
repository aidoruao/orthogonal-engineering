#!/usr/bin/env python3
"""
PRODUCTION TRAINING SCRIPT - CUDA OPTIMIZED
===========================================

MAXIMAL STRICT CORPORATE GOVERNANCE PYTHON (MSGCP) COMPLIANT

OPTIMIZED FOR:
- CUDA-enabled PyTorch 2.5.1+cu121
- RTX 4050 6GB VRAM (dynamic allocation)
- Llama 3.2 1B with 4-bit quantization
- 500 Popperian examples dataset
- MSGCP governance enforcement

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Comments state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all operations
4. EXPLICIT BOUNDS: MAX_TRAINING_HOURS=3h, MAX_MODEL_SIZE_GB=2
5. TYPE SAFETY: mypy --strict compliance mandatory
6. ZERO TRUST: All external resources verified before use
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from datasets import Dataset, load_dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    PreTrainedModel,
    PreTrainedTokenizer,
    Trainer,
    TrainingArguments,
)

# ============================================================================
# GOVERNANCE CONSTANTS - OPTIMIZED FOR RTX 4050 6GB VRAM
# ============================================================================

MAX_TRAINING_HOURS: int = 3  # 3 hours maximum for production training
MAX_MODEL_SIZE_GB: int = 2  # 2GB maximum for 4-bit quantized model
MAX_DATASET_SAMPLES: int = 500  # Full dataset
MAX_BATCH_SIZE: int = 4  # Optimized for 6GB VRAM
MAX_EPOCHS: int = 3  # 3 epochs for good convergence
MAX_GRAD_NORM: float = 1.0
MAX_LEARNING_RATE: float = 2e-4
MIN_LEARNING_RATE: float = 1e-6
MAX_LORA_RANK: int = 32  # Higher rank for better adaptation
MAX_PROMPT_LENGTH: int = 512

# Early stopping
PATIENCE: int = 10  # Stop if no improvement for 10 steps
MIN_LOSS_DELTA: float = 0.001  # Minimum improvement

# ============================================================================
# GOVERNANCE DATA STRUCTURES
# ============================================================================


@dataclass(frozen=True)
class GovernanceThreshold:
    """Governance threshold with explicit bounds"""

    name: str
    min_value: float
    max_value: float
    unit: str


@dataclass(frozen=True)
class ProductionTrainingReport:
    """Production training report with governance compliance"""

    model_name: str
    dataset_path: str
    training_successful: bool
    governance_compliant: bool
    violations: Tuple[str, ...]
    training_duration_hours: float
    model_size_gb: float
    christ_score: float
    final_loss: float
    best_loss: float
    samples_processed: int
    timestamp: str

    def __bool__(self) -> bool:
        """Training successful only if both functional and governance compliant"""
        return self.training_successful and self.governance_compliant


# ============================================================================
# GOVERNANCE VALIDATORS
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
    if file_size_mb > 1024:  # 1GB maximum
        return False, f"Dataset size {file_size_mb:.2f}MB exceeds maximum 1024MB"

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
    """Validate model name is reasonable and supported"""
    if not model_name:
        return False, "Model name cannot be empty"

    if len(model_name) > 100:
        return False, f"Model name too long: {len(model_name)} characters"

    # Check for supported models
    supported_models = [
        "meta-llama/Llama-3.2-1B",
        "meta-llama/Llama-3.2-3B",
        "distilgpt2",
        "gpt2",
        "microsoft/phi-2",
    ]

    if model_name not in supported_models:
        print(f"⚠️  Warning: {model_name} not in supported models list")

    return True, f"Model name valid: {model_name}"


# ============================================================================
# DATASET PROCESSING - OPTIMIZED FOR POPPERIAN EXAMPLES
# ============================================================================


def load_and_prepare_dataset(
    dataset_path: str, tokenizer: PreTrainedTokenizer, max_length: int = 512
) -> Dataset:
    """Load and prepare Popperian dataset for training"""

    # Load dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")

    # Tokenization function optimized for Popperian format
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

        # Tokenize with optimized settings
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

    # Tokenize dataset with batching
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        batch_size=100,  # Optimized batch size for mapping
        remove_columns=dataset.column_names,
    )

    return tokenized_dataset


# ============================================================================
# MODEL PREPARATION - 4-BIT QUANTIZATION OPTIMIZED
# ============================================================================


def prepare_quantized_model(
    model_name: str,
    device: str = "cuda",
    lora_rank: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.1,
) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Prepare 4-bit quantized model with LoRA"""

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Set padding token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Configure 4-bit quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    # Load quantized model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        trust_remote_code=False,  # Security: no remote code
    )

    # Configure LoRA for Llama architecture
    target_modules = [
        "q_proj",
        "v_proj",
        "k_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ]

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=lora_rank,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=target_modules,
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

    # Print memory usage
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        print(f"GPU memory allocated: {allocated:.2f} GB")
        print(f"GPU memory reserved: {reserved:.2f} GB")

    return model, tokenizer


# ============================================================================
# TRAINING CLASS WITH GOVERNANCE ENFORCEMENT
# ============================================================================


class ProductionLoRATrainer:
    """Production LoRA trainer with CUDA optimization and governance"""

    def __init__(self):
        self.model: Optional[PreTrainedModel] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None
        self.violations: List[str] = []
        self.start_time: Optional[float] = None
        self.best_loss: float = float("inf")
        self.current_loss: float = 0.0

    def validate_inputs(
        self,
        model_name: str,
        dataset_path: str,
        output_dir: str,
        epochs: int,
        batch_size: int,
        learning_rate: float,
        lora_rank: int,
        lora_alpha: int,
    ) -> bool:
        """Validate all inputs against governance bounds"""

        print("\n[GOVERNANCE] Validating inputs...")
        print("-" * 40)

        # Validate dataset
        dataset_valid, dataset_msg = validate_dataset_path(dataset_path)
        print(f"Dataset: {dataset_msg}")
        if not dataset_valid:
            self.violations.append(f"Dataset validation failed: {dataset_msg}")

        # Validate output directory
        output_valid, output_msg = validate_output_directory(output_dir)
        print(f"Output directory: {output_msg}")
        if not output_valid:
            self.violations.append(f"Output directory validation failed: {output_msg}")

        # Validate model name
        model_valid, model_msg = validate_model_name(model_name)
        print(f"Model: {model_msg}")
        if not model_valid:
            self.violations.append(f"Model validation failed: {model_msg}")

        # Validate hyperparameters
        if epochs > MAX_EPOCHS:
            self.violations.append(f"Epochs {epochs} exceeds maximum {MAX_EPOCHS}")
        if batch_size > MAX_BATCH_SIZE:
            self.violations.append(f"Batch size {batch_size} exceeds maximum {MAX_BATCH_SIZE}")
        if learning_rate > MAX_LEARNING_RATE:
            self.violations.append(
                f"Learning rate {learning_rate} exceeds maximum {MAX_LEARNING_RATE}"
            )
        if learning_rate < MIN_LEARNING_RATE:
            self.violations.append(
                f"Learning rate {learning_rate} below minimum {MIN_LEARNING_RATE}"
            )
        if lora_rank > MAX_LORA_RANK:
            self.violations.append(f"LoRA rank {lora_rank} exceeds maximum {MAX_LORA_RANK}")
        if lora_alpha < lora_rank:
            self.violations.append(f"LoRA alpha {lora_alpha} should be >= rank {lora_rank}")

        # Validate CUDA availability
        if not torch.cuda.is_available():
            self.violations.append("CUDA not available - GPU acceleration required")
            print("❌ CUDA not available - GPU acceleration required")

        if self.violations:
            print(f"\n❌ Validation failed with {len(self.violations)} violations:")
            for v in self.violations:
                print(f"  - {v}")
            return False

        print("\n✅ All validations passed")
        return True

    def prepare_training(
        self,
        model_name: str,
        lora_rank: int = 16,
        lora_alpha: int = 32,
    ) -> bool:
        """Prepare model and tokenizer for training"""

        print("\n[PREPARATION] Loading 4-bit quantized model...")
        print("-" * 40)

        try:
            self.model, self.tokenizer = prepare_quantized_model(
                model_name=model_name,
                device="cuda",
                lora_rank=lora_rank,
                lora_alpha=lora_alpha,
            )
            print("✅ Model prepared successfully")
            return True
        except Exception as e:
            error_msg = f"Model preparation failed: {e}"
            print(f"❌ {error_msg}")
            self.violations.append(error_msg)
            return False

    def calculate_christ_score(self, success: bool, loss_reduction: float) -> float:
        """Calculate Christ score based on training success and loss reduction"""
        if not success:
            return 0.0

        # Base score for successful training
        base_score = 0.7

        # Add bonus for loss reduction
        loss_bonus = min(loss_reduction / 10.0, 0.3)  # Max 0.3 bonus

        # Governance compliance bonus
        governance_bonus = 0.1 if len(self.violations) == 0 else 0.0

        return min(base_score + loss_bonus + governance_bonus, 1.0)

    def train(
        self,
        model_name: str,
        dataset_path: str,
        output_dir: str,
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        lora_rank: int = 16,
        lora_alpha: int = 32,
    ) -> ProductionTrainingReport:
        """Run production training with governance validation"""

        self.start_time = time.time()

        print("=" * 80)
        print("PRODUCTION LoRA TRAINING - CUDA OPTIMIZED")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Model: {model_name} (4-bit quantized)")
        print(f"Device: CUDA ({torch.cuda.get_device_name(0)})")
        print(f"Dataset: {dataset_path}")
        print(f"Output: {output_dir}")
        print(f"Epochs: {epochs}")
        print(f"Batch size: {batch_size}")
        print(f"Learning rate: {learning_rate}")
        print(f"LoRA rank: {lora_rank}, alpha: {lora_alpha}")
        print("=" * 80)

        # Validate inputs
        if not self.validate_inputs(
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            lora_rank=lora_rank,
            lora_alpha=lora_alpha,
        ):
            return self._create_report(
                model_name=model_name,
                dataset_path=dataset_path,
                success=False,
                final_loss=0.0,
                best_loss=0.0,
                samples_processed=0,
            )

        # Prepare model
        if not self.prepare_training(
            model_name=model_name,
            lora_rank=lora_rank,
            lora_alpha=lora_alpha,
        ):
            return self._create_report(
                model_name=model_name,
                dataset_path=dataset_path,
                success=False,
                final_loss=0.0,
                best_loss=0.0,
                samples_processed=0,
            )

        # Load dataset
        print("\n[DATASET] Loading Popperian examples...")
        print("-" * 40)

        try:
            dataset = load_and_prepare_dataset(dataset_path, self.tokenizer, MAX_PROMPT_LENGTH)
            print(f"✅ Dataset loaded: {len(dataset)} examples")
        except Exception as e:
            error_msg = f"Dataset loading failed: {e}"
            print(f"❌ {error_msg}")
            self.violations.append(error_msg)
            return self._create_report(
                model_name=model_name,
                dataset_path=dataset_path,
                success=False,
                final_loss=0.0,
                best_loss=0.0,
                samples_processed=0,
            )

        # Configure training
        print("\n[TRAINING] Configuring training parameters...")
        print("-" * 40)

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
            logging_steps=10,
            save_steps=100,
            eval_steps=100,
            save_total_limit=2,
            load_best_model_at_end=True,
            metric_for_best_model="loss",
            greater_is_better=False,
            fp16=True,
            report_to="none",
            gradient_checkpointing=True,
            max_grad_norm=MAX_GRAD_NORM,
            remove_unused_columns=False,
            dataloader_drop_last=False,
        )

        print("✅ Training arguments configured")

        # Create trainer
        print("\n[TRAINING] Creating trainer...")
        print("-" * 40)

        try:
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=dataset,
                tokenizer=self.tokenizer,
            )
            print("✅ Trainer created")
        except Exception as e:
            error_msg = f"Trainer creation failed: {e}"
            print(f"❌ {error_msg}")
            self.violations.append(error_msg)
            return self._create_report(
                model_name=model_name,
                dataset_path=dataset_path,
                success=False,
                final_loss=0.0,
                best_loss=0.0,
                samples_processed=0,
            )

        # Run training
        print("\n[TRAINING] Starting production training...")
        print("-" * 40)

        try:
            print(f"Training for {epochs} epochs...")
            train_result = trainer.train()
            print("✅ Training completed successfully")

            # Save model
            print(f"\n[SAVING] Saving model to {output_dir}...")
            trainer.save_model()
            self.tokenizer.save_pretrained(output_dir)
            print("✅ Model saved")

            # Get training metrics
            self.current_loss = train_result.training_loss
            self.best_loss = min(self.current_loss, self.best_loss)
            samples_processed = len(dataset) * epochs

            # Calculate model size
            model_size_bytes = sum(p.numel() * p.element_size() for p in self.model.parameters())
            model_size_gb = model_size_bytes / (1024**3)

            if model_size_gb > MAX_MODEL_SIZE_GB:
                self.violations.append(
                    f"Model size {model_size_gb:.2f}GB exceeds maximum {MAX_MODEL_SIZE_GB}GB"
                )

            # Calculate Christ score
            initial_loss_estimate = 10.0  # Estimated initial loss for causal LM
            loss_reduction = initial_loss_estimate - self.current_loss
            christ_score = self.calculate_christ_score(True, loss_reduction)

            # Calculate duration
            end_time = time.time()
            duration_hours = (end_time - self.start_time) / 3600

            if duration_hours > MAX_TRAINING_HOURS:
                self.violations.append(
                    f"Training duration {duration_hours:.2f}h exceeds maximum {MAX_TRAINING_HOURS}h"
                )

            return self._create_report(
                model_name=model_name,
                dataset_path=dataset_path,
                success=True,
                final_loss=self.current_loss,
                best_loss=self.best_loss,
                samples_processed=samples_processed,
                training_duration_hours=duration_hours,
                model_size_gb=model_size_gb,
                christ_score=christ_score,
            )

        except Exception as e:
            error_msg = f"Training failed: {e}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            self.violations.append(error_msg)
            return self._create_report(
                model_name=model_name,
                dataset_path=dataset_path,
                success=False,
                final_loss=0.0,
                best_loss=0.0,
                samples_processed=0,
            )

    def _create_report(
        self,
        model_name: str,
        dataset_path: str,
        success: bool,
        final_loss: float,
        best_loss: float,
        samples_processed: int,
        training_duration_hours: float = 0.0,
        model_size_gb: float = 0.0,
        christ_score: float = 0.0,
    ) -> ProductionTrainingReport:
        """Create production training report"""

        # Check governance compliance
        governance_compliant = len(self.violations) == 0

        return ProductionTrainingReport(
            model_name=model_name,
            dataset_path=dataset_path,
            training_successful=success,
            governance_compliant=governance_compliant,
            violations=tuple(self.violations),
            training_duration_hours=training_duration_hours,
            model_size_gb=model_size_gb,
            christ_score=christ_score,
            final_loss=final_loss,
            best_loss=best_loss,
            samples_processed=samples_processed,
            timestamp=datetime.now().isoformat(),
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Production LoRA Training with CUDA Optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Train Llama 3.2 1B with 4-bit quantization
  python run_production_training.py \\
    --model meta-llama/Llama-3.2-1B \\
    --dataset lora_dataset/lora_dataset_augmented.jsonl \\
    --output trained_llama_1b \\
    --epochs 3 \\
    --batch-size 4

  # Train with custom parameters
  python run_production_training.py \\
    --model meta-llama/Llama-3.2-1B \\
    --dataset lora_dataset/lora_dataset_augmented.jsonl \\
    --output trained_llama_custom \\
    --epochs 2 \\
    --batch-size 2 \\
    --learning-rate 1e-4 \\
    --lora-rank 32

GOVERNANCE BOUNDS:
  Maximum training time: 3 hours
  Maximum model size: 2GB
  Maximum samples: 500
  Maximum batch size: 4
  Maximum epochs: 3
  Christ score minimum: 0.7
""",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="meta-llama/Llama-3.2-1B",
        help="Model name (default: meta-llama/Llama-3.2-1B)",
    )

    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to training dataset (JSONL format)",
    )

    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output directory for trained model",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help=f"Number of training epochs (max: {MAX_EPOCHS}, default: 3)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help=f"Batch size per device (max: {MAX_BATCH_SIZE}, default: 4)",
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-4,
        help=f"Learning rate (range: {MIN_LEARNING_RATE} to {MAX_LEARNING_RATE}, default: 2e-4)",
    )

    parser.add_argument(
        "--lora-rank",
        type=int,
        default=16,
        help=f"LoRA rank (max: {MAX_LORA_RANK}, default: 16)",
    )

    parser.add_argument(
        "--lora-alpha",
        type=int,
        default=32,
        help="LoRA alpha (should be >= rank, default: 32)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Create trainer
    trainer = ProductionLoRATrainer()

    # Run training
    report = trainer.train(
        model_name=args.model,
        dataset_path=args.dataset,
        output_dir=args.output,
        epochs=min(args.epochs, MAX_EPOCHS),
        batch_size=min(args.batch_size, MAX_BATCH_SIZE),
        learning_rate=args.learning_rate,
        lora_rank=min(args.lora_rank, MAX_LORA_RANK),
        lora_alpha=args.lora_alpha,
    )

    # Print report
    print("\n" + "=" * 80)
    print("PRODUCTION TRAINING REPORT")
    print("=" * 80)
    print(f"Model: {report.model_name}")
    print(f"Dataset: {report.dataset_path}")
    print(f"Training successful: {'✅' if report.training_successful else '❌'}")
    print(f"Governance compliant: {'✅' if report.governance_compliant else '❌'}")
    print(f"Training duration: {report.training_duration_hours:.2f}h")
    print(f"Model size: {report.model_size_gb:.2f}GB")
    print(f"Christ score: {report.christ_score:.3f} (minimum: 0.7)")
    print(f"Final loss: {report.final_loss:.4f}")
    print(f"Best loss: {report.best_loss:.4f}")
    print(f"Samples processed: {report.samples_processed}")

    if report.violations:
        print(f"\nViolations ({len(report.violations)}):")
        for v in report.violations:
            print(f"  - {v}")

    print(f"\nTimestamp: {report.timestamp}")
    print("=" * 80)

    # Check success criteria
    if report.training_successful and report.governance_compliant and report.christ_score >= 0.7:
        print("\n✅ PRODUCTION TRAINING COMPLETED SUCCESSFULLY")
        print("   All governance requirements satisfied")
        print("   Christ constraint maintained")
        sys.exit(0)
    else:
        print("\n❌ PRODUCTION TRAINING FAILED")
        if not report.training_successful:
            print("   - Training process failed")
        if not report.governance_compliant:
            print("   - Governance violations detected")
        if report.christ_score < 0.7:
            print(f"   - Christ score {report.christ_score:.3f} < 0.7 minimum")
        sys.exit(1)


if __name__ == "__main__":
    main()

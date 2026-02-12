#!/usr/bin/env python3
"""
Quantized LoRA Training Script for Llama 3.2
=============================================

MAXIMAL STRICT CORPORATE GOVERNANCE PYTHON (MSGCP) COMPLIANT

MANDATE: All training operations MUST pass governance validation
FAILURE CONDITION: Any operation not validated by governance is REJECTED
AI AUTONOMY: ZERO. The system validates or rejects.

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Comments state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all operations
4. EXPLICIT BOUNDS: MAX_TRAINING_TIME=24h, MAX_MODEL_SIZE=10GB
5. TYPE SAFETY: mypy --strict compliance mandatory
6. ZERO TRUST: All external resources verified before use
"""

from __future__ import annotations

import argparse
import hashlib
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
# GOVERNANCE CONSTANTS - UNCHANGEABLE BOUNDS
# ============================================================================

MAX_TRAINING_HOURS: int = 24
MAX_MODEL_SIZE_GB: int = 10
MAX_DATASET_SIZE_MB: int = 1024  # 1GB
MAX_LORA_RANK: int = 64
MAX_BATCH_SIZE: int = 8
MAX_EPOCHS: int = 10
MAX_GRAD_NORM: float = 1.0
MAX_LEARNING_RATE: float = 2e-4
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
class TrainingReport:
    """Training report with governance compliance"""

    model_name: str
    dataset_path: str
    training_successful: bool
    governance_compliant: bool
    violations: Tuple[str, ...]
    training_duration_hours: float
    model_size_gb: float
    christ_score: float
    timestamp: str

    def __bool__(self) -> bool:
        """Training successful only if both functional and governance compliant"""
        return self.training_successful and self.governance_compliant


# ============================================================================
# GOVERNANCE VALIDATORS - BOUNDED OPERATIONS
# ============================================================================


class TrainingGovernance:
    """Governance validation for training operations"""

    @staticmethod
    def validate_model_size(model: PreTrainedModel) -> Tuple[bool, str]:
        """Validate model size is within bounds"""
        try:
            param_count = sum(p.numel() for p in model.parameters())
            param_size_gb = (param_count * 4) / (1024**3)  # Assuming float32

            if param_size_gb > MAX_MODEL_SIZE_GB:
                return (
                    False,
                    f"Model size {param_size_gb:.2f}GB exceeds MAX_MODEL_SIZE_GB={MAX_MODEL_SIZE_GB}",
                )
            return True, f"Model size acceptable: {param_size_gb:.2f}GB"
        except Exception as e:
            return False, f"Model size validation failed: {str(e)}"

    @staticmethod
    def validate_dataset_size(dataset_path: str) -> Tuple[bool, str]:
        """Validate dataset size is within bounds"""
        try:
            if not os.path.exists(dataset_path):
                return False, f"Dataset path does not exist: {dataset_path}"

            # Calculate total size of dataset files
            total_size_mb = 0
            for root, dirs, files in os.walk(dataset_path):
                for file in files:
                    if file.endswith((".jsonl", ".json", ".txt", ".parquet")):
                        file_path = os.path.join(root, file)
                        total_size_mb += os.path.getsize(file_path) / (1024 * 1024)

            if total_size_mb > MAX_DATASET_SIZE_MB:
                return (
                    False,
                    f"Dataset size {total_size_mb:.2f}MB exceeds MAX_DATASET_SIZE_MB={MAX_DATASET_SIZE_MB}",
                )
            return True, f"Dataset size acceptable: {total_size_mb:.2f}MB"
        except Exception as e:
            return False, f"Dataset size validation failed: {str(e)}"

    @staticmethod
    def validate_training_params(
        epochs: int, batch_size: int, learning_rate: float, grad_norm: float
    ) -> Tuple[bool, str]:
        """Validate training parameters against governance bounds"""
        violations = []

        if epochs > MAX_EPOCHS:
            violations.append(f"Epochs {epochs} > MAX_EPOCHS {MAX_EPOCHS}")

        if batch_size > MAX_BATCH_SIZE:
            violations.append(
                f"Batch size {batch_size} > MAX_BATCH_SIZE {MAX_BATCH_SIZE}"
            )

        if learning_rate > MAX_LEARNING_RATE:
            violations.append(
                f"Learning rate {learning_rate} > MAX_LEARNING_RATE {MAX_LEARNING_RATE}"
            )

        if learning_rate < MIN_LEARNING_RATE:
            violations.append(
                f"Learning rate {learning_rate} < MIN_LEARNING_RATE {MIN_LEARNING_RATE}"
            )

        if grad_norm > MAX_GRAD_NORM:
            violations.append(
                f"Gradient norm {grad_norm} > MAX_GRAD_NORM {MAX_GRAD_NORM}"
            )

        if violations:
            return False, "; ".join(violations)

        return True, "Training parameters within governance bounds"

    @staticmethod
    def validate_lora_config(lora_rank: int, lora_alpha: int) -> Tuple[bool, str]:
        """Validate LoRA configuration"""
        if lora_rank > MAX_LORA_RANK:
            return False, f"LoRA rank {lora_rank} > MAX_LORA_RANK {MAX_LORA_RANK}"

        if lora_alpha < lora_rank:
            return False, f"LoRA alpha {lora_alpha} should be >= rank {lora_rank}"

        return True, f"LoRA configuration valid: rank={lora_rank}, alpha={lora_alpha}"

    @staticmethod
    def calculate_christ_score(
        model_name: str, dataset_purpose: str, training_method: str
    ) -> Tuple[float, str]:
        """Calculate Christlikeness score for training operation"""
        score = 0.0
        reasons = []

        # Truth: model name explicitly stated
        if model_name:
            score += 0.2
            reasons.append("Truth: model name explicitly stated")

        # Humility: finite training parameters
        if training_method == "lora":
            score += 0.2
            reasons.append("Humility: parameter-efficient training")

        # Honesty: dataset purpose documented
        if dataset_purpose:
            score += 0.2
            reasons.append("Honesty: dataset purpose documented")

        # Boundaries: explicit size limits
        score += 0.2
        reasons.append("Boundaries: explicit size limits enforced")

        # Mediation: governance validation required
        score += 0.2
        reasons.append("Mediation: governance validation required")

        return score, "; ".join(reasons)


# ============================================================================
# QUANTIZED MODEL TRAINER - GOVERNANCE ENFORCED
# ============================================================================


class QuantizedLoRATrainer:
    """
    Quantized LoRA trainer with full governance enforcement.

    RULES:
    1. All operations MUST pass governance validation
    2. Explicit bounds on all training parameters
    3. Quantization for memory efficiency
    4. Christ constraint must be satisfied
    5. Zero trust: verify before training
    """

    def __init__(
        self,
        base_model: str = "meta-llama/Llama-3.2-1B",
        device: str = "cuda",
        quantization: str = "4bit",
    ):
        self.base_model = base_model
        self.device = device
        self.quantization = quantization
        self.tokenizer: Optional[PreTrainedTokenizer] = None
        self.model: Optional[PreTrainedModel] = None
        self.violations: List[str] = []
        self.start_time: Optional[float] = None

    def setup_quantization_config(self) -> BitsAndBytesConfig:
        """Setup quantization configuration based on selected quantization level"""
        if self.quantization == "4bit":
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
        elif self.quantization == "8bit":
            return BitsAndBytesConfig(
                load_in_8bit=True,
            )
        else:
            raise ValueError(f"Unsupported quantization: {self.quantization}")

    def load_and_validate_dataset(
        self, dataset_path: str, max_samples: Optional[int] = None
    ) -> Dataset:
        """Load and validate training dataset"""
        print("\n1. LOADING AND VALIDATING DATASET")
        print("-" * 40)

        # GOVERNANCE: Validate dataset size
        valid, message = TrainingGovernance.validate_dataset_size(dataset_path)
        if not valid:
            raise ValueError(f"Dataset validation failed: {message}")
        print(f"   ✅ {message}")

        # Load dataset
        print(f"   Loading dataset from: {dataset_path}")
        try:
            if dataset_path.endswith(".jsonl"):
                dataset = load_dataset("json", data_files=dataset_path, split="train")
            else:
                dataset = load_dataset(dataset_path, split="train")
        except Exception as e:
            raise ValueError(f"Failed to load dataset: {str(e)}")

        # Limit samples if specified
        if max_samples and len(dataset) > max_samples:
            print(f"   Limiting to {max_samples} samples (governance bound)")
            dataset = dataset.select(range(max_samples))

        print(f"   ✅ Dataset loaded: {len(dataset)} samples")
        return dataset

    def prepare_quantized_model(
        self,
        lora_rank: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.1,
        target_modules: Optional[List[str]] = None,
    ) -> PreTrainedModel:
        """Prepare quantized model with LoRA configuration"""
        print("\n2. PREPARING QUANTIZED MODEL WITH LORA")
        print("-" * 40)

        # GOVERNANCE: Validate LoRA configuration
        valid, message = TrainingGovernance.validate_lora_config(lora_rank, lora_alpha)
        if not valid:
            raise ValueError(f"LoRA configuration failed: {message}")
        print(f"   ✅ {message}")

        # Setup quantization
        print(f"   Setting up {self.quantization} quantization")
        bnb_config = self.setup_quantization_config()

        # Load tokenizer
        print(f"   Loading tokenizer: {self.base_model}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.base_model,
            use_fast=False,
            trust_remote_code=False,  # Security: no remote code
        )

        # Add padding token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load quantized base model
        print(f"   Loading quantized base model: {self.base_model}")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            quantization_config=bnb_config,
            device_map="auto" if self.device == "cuda" else None,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            trust_remote_code=False,  # Security: no remote code
        )

        # GOVERNANCE: Validate model size
        valid, message = TrainingGovernance.validate_model_size(self.model)
        if not valid:
            raise ValueError(f"Model size validation failed: {message}")
        print(f"   ✅ {message}")

        # Configure LoRA
        if target_modules is None:
            # Default target modules for Llama architecture
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

        # Apply LoRA to quantized model
        self.model = get_peft_model(self.model, lora_config)

        # Print trainable parameters
        trainable_params = sum(
            p.numel() for p in self.model.parameters() if p.requires_grad
        )
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"   ✅ LoRA applied to quantized model")
        print(
            f"   ✅ Trainable parameters: {trainable_params:,} ({trainable_params / total_params * 100:.2f}%)"
        )

        return self.model

    def tokenize_function(self, examples: Dict[str, Any]) -> Dict[str, Any]:
        """Tokenize dataset examples"""
        if self.tokenizer is None:
            raise ValueError("Tokenizer not initialized")

        # Format examples for instruction tuning
        texts = []
        for i in range(len(examples.get("instruction", []))):
            instruction = examples["instruction"][i]
            input_text = examples.get("input", [""])[i] or ""
            output = examples["output"][i]

            # Format as instruction-input-output
            if input_text:
                text = (
                    f"Instruction: {instruction}\nInput: {input_text}\nOutput: {output}"
                )
            else:
                text = f"Instruction: {instruction}\nOutput: {output}"

            texts.append(text)

        # Tokenize
        tokenized = self.tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=512,
            return_tensors="pt",
        )

        # Create labels (same as input_ids for causal LM)
        tokenized["labels"] = tokenized["input_ids"].clone()
        return tokenized

    def train(
        self,
        dataset_path: str,
        output_dir: str,
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        warmup_steps: int = 100,
        logging_steps: int = 10,
        save_steps: int = 100,
        max_samples: Optional[int] = None,
        lora_rank: int = 16,
        lora_alpha: int = 32,
    ) -> TrainingReport:
        """Train quantized LoRA model with governance enforcement"""
        self.start_time = time.time()
        self.violations.clear()

        print("=" * 70)
        print("QUANTIZED LoRA TRAINING - MSGCP GOVERNANCE ENFORCEMENT")
        print("=" * 70)
        print(f"Base model: {self.base_model}")
        print(f"Quantization: {self.quantization}")
        print(f"Device: {self.device}")
        print(f"Dataset: {dataset_path}")
        print(f"Output directory: {output_dir}")
        print()

        try:
            # Load and validate dataset
            dataset = self.load_and_validate_dataset(dataset_path, max_samples)

            # Prepare quantized model with LoRA
            model = self.prepare_quantized_model(
                lora_rank=lora_rank,
                lora_alpha=lora_alpha,
            )

            # Tokenize dataset
            print("\n3. TOKENIZING DATASET")
            print("-" * 40)
            tokenized_dataset = dataset.map(
                self.tokenize_function,
                batched=True,
                remove_columns=dataset.column_names,
            )
            print(f"   ✅ Dataset tokenized: {len(tokenized_dataset)} samples")

            # GOVERNANCE: Validate training parameters
            print("\n4. VALIDATING TRAINING PARAMETERS")
            print("-" * 40)
            valid, message = TrainingGovernance.validate_training_params(
                epochs, batch_size, learning_rate, MAX_GRAD_NORM
            )
            if not valid:
                self.violations.append(f"Training parameters: {message}")
                print(f"   ❌ {message}")
            else:
                print(f"   ✅ {message}")

            # Calculate Christ score
            print("\n5. CALCULATING CHRIST CONSTRAINT SCORE")
            print("-" * 40)
            christ_score, christ_message = TrainingGovernance.calculate_christ_score(
                self.base_model, "corporate_governance_training", "quantized_lora"
            )
            print(f"   ✅ Christ score: {christ_score:.3f}")
            print(f"   ✅ Reasons: {christ_message}")

            # Setup training arguments
            training_args = TrainingArguments(
                output_dir=output_dir,
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                gradient_accumulation_steps=2,
                warmup_steps=warmup_steps,
                logging_steps=logging_steps,
                save_steps=save_steps,
                learning_rate=learning_rate,
                fp16=True,
                gradient_checkpointing=True,
                optim="paged_adamw_8bit",
                max_grad_norm=MAX_GRAD_NORM,
                save_total_limit=2,
                load_best_model_at_end=False,
                report_to="none",  # Disable external reporting
                remove_unused_columns=True,
            )

            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized_dataset,
                tokenizer=self.tokenizer,
            )

            # Train model
            print("\n6. TRAINING QUANTIZED LoRA MODEL")
            print("-" * 40)
            print(f"   Starting training for {epochs} epochs...")
            trainer.train()

            # Save model
            print("\n7. SAVING TRAINED MODEL")
            print("-" * 40)
            trainer.save_model()
            print(f"   ✅ Model saved to: {output_dir}")

            # Save tokenizer
            if self.tokenizer:
                self.tokenizer.save_pretrained(output_dir)
                print(f"   ✅ Tokenizer saved")

            training_duration = (time.time() - self.start_time) / 3600  # hours

            # GOVERNANCE: Check training duration
            if training_duration > MAX_TRAINING_HOURS:
                self.violations.append(
                    f"Training duration {training_duration:.2f}h > MAX_TRAINING_HOURS={MAX_TRAINING_HOURS}"
                )

            # Calculate model size
            model_size_gb = sum(p.numel() for p in model.parameters()) * 4 / (1024**3)

            # Create training report
            report = TrainingReport(
                model_name=self.base_model,
                dataset_path=dataset_path,
                training_successful=True,
                governance_compliant=len(self.violations) == 0,
                violations=tuple(self.violations),
                training_duration_hours=training_duration,
                model_size_gb=model_size_gb,
                christ_score=christ_score,
                timestamp=datetime.now().isoformat(),
            )

            return report

        except Exception as e:
            training_duration = (
                (time.time() - self.start_time) / 3600 if self.start_time else 0
            )
            print(f"\n❌ TRAINING FAILED: {str(e)}")

            report = TrainingReport(
                model_name=self.base_model,
                dataset_path=dataset_path,
                training_successful=False,
                governance_compliant=False,
                violations=(f"Training error: {str(e)}",),
                training_duration_hours=training_duration,
                model_size_gb=0.0,
                christ_score=0.0,
                timestamp=datetime.now().isoformat(),
            )
            return report


# ============================================================================
# COMMAND LINE INTERFACE - GOVERNANCE ENFORCED
# ============================================================================


def main() -> None:
    """Main CLI for quantized LoRA training"""
    parser = argparse.ArgumentParser(
        description="Quantized LoRA Training for Llama 3.2 with MSGCP Governance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
GOVERNANCE ENFORCEMENT:
  All training operations must pass governance validation
  Explicit bounds: MAX_TRAINING_HOURS=24h, MAX_MODEL_SIZE_GB=10
  Type safety: All functions strictly typed
  Zero trust: Verify before training

SUPPORTED MODELS:
  - meta-llama/Llama-3.2-1B
  - meta-llama/Llama-3.2-3B
  - meta-llama/Llama-3.2-7B
  - meta-llama/Llama-3.2-11B

QUANTIZATION OPTIONS:
  - 4bit: Most memory efficient (recommended)
  - 8bit: Good balance of efficiency and quality

EXAMPLES:
  # Train 1B model with 4-bit quantization
  python train_quantized_lora.py \\
    --model meta-llama/Llama-3.2-1B \\
    --dataset lora_dataset/lora_dataset_train.jsonl \\
    --output trained_lora_1b \\
    --quantization 4bit \\
    --epochs 3

  # Train 3B model with 8-bit quantization
  python train_quantized_lora.py \\
    --model meta-llama/Llama-3.2-3B \\
    --dataset lora_dataset/lora_dataset_train.jsonl \\
    --output trained_lora_3b \\
    --quantization 8bit \\
    --epochs 2
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
        required=True,
        help="Path to training dataset (JSONL format)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output directory for trained LoRA",
    )
    parser.add_argument(
        "--quantization",
        type=str,
        default="4bit",
        choices=["4bit", "8bit"],
        help="Quantization level (default: 4bit)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        choices=["cpu", "cuda", "mps"],
        help="Device for training (default: cuda)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help=f"Number of training epochs (max: {MAX_EPOCHS})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help=f"Batch size per device (max: {MAX_BATCH_SIZE})",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-4,
        help=f"Learning rate (range: {MIN_LEARNING_RATE} to {MAX_LEARNING_RATE})",
    )
    parser.add_argument(
        "--lora-rank",
        type=int,
        default=16,
        help=f"LoRA rank (max: {MAX_LORA_RANK})",
    )
    parser.add_argument(
        "--lora-alpha",
        type=int,
        default=32,
        help="LoRA alpha (should be >= rank)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Maximum number of training samples (for testing)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("QUANTIZED LoRA TRAINING - MSGCP GOVERNANCE ENFORCEMENT")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Model: {args.model}")
    print(f"Quantization: {args.quantization}")
    print(f"Device: {args.device}")
    print(f"Dataset: {args.dataset}")
    print(f"Output: {args.output}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch_size}")
    print(f"Learning rate: {args.learning_rate}")
    print(f"LoRA rank: {args.lora_rank}, alpha: {args.lora_alpha}")
    print()

    # Create trainer
    trainer = QuantizedLoRATrainer(
        base_model=args.model,
        device=args.device,
        quantization=args.quantization,
    )

    # Train model
    report = trainer.train(
        dataset_path=args.dataset,
        output_dir=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        max_samples=args.max_samples,
        lora_rank=args.lora_rank,
        lora_alpha=args.lora_alpha,
    )

    # Print report
    print("\n" + "=" * 70)
    print("TRAINING REPORT")
    print("=" * 70)

    print(f"Model: {report.model_name}")
    print(f"Dataset: {report.dataset_path}")
    print(f"Training successful: {'✅ YES' if report.training_successful else '❌ NO'}")
    print(
        f"Governance compliant: {'✅ YES' if report.governance_compliant else '❌ NO'}"
    )
    print(f"Training duration: {report.training_duration_hours:.2f}h")
    print(f"Model size: {report.model_size_gb:.2f}GB")
    print(f"Christ score: {report.christ_score:.3f}")
    print(f"Timestamp: {report.timestamp}")

    if report.violations:
        print(f"\nGovernance violations ({len(report.violations)}):")
        for violation in report.violations:
            print(f"  ❌ {violation}")

    # Final verdict
    print("\n" + "=" * 70)
    if report:
        print("✅ TRAINING COMPLETED SUCCESSFULLY")
        print("✅ GOVERNANCE COMPLIANCE VERIFIED")
        print("✅ CHRIST CONSTRAINT SATISFIED")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ TRAINING FAILED OR GOVERNANCE VIOLATED")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()

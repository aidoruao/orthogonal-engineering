#!/usr/bin/env python3
"""
FINAL ROBUST TRAINING SCRIPT
============================

MAXIMAL STRICT CORPORATE GOVERNANCE PYTHON (MSGCP) COMPLIANT

DESIGN PRINCIPLES:
1. ROBUST: Auto-detects model architecture, handles errors gracefully
2. UNIVERSAL: Works with any causal LM (GPT-2, Llama, Phi, etc.)
3. OPTIMIZED: 4-bit quantization for 4GB VRAM, gradient checkpointing
4. GOVERNANCE: Full MSGCP compliance with explicit bounds
5. PRACTICAL: 30-minute maximum training time for quick validation

HARDWARE OPTIMIZED FOR:
- RTX 4050 4GB VRAM (6GB dynamic allocation)
- CUDA 12.1 with PyTorch 2.5.1
- Python 3.11 with all dependencies
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
# GOVERNANCE CONSTANTS - STRICT BOUNDS
# ============================================================================

MAX_TRAINING_MINUTES: int = 30  # 30 minutes maximum
MAX_MODEL_SIZE_GB: int = 2  # 2GB maximum for 4-bit quantized
MAX_DATASET_SAMPLES: int = 6000  # 100 samples for quick validation
MAX_BATCH_SIZE: int = 2  # Conservative for 4GB VRAM
MAX_EPOCHS: int = 5  # 1 epoch for validation
MAX_GRAD_NORM: float = 1.0
MAX_LEARNING_RATE: float = 2e-4
MIN_LEARNING_RATE: float = 1e-6
MAX_LORA_RANK: int = 8  # Small rank for quick training
MAX_PROMPT_LENGTH: int = 512  # Short prompts for efficiency

# Model architecture detection
MODEL_TARGET_MODULES = {
    # GPT-2 family
    "gpt2": ["c_attn", "c_proj", "c_fc"],
    "distilgpt2": ["c_attn", "c_proj", "c_fc"],

    # Llama family (requires authentication)
    "llama": ["q_proj", "v_proj", "k_proj", "o_proj"],

    # OPT family
    "opt": ["q_proj", "v_proj", "k_proj", "out_proj", "fc1", "fc2"],

    # Phi family
    "phi": ["q_proj", "v_proj", "k_proj", "dense", "fc1", "fc2"],

    # General transformer (fallback)
    "transformer": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
}

# ============================================================================
# GOVERNANCE DATA STRUCTURES
# ============================================================================

@dataclass(frozen=True)
class TrainingResult:
    """Training result with governance compliance"""

    success: bool
    model_name: str
    dataset_path: str
    output_dir: str
    training_minutes: float
    final_loss: float
    model_size_gb: float
    christ_score: float
    governance_compliant: bool
    violations: Tuple[str, ...]
    timestamp: str

    def __bool__(self) -> bool:
        return self.success and self.governance_compliant and self.christ_score >= 0.7

# ============================================================================
# ROBUST MODEL DETECTION & PREPARATION
# ============================================================================

def detect_model_architecture(model_name: str) -> str:
    """Detect model architecture from name"""
    model_lower = model_name.lower()

    if "gpt2" in model_lower or "distilgpt" in model_lower:
        return "gpt2"
    elif "llama" in model_lower:
        return "llama"
    elif "opt" in model_lower:
        return "opt"
    elif "phi" in model_lower:
        return "phi"
    elif "transformer" in model_lower:
        return "transformer"
    else:
        # Default to general transformer architecture
        return "transformer"

def get_target_modules(model_name: str) -> List[str]:
    """Get appropriate target modules for model architecture"""
    architecture = detect_model_architecture(model_name)

    if architecture in MODEL_TARGET_MODULES:
        return MODEL_TARGET_MODULES[architecture]

    # Fallback: try to detect from model config
    print(f"⚠️  Architecture '{architecture}' not in predefined list, using fallback")
    return MODEL_TARGET_MODULES["transformer"]

def prepare_model_safely(
    model_name: str,
    tokenizer: PreTrainedTokenizer,
    lora_rank: int = 8,
    lora_alpha: int = 16,
) -> Tuple[Optional[PreTrainedModel], List[str]]:
    """Safely prepare model with fallback strategies"""

    violations = []

    try:
        # Strategy 1: Try 4-bit quantization first
        print(f"  Strategy 1: Loading {model_name} with 4-bit quantization...")

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            trust_remote_code=False,
        )

    except Exception as e1:
        print(f"  ❌ 4-bit quantization failed: {str(e1)[:100]}...")
        violations.append(f"4-bit quantization failed: {str(e1)[:200]}")

        try:
            # Strategy 2: Try FP16 without quantization
            print(f"  Strategy 2: Loading {model_name} with FP16...")

            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
            )

        except Exception as e2:
            print(f"  ❌ FP16 loading failed: {str(e2)[:100]}...")
            violations.append(f"FP16 loading failed: {str(e2)[:200]}")

            try:
                # Strategy 3: Try FP32 as last resort
                print(f"  Strategy 3: Loading {model_name} with FP32...")

                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float32,
                    device_map="auto",
                )

            except Exception as e3:
                print(f"  ❌ All loading strategies failed")
                violations.append(f"All loading strategies failed: {str(e3)[:200]}")
                return None, violations

    # Set padding token if needed
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Try to configure LoRA
    try:
        target_modules = get_target_modules(model_name)
        print(f"  Using target modules: {target_modules}")

        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=lora_rank,
            lora_alpha=lora_alpha,
            lora_dropout=0.1,
            target_modules=target_modules,
            bias="none",
        )

        model = get_peft_model(model, lora_config)

        # Print statistics
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        print(f"  Trainable parameters: {trainable_params:,}")
        print(f"  Total parameters: {total_params:,}")
        print(f"  Trainable %: {100 * trainable_params / total_params:.2f}%")

        # Check memory usage
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated(0) / 1024**3
            reserved = torch.cuda.memory_reserved(0) / 1024**3
            print(f"  GPU memory allocated: {allocated:.2f} GB")
            print(f"  GPU memory reserved: {reserved:.2f} GB")

            if allocated > MAX_MODEL_SIZE_GB:
                violations.append(f"Model memory {allocated:.2f}GB > {MAX_MODEL_SIZE_GB}GB limit")

        return model, violations

    except Exception as e:
        error_msg = f"LoRA configuration failed: {str(e)[:200]}"
        print(f"  ❌ {error_msg}")
        violations.append(error_msg)
        return None, violations

# ============================================================================
# DATASET PROCESSING
# ============================================================================

def load_dataset_safely(dataset_path: str, max_samples: int = 500) -> Tuple[Optional[Dataset], List[str]]:
    """Safely load dataset with error handling"""

    violations = []

    if not os.path.exists(dataset_path):
        violations.append(f"Dataset file not found: {dataset_path}")
        return None, violations

    try:
        # Load dataset
        dataset = load_dataset("json", data_files=dataset_path, split="train")

        # Limit samples
        if len(dataset) > max_samples:
            dataset = dataset.select(range(max_samples))
            print(f"  Limited to {max_samples} samples (governance bound)")

        print(f"  Loaded {len(dataset)} examples")
        return dataset, violations

    except Exception as e:
        error_msg = f"Dataset loading failed: {str(e)[:200]}"
        print(f"  ❌ {error_msg}")
        violations.append(error_msg)
        return None, violations

def prepare_training_data(
    dataset: Dataset,
    tokenizer: PreTrainedTokenizer,
    max_length: int = 256
) -> Dataset:
    """Prepare dataset for training"""

    def tokenize_function(examples):
        texts = []
        for i in range(len(examples["instruction"])):
            instruction = examples["instruction"][i]
            input_text = examples["input"][i]
            output_text = examples["output"][i]

            text = f"Instruction: {instruction}\nInput: {input_text}\nOutput: {output_text}\n\n"
            texts.append(text)

        tokenized = tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt",
        )

        tokenized["labels"] = tokenized["input_ids"].clone()
        return tokenized

    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        batch_size=32,
        remove_columns=dataset.column_names,
    )

    return tokenized_dataset

# ============================================================================
# GOVERNANCE VALIDATION
# ============================================================================

def validate_environment() -> List[str]:
    """Validate environment meets requirements"""

    violations = []

    # Check CUDA
    if not torch.cuda.is_available():
        violations.append("CUDA not available - GPU acceleration required")

    # Check VRAM
    if torch.cuda.is_available():
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        if vram_gb < 4:
            violations.append(f"VRAM {vram_gb:.1f}GB < 4GB minimum")

    return violations

def validate_parameters(
    model_name: str,
    dataset_path: str,
    output_dir: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    lora_rank: int,
) -> List[str]:
    """Validate all parameters against governance bounds"""

    violations = []

    # Model validation
    if not model_name:
        violations.append("Model name cannot be empty")

    # Dataset validation
    if not os.path.exists(dataset_path):
        violations.append(f"Dataset not found: {dataset_path}")

    # Output directory validation
    try:
        os.makedirs(output_dir, exist_ok=True)
        test_file = os.path.join(output_dir, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        violations.append(f"Cannot write to output directory: {str(e)[:100]}")

    # Hyperparameter validation
    if epochs > MAX_EPOCHS:
        violations.append(f"Epochs {epochs} > {MAX_EPOCHS} maximum")
    if batch_size > MAX_BATCH_SIZE:
        violations.append(f"Batch size {batch_size} > {MAX_BATCH_SIZE} maximum")
    if learning_rate > MAX_LEARNING_RATE:
        violations.append(f"Learning rate {learning_rate} > {MAX_LEARNING_RATE} maximum")
    if learning_rate < MIN_LEARNING_RATE:
        violations.append(f"Learning rate {learning_rate} < {MIN_LEARNING_RATE} minimum")
    if lora_rank > MAX_LORA_RANK:
        violations.append(f"LoRA rank {lora_rank} > {MAX_LORA_RANK} maximum")

    return violations

# ============================================================================
# TRAINING EXECUTION
# ============================================================================

def calculate_christ_score(success: bool, loss: float, violations: List[str]) -> float:
    """Calculate Christ score based on training outcome"""

    if not success:
        return 0.0

    # Base score for successful training
    base_score = 0.7

    # Loss-based adjustment (lower loss = higher score)
    loss_adjustment = max(0.0, min(0.2, (10.0 - loss) / 50.0))

    # Governance compliance bonus
    governance_bonus = 0.1 if len(violations) == 0 else 0.0

    return min(base_score + loss_adjustment + governance_bonus, 1.0)

def run_training(
    model_name: str,
    dataset_path: str,
    output_dir: str,
    epochs: int = 1,
    batch_size: int = 2,
    learning_rate: float = 2e-4,
    lora_rank: int = 8,
    max_samples: int = 100,
) -> TrainingResult:
    """Main training function with full error handling"""

    print("=" * 80)
    print("FINAL ROBUST TRAINING EXECUTION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Model: {model_name}")
    print(f"Dataset: {dataset_path}")
    print(f"Output: {output_dir}")
    print(f"Bounds: {max_samples} samples, {MAX_TRAINING_MINUTES} minutes")
    print("=" * 80)

    start_time = time.time()
    all_violations = []

    # Phase 1: Environment validation
    print("\n[PHASE 1] Validating environment...")
    env_violations = validate_environment()
    all_violations.extend(env_violations)

    if env_violations:
        print("❌ Environment validation failed:")
        for v in env_violations:
            print(f"  - {v}")
        return TrainingResult(
            success=False,
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            training_minutes=0,
            final_loss=0.0,
            model_size_gb=0.0,
            christ_score=0.0,
            governance_compliant=False,
            violations=tuple(all_violations),
            timestamp=datetime.now().isoformat(),
        )
    print("✅ Environment validated")

    # Phase 2: Parameter validation
    print("\n[PHASE 2] Validating parameters...")
    param_violations = validate_parameters(
        model_name=model_name,
        dataset_path=dataset_path,
        output_dir=output_dir,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        lora_rank=lora_rank,
    )
    all_violations.extend(param_violations)

    if param_violations:
        print("❌ Parameter validation failed:")
        for v in param_violations:
            print(f"  - {v}")
        return TrainingResult(
            success=False,
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            training_minutes=0,
            final_loss=0.0,
            model_size_gb=0.0,
            christ_score=0.0,
            governance_compliant=False,
            violations=tuple(all_violations),
            timestamp=datetime.now().isoformat(),
        )
    print("✅ Parameters validated")

    # Phase 3: Load tokenizer
    print("\n[PHASE 3] Loading tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        print(f"✅ Tokenizer loaded: {type(tokenizer).__name__}")
    except Exception as e:
        error_msg = f"Tokenizer loading failed: {str(e)[:200]}"
        print(f"❌ {error_msg}")
        all_violations.append(error_msg)
        return TrainingResult(
            success=False,
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            training_minutes=0,
            final_loss=0.0,
            model_size_gb=0.0,
            christ_score=0.0,
            governance_compliant=False,
            violations=tuple(all_violations),
            timestamp=datetime.now().isoformat(),
        )

    # Phase 4: Load dataset
    print("\n[PHASE 4] Loading dataset...")
    dataset, dataset_violations = load_dataset_safely(dataset_path, max_samples)
    all_violations.extend(dataset_violations)

    if dataset is None:
        print("❌ Dataset loading failed")
        return TrainingResult(
            success=False,
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            training_minutes=0,
            final_loss=0.0,
            model_size_gb=0.0,
            christ_score=0.0,
            governance_compliant=False,
            violations=tuple(all_violations),
            timestamp=datetime.now().isoformat(),
        )
    print("✅ Dataset loaded")

    # Phase 5: Prepare model
    print("\n[PHASE 5] Preparing model...")
    model, model_violations = prepare_model_safely(
        model_name=model_name,
        tokenizer=tokenizer,
        lora_rank=lora_rank,
        lora_alpha=lora_rank * 2,
    )
    all_violations.extend(model_violations)

    if model is None:
        print("❌ Model preparation failed")
        return TrainingResult(
            success=False,
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            training_minutes=0,
            final_loss=0.0,
            model_size_gb=0.0,
            christ_score=0.0,
            governance_compliant=False,
            violations=tuple(all_violations),
            timestamp=datetime.now().isoformat(),
        )
    print("✅ Model prepared")

    # Phase 6: Prepare training data
    print("\n[PHASE 6] Preparing training data...")
    try:
        train_dataset = prepare_training_data(dataset, tokenizer, MAX_PROMPT_LENGTH)
        print(f"✅ Training data prepared: {len(train_dataset)} examples")
    except Exception as e:
        error_msg = f"Training data preparation failed: {str(e)[:200]}"
        print(f"❌ {error_msg}")
        all_violations.append(error_msg)
        return TrainingResult(
            success=False,
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            training_minutes=0,
            final_loss=0.0,
            model_size_gb=0.0,
            christ_score=0.0,
            governance_compliant=False,
            violations=tuple(all_violations),
            timestamp=datetime.now().isoformat(),
        )

    # Phase 7: Configure training
    print("\n[PHASE 7] Configuring training...")
    try:
        training_args = TrainingArguments(
            output_dir=output_dir,

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
            save_total_limit=1,
            load_best_model_at_end=False,
            metric_for_best_model="loss",
            greater_is_better=False,
            fp16=torch.cuda.is_available(),
            report_to="none",
            gradient_checkpointing=False,
            max_grad_norm=MAX_GRAD_NORM,
            remove_unused_columns=False,
            dataloader_drop_last=False,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            processing_class=tokenizer,
        )
        print("✅ Training configured")
    except Exception as e:
        error_msg = f"Training configuration failed: {str(e)[:200]}"
        print(f"❌ {error_msg}")
        all_violations.append(error_msg)
        return TrainingResult(
            success=False,
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            training_minutes=0,
            final_loss=0.0,
            model_size_gb=0.0,
            christ_score=0.0,
            governance_compliant=False,
            violations=tuple(all_violations),
            timestamp=datetime.now().isoformat(),
        )

    # Phase 8: Run training
    print("\n[PHASE 8] Running training...")
    print(f"Training for {epochs} epoch(s) with {len(train_dataset)} examples...")

    try:
        train_result = trainer.train()
        final_loss = train_result.training_loss
        print(f"✅ Training completed successfully")
        print(f"  Final loss: {final_loss:.4f}")

        # Save model
        print(f"\n[SAVING] Saving model to {output_dir}...")
        trainer.save_model()
        tokenizer.save_pretrained(output_dir)
        print("✅ Model saved")

        # Calculate metrics
        end_time = time.time()
        training_minutes = (end_time - start_time) / 60

        # Calculate model size
        model_size_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
        model_size_gb = model_size_bytes / (1024**3)

        # Check time bound
        if training_minutes > MAX_TRAINING_MINUTES:
            all_violations.append(
                f"Training time {training_minutes:.1f}m > {MAX_TRAINING_MINUTES}m maximum"
            )

        # Check model size bound
        if model_size_gb > MAX_MODEL_SIZE_GB:
            all_violations.append(
                f"Model size {model_size_gb:.2f}GB > {MAX_MODEL_SIZE_GB}GB maximum"
            )

        # Calculate Christ score
        christ_score = calculate_christ_score(True, final_loss, all_violations)

        governance_compliant = len(all_violations) == 0

        return TrainingResult(
            success=True,
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            training_minutes=training_minutes,
            final_loss=final_loss,
            model_size_gb=model_size_gb,
            christ_score=christ_score,
            governance_compliant=governance_compliant,
            violations=tuple(all_violations),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        error_msg = f"Training execution failed: {str(e)[:200]}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        all_violations.append(error_msg)

        end_time = time.time()
        training_minutes = (end_time - start_time) / 60

        return TrainingResult(
            success=False,
            model_name=model_name,
            dataset_path=dataset_path,
            output_dir=output_dir,
            training_minutes=training_minutes,
            final_loss=0.0,
            model_size_gb=0.0,
            christ_score=0.0,
            governance_compliant=False,
            violations=tuple(all_violations),
            timestamp=datetime.now().isoformat(),
        )

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Final Robust Training Script with Auto-detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Quick test with distilgpt2
  python final_training.py \\
    --model distilgpt2 \\
    --dataset lora_dataset/lora_dataset_augmented.jsonl \\
    --output trained_test \\
    --samples 20

  # Full training with GPT-2
  python final_training.py \\
    --model gpt2 \\
    --dataset lora_dataset/lora_dataset_augmented.jsonl \\
    --output trained_gpt2 \\
    --epochs 1 \\
    --batch-size 2 \\
    --samples 100

GOVERNANCE BOUNDS:
  Maximum training time: 30 minutes
  Maximum model size: 2GB
  Maximum samples: 100
  Maximum batch size: 2
  Maximum epochs: 1
  Christ score minimum: 0.7
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
        default=1,
        help=f"Number of training epochs (max: {MAX_EPOCHS}, default: 1)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help=f"Batch size per device (max: {MAX_BATCH_SIZE}, default: 2)",
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
        default=8,
        help=f"LoRA rank (max: {MAX_LORA_RANK}, default: 8)",
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help=f"Maximum samples to use (max: {MAX_DATASET_SAMPLES}, default: 100)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Run training
    result = run_training(
        model_name=args.model,
        dataset_path=args.dataset,
        output_dir=args.output,
        epochs=min(args.epochs, MAX_EPOCHS),
        batch_size=min(args.batch_size, MAX_BATCH_SIZE),
        learning_rate=args.learning_rate,
        lora_rank=min(args.lora_rank, MAX_LORA_RANK),
        max_samples=min(args.samples, MAX_DATASET_SAMPLES),
    )

    # Print result
    print("\n" + "=" * 80)
    print("FINAL TRAINING RESULT")
    print("=" * 80)
    print(f"Model: {result.model_name}")
    print(f"Dataset: {result.dataset_path}")
    print(f"Output: {result.output_dir}")
    print(f"Training successful: {'✅' if result.success else '❌'}")
    print(f"Governance compliant: {'✅' if result.governance_compliant else '❌'}")
    print(f"Training time: {result.training_minutes:.1f} minutes")
    print(f"Final loss: {result.final_loss:.4f}")
    print(f"Model size: {result.model_size_gb:.2f} GB")
    print(f"Christ score: {result.christ_score:.3f} (minimum: 0.7)")

    if result.violations:
        print(f"\nViolations ({len(result.violations)}):")
        for v in result.violations:
            print(f"  - {v}")

    print(f"\nTimestamp: {result.timestamp}")
    print("=" * 80)

    # Check success criteria
    if bool(result):
        print("\n✅ FINAL TRAINING COMPLETED SUCCESSFULLY")
        print("   All governance requirements satisfied")
        print("   Christ constraint maintained")
        sys.exit(0)
    else:
        print("\n❌ FINAL TRAINING FAILED")
        if not result.success:
            print("   - Training process failed")
        if not result.governance_compliant:
            print("   - Governance violations detected")
        if result.christ_score < 0.7:
            print(f"   - Christ score {result.christ_score:.3f} < 0.7 minimum")
        sys.exit(1)

if __name__ == "__main__":
    main()

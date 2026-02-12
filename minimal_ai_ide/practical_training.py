#!/usr/bin/env python3
"""
PRACTICAL BOUNDED TRAINING SCRIPT
==================================

MAXIMAL STRICT CORPORATE GOVERNANCE PYTHON (MSGCP) COMPLIANT

DESIGN PRINCIPLES FOR CURRENT SETUP:
1. CPU-ONLY COMPATIBLE: Works without CUDA
2. MEMORY EFFICIENT: Fits in 4GB available RAM
3. TIME BOUNDED: Maximum 30 minutes training time
4. MINIMAL DEPENDENCIES: Avoids problematic packages
5. GOVERNANCE ENFORCED: All MSGCP principles maintained

HARDWARE CONSTRAINTS:
- CPU: i7-12650H (16 threads)
- RAM: 4.6GB available
- NO CUDA: PyTorch CPU-only
- Python 3.14 compatibility issues

TRAINING STRATEGY:
1. Tiny model: distilgpt2 (82M parameters)
2. Small dataset: 100 samples max
3. Short training: 1-2 epochs
4. LoRA efficient: <1% trainable parameters
5. Early stopping: Stop if loss plateaus
"""

from __future__ import annotations

import sys

print(f"[DEBUG] Python executable: {sys.executable}")
print(f"[DEBUG] Python version: {sys.version}")

import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import torch

    print(f"[DEBUG] PyTorch version: {torch.__version__}")
    print(f"[DEBUG] CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"[ERROR] PyTorch import failed: {e}")
    sys.exit(1)

from torch.utils.data import Dataset as TorchDataset

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        PreTrainedModel,
        PreTrainedTokenizer,
    )

    print("[DEBUG] Transformers imported successfully")
except ImportError as e:
    print(f"[ERROR] Transformers import failed: {e}")
    sys.exit(1)

# ============================================================================
# GOVERNANCE CONSTANTS - STRICT BOUNDS FOR CURRENT SETUP
# ============================================================================

MAX_TRAINING_MINUTES: int = 30  # 30 minutes maximum
MAX_MODEL_SIZE_MB: int = 500  # 500MB maximum
MAX_DATASET_SAMPLES: int = 100  # 100 samples maximum
MAX_BATCH_SIZE: int = 2  # Small batches for CPU
MAX_EPOCHS: int = 2  # Maximum 2 epochs
MAX_LORA_RANK: int = 8  # Small LoRA rank
MAX_PROMPT_LENGTH: int = 256  # Short prompts
MAX_GRAD_NORM: float = 1.0  # Gradient clipping

# Early stopping
PATIENCE: int = 5  # Stop if no improvement for 5 steps
MIN_LOSS_DELTA: float = 0.001  # Minimum improvement

# ============================================================================
# GOVERNANCE DATA STRUCTURES
# ============================================================================


@dataclass(frozen=True)
class TrainingBounds:
    """Training bounds for current hardware constraints"""

    max_minutes: int = MAX_TRAINING_MINUTES
    max_samples: int = MAX_DATASET_SAMPLES
    max_model_mb: int = MAX_MODEL_SIZE_MB
    max_batch_size: int = MAX_BATCH_SIZE
    max_epochs: int = MAX_EPOCHS


@dataclass
class TrainingMetrics:
    """Training metrics tracking"""

    start_time: float
    current_loss: float = 0.0
    best_loss: float = float("inf")
    steps_without_improvement: int = 0
    total_steps: int = 0
    samples_processed: int = 0

    def update_loss(self, loss: float) -> bool:
        """Update loss and check for improvement"""
        self.current_loss = loss
        self.total_steps += 1

        if loss < self.best_loss - MIN_LOSS_DELTA:
            self.best_loss = loss
            self.steps_without_improvement = 0
            return True  # Improvement
        else:
            self.steps_without_improvement += 1
            return False  # No improvement

    def should_stop(self) -> bool:
        """Check if training should stop early"""
        return self.steps_without_improvement >= PATIENCE

    def elapsed_minutes(self) -> float:
        """Get elapsed time in minutes"""
        return (time.time() - self.start_time) / 60

    def time_exceeded(self, max_minutes: int) -> bool:
        """Check if time limit exceeded"""
        return self.elapsed_minutes() > max_minutes


@dataclass(frozen=True)
class TrainingResult:
    """Training result with governance compliance"""

    success: bool
    model_path: str
    dataset_samples: int
    training_minutes: float
    final_loss: float
    model_size_mb: float
    governance_compliant: bool
    violations: Tuple[str, ...]
    timestamp: str


# ============================================================================
# MINIMAL DATASET - AVOIDS DATASETS LIBRARY
# ============================================================================


class SimplePopperianDataset(TorchDataset):
    """Simple dataset that loads JSONL directly without datasets library"""

    def __init__(self, file_path: str, max_samples: int = 100):
        self.examples: List[Dict[str, Any]] = []
        self.load_dataset(file_path, max_samples)

    def load_dataset(self, file_path: str, max_samples: int):
        """Load dataset from JSONL file"""
        print(f"[DEBUG] Loading dataset from: {file_path}")
        print(f"[DEBUG] Max samples: {max_samples}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        count = 0
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if count >= max_samples:
                    break
                if line.strip():
                    try:
                        example = json.loads(line)
                        # Validate required fields
                        if all(
                            k in example for k in ["instruction", "input", "output"]
                        ):
                            self.examples.append(example)
                            count += 1
                    except json.JSONDecodeError:
                        continue

        print(f"[DEBUG] Loaded {len(self.examples)} examples from {file_path}")
        if len(self.examples) == 0:
            print("[WARNING] No examples loaded!")

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, str]:
        example = self.examples[idx]
        return {
            "instruction": example["instruction"],
            "input": example["input"],
            "output": example["output"],
        }

    def format_for_training(self, idx: int) -> str:
        """Format example for training"""
        example = self.examples[idx]
        return (
            f"Instruction: {example['instruction']}\n"
            f"Input: {example['input']}\n"
            f"Output: {example['output']}\n\n"
        )


# ============================================================================
# MINIMAL TRAINING - NO TRAINER CLASS, MANUAL LOOP
# ============================================================================


class PracticalLoRATrainer:
    """Practical LoRA trainer for CPU-only constrained environment"""

    def __init__(self, model_name: str = "distilgpt2"):
        self.model_name = model_name
        self.model: Optional[PreTrainedModel] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None
        self.bounds = TrainingBounds()
        self.violations: List[str] = []

    def validate_setup(self, dataset_path: str, output_dir: str) -> bool:
        """Validate setup against governance bounds"""
        print("\n[VALIDATION] Checking setup...")
        print(f"[DEBUG] Dataset path: {dataset_path}")
        print(f"[DEBUG] Output dir: {output_dir}")
        print(f"[DEBUG] Model name: {self.model_name}")

        # Check dataset
        if not os.path.exists(dataset_path):
            print(f"[ERROR] Dataset not found: {dataset_path}")
            self.violations.append(f"Dataset not found: {dataset_path}")
            return False
        else:
            print(f"[DEBUG] Dataset exists: {os.path.getsize(dataset_path)} bytes")

        # Check output directory
        os.makedirs(output_dir, exist_ok=True)
        test_file = os.path.join(output_dir, ".write_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print("[DEBUG] Output directory is writable")
        except Exception as e:
            print(f"[ERROR] Cannot write to output directory: {e}")
            self.violations.append(f"Cannot write to output directory: {e}")
            return False

        # Check model size expectations
        if (
            "gpt2" not in self.model_name.lower()
            and "distil" not in self.model_name.lower()
        ):
            print(f"[WARNING] {self.model_name} may be too large for CPU training")

        print("[OK] Setup validated")
        return True

    def prepare_model(self) -> bool:
        """Prepare model with minimal LoRA-like adaptation"""
        print("\n[PREPARATION] Loading model...")
        print(f"[DEBUG] Model name: {self.model_name}")

        try:
            # Load tokenizer
            print("[DEBUG] Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            print(f"[DEBUG] Tokenizer loaded: {type(self.tokenizer).__name__}")

            # Load model
            print("[DEBUG] Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
            )
            print(f"[DEBUG] Model loaded: {type(self.model).__name__}")

            # Freeze most parameters (simplified LoRA)
            print("[DEBUG] Freezing parameters...")
            for param in self.model.parameters():
                param.requires_grad = False

            # Unfreeze last layer (simplified adaptation)
            if hasattr(self.model, "transformer") and hasattr(
                self.model.transformer, "h"
            ):
                print("[DEBUG] Unfreezing last transformer layer...")
                for param in self.model.transformer.h[-1].parameters():
                    param.requires_grad = True
            else:
                print(
                    "[WARNING] Could not find transformer.h, trying different architecture..."
                )
                # Try to unfreeze some other layer
                for name, param in self.model.named_parameters():
                    if "ln_f" in name or "lm_head" in name:  # Last layer norm or head
                        param.requires_grad = True
                        print(f"[DEBUG] Unfroze layer: {name}")

            # Count parameters
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(
                p.numel() for p in self.model.parameters() if p.requires_grad
            )

            print(f"[INFO] Total parameters: {total_params:,}")
            print(f"[INFO] Trainable parameters: {trainable_params:,}")
            print(f"[INFO] Trainable %: {100 * trainable_params / total_params:.2f}%")

            # Check model size
            model_size_bytes = sum(
                p.numel() * p.element_size() for p in self.model.parameters()
            )
            model_size_mb = model_size_bytes / (1024 * 1024)

            if model_size_mb > self.bounds.max_model_mb:
                print(
                    f"[ERROR] Model size {model_size_mb:.1f}MB exceeds maximum {self.bounds.max_model_mb}MB"
                )
                self.violations.append(
                    f"Model size {model_size_mb:.1f}MB exceeds maximum {self.bounds.max_model_mb}MB"
                )
                return False

            print(f"[OK] Model prepared: {model_size_mb:.1f}MB")
            return True

        except Exception as e:
            print(f"[ERROR] Model preparation failed: {e}")
            import traceback

            traceback.print_exc()
            self.violations.append(f"Model preparation failed: {e}")
            return False

    def train_manual(
        self,
        dataset_path: str,
        output_dir: str,
        learning_rate: float = 1e-4,
        batch_size: int = 2,
        epochs: int = 1,
    ) -> TrainingResult:
        """Manual training loop for maximum control"""

        print("\n" + "=" * 80)
        print("PRACTICAL BOUNDED TRAINING")
        print("=" * 80)
        print(f"Model: {self.model_name}")
        print(f"Dataset: {dataset_path}")
        print(f"Output: {output_dir}")
        print(
            f"Bounds: {self.bounds.max_samples} samples, {self.bounds.max_minutes} minutes"
        )
        print("=" * 80)

        # Validate setup
        if not self.validate_setup(dataset_path, output_dir):
            return self._create_result(False, dataset_path, output_dir, 0.0, 0.0)

        # Prepare model
        if not self.prepare_model():
            return self._create_result(False, dataset_path, output_dir, 0.0, 0.0)

        # Load dataset
        try:
            print("[DEBUG] Creating dataset...")
            dataset = SimplePopperianDataset(dataset_path, self.bounds.max_samples)
            if len(dataset) == 0:
                print("[ERROR] Dataset is empty or invalid")
                self.violations.append("Dataset is empty or invalid")
                return self._create_result(False, dataset_path, output_dir, 0.0, 0.0)
            print(f"[INFO] Using {len(dataset)} samples")

            # Show first example
            if len(dataset) > 0:
                first_example = dataset[0]
                print(f"[DEBUG] First example: {first_example}")
        except Exception as e:
            print(f"[ERROR] Dataset loading failed: {e}")
            import traceback

            traceback.print_exc()
            self.violations.append(f"Dataset loading failed: {e}")
            return self._create_result(False, dataset_path, output_dir, 0.0, 0.0)

        # Setup optimizer
        optimizer = torch.optim.Adam(
            [p for p in self.model.parameters() if p.requires_grad], lr=learning_rate
        )

        # Training metrics
        metrics = TrainingMetrics(start_time=time.time())

        print("\n[TRAINING] Starting manual training loop...")
        print(f"Batch size: {batch_size}, Epochs: {epochs}")

        try:
            for epoch in range(epochs):
                print(f"\n[EPOCH {epoch + 1}/{epochs}]")

                # Simple batching
                for batch_start in range(0, len(dataset), batch_size):
                    batch_end = min(batch_start + batch_size, len(dataset))

                    # Check bounds
                    if metrics.time_exceeded(self.bounds.max_minutes):
                        print(
                            f"[STOP] Time limit reached: {metrics.elapsed_minutes():.1f} minutes"
                        )
                        break

                    if metrics.should_stop():
                        print(
                            f"[STOP] Early stopping: no improvement for {PATIENCE} steps"
                        )
                        break

                    # Prepare batch
                    batch_texts = []
                    for i in range(batch_start, batch_end):
                        batch_texts.append(dataset.format_for_training(i))

                    # Tokenize
                    inputs = self.tokenizer(
                        batch_texts,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=MAX_PROMPT_LENGTH,
                    )

                    # Labels for causal LM
                    inputs["labels"] = inputs["input_ids"].clone()

                    # Forward pass
                    optimizer.zero_grad()
                    outputs = self.model(**inputs)
                    loss = outputs.loss

                    # Backward pass
                    loss.backward()

                    # Gradient clipping
                    torch.nn.utils.clip_grad_norm_(
                        [p for p in self.model.parameters() if p.requires_grad],
                        MAX_GRAD_NORM,
                    )

                    optimizer.step()

                    # Update metrics
                    metrics.update_loss(loss.item())
                    metrics.samples_processed += len(batch_texts)

                    # Log progress
                    if metrics.total_steps % 5 == 0:
                        elapsed = metrics.elapsed_minutes()
                        print(
                            f"  Step {metrics.total_steps}: "
                            f"loss={loss.item():.4f}, "
                            f"time={elapsed:.1f}m, "
                            f"samples={metrics.samples_processed}"
                        )

                # Check stopping conditions
                if (
                    metrics.time_exceeded(self.bounds.max_minutes)
                    or metrics.should_stop()
                ):
                    break

            # Training completed
            print(f"\n[TRAINING] Completed in {metrics.elapsed_minutes():.1f} minutes")
            print(f"  Final loss: {metrics.current_loss:.4f}")
            print(f"  Best loss: {metrics.best_loss:.4f}")
            print(f"  Total steps: {metrics.total_steps}")
            print(f"  Samples processed: {metrics.samples_processed}")

            # Save model
            print(f"\n[SAVING] Saving model to {output_dir}...")
            self.model.save_pretrained(output_dir)
            self.tokenizer.save_pretrained(output_dir)
            print("[OK] Model saved")

            # Calculate final model size
            model_size_bytes = sum(
                p.numel() * p.element_size() for p in self.model.parameters()
            )
            model_size_mb = model_size_bytes / (1024 * 1024)

            return self._create_result(
                success=True,
                model_path=output_dir,
                dataset_samples=len(dataset),
                training_minutes=metrics.elapsed_minutes(),
                final_loss=metrics

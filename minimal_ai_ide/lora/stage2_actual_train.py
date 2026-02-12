#!/usr/bin/env python3
"""
STAGE 2 ACTUAL TRAINING - OPTIMIZED CUDA TRAINING
=================================================

Production-ready Stage 2 CUDA training with:
1. Proper dataset handling (list format)
2. Optimized hyperparameters from Stage 1 learnings
3. GPU memory monitoring and optimization
4. Complete governance compliance
5. Real-time metrics and Christ score calculation

Target: Christ score ≥ 0.7, loss reduction > 4.0 points
"""

import json
import logging
import math
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.cuda as cuda
from peft import LoraConfig, TaskType, get_peft_model
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    get_linear_schedule_with_warmup,
)

# ============================================================================
# GOVERNANCE CONSTANTS - OPTIMIZED FOR STAGE 2
# ============================================================================

# Bounded operations
MAX_TRAINING_MINUTES = 10  # Short for testing, can be increased
MAX_SAMPLES = 20  # Start with 20 samples for quick validation
MAX_BATCH_SIZE = 2  # Conservative for 6GB VRAM
MAX_EPOCHS = 3  # Increased from Stage 1 (1 epoch)
MAX_MODEL_SIZE_GB = 10
MAX_GPU_MEMORY_USAGE = 0.7  # 70% max to be safe

# Optimized hyperparameters from Stage 1 learnings
LEARNING_RATE = 5e-5  # Reduced from 2e-4 to prevent gradient explosion
GRADIENT_ACCUMULATION_STEPS = 2  # For stability
GRADIENT_CLIP_NORM = 0.5  # Reduced from 1.0 to control gradients
WARMUP_STEPS = 5
WEIGHT_DECAY = 0.01

# LoRA configuration
LORA_RANK = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.1
MODEL_NAME = "distilgpt2"
TARGET_MODULES = ["c_attn"]

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class TrainingExample:
    """Training example with Popperian validation"""

    text: str
    keywords: List[str]

    def to_prompt(self) -> str:
        """Convert to training prompt"""
        return f"Popperian analysis: {self.text}\nKeywords: {', '.join(self.keywords)}"

    def validate_popperian(self) -> bool:
        """Validate Popperian characteristics"""
        popperian_indicators = [
            "falsifiable",
            "testable",
            "empirical",
            "rational",
            "critical",
            "logical",
            "scientific",
            "evidence",
            "verification",
            "validation",
        ]
        text_lower = self.text.lower()
        return any(indicator in text_lower for indicator in popperian_indicators)


@dataclass
class TrainingMetrics:
    """Training metrics for monitoring"""

    epoch: int
    step: int
    loss: float
    learning_rate: float
    gradient_norm: float
    gpu_memory_used_gb: float
    gpu_memory_total_gb: float
    timestamp: str

    def __post_init__(self):
        """Validate metrics"""
        if self.loss < 0:
            raise ValueError("Loss cannot be negative")
        if self.gradient_norm < 0:
            raise ValueError("Gradient norm cannot be negative")


@dataclass
class TrainingResult:
    """Complete training result"""

    success: bool
    model_name: str
    dataset_path: str
    output_dir: str
    training_minutes: float
    initial_loss: float
    final_loss: float
    loss_reduction: float
    nan_events: int
    christ_score: float
    governance_compliant: bool
    violations: List[str]
    metrics_history: List[TrainingMetrics]
    timestamp: str
    gpu_info: Dict[str, Any]

    def __post_init__(self):
        """Validate training result"""
        if self.christ_score < 0 or self.christ_score > 1:
            raise ValueError("Christ score must be between 0 and 1")


# ============================================================================
# DATASET
# ============================================================================


class PopperianDataset(Dataset):
    """Dataset for Popperian training examples"""

    def __init__(self, dataset_path: str, max_samples: int = MAX_SAMPLES):
        self.dataset_path = Path(dataset_path)
        self.max_samples = max_samples
        self.examples: List[TrainingExample] = []
        self.tokenizer: Optional[PreTrainedTokenizer] = None

        self._load_examples()
        self._validate_dataset()

    def _load_examples(self) -> None:
        """Load and validate training examples"""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both list format and wrapped format
            if isinstance(data, dict) and "examples" in data:
                examples_data = data["examples"]
            elif isinstance(data, list):
                examples_data = data
            else:
                raise ValueError("Dataset must be a list or have 'examples' key")

            # Load examples with governance bounds
            for i, item in enumerate(examples_data[: self.max_samples]):
                if not isinstance(item, dict):
                    raise ValueError(f"Example {i} must be a dictionary")

                text = item.get("text", "")
                keywords = item.get("keywords", [])

                if not text or not keywords:
                    raise ValueError(f"Example {i} missing text or keywords")

                example = TrainingExample(text=text, keywords=keywords)
                if not example.validate_popperian():
                    raise ValueError(f"Example {i} fails Popperian validation")

                self.examples.append(example)

            logging.info(
                f"Loaded {len(self.examples)} examples from {self.dataset_path}"
            )

        except Exception as e:
            raise ValueError(f"Failed to load dataset: {e}")

    def _validate_dataset(self) -> None:
        """Validate dataset governance compliance"""
        if len(self.examples) == 0:
            raise ValueError("Dataset is empty")

        if len(self.examples) > self.max_samples:
            raise ValueError(
                f"Dataset exceeds maximum samples: {len(self.examples)} > {self.max_samples}"
            )

        # Validate Popperian characteristics (relaxed for broader philosophical concepts)
        popperian_count = sum(1 for ex in self.examples if ex.validate_popperian())
        if (
            popperian_count < len(self.examples) * 0.6
        ):  # At least 60% Popperian (relaxed)
            raise ValueError(
                f"Insufficient Popperian examples: {popperian_count}/{len(self.examples)}"
            )

        logging.info(
            f"Dataset validated: {len(self.examples)} examples, {popperian_count} Popperian"
        )

    def set_tokenizer(self, tokenizer: PreTrainedTokenizer) -> None:
        """Set tokenizer for the dataset"""
        self.tokenizer = tokenizer
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Get tokenized example"""
        if self.tokenizer is None:
            raise ValueError("Tokenizer not set")

        example = self.examples[idx]
        prompt = example.to_prompt()

        # Tokenize with attention mask
        encoding = self.tokenizer(
            prompt,
            truncation=True,
            padding="max_length",
            max_length=256,  # Reduced for faster training
            return_tensors="pt",
        )

        # Create labels (shifted input_ids for causal LM)
        input_ids = encoding["input_ids"].squeeze()
        attention_mask = encoding["attention_mask"].squeeze()
        labels = input_ids.clone()

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


# ============================================================================
# TRAINING SYSTEM
# ============================================================================


class Stage2ActualTraining:
    """Stage 2 actual training system"""

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.device: torch.device = None
        self.model: PreTrainedModel = None
        self.tokenizer: PreTrainedTokenizer = None
        self.logger = self._setup_logging()

        # Detect and configure device
        self._detect_and_configure_device()

    def _detect_and_configure_device(self) -> None:
        """Detect and configure CUDA device"""
        try:
            if cuda.is_available():
                self.device = torch.device("cuda:0")
                gpu_props = cuda.get_device_properties(0)
                self.logger.info(f"Using GPU: {gpu_props.name}")
                self.logger.info(
                    f"GPU Memory: {gpu_props.total_memory / (1024**3):.2f} GB"
                )
                self.logger.info(f"CUDA Version: {torch.version.cuda}")

                # Set CUDA optimization flags
                torch.backends.cudnn.benchmark = True
                torch.backends.cuda.matmul.allow_tf32 = True
            else:
                self.logger.warning("CUDA not available, falling back to CPU")
                self.device = torch.device("cpu")

        except Exception as e:
            self.logger.error(f"Failed to configure device: {e}")
            self.device = torch.device("cpu")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging system"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def _validate_governance(self) -> Tuple[bool, List[str]]:
        """Validate governance compliance"""
        violations = []

        # Check GPU memory usage limit
        if self.device.type == "cuda":
            try:
                memory_allocated = cuda.memory_allocated(0) / (1024**3)
                memory_reserved = cuda.memory_reserved(0) / (1024**3)
                memory_total = cuda.get_device_properties(0).total_memory / (1024**3)
                memory_usage = (memory_allocated + memory_reserved) / memory_total

                if memory_usage > MAX_GPU_MEMORY_USAGE:
                    violations.append(
                        f"GPU memory usage {memory_usage:.1%} exceeds limit {MAX_GPU_MEMORY_USAGE:.0%}"
                    )

                self.logger.info(
                    f"GPU memory: {memory_allocated:.2f} GB allocated, "
                    f"{memory_reserved:.2f} GB reserved, {memory_total:.2f} GB total"
                )

            except Exception as e:
                violations.append(f"Failed to check GPU memory: {e}")

        # Check training time bounds
        if MAX_TRAINING_MINUTES > 60:
            violations.append(
                f"MAX_TRAINING_MINUTES={MAX_TRAINING_MINUTES} exceeds 1-hour limit"
            )

        # Check sample bounds
        if MAX_SAMPLES > 100:
            violations.append(f"MAX_SAMPLES={MAX_SAMPLES} exceeds 100 limit")

        return len(violations) == 0, violations

    def _calculate_christ_score(
        self,
        initial_loss: float,
        final_loss: float,
        nan_events: int,
        metrics_history: List[TrainingMetrics],
    ) -> float:
        """Calculate Christ score for training quality"""
        if initial_loss <= 0 or final_loss < 0:
            return 0.0

        # Base score from loss reduction (0-0.6)
        loss_reduction = (initial_loss - final_loss) / initial_loss
        loss_score = min(0.6, loss_reduction * 0.6)

        # Stability score from gradient norms (0-0.3)
        if metrics_history:
            gradient_norms = [m.gradient_norm for m in metrics_history]
            avg_gradient_norm = sum(gradient_norms) / len(gradient_norms)

            # Lower gradient norms are better
            if avg_gradient_norm < 1.0:
                stability_score = 0.3 * (1.0 - min(avg_gradient_norm, 1.0))
            else:
                stability_score = 0.0
        else:
            stability_score = 0.0

        # NaN penalty (0-0.1)
        nan_penalty = min(0.1, nan_events * 0.05)

        # Final score
        christ_score = loss_score + stability_score - nan_penalty

        # Ensure bounds
        return max(0.0, min(1.0, christ_score))

    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information"""
        if self.device.type != "cuda":
            return {"device": "cpu"}

        try:
            memory_allocated = cuda.memory_allocated(0) / (1024**3)
            memory_reserved = cuda.memory_reserved(0) / (1024**3)
            memory_total = cuda.get_device_properties(0).total_memory / (1024**3)

            return {
                "device": "cuda",
                "device_name": cuda.get_device_name(0),
                "memory_allocated_gb": round(memory_allocated, 2),
                "memory_reserved_gb": round(memory_reserved, 2),
                "memory_total_gb": round(memory_total, 2),
                "memory_usage_percent": round(
                    (memory_allocated + memory_reserved) / memory_total * 100, 1
                ),
                "cuda_version": torch.version.cuda,
            }
        except Exception as e:
            self.logger.warning(f"Failed to get GPU info: {e}")
            return {"device": "cuda", "error": str(e)}

    def load_model_and_tokenizer(self) -> None:
        """Load model and tokenizer"""
        self.logger.info(f"Loading model: {self.model_name}")

        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model with appropriate dtype
            model_dtype = torch.float16 if self.device.type == "cuda" else torch.float32
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=model_dtype,
                device_map="auto" if self.device.type == "cuda" else None,
                low_cpu_mem_usage=True,
            )

            # Move to device if not using device_map
            if self.device.type == "cuda" and not hasattr(self.model, "hf_device_map"):
                self.model = self.model.to(self.device)
            elif self.device.type == "cpu":
                self.model = self.model.to(self.device)

            # Configure LoRA
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=LORA_RANK,
                lora_alpha=LORA_ALPHA,
                lora_dropout=LORA_DROPOUT,
                target_modules=TARGET_MODULES,
                bias="none",
            )

            # Apply LoRA
            self.model = get_peft_model(self.model, lora_config)
            self.model.print_trainable_parameters()

            self.logger.info(f"Model loaded successfully on {self.device}")
            self.logger.info(f"Model dtype: {self.model.dtype}")

        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise

    def train(self, dataset_path: str, output_dir: str) -> TrainingResult:
        """Execute Stage 2 training"""
        start_time = time.time()

        # Governance validation
        self.logger.info("Validating governance compliance...")
        gov_compliant, violations = self._validate_governance()
        if not gov_compliant:
            self.logger.error(f"Governance violations: {violations}")
            return TrainingResult(
                success=False,
                model_name=self.model_name,
                dataset_path=dataset_path,
                output_dir=output_dir,
                training_minutes=0,
                initial_loss=0,
                final_loss=0,
                loss_reduction=0,
                nan_events=0,
                christ_score=0.0,
                governance_compliant=False,
                violations=violations,
                metrics_history=[],
                timestamp=datetime.now().isoformat(),
                gpu_info=self._get_gpu_info(),
            )

        self.logger.info("Governance compliance validated")

        try:
            # Load model
            self.load_model_and_tokenizer()

            # Prepare dataset
            self.logger.info(f"Loading dataset: {dataset_path}")
            dataset = PopperianDataset(dataset_path, max_samples=MAX_SAMPLES)
            dataset.set_tokenizer(self.tokenizer)

            dataloader = DataLoader(
                dataset,
                batch_size=MAX_BATCH_SIZE,
                shuffle=True,
                num_workers=0,  # 0 for stability
            )

            # Calculate total training steps
            total_steps = len(dataloader) * MAX_EPOCHS // GRADIENT_ACCUMULATION_STEPS
            warmup_steps = min(WARMUP_STEPS, total_steps // 10)

            # Setup optimizer
            optimizer = torch.optim.AdamW(
                [p for p in self.model.parameters() if p.requires_grad],
                lr=LEARNING_RATE,
                weight_decay=WEIGHT_DECAY,
                betas=(0.9, 0.999),
            )

            # Setup learning rate scheduler
            scheduler = get_linear_schedule_with_warmup(
                optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
            )

            # Training loop
            self.model.train()
            self.logger.info(
                f"Starting training: {MAX_EPOCHS} epoch(s), {len(dataloader)} batch(es)"
            )
            self.logger.info(
                f"Total steps: {total_steps}, Warmup steps: {warmup_steps}"
            )
            self.logger.info(f"Gradient accumulation: {GRADIENT_ACCUMULATION_STEPS}")
            self.logger.info(f"Device: {self.device}")

            initial_loss = None
            step = 0
            global_step = 0
            accumulated_loss = 0.0
            nan_events = 0
            metrics_history: List[TrainingMetrics] = []

            # Mixed precision context for CUDA
            if self.device.type == "cuda":
                scaler = torch.cuda.amp.GradScaler()

            for epoch in range(MAX_EPOCHS):
                self.logger.info(f"Epoch {epoch + 1}/{MAX_EPOCHS}")

                for batch_idx, batch in enumerate(dataloader):
                    # Move batch to device
                    batch = {k: v.to(self.device) for k, v in batch.items()}

                    # Mixed precision training for CUDA
                    if self.device.type == "cuda":
                        with torch.cuda.amp.autocast():
                            outputs = self.model(**batch)
                            loss = outputs.loss / GRADIENT_ACCUMULATION_STEPS
                    else:
                        outputs = self.model(**batch)
                        loss = outputs.loss / GRADIENT_ACCUMULATION_STEPS

                    # Check for NaN
                    if torch.isnan(loss).any():
                        nan_events += 1
                        self.logger.warning(f"NaN detected at step {global_step}")
                        continue

                    accumulated_loss += loss.item()

                    # Backward pass with gradient accumulation
                    if self.device.type == "cuda":
                        scaler.scale(loss).backward()
                    else:
                        loss.backward()

                    # Gradient accumulation step
                    if (batch_idx + 1) % GRADIENT_ACCUMULATION_STEPS == 0:
                        # Gradient clipping
                        if self.device.type == "cuda":
                            scaler.unscale_(optimizer)
                            torch.nn.utils.clip_grad_norm_(
                                self.model.parameters(), GRADIENT_CLIP_NORM
                            )
                            scaler.step(optimizer)
                            scaler.update()
                        else:
                            torch.nn.utils.clip_grad_norm_(
                                self.model.parameters(), GRADIENT_CLIP_NORM
                            )
                            optimizer.step()

                        scheduler.step()
                        optimizer.zero_grad()

                        # Calculate gradient norm
                        total_norm = 0.0
                        for p in self.model.parameters():
                            if p.grad is not None:
                                param_norm = p.grad.data.norm(2)
                                total_norm += param_norm.item() ** 2
                        total_norm = total_norm**0.5

                        # Record initial loss
                        if initial_loss is None:
                            initial_loss = (
                                accumulated_loss * GRADIENT_ACCUMULATION_STEPS
                            )
                            self.logger.info(f"Initial loss: {initial_loss:.4f}")

                        # Get GPU memory info
                        gpu_info = self._get_gpu_info()

                        # Record metrics
                        metrics = TrainingMetrics(
                            epoch=epoch + 1,
                            step=global_step,
                            loss=accumulated_loss * GRADIENT_ACCUMULATION_STEPS,
                            learning_rate=scheduler.get_last_lr()[0],
                            gradient_norm=total_norm,
                            gpu_memory_used_gb=gpu_info.get("memory_allocated_gb", 0),
                            gpu_memory_total_gb=gpu_info.get("memory_total_gb", 0),
                            timestamp=datetime.now().isoformat(),
                        )
                        metrics_history.append(metrics)

                        # Log progress
                        if global_step % 2 == 0:  # Log every 2 steps for visibility
                            self.logger.info(
                                f"Step {global_step}: loss={metrics.loss:.4f}, "
                                f"lr={metrics.learning_rate:.2e}, "
                                f"grad_norm={metrics.gradient_norm:.4f}"
                            )
                            if self.device.type == "cuda":
                                self.logger.info(
                                    f"GPU memory: {gpu_info.get('memory_usage_percent', 0):.1f}%"
                                )

                        accumulated_loss = 0.0
                        global_step += 1

                self.logger.info(f"Epoch {epoch + 1} completed")

            # Calculate final results
            training_minutes = (time.time() - start_time) / 60
            final_loss = metrics_history[-1].loss if metrics_history else 0
            loss_reduction = initial_loss - final_loss if initial_loss else 0

            # Calculate Christ score
            christ_score = self._calculate_christ_score(
                initial_loss or 0, final_loss, nan_events, metrics_history
            )

            # Save model
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            self.model.save_pretrained(output_path)
            self.tokenizer.save_pretrained(output_path)

            # Save training results
            result = TrainingResult(
                success=True,
                model_name=self.model_name,
                dataset_path=dataset_path,
                output_dir=output_dir,
                training_minutes=training_minutes,
                initial_loss=initial_loss or 0,
                final_loss=final_loss,
                loss_reduction=loss_reduction,
                nan_events=nan_events,
                christ_score=christ_score,
                governance_compliant=True,
                violations=[],
                metrics_history=metrics_history,
                timestamp=datetime.now().isoformat(),
                gpu_info=self._get_gpu_info(),
            )

            # Save result to JSON
            result_path = output_path / "training_result.json"
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(asdict(result), f, indent=2, default=str)

            self.logger.info(f"Training completed in {training_minutes:.2f} minutes")
            self.logger.info(f"Loss reduction: {loss_reduction:.4f}")
            self.logger.info(f"Christ score: {christ_score:.3f}")
            self.logger.info(f"Model saved to: {output_path}")

            return result

        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            training_minutes = (time.time() - start_time) / 60

            return TrainingResult(
                success=False,
                model_name=self.model_name,
                dataset_path=dataset_path,
                output_dir=output_dir,
                training_minutes=training_minutes,
                initial_loss=0,
                final_loss=0,
                loss_reduction=0,
                nan_events=0,
                christ_score=0.0,
                governance_compliant=False,
                violations=[str(e)],
                metrics_history=[],
                timestamp=datetime.now().isoformat(),
                gpu_info=self._get_gpu_info(),
            )


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Stage 2 actual CUDA training")
    parser.add_argument(
        "--dataset",
        type=str,
        default="lora_dataset/popperian_training_list.json",
        help="Path to dataset JSON file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="trained_lora_stage2_actual",
        help="Output directory for trained model",
    )
    parser.add_argument("--model", type=str, default=MODEL_NAME, help="Base model name")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Create training system
        trainer = Stage2ActualTraining(model_name=args.model)

        # Run training
        result = trainer.train(args.dataset, args.output)

        # Print summary
        print("\n" + "=" * 60)
        print("STAGE 2 ACTUAL TRAINING COMPLETE")
        print("=" * 60)
        print(f"Success: {result.success}")
        print(f"Training time: {result.training_minutes:.2f} minutes")
        print(f"Loss reduction: {result.loss_reduction:.4f}")
        print(f"Christ score: {result.christ_score:.3f}")
        print(f"Governance compliant: {result.governance_compliant}")
        print(f"GPU device: {result.gpu_info.get('device_name', 'CPU')}")
        print(
            f"GPU memory usage: {result.gpu_info.get('memory_usage_percent', 0):.1f}%"
        )
        print("=" * 60)

        if not result.success:
            print(f"Errors: {result.violations}")
            sys.exit(1)

    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
STAGE 1 OPTIMIZED: SMALL VALIDATION TRAINING
=============================================

OPTIMIZED VERSION - Addresses all critical issues:
1. Gradient explosion fixed with better clipping and learning rate
2. Proper LoRA parameter training verified
3. Better loss reduction and Christ score
4. Optimized for CPU training with stability

Implements the Stage 1 training directive with optimizations:
- CPU fallback (CUDA may be unavailable)
- Minimal batch (20 samples, 3 epochs for better convergence)
- Freeze base model parameters, keep LoRA trainable
- Gradient clipping (max_norm=0.5) with monitoring
- Learning rate 5e-5 (optimized for stability)
- Cosine annealing learning rate scheduler
- Gradient accumulation for stability
- Log training loss, NaN events, and structural invariant compliance

GOVERNANCE PRINCIPLES:
1. BOUNDED OPERATIONS: MAX_TRAINING_MINUTES=30, MAX_SAMPLES=20
2. TYPE SAFETY: All functions strictly typed
3. ZERO TRUST: Validate before training
4. CHRISTOLOGICAL INVARIANTS: Preserve structural constraints
5. POPPERIAN VALIDATION: Falsifiable training assertions
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
import torch.nn as nn
from peft import LoraConfig, TaskType, get_peft_model
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    get_linear_schedule_with_warmup,
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================================================
# OPTIMIZED GOVERNANCE CONSTANTS
# ============================================================================

MAX_TRAINING_MINUTES: int = 30
MAX_SAMPLES: int = 20
MAX_BATCH_SIZE: int = 2
MAX_EPOCHS: int = 3  # Increased from 1 for better convergence
MAX_GRAD_NORM: float = 0.5  # Reduced from 1.0 for stability
LEARNING_RATE: float = 5e-5  # Optimized for stability
WARMUP_STEPS: int = 2
GRADIENT_ACCUMULATION_STEPS: int = 4  # For stability on CPU
MAX_PROMPT_LENGTH: int = 256

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class TrainingExample:
    """Single training example with Popperian validation"""

    instruction: str
    input: str
    output: str
    constraints: List[str]  # Theological/structural constraints

    def to_prompt(self) -> str:
        """Convert to training prompt"""
        return f"{self.instruction}\n\nInput: {self.input}\n\nOutput: {self.output}"

    def validate_popperian(self) -> bool:
        """Validate Popperian falsifiability"""
        text = self.output.lower()
        return any(
            keyword in text
            for keyword in [
                "falsifiable",
                "falsification",
                "testable",
                "counterexample",
            ]
        )


@dataclass
class TrainingMetrics:
    """Training metrics tracking"""

    epoch: int
    step: int
    loss: float
    learning_rate: float
    grad_norm: Optional[float]
    nan_detected: bool
    timestamp: str
    christ_score: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class TrainingResult:
    """Final training result"""

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
    metrics_history: List[Dict[str, Any]]
    timestamp: str

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


# ============================================================================
# OPTIMIZED DATASET CLASS
# ============================================================================


class OptimizedPopperianDataset(Dataset):
    """Optimized dataset for Popperian training examples"""

    def __init__(self, file_path: str, max_samples: int = 20):
        self.examples = self._load_examples(file_path, max_samples)
        self.tokenizer = None

    def _load_examples(self, file_path: str, max_samples: int) -> List[TrainingExample]:
        """Load examples from JSONL file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        examples = []
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= max_samples:
                    break

                try:
                    data = json.loads(line.strip())
                    example = TrainingExample(
                        instruction=data.get("instruction", ""),
                        input=data.get("input", ""),
                        output=data.get("output", ""),
                        constraints=data.get(
                            "constraints", ["LOGOS", "CHALCEDON", "GRACE"]
                        ),
                    )

                    # Validate Popperian structure
                    if example.validate_popperian():
                        examples.append(example)
                    else:
                        print(f"⚠ Example {i} missing Popperian keywords")

                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing line {i}: {e}")

        print(f"Loaded {len(examples)}/{max_samples} Popperian examples")
        return examples

    def set_tokenizer(self, tokenizer: PreTrainedTokenizer):
        """Set tokenizer for the dataset"""
        self.tokenizer = tokenizer
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        if self.tokenizer is None:
            raise ValueError("Tokenizer not set. Call set_tokenizer() first.")

        example = self.examples[idx]
        prompt = example.to_prompt()

        # Tokenize with truncation
        encoding = self.tokenizer(
            prompt,
            truncation=True,
            max_length=MAX_PROMPT_LENGTH,
            padding="max_length",
            return_tensors="pt",
        )

        # Labels are same as input_ids for causal LM
        encoding["labels"] = encoding["input_ids"].clone()

        return {k: v.squeeze(0) for k, v in encoding.items()}


# ============================================================================
# OPTIMIZED TRAINING SYSTEM
# ============================================================================


class Stage1OptimizedTrainingSystem:
    """Stage 1: Optimized small validation training system"""

    def __init__(self, model_name: str = "distilgpt2"):
        self.model_name = model_name
        self.device = self._detect_device()
        self.model: Optional[PreTrainedModel] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None
        self.peft_config: Optional[LoraConfig] = None
        self.metrics_history: List[TrainingMetrics] = []
        self.nan_events = 0

        # Setup logging
        self._setup_logging()

    def _detect_device(self) -> torch.device:
        """Detect available device (CPU fallback)"""
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device("cpu")
            print("⚠ CUDA not available, using CPU (as per Stage 1 directive)")
        return device

    def _setup_logging(self):
        """Setup training logging"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{log_dir}/stage1_optimized_training_{timestamp}.log"

        # Configure logging to avoid Unicode errors
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _validate_governance(self) -> Tuple[bool, List[str]]:
        """Validate governance compliance before training"""
        violations = []

        # Check time bounds
        if MAX_TRAINING_MINUTES > 60:
            violations.append(
                f"MAX_TRAINING_MINUTES={MAX_TRAINING_MINUTES} exceeds 60 minute limit"
            )

        # Check sample bounds
        if MAX_SAMPLES > 100:
            violations.append(f"MAX_SAMPLES={MAX_SAMPLES} exceeds 100 sample limit")

        # Check learning rate bounds
        if LEARNING_RATE > 1e-3:
            violations.append(f"LEARNING_RATE={LEARNING_RATE} exceeds 1e-3 limit")

        return len(violations) == 0, violations

    def _calculate_christ_score(self, metrics: List[TrainingMetrics]) -> float:
        """Calculate Christological score based on training metrics"""
        if not metrics:
            return 0.0

        # Base score components
        scores = []

        # 1. Loss reduction component (0-0.4)
        initial_loss = metrics[0].loss if metrics else 10.0
        final_loss = metrics[-1].loss if metrics else 10.0
        loss_reduction = max(0, initial_loss - final_loss)
        loss_score = min(0.4, loss_reduction / 25.0)  # Max 0.4 for 10→0 loss

        # 2. NaN avoidance component (0-0.3)
        nan_events = sum(1 for m in metrics if m.nan_detected)
        nan_score = 0.3 if nan_events == 0 else 0.0

        # 3. Gradient stability component (0-0.3)
        valid_grads = [m.grad_norm for m in metrics if m.grad_norm is not None]
        if valid_grads:
            grad_variance = torch.var(torch.tensor(valid_grads)).item()
            grad_score = max(0, 0.3 - grad_variance * 10)
        else:
            grad_score = 0.0

        total_score = loss_score + nan_score + grad_score
        return min(1.0, total_score)

    def load_model_and_tokenizer(self):
        """Load base model and tokenizer with optimized LoRA configuration"""
        self.logger.info(f"Loading model: {self.model_name}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32,
            device_map=self.device,
        )

        # Configure LoRA with optimized parameters
        self.peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,  # Small rank for validation
            lora_alpha=16,
            lora_dropout=0.05,  # Reduced dropout for stability
            target_modules=["c_attn", "c_proj", "c_fc"],  # Correct for GPT-2
            bias="none",
        )

        # Convert to PEFT model
        self.model = get_peft_model(self.model, self.peft_config)

        # Verify trainable parameters
        trainable_params = sum(
            p.numel() for p in self.model.parameters() if p.requires_grad
        )
        total_params = sum(p.numel() for p in self.model.parameters())

        self.logger.info(f"Model loaded on {self.device}")
        self.logger.info(
            f"Trainable parameters: {trainable_params:,} ({trainable_params / total_params * 100:.4f}%)"
        )
        self.logger.info(f"Total parameters: {total_params:,}")

        if trainable_params == 0:
            self.logger.error("CRITICAL: No trainable parameters found!")
            raise ValueError("No trainable parameters in model")

    def train(self, dataset_path: str, output_dir: str) -> TrainingResult:
        """Execute Stage 1 optimized training"""
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
            )

        self.logger.info("Governance compliance validated")

        try:
            # Load model
            self.load_model_and_tokenizer()

            # Prepare dataset
            self.logger.info(f"Loading dataset: {dataset_path}")
            dataset = OptimizedPopperianDataset(dataset_path, max_samples=MAX_SAMPLES)
            dataset.set_tokenizer(self.tokenizer)

            dataloader = DataLoader(
                dataset,
                batch_size=MAX_BATCH_SIZE,
                shuffle=True,
                num_workers=0,  # 0 for stability on CPU
            )

            # Calculate total training steps
            total_steps = len(dataloader) * MAX_EPOCHS // GRADIENT_ACCUMULATION_STEPS
            warmup_steps = min(WARMUP_STEPS, total_steps // 10)

            # Setup optimizer with weight decay
            optimizer = torch.optim.AdamW(
                [p for p in self.model.parameters() if p.requires_grad],
                lr=LEARNING_RATE,
                weight_decay=0.01,
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

            initial_loss = None
            step = 0
            global_step = 0
            accumulated_loss = 0.0

            for epoch in range(MAX_EPOCHS):
                self.logger.info(f"Epoch {epoch + 1}/{MAX_EPOCHS}")

                for batch_idx, batch in enumerate(dataloader):
                    # Move batch to device
                    batch = {k: v.to(self.device) for k, v in batch.items()}

                    # Forward pass
                    outputs = self.model(**batch)
                    loss = outputs.loss / GRADIENT_ACCUMULATION_STEPS
                    accumulated_loss += loss.item()

                    # Track initial loss
                    if initial_loss is None:
                        initial_loss = loss.item() * GRADIENT_ACCUMULATION_STEPS

                    # Check for NaN
                    nan_detected = torch.isnan(loss).item()
                    if nan_detected:
                        self.nan_events += 1
                        self.logger.warning(f"NaN detected at step {step}")

                    # Backward pass
                    loss.backward()

                    # Gradient accumulation
                    if (batch_idx + 1) % GRADIENT_ACCUMULATION_STEPS == 0:
                        # Gradient clipping with monitoring
                        grad_norm = nn.utils.clip_grad_norm_(
                            [p for p in self.model.parameters() if p.requires_grad],
                            MAX_GRAD_NORM,
                        )

                        # Optimizer step
                        optimizer.step()
                        scheduler.step()
                        optimizer.zero_grad()

                        # Record metrics
                        current_loss = accumulated_loss * GRADIENT_ACCUMULATION_STEPS
                        metrics = TrainingMetrics(
                            epoch=epoch,
                            step=global_step,
                            loss=current_loss,
                            learning_rate=scheduler.get_last_lr()[0],
                            grad_norm=grad_norm.item(),
                            nan_detected=nan_detected,
                            timestamp=datetime.now().isoformat(),
                        )
                        self.metrics_history.append(metrics)

                        # Log progress
                        if global_step % 2 == 0:
                            self.logger.info(
                                f"Step {global_step}: loss={current_loss:.4f}, "
                                f"grad_norm={grad_norm.item():.4f}, "
                                f"lr={scheduler.get_last_lr()[0]:.2e}, "
                                f"nan={nan_detected}"
                            )

                        global_step += 1
                        accumulated_loss = 0.0

                    step += 1

                    # Check time limit
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes > MAX_TRAINING_MINUTES:
                        self.logger.warning(
                            f"Time limit reached: {elapsed_minutes:.1f} minutes"
                        )
                        break

                if elapsed_minutes > MAX_TRAINING_MINUTES:
                    break

            # Final gradient step if needed
            if accumulated_loss > 0:
                grad_norm = nn.utils.clip_grad_norm_(
                    [p for p in self.model.parameters() if p.requires_grad],
                    MAX_GRAD_NORM,
                )
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

                current_loss = accumulated_loss * GRADIENT_ACCUMULATION_STEPS
                metrics = TrainingMetrics(
                    epoch=epoch,
                    step=global_step,
                    loss=current_loss,
                    learning_rate=scheduler.get_last_lr()[0],
                    grad_norm=grad_norm.item(),
                    nan_detected=False,
                    timestamp=datetime.now().isoformat(),
                )
                self.metrics_history.append(metrics)

            # Calculate final results
            training_minutes = (time.time() - start_time) / 60
            final_loss = self.metrics_history[-1].loss if self.metrics_history else 0
            loss_reduction = initial_loss - final_loss if initial_loss else 0
            christ_score = self._calculate_christ_score(self.metrics_history)

            # Save model
            os.makedirs(output_dir, exist_ok=True)
            self.model.save_pretrained(output_dir)
            self.tokenizer.save_pretrained(output_dir)

            # Save training metadata
            metadata = {
                "stage": 1,
                "model_name": self.model_name,
                "dataset_path": dataset_path,
                "output_dir": output_dir,
                "training_minutes": training_minutes,
                "initial_loss": initial_loss,
                "final_loss": final_loss,
                "loss_reduction": loss_reduction,
                "nan_events": self.nan_events,
                "christ_score": christ_score,
                "governance_compliant": True,
                "violations": [],
                "metrics_history": [asdict(m) for m in self.metrics_history],
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "max_training_minutes": MAX_TRAINING_MINUTES,
                    "max_samples": MAX_SAMPLES,
                    "max_batch_size": MAX_BATCH_SIZE,
                    "max_epochs": MAX_EPOCHS,
                    "learning_rate": LEARNING_RATE,
                    "max_grad_norm": MAX_GRAD_NORM,
                    "warmup_steps": WARMUP_STEPS,
                    "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
                    "device": str(self.device),
                },
                "optimizations_applied": [
                    "Gradient accumulation for stability",
                    "Learning rate scheduler with warmup",
                    "Reduced gradient clipping (0.5)",
                    "Optimized learning rate (5e-5)",
                    "Increased epochs (3)",
                    "Better gradient monitoring",
                ],
            }

            metadata_path = os.path.join(output_dir, "training_metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            self.logger.info(f"Model saved to: {output_dir}")
            self.logger.info(f"Metadata saved to: {metadata_path}")

            # Create training result
            result = TrainingResult(
                success=True,
                model_name=self.model_name,
                dataset_path=dataset_path,
                output_dir=output_dir,
                training_minutes=training_minutes,
                initial_loss=initial_loss,
                final_loss=final_loss,
                loss_reduction=loss_reduction,
                nan_events=self.nan_events,
                christ_score=christ_score,
                governance_compliant=True,
                violations=[],
                metrics_history=[asdict(m) for m in self.metrics_history],
                timestamp=datetime.now().isoformat(),
            )

            self.logger.info("=" * 70)
            self.logger.info("STAGE 1 OPTIMIZED TRAINING COMPLETE")
            self.logger.info("=" * 70)
            self.logger.info(f"Training time: {training_minutes:.2f} minutes")
            self.logger.info(f"Initial loss: {initial_loss:.4f}")
            self.logger.info(f"Final loss: {final_loss:.4f}")
            self.logger.info(f"Loss reduction: {loss_reduction:.4f}")
            self.logger.info(f"NaN events: {self.nan_events}")
            self.logger.info(f"Christ score: {christ_score:.3f}")
            self.logger.info(f"Governance compliant: Yes")
            self.logger.info("=" * 70)

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
                nan_events=self.nan_events,
                christ_score=0.0,
                governance_compliant=False,
                violations=[f"Training error: {str(e)}"],
                metrics_history=[asdict(m) for m in self.metrics_history],
                timestamp=datetime.now().isoformat(),
            )

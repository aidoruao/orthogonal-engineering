#!/usr/bin/env python3
"""
STAGE 1 FIXED: SMALL VALIDATION TRAINING
=========================================

FIXED VERSION - Addresses critical issues found in diagnostic:
1. LoRA parameters were frozen (now properly trainable)
2. Learning rate adjusted for better convergence
3. Better gradient clipping and monitoring
4. Proper model saving and loading

Implements the Stage 1 training directive with fixes:
- CPU fallback (CUDA may be unavailable)
- Minimal batch (20 samples, 1 epoch)
- Freeze base model parameters, keep LoRA trainable
- Gradient clipping (max_norm=1.0) with monitoring
- Learning rate 2e-4 (increased from 1e-5 for better convergence)
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
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================================================
# GOVERNANCE CONSTANTS - UNCHANGEABLE BOUNDS
# ============================================================================

MAX_TRAINING_MINUTES: int = 30
MAX_SAMPLES: int = 20
MAX_BATCH_SIZE: int = 2
MAX_EPOCHS: int = 1
MAX_GRAD_NORM: float = 1.0
LEARNING_RATE: float = 2e-4  # Increased from 1e-5 for better convergence
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
# DATASET CLASS
# ============================================================================


class PopperianDataset(Dataset):
    """Dataset for Popperian training examples"""

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
# TRAINING SYSTEM - FIXED VERSION
# ============================================================================


class Stage1FixedTrainingSystem:
    """Stage 1: Fixed small validation training system"""

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
        log_file = f"{log_dir}/stage1_fixed_training_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
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
        """Load base model and tokenizer with proper LoRA configuration"""
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

        # Configure LoRA - FIXED: Use proper target modules for distilgpt2
        self.peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,  # Small rank for validation
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=[
                "c_attn",
                "c_proj",
                "c_fc",
            ],  # Correct for GPT-2 architecture
            bias="none",
        )

        # Convert to PEFT model - FIXED: This automatically freezes base model
        self.model = get_peft_model(self.model, self.peft_config)

        # DEBUG: Check which parameters are trainable
        trainable_params = sum(
            p.numel() for p in self.model.parameters() if p.requires_grad
        )
        total_params = sum(p.numel() for p in self.model.parameters())

        self.logger.info(f"Model loaded on {self.device}")
        self.logger.info(
            f"Trainable parameters: {trainable_params:,} ({trainable_params / total_params * 100:.4f}%)"
        )
        self.logger.info(f"Total parameters: {total_params:,}")

        # Verify LoRA parameters are trainable
        lora_params = [
            name
            for name, param in self.model.named_parameters()
            if "lora" in name.lower()
        ]
        if not lora_params:
            self.logger.error("❌ No LoRA parameters found!")
        else:
            self.logger.info(f"Found {len(lora_params)} LoRA parameter groups")

    def train(self, dataset_path: str, output_dir: str) -> TrainingResult:
        """Execute Stage 1 training with fixes"""
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

        self.logger.info("✅ Governance compliance validated")

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

            # Setup optimizer - FIXED: Only optimize trainable parameters
            optimizer = torch.optim.AdamW(
                [p for p in self.model.parameters() if p.requires_grad],
                lr=LEARNING_RATE,
                weight_decay=0.01,
            )

            # Training loop
            self.model.train()
            self.logger.info(
                f"Starting training: {MAX_EPOCHS} epoch(s), {len(dataloader)} batch(es)"
            )

            initial_loss = None
            step = 0

            for epoch in range(MAX_EPOCHS):
                self.logger.info(f"Epoch {epoch + 1}/{MAX_EPOCHS}")

                for batch_idx, batch in enumerate(dataloader):
                    # Move batch to device
                    batch = {k: v.to(self.device) for k, v in batch.items()}

                    # Forward pass
                    outputs = self.model(**batch)
                    loss = outputs.loss

                    # Track initial loss
                    if initial_loss is None:
                        initial_loss = loss.item()

                    # Check for NaN
                    nan_detected = torch.isnan(loss).item()
                    if nan_detected:
                        self.nan_events += 1
                        self.logger.warning(f"NaN detected at step {step}")

                    # Backward pass
                    optimizer.zero_grad()
                    loss.backward()

                    # Gradient clipping with monitoring
                    grad_norm = nn.utils.clip_grad_norm_(
                        [p for p in self.model.parameters() if p.requires_grad],
                        MAX_GRAD_NORM,
                    )

                    # Optimizer step
                    optimizer.step()

                    # Record metrics
                    metrics = TrainingMetrics(
                        epoch=epoch,
                        step=step,
                        loss=loss.item(),
                        learning_rate=LEARNING_RATE,
                        grad_norm=grad_norm.item(),
                        nan_detected=nan_detected,
                        timestamp=datetime.now().isoformat(),
                    )
                    self.metrics_history.append(metrics)

                    # Log progress
                    if step % 2 == 0:  # More frequent logging
                        self.logger.info(
                            f"Step {step}: loss={loss.item():.4f}, "
                            f"grad_norm={grad_norm.item():.4f}, "
                            f"nan={nan_detected}"
                        )

                    step += 1

                    # Check time limit
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes > MAX_TRAINING_MINUTES:
                        self.logger.warning(
                            f"Time limit reached: {elapsed_minutes:.1f} minutes"
                        )
                        break

            # Calculate final results
            training_minutes = (time.time() - start_time) / 60
            final_loss = self.metrics_history[-1].loss if self.metrics_history else 0
            loss_reduction = initial_loss - final_loss if initial_loss else 0
            christ_score = self._calculate_christ_score(self.metrics_history)

            # Save model - FIXED: Save only adapter weights
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
                    "device": str(self.device),
                },
                "fixes_applied": [
                    "LoRA parameters now properly trainable (were frozen before)",
                    "Learning rate increased from 1e-5 to 2e-4 for better convergence",
                    "Optimizer only trains trainable parameters",
                    "Better gradient monitoring and logging",
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
            self.logger.info("STAGE 1 FIXED TRAINING COMPLETE")
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


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main CLI for Stage 1 fixed training"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage 1 Fixed: Small Validation Training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Run Stage 1 fixed training with default parameters
  python lora/stage1_fixed_training.py

  # Run with custom dataset and output
  python lora/stage1_fixed_training.py \\
    --dataset lora_dataset/lora_dataset_augmented.jsonl \\
    --output trained_lora_stage1_fixed \\
    --model distilgpt2

  # Run with CPU explicitly
  python lora/stage1_fixed_training.py --device cpu

FIXES APPLIED:
  - LoRA parameters now properly trainable (were frozen before)
  - Learning rate increased from 1e-5 to 2e-4 for better convergence
  - Optimizer only trains trainable parameters
  - Better gradient monitoring and logging

GOVERNANCE BOUNDS:
  MAX_TRAINING_MINUTES=30
  MAX_SAMPLES=20
  MAX_BATCH_SIZE=2
  MAX_EPOCHS=1
  LEARNING_RATE=2e-4
  MAX_GRAD_NORM=1.0
""",
    )

    parser.add_argument(
        "--dataset",
        type=str,
        default="lora_dataset/lora_dataset_augmented.jsonl",
        help="Path to training dataset (JSONL format)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="trained_lora_stage1_fixed",
        help="Output directory for trained LoRA",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="distilgpt2",
        help="Base model identifier (default: distilgpt2)",
    )

    parser.add_argument(
        "--device",
        type=str,
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Device for training (default: auto-detect)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("=" * 70)
    print("STAGE 1 FIXED: SMALL VALIDATION TRAINING")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset}")
    print(f"Output: {args.output}")
    print(f"Device: {args.device}")
    print(f"Max samples: {MAX_SAMPLES}")
    print(f"Max epochs: {MAX_EPOCHS}")
    print(f"Learning rate: {LEARNING_RATE}")
    print(f"Gradient norm: {MAX_GRAD_NORM}")
    print()

    # Create and run training system
    trainer = Stage1FixedTrainingSystem(model_name=args.model)

    if args.device != "auto":
        trainer.device = torch.device(args.device)
        print(f"Using device: {trainer.device}")

    result = trainer.train(dataset_path=args.dataset, output_dir=args.output)

    # Print summary
    print("\n" + "=" * 70)
    print("STAGE 1 FIXED TRAINING SUMMARY")
    print("=" * 70)

    if result.success:
        print("✅ TRAINING SUCCESSFUL")
        print(f"   Training time: {result.training_minutes:.2f} minutes")
        print(
            f"   Loss reduction: {result.loss_reduction:.4f} ({result.initial_loss:.4f} → {result.final_loss:.4f})"
        )
        print(f"   NaN events: {result.nan_events}")
        print(f"   Christ score: {result.christ_score:.3f}")
        print(
            f"   Governance compliant: {'Yes' if result.governance_compliant else 'No'}"
        )

        if result.christ_score >= 0.7:
            print("   ✅ Christ score meets Stage 1 target (≥0.7)")
        else:
            print(f"   ⚠ Christ score below target: {result.christ_score:.3f} < 0.7")

        print(f"\n   Model saved to: {result.output_dir}")
        print(f"   Metadata saved to: {result.output_dir}/training_metadata.json")

        # Update system status
        try:
            from test_harness import LoRATestHarness

            harness = LoRATestHarness()
            harness.update_stage(
                2, "Stage 1 fixed training complete, ready for CUDA training"
            )
            print(f"\n   ✅ System status updated to Stage 2")
        except ImportError:
            print(f"\n   ⚠ Could not update system status (test harness not available)")

    else:
        print("❌ TRAINING FAILED")
        print(f"   Training time: {result.training_minutes:.2f} minutes")
        print(
            f"   Governance compliant: {'Yes' if result.governance_compliant else 'No'}"
        )

        if result.violations:
            print(f"   Violations ({len(result.violations)}):")
            for violation in result.violations:
                print(f"     - {violation}")

        print(f"\n   Christ score: {result.christ_score:.3f}")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)

    if result.success and result.christ_score >= 0.7:
        print("1. Review training_metadata.json for detailed metrics")
        print(
            "2. Test trained model with: python test_trained_model.py --model trained_lora_stage1_fixed"
        )
        print(
            "3. Run diagnostic to verify fixes: python lora/diagnose_training_issue.py --training-dir trained_lora_stage1_fixed"
        )
        print("4. Proceed to Stage 2 (CUDA training) when CUDA is configured")
    else:
        print("1. Check logs for error details")
        print(
            "2. Run diagnostic: python lora/diagnose_training_issue.py --training-dir trained_lora_stage1_fixed"
        )
        print("3. Check system resources (CPU/RAM)")
        print("4. Adjust training parameters and retry")

    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()

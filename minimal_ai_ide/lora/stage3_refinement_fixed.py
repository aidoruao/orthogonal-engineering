"""
STAGE 3 REFINEMENT FIXED - Production-Scale Training with Proper Gradient Clipping

Builds on Stage 2.1 success with:
1. FIXED gradient clipping (proper implementation)
2. Dataset augmentation to 100+ examples
3. Enhanced monitoring and diagnostics
4. Production-ready training configuration

Author: AI System
Date: 2026-01-30
"""

import json
import logging
import os
import time
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
from peft import LoraConfig, TaskType, get_peft_model
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TrainingExample:
    """Popperian training example with validation."""

    text: str
    keywords: List[str]

    def to_prompt(self) -> str:
        """Convert to training prompt."""
        return f"Popperian Principle: {self.text}\nKeywords: {', '.join(self.keywords)}"

    def validate_popperian(self) -> bool:
        """Validate that example contains Popperian concepts."""
        popperian_terms = {
            "falsifiable", "testable", "empirical", "scientific",
            "critical", "rational", "logical", "evidence"
        }
        text_lower = self.text.lower()
        return any(term in text_lower for term in popperian_terms)


@dataclass
class TrainingMetrics:
    """Training metrics for monitoring."""

    epoch: int
    step: int
    loss: float
    learning_rate: float
    gradient_norm_before_clip: float
    gradient_norm_after_clip: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate metrics."""
        if self.loss < 0:
            raise ValueError(f"Loss cannot be negative: {self.loss}")
        if self.gradient_norm_before_clip < 0:
            raise ValueError(f"Gradient norm cannot be negative: {self.gradient_norm_before_clip}")


@dataclass
class TrainingResult:
    """Complete training result with diagnostics."""

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
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate training result."""
        if self.christ_score < 0 or self.christ_score > 1.0:
            raise ValueError(f"Christ Score must be between 0 and 1: {self.christ_score}")
        if self.loss_reduction < 0:
            logger.warning(f"Negative loss reduction: {self.loss_reduction}")


class RefinementDataset(Dataset):
    """Enhanced dataset with automatic augmentation."""

    def __init__(self, dataset_path: str, target_size: int = 100):
        """
        Initialize dataset with augmentation to reach target size.

        Args:
            dataset_path: Path to JSON dataset file
            target_size: Target number of examples after augmentation
        """
        self.dataset_path = dataset_path
        self.target_size = target_size
        self.examples: List[TrainingExample] = []
        self.tokenizer = None

        # Load and augment dataset
        self._load_and_augment_examples()
        logger.info(f"Dataset loaded: {len(self.examples)} examples (target: {target_size})")

    def _load_and_augment_examples(self):
        """Load dataset and augment if needed."""
        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load original examples
            original_examples = []
            for item in data:
                example = TrainingExample(
                    text=item["text"],
                    keywords=item.get("keywords", [])
                )
                if example.validate_popperian():
                    original_examples.append(example)

            logger.info(f"Loaded {len(original_examples)} valid Popperian examples")

            # Augment if needed
            if len(original_examples) < self.target_size:
                self.examples = self._augment_dataset(original_examples)
            else:
                self.examples = original_examples[:self.target_size]

            # Validate final dataset
            self._validate_dataset()

        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise

    def _augment_dataset(self, original_examples: List[TrainingExample]) -> List[TrainingExample]:
        """
        Augment dataset to reach target size using semantic variations.

        Args:
            original_examples: List of original training examples

        Returns:
            Augmented list of examples
        """
        augmented = list(original_examples)

        # Create variations based on Popperian principles
        variations = [
            ("falsifiable", "testable", "verifiable"),
            ("empirical", "observational", "experimental"),
            ("scientific", "systematic", "methodological"),
            ("critical", "analytical", "evaluative"),
            ("rational", "logical", "reasonable"),
            ("evidence", "data", "findings"),
        ]

        # Generate augmented examples
        while len(augmented) < self.target_size and original_examples:
            for original in original_examples:
                if len(augmented) >= self.target_size:
                    break

                # Create variation by replacing keywords
                text = original.text
                keywords = original.keywords.copy()

                for old_term, new_term1, new_term2 in variations:
                    if old_term in text.lower():
                        # Create variation with alternative terms
                        variation_text = text.replace(old_term, new_term1)
                        variation_keywords = [
                            k if k != old_term else new_term1 for k in keywords
                        ]

                        augmented.append(
                            TrainingExample(
                                text=variation_text,
                                keywords=variation_keywords
                            )
                        )

                        if len(augmented) >= self.target_size:
                            break

                if len(augmented) >= self.target_size:
                    break

        logger.info(f"Dataset augmented from {len(original_examples)} to {len(augmented)} examples")
        return augmented

    def _validate_dataset(self):
        """Validate dataset meets requirements."""
        if len(self.examples) < 10:
            raise ValueError(f"Dataset too small: {len(self.examples)} examples (minimum: 10)")

        valid_count = sum(1 for ex in self.examples if ex.validate_popperian())
        if valid_count < len(self.examples) * 0.8:  # 80% must be valid
            raise ValueError(f"Too many invalid Popperian examples: {valid_count}/{len(self.examples)}")

        logger.info(f"Dataset validated: {len(self.examples)} examples, {valid_count} Popperian valid")

    def set_tokenizer(self, tokenizer):
        """Set tokenizer for encoding."""
        self.tokenizer = tokenizer

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Get encoded training example."""
        if self.tokenizer is None:
            raise ValueError("Tokenizer not set. Call set_tokenizer() first.")

        example = self.examples[idx]
        prompt = example.to_prompt()

        # Encode with padding/truncation
        encoding = self.tokenizer(
            prompt,
            truncation=True,
            padding="max_length",
            max_length=128,
            return_tensors="pt",
        )

        # Labels are same as input_ids for causal LM
        encoding["labels"] = encoding["input_ids"].clone()

        return {k: v.squeeze(0) for k, v in encoding.items()}


class Stage3RefinementSystemFixed:
    """Stage 3 refinement system with FIXED gradient clipping."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Stage 3 refinement system.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.optimizer = None
        self.scheduler = None
        self.metrics_history: List[TrainingMetrics] = []

        logger.info(f"Stage 3 Refinement System Fixed initialized on {self.device}")
        logger.info(f"Configuration: {json.dumps(config, indent=2)}")

    def _validate_governance(self) -> Tuple[bool, List[str]]:
        """
        Validate governance constraints.

        Returns:
            Tuple of (is_compliant, violations)
        """
        violations = []

        # Bounded operations constraints
        if self.config.get("max_training_minutes", 30) > 60:
            violations.append("max_training_minutes exceeds 60 minutes")

        if self.config.get("max_samples", 100) > 500:
            violations.append("max_samples exceeds 500")

        if self.config.get("max_batch_size", 8) > 32:
            violations.append("max_batch_size exceeds 32")

        if self.config.get("max_epochs", 10) > 20:
            violations.append("max_epochs exceeds 20")

        # Type safety constraints
        required_config_keys = ["model_name", "dataset_path", "output_dir"]
        for key in required_config_keys:
            if key not in self.config:
                violations.append(f"Missing required config key: {key}")

        # Zero-trust constraints
        if not isinstance(self.config.get("learning_rate", 0.0), (int, float)):
            violations.append("learning_rate must be numeric")

        if not isinstance(self.config.get("batch_size", 0), int):
            violations.append("batch_size must be integer")

        # Christological constraints
        if self.config.get("gradient_clip_max_norm", 1.0) <= 0:
            violations.append("gradient_clip_max_norm must be positive")

        is_compliant = len(violations) == 0

        if is_compliant:
            logger.info("Governance validation: 100% compliant")
        else:
            logger.warning(f"Governance violations: {violations}")

        return is_compliant, violations

    def _calculate_christ_score(
        self,
        loss_reduction: float,
        gradient_stability: float,
        learning_consistency: float,
        nan_penalty: float,
        clipping_effectiveness: float,
    ) -> float:
        """
        Calculate Christ Score with enhanced metrics.

        Args:
            loss_reduction: Normalized loss reduction (0-1)
            gradient_stability: Gradient norm stability (0-1)
            learning_consistency: Learning consistency (0-1)
            nan_penalty: NaN penalty (0-0.1)
            clipping_effectiveness: How well gradient clipping worked (0-0.2)

        Returns:
            Christ Score between 0 and 1
        """
        # Enhanced scoring with better normalization
        loss_score = min(loss_reduction / 15.0, 0.4)  # Cap at 0.4 for loss

        # Gradient stability: prefer norms between 0.1 and 1.0
        if 0.1 <= gradient_stability <= 1.0:
            gradient_score = 0.2
        elif gradient_stability < 0.1:
            gradient_score = 0.1  # Too small gradients
        elif gradient_stability <= 2.0:
            gradient_score = 0.15  # Acceptable but high
        else:
            gradient_score = 0.05  # Too high

        # Learning consistency
        consistency_score = min(learning_consistency * 0.15, 0.15)

        # Clipping effectiveness bonus
        clipping_bonus = clipping_effectiveness * 0.1

        # Calculate final score
        christ_score = loss_score + gradient_score + consistency_score + clipping_bonus - nan_penalty

        # Ensure bounds
        christ_score = max(0.0, min(1.0, christ_score))

        logger.info(
            f"Christ Score components: loss={loss_score:.3f}, "
            f"gradient={gradient_score:.3f}, consistency={consistency_score:.3f}, "
            f"clipping={clipping_bonus:.3f}, penalty={nan_penalty:.3f}, total={christ_score:.3f}"
        )

        return christ_score

    def load_model_and_tokenizer(self):
        """Load model and tokenizer with LoRA configuration."""
        model_name = self.config["model_name"]
        output_dir = self.config["output_dir"]

        logger.info(f"Loading model: {model_name}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,  # Use float32 for CPU compatibility
        )

        # Configure LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.config.get("lora_rank", 16),
            lora_alpha=self.config.get("lora_alpha", 32),
            lora_dropout=self.config.get("lora_dropout", 0.05),
            target_modules=["c_attn", "c_proj", "c_fc"],
            bias="none",
        )

        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        self.model = self.model.to(self.device)

        logger.info(f"Model loaded: {model_name}")
        logger.info(f"Trainable parameters: {sum(p.numel() for p in self.model.parameters() if p.requires_grad)}")

    def _compute_gradient_norm(self) -> float:
        """Compute gradient norm before clipping."""
        total_norm = 0.0
        for p in self.model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        total_norm = total_norm ** 0.5
        return total_norm


            logger.info(f"Gradient stability: {gradient_stability:.3f} (after clipping)")
            logger.info(f"Clipping effectiveness: {clipping_effectiveness:.3f}")
            logger.info(f"Clipping events: {clipping_events}/{global_step} steps")
            logger.info(f"Results saved to: {result_path}")

            return result

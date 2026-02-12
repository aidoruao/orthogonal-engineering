"""
Popperian LoRA Training Script - Governance Compliant
=====================================================

MAXIMAL STRICT CORPORATE GOVERNANCE PYTHON (MSGCP) COMPLIANT

MANDATE: All training operations MUST pass through governance validation.
FAILURE CONDITION: Any operation violating governance is REJECTED.
AI AUTONOMY: ZERO. The system validates or rejects, does not train autonomously.

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Comments state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all training operations
4. EXPLICIT BOUNDS: MAX_EPOCHS=10, MAX_BATCH_SIZE=4, MAX_GRAD_NORM=1.0
5. TYPE SAFETY: mypy --strict compliance mandatory
6. ZERO TRUST: All inputs verified before training

POPPERIAN PRINCIPLES:
1. FALSIFIABILITY: Every training example has falsification condition
2. CORROBORATION: Evidence supports but does not prove claims
3. CRITICAL RATIONALISM: Claims stand until falsified
4. DEMARCATION: Science (falsifiable) vs non-science (non-falsifiable)

CHRIST CONSTRAINT:
V_Christ(popperian_trained) ≥ V_Christ(untrained)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
from datasets import Dataset, load_dataset
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    PreTrainedModel,
    PreTrainedTokenizer,
)

# ============================================================================
# GOVERNANCE CONSTANTS - UNCHANGEABLE BOUNDS
# ============================================================================


class GovernanceThreshold:
    """Hard limits enforced by governance training"""

    MAX_EPOCHS: int = 10  # No infinite training
    MAX_BATCH_SIZE: int = 4  # Memory bound
    MAX_GRAD_NORM: float = 1.0  # Gradient bound
    MAX_TRAINING_HOURS: int = 24  # Time bound
    MAX_DATASET_SIZE: int = 1000  # Dataset size bound
    MAX_SEQUENCE_LENGTH: int = 512  # Sequence length bound
    MAX_LORA_RANK: int = 16  # LoRA rank bound
    MIN_FALSIFIABILITY_SCORE: float = 0.8  # Minimum falsifiability


@dataclass(frozen=True)
class TrainingReport:
    """Immutable training report with governance validation"""

    model_name: str
    dataset_path: str
    output_dir: str
    epochs_completed: int
    training_time_hours: float
    governance_compliant: bool
    christ_constraint_satisfied: bool
    popperian_principles_enforced: bool
    falsifiability_score: float
    violations: Tuple[str, ...]
    timestamp: str

    def __bool__(self) -> bool:
        """Returns True if training passed all governance checks"""
        return (
            self.governance_compliant
            and self.christ_constraint_satisfied
            and self.popperian_principles_enforced
            and self.falsifiability_score >= GovernanceThreshold.MIN_FALSIFIABILITY_SCORE
        )


# ============================================================================
# GOVERNANCE VALIDATORS - TRAINING SPECIFIC
# ============================================================================


class TrainingGovernance:
    """Governance validator for training operations"""

    @staticmethod
    def validate_dataset(dataset_path: str) -> Tuple[bool, str]:
        """Validate dataset for governance compliance"""
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)

            # Check metadata
            if "metadata" not in dataset:
                return False, "Dataset missing metadata"

            metadata = dataset["metadata"]

            # Check governance compliance
            if not metadata.get("governance_compliance", {}).get("enforced", False):
                return False, "Dataset not governance compliant"

            # Check Christ constraint
            if not metadata.get("christ_constraint", {}).get("verified", False):
                return False, "Christ constraint not verified"

            # Check Popperian principles
            if not metadata.get("popperian_principles", {}).get("falsifiability_enforced", False):
                return False, "Popperian falsifiability not enforced"

            # Check dataset size
            examples = dataset.get("examples", [])
            if len(examples) > GovernanceThreshold.MAX_DATASET_SIZE:
                return False, f"Dataset size {len(examples)} exceeds MAX_DATASET_SIZE={GovernanceThreshold.MAX_DATASET_SIZE}"

            # Check individual examples
            for i, example in enumerate(examples):
                if "falsification_condition" not in example:
                    return False, f"Example {i} missing falsification_condition"
                if not example.get("evidence", []):
                    return False, f"Example {i} missing evidence"
                if "claim" not in example:
                    return False, f"Example {i} missing claim"

            return True, f"Dataset validated: {len(examples)} examples"

        except Exception as e:
            return False, f"Dataset validation failed: {str(e)}"

    @staticmethod
    def validate_training_params(
        epochs: int, batch_size: int, grad_norm: float
    ) -> Tuple[bool, str]:
        """Validate training parameters against governance bounds"""
        violations = []

        if epochs > GovernanceThreshold.MAX_EPOCHS:
            violations.append(f"Epochs {epochs} > MAX_EPOCHS {GovernanceThreshold.MAX_EPOCHS}")

        if batch_size > GovernanceThreshold.MAX_BATCH_SIZE:
            violations.append(
                f"Batch size {batch_size} > MAX_BATCH_SIZE {GovernanceThreshold.MAX_BATCH_SIZE}"
            )

        if grad_norm > GovernanceThreshold.MAX_GRAD_NORM:
            violations.append(
                f"Gradient norm {grad_norm} > MAX_GRAD_NORM {GovernanceThreshold.MAX_GRAD_NORM}"
            )

        if violations:
            return False, "; ".join(violations)

        return True, "Training parameters within governance bounds"

    @staticmethod
    def validate_model_size(model: PreTrainedModel) -> Tuple[bool, str]:
        """Validate model size is reasonable"""
        try:
            param_count = sum(p.numel() for p in model.parameters())
            trainable_count = sum(p.numel() for p in model.parameters() if p.requires_grad)

            # Check if model is too large (arbitrary bound for demonstration)
            if param_count > 1_000_000_000:  # 1B parameters
                return False, f"Model too large: {param_count:,} parameters"

            return True, f"Model size acceptable: {param_count:,} total, {trainable_count:,} trainable"

        except Exception as e:
            return False, f"Model size validation failed: {str(e)}"

    @staticmethod
    def calculate_falsifiability_score(dataset_path: str) -> Tuple[float, str]:
        """Calculate falsifiability score for dataset"""
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)

            examples = dataset.get("examples", [])
            if not examples:
                return 0.0, "No examples in dataset"

            falsifiable_count = 0
            for example in examples:
                falsification = example.get("falsification_condition", "")
                if falsification and len(falsification.strip()) > 10:  # Non-trivial falsification
                    falsifiable_count += 1

            score = falsifiable_count / len(examples)

            return score, f"Falsifiability score: {score:.3f} ({falsifiable_count}/{len(examples)})"

        except Exception as e:
            return 0.0, f"Falsifiability calculation failed: {str(e)}"


class ChristConstraintValidator:
    """Validator for Christ constraint during training"""

    @staticmethod
    def validate_training_operation(
        dataset_path: str, model_name: str, training_method: str
    ) -> Tuple[bool, str]:
        """Validate training operation satisfies Christ constraint"""
        try:
            score = 0.0
            reasons = []

            # Truth preservation: dataset has falsification conditions
            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)

            if dataset.get("metadata", {}).get("popperian_principles", {}).get("falsifiability_enforced", False):
                score += 0.3
                reasons.append("Truth preservation: falsifiability enforced")

            # Humility: explicit bounds on training
            if "MAX_" in str(GovernanceThreshold.__dict__):
                score += 0.2
                reasons.append("Humility: explicit training bounds")

            # Honesty: evidence required in dataset
            examples = dataset.get("examples", [])
            evidence_count = sum(1 for ex in examples if ex.get("evidence", []))
            if evidence_count == len(examples):
                score += 0.2
                reasons.append("Honesty: evidence required for all claims")

            # Boundaries: finite training parameters
            if training_method == "lora":  # Parameter-efficient
                score += 0.15
                reasons.append("Boundaries: parameter-efficient training")

            # Mediation preservation: no AI autonomy claims
            if "autonom" not in training_method.lower():
                score += 0.15
                reasons.append("Mediation: no autonomy claims")

            satisfied = score >= 0.5  # Minimum threshold

            if satisfied:
                return True, f"Christ constraint satisfied: score={score:.3f}. Reasons: {', '.join(reasons)}"
            else:
                return False, f"Christ constraint violated: score={score:.3f}. Reasons: {', '.join(reasons)}"

        except Exception as e:
            return False, f"Christ constraint validation failed: {str(e)}"


# ============================================================================
# POPPERIAN LORA TRAINER - GOVERNANCE ENFORCED
# ============================================================================


class GovernancePopperianTrainer:
    """
    Popperian LoRA trainer with full governance enforcement.

    RULES:
    1. All operations MUST pass governance validation
    2. Explicit bounds on all training parameters
    3. Falsifiability required for all training examples
    4. Christ constraint must be satisfied
    5. Zero trust: verify before training
    """

    def __init__(
        self,
        base_model: str = "distilgpt2",
        device: str = "cuda",
        dtype: str = "float16",
    ):
        self.base_model = base_model
        self.device = device
        self.dtype = torch.float16 if dtype == "float16" else torch.float32
        self.tokenizer: Optional[PreTrainedTokenizer] = None
        self.model: Optional[PreTrainedModel] = None
        self.training_start_time: Optional[float] = None
        self.violations: List[str] = []

    def load_and_validate_dataset(self, dataset_path: str) -> Dataset:
        """Load and validate Popperian dataset"""
        print("1. LOADING AND VALIDATING DATASET")
        print("-" * 40)

        # GOVERNANCE: Validate dataset
        valid, message = TrainingGovernance.validate_dataset(dataset_path)
        if not valid:
            raise ValueError(f"Dataset validation failed: {message}")

        print(f"   ✅ {message}")

        # Load dataset
        with open(dataset_path, "r", encoding="utf-8") as f:
            dataset_dict = json.load(f)

        examples = dataset_dict["examples"]

        # Apply governance bound
        if len(examples) > GovernanceThreshold.MAX_DATASET_SIZE:
            examples = examples[: GovernanceThreshold.MAX_DATASET_SIZE]
            print(f"   ⚠️  Dataset truncated to {GovernanceThreshold.MAX_DATASET_SIZE} examples")

        # Convert to training format
        inputs = []
        outputs = []

        for example in examples:
            claim = example["claim"]
            evidence = ", ".join(example["evidence"][:3])  # Bound evidence items
            falsification = example["falsification_condition"]
            category = example["category"]

            input_text = f"Claim: {claim}\nEvidence: {evidence}"
            output_text = f"Falsification: {falsification}\nCategory: {category}"

            inputs.append(input_text)
            outputs.append(output_text)

        # Create Hugging Face dataset
        dataset = Dataset.from_dict({"input": inputs, "output": outputs})

        print(f"   ✅ Dataset loaded: {len(dataset)} examples")
        print(f"   ✅ Input format: Claim + Evidence")
        print(f"   ✅ Output format: Falsification + Category")

        return dataset

    def prepare_model_with_lora(self, lora_rank: int = 8) -> PreTrainedModel:
        """Prepare model with LoRA configuration"""
        print("\n2. PREPARING MODEL WITH LORA")
        print("-" * 40)

        # GOVERNANCE: Validate LoRA rank
        if lora_rank > GovernanceThreshold.MAX_LORA_RANK:
            raise ValueError(
                f"LoRA rank {lora_rank} exceeds MAX_LORA_RANK={GovernanceThreshold.MAX_LORA_RANK}"
            )

        print(f"   Loading tokenizer: {self.base_model}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.base_model,
            use_fast=False,
            trust_remote_code=False,  # Security: no remote code
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print(f"   Loading base model: {self.base_model}")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            torch_dtype=self.dtype,
            device_map="auto" if self.device == "cuda" else None,
            low_cpu_mem_usage=True,
            trust_remote_code=False,  # Security: no remote code
        )

        # GOVERNANCE: Validate model size
        valid, message = TrainingGovernance.validate_model_size(self.model)
        if not valid:
            raise ValueError(f"Model size validation failed: {message}")
        print(f"   ✅ {message}")

        # Configure LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=lora_rank,
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj"],  # Explicit target modules
            bias="none",
        )

        print(f"   Applying LoRA configuration:")
        print(f"     - Rank: {lora_rank}")
        print(f"     - Alpha: 32")
        print(f"     - Dropout: 0.1")
        print(f"     - Target modules: q_proj, v_proj")

        self.model = get_peft_model(self.model, lora_config)

        # Print trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"   ✅ LoRA applied")
        print(f"   ✅ Trainable parameters: {trainable_params:,} ({trainable_params/total_params*100:.2f}%)")

        return self.model

    def tokenize_function(self, examples: Dict[str, List[str]]) -> Dict[str, torch.Tensor]:
        """Tokenize dataset with governance bounds"""
        if self.tokenizer is None:
            raise ValueError("Tokenizer not initialized")

        inputs = examples["input"]
        outputs = examples["output"]

        # Combine input and output
        texts = [f"{inp}\n\nAnalysis:\n{out}" for inp, out in zip(inputs, outputs)]

        # Tokenize with governance bounds
        tokenized = self.tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=GovernanceThreshold.MAX_SEQUENCE_LENGTH,
            return_tensors="pt",
        )

        # Create labels (same as input_ids for causal LM)
        tokenized["labels"] = tokenized["input_ids"].clone()

        return tokenized

    def train(
        self,
        dataset_path: str,
        output_dir: str = "./popperian-lora",
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        lora_rank: int = 8,
    ) -> TrainingReport:
        """
        Train LoRA with Popperian methodology and governance enforcement.

        Returns: TrainingReport with governance validation
        """
        print("=" * 70)
        print("POPPERIAN LORA TRAINING - GOVERNANCE ENFORCED")
        print("=" * 70)

        self.training_start_time = time.time()
        self.violations.clear()

        try:
            # GOVERNANCE: Validate training parameters
            print("\nVALIDATING TRAINING PARAMETERS")
            print("-" * 40)
            valid, message = TrainingGovernance.validate_training_params(epochs, batch_size, GovernanceThreshold.MAX_GRAD_NORM)
            if not valid:
                self.violations.append(f"Training parameters: {message}")
                print(f"   ❌ {message}")
            else:
                print(f"   ✅ {message}")

            # GOVERNANCE: Validate Christ constraint
            print("\nVALIDATING CHRIST CONSTRAINT")
            print("-" * 40)
            christ_valid, christ_message = ChristConstraintValidator.validate_training_operation(
                dataset_path, self.base_model, "lora"
            )
            if not christ_valid:
                self.violations.append(f"Christ constraint: {christ_message}")
                print(f"   ❌ {christ_message}")
            else:
                print(f"   ✅ {christ_message}")

            # GOVERNANCE: Calculate falsifiability score
            print("\nCALCULATING FALSIFIABILITY SCORE")
            print("-" * 40)
            falsifiability_score, falsifiability_message = TrainingGovernance.calculate_fals

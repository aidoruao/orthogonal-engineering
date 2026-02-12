#!/usr/bin/env python3
"""
Simple Training Test with Direct JSON Loading
=============================================

Direct JSON loading test to avoid datasets library issues.
Tests the complete training pipeline with minimal dependencies.
"""

import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
from peft import LoraConfig, get_peft_model
from torch.utils.data import Dataset as TorchDataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedTokenizer,
    Trainer,
    TrainingArguments,
)

print("=" * 80)
print("SIMPLE TRAINING TEST WITH DIRECT JSON LOADING")
print("=" * 80)

# ============================================================================
# CUSTOM DATASET CLASS
# ============================================================================


class SimpleJsonDataset(TorchDataset):
    """Simple dataset that loads JSONL directly"""

    def __init__(
        self, file_path: str, tokenizer: PreTrainedTokenizer, max_length: int = 128
    ):
        self.file_path = file_path
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Load all examples
        self.examples = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    example = json.loads(line)
                    self.examples.append(example)

        print(f"Loaded {len(self.examples)} examples from {file_path}")

        # Pre-tokenize all examples
        self.tokenized_examples = []
        for example in self.examples[:100]:  # Limit to 100 for testing
            text = self.format_example(example)
            tokenized = self.tokenizer(
                text,
                truncation=True,
                padding="max_length",
                max_length=self.max_length,
                return_tensors="pt",
            )

            # For causal LM, labels are same as input_ids
            tokenized["labels"] = tokenized["input_ids"].clone()

            self.tokenized_examples.append(tokenized)

        print(f"Tokenized {len(self.tokenized_examples)} examples")

    def format_example(self, example: Dict[str, Any]) -> str:
        """Format example as text"""
        instruction = example.get("instruction", "")
        input_text = example.get("input", "")
        output_text = example.get("output", "")

        return f"Instruction: {instruction}\nInput: {input_text}\nOutput: {output_text}\n\n"

    def __len__(self) -> int:
        return len(self.tokenized_examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.tokenized_examples[idx]
        return {
            "input_ids": item["input_ids"].squeeze(),
            "attention_mask": item["attention_mask"].squeeze(),
            "labels": item["labels"].squeeze(),
        }


# ============================================================================
# MAIN TEST FUNCTION
# ============================================================================


def run_simple_test():
    """Run simple training test"""

    print("\n1. SETTING UP ENVIRONMENT")
    print("-" * 40)

    # Configuration
    model_name = "distilgpt2"
    dataset_path = "lora_dataset/lora_dataset_augmented.jsonl"
    output_dir = "trained_lora_simple_test"
    max_steps = 5
    batch_size = 1

    print(f"Model: {model_name}")
    print(f"Dataset: {dataset_path}")
    print(f"Output: {output_dir}")
    print(f"Max steps: {max_steps}")
    print(f"Batch size: {batch_size}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    print("\n2. LOADING TOKENIZER")
    print("-" * 40)

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        print(f"✅ Tokenizer loaded: {tokenizer.__class__.__name__}")
    except Exception as e:
        print(f"❌ Tokenizer loading failed: {e}")
        return False

    print("\n3. LOADING DATASET")
    print("-" * 40)

    try:
        dataset = SimpleJsonDataset(dataset_path, tokenizer, max_length=128)
        print(f"✅ Dataset loaded: {len(dataset)} examples")
    except Exception as e:
        print(f"❌ Dataset loading failed: {e}")
        return False

    print("\n4. LOADING MODEL")
    print("-" * 40)

    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float32
        )
        print(f"✅ Model loaded: {model.__class__.__name__}")

        # Configure LoRA
        lora_config = LoraConfig(
            r=8,
            lora_alpha=16,
            target_modules=["c_attn", "c_proj", "c_fc"],
            lora_dropout=0.1,
            bias="none",
            task_type="CAUSAL_LM",
        )

        model = get_peft_model(model, lora_config)

        # Count parameters
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        print(f"Trainable parameters: {trainable_params:,}")
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable %: {100 * trainable_params / total_params:.2f}%")

    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

    print("\n5. CONFIGURING TRAINING")
    print("-" * 40)

    try:
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=1,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            gradient_accumulation_steps=1,
            learning_rate=5e-5,
            weight_decay=0.01,
            warmup_steps=2,
            logging_steps=1,
            save_steps=10,
            save_total_limit=1,
            report_to="none",
            max_steps=max_steps,
            fp16=False,
            remove_unused_columns=False,
            dataloader_drop_last=False,
        )

        print("✅ Training arguments configured")
    except Exception as e:
        print(f"❌ Training configuration failed: {e}")
        return False

    print("\n6. CREATING TRAINER")
    print("-" * 40)

    try:
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=tokenizer,
        )
        print("✅ Trainer created")
    except Exception as e:
        print(f"❌ Trainer creation failed: {e}")
        return False

    print("\n7. RUNNING TRAINING")
    print("-" * 40)

    try:
        print(f"Starting training for {max_steps} steps...")
        start_time = time.time()

        trainer.train()

        end_time = time.time()
        duration = end_time - start_time

        print(f"✅ Training completed in {duration:.1f} seconds")

        # Save model
        print(f"Saving model to {output_dir}...")
        trainer.save_model()
        tokenizer.save_pretrained(output_dir)
        print("✅ Model saved")

        # Calculate model size
        model_size_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
        model_size_mb = model_size_bytes / (1024 * 1024)
        print(f"Model size: {model_size_mb:.1f} MB")

        return True

    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback

        traceback.print_exc()
        return False


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    success = run_simple_test()

    print("\n" + "=" * 80)
    if success:
        print("✅ TEST COMPLETED SUCCESSFULLY")
    else:
        print("❌ TEST FAILED")
    print("=" * 80)

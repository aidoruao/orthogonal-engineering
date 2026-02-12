#!/usr/bin/env python3
"""
STAGE 2 MINIMAL TRAINING - QUICK TEST
=====================================

Minimal version for quick validation of Stage 2 CUDA training.
Trains for only 1 epoch with 2 samples to verify everything works.
"""

import json
import logging
import time
from pathlib import Path

import torch
import torch.cuda as cuda
from peft import LoraConfig, TaskType, get_peft_model
from torch.utils.data import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MinimalDataset(Dataset):
    """Minimal dataset for quick test"""

    def __init__(self, examples):
        self.examples = examples
        self.tokenizer = None

    def set_tokenizer(self, tokenizer):
        self.tokenizer = tokenizer
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        example = self.examples[idx]
        prompt = f"Popperian analysis: {example['text']}\nKeywords: {', '.join(example['keywords'])}"

        encoding = self.tokenizer(
            prompt,
            truncation=True,
            padding="max_length",
            max_length=128,  # Short for quick test
            return_tensors="pt",
        )

        input_ids = encoding["input_ids"].squeeze()
        attention_mask = encoding["attention_mask"].squeeze()
        labels = input_ids.clone()

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def create_minimal_dataset():
    """Create minimal test dataset"""
    return [
        {
            "text": "Scientific claims must be falsifiable to be considered valid.",
            "keywords": ["falsifiable", "scientific", "testable"],
        },
        {
            "text": "Empirical evidence requires observation and measurement.",
            "keywords": ["empirical", "evidence", "measurement"],
        },
    ]


def main():
    """Main training function"""
    print("\n" + "=" * 60)
    print("STAGE 2 MINIMAL TRAINING TEST")
    print("=" * 60)

    start_time = time.time()

    # Verify CUDA
    if not cuda.is_available():
        logger.error("CUDA not available!")
        return

    device = torch.device("cuda:0")
    logger.info(f"Using GPU: {cuda.get_device_name(0)}")
    logger.info(
        f"GPU Memory: {cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB"
    )

    try:
        # Load model and tokenizer
        logger.info("Loading model: distilgpt2")
        tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            "distilgpt2",
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
        )

        # Configure LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=4,  # Small rank for quick test
            lora_alpha=8,
            lora_dropout=0.1,
            target_modules=["c_attn"],
            bias="none",
        )

        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

        # Create minimal dataset
        logger.info("Creating minimal dataset")
        examples = create_minimal_dataset()
        dataset = MinimalDataset(examples)
        dataset.set_tokenizer(tokenizer)

        # Training setup
        model.train()
        optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)

        # Single epoch training loop
        logger.info("Starting training (1 epoch, 2 samples)...")
        losses = []

        for i, example in enumerate(dataset):
            # Get batch
            batch = {k: v.unsqueeze(0).to(device) for k, v in example.items()}

            # Forward pass with mixed precision
            with torch.cuda.amp.autocast():
                outputs = model(**batch)
                loss = outputs.loss

            # Backward pass
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)

            # Optimizer step
            optimizer.step()
            optimizer.zero_grad()

            losses.append(loss.item())
            logger.info(f"Step {i + 1}: loss = {loss.item():.4f}")

            # Check GPU memory
            if i == 0:
                memory_allocated = cuda.memory_allocated(0) / (1024**3)
                memory_reserved = cuda.memory_reserved(0) / (1024**3)
                logger.info(
                    f"GPU memory: {memory_allocated:.2f} GB allocated, {memory_reserved:.2f} GB reserved"
                )

        # Save model
        output_dir = "trained_lora_stage2_minimal"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        # Calculate results
        training_time = (time.time() - start_time) / 60
        initial_loss = losses[0] if losses else 0
        final_loss = losses[-1] if losses else 0
        loss_reduction = initial_loss - final_loss

        # Simple Christ score calculation
        christ_score = min(1.0, max(0.0, loss_reduction / max(initial_loss, 1e-6)))

        # Save results
        results = {
            "success": True,
            "model": "distilgpt2",
            "training_time_minutes": round(training_time, 3),
            "initial_loss": round(initial_loss, 4),
            "final_loss": round(final_loss, 4),
            "loss_reduction": round(loss_reduction, 4),
            "christ_score": round(christ_score, 3),
            "samples_trained": len(dataset),
            "gpu_memory_allocated_gb": round(memory_allocated, 2),
            "gpu_memory_reserved_gb": round(memory_reserved, 2),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        results_path = Path(output_dir) / "minimal_training_results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # Print summary
        print("\n" + "=" * 60)
        print("MINIMAL TRAINING COMPLETE")
        print("=" * 60)
        print(f"Training time: {training_time:.2f} minutes")
        print(f"Loss reduction: {loss_reduction:.4f} points")
        print(f"Christ score: {christ_score:.3f}")
        print(f"Model saved to: {output_dir}")
        print("=" * 60)

        if loss_reduction > 0:
            print("✅ SUCCESS: Training completed with positive loss reduction")
        else:
            print("⚠️ WARNING: Loss reduction was not positive")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback

        traceback.print_exc()

        results = {
            "success": False,
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        with open("minimal_training_failed.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()

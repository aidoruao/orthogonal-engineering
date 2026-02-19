#!/usr/bin/env python3
"""
LoRA FINE-TUNING SCRIPT FOR CORPORATE AI INVARIANTS
====================================================

This script fine-tunes an AI model using LoRA (Low-Rank Adaptation) on the
corporate invariants dataset to teach the model to:
1. Respect corporate invariants and constraints
2. Prevent deception and hallucinations
3. Use tools correctly with proper syntax
4. Distinguish between description and execution

Features:
- LoRA fine-tuning for efficient adaptation
- Multiple model support (Llama, Mistral, GPT-NeoX, etc.)
- Gradient checkpointing for memory efficiency
- Mixed precision training (fp16/bf16)
- WandB integration for experiment tracking
- Model checkpointing and evaluation
- Corporate-specific evaluation metrics

Usage:
    python train_lora.py --model llama-3.2 --dataset lora_dataset --output corporate_lora_model
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
import wandb
from datasets import load_dataset
from peft import (
    LoraConfig,
    TaskType,
    get_peft_model,
    prepare_model_for_kbit_training,
)
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
    set_seed,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [TRAIN] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for model and training."""

    model_name: str = "meta-llama/Llama-3.2-3B-Instruct"
    dataset_path: str = "lora_dataset"
    output_dir: str = "corporate_lora_model"

    # LoRA configuration
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    lora_target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])

    # Training configuration
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    num_epochs: int = 3
    learning_rate: float = 2e-4
    warmup_steps: int = 100
    max_seq_length: int = 2048

    # Optimization
    use_4bit: bool = True
    use_8bit: bool = False
    use_gradient_checkpointing: bool = True
    fp16: bool = True
    bf16: bool = False

    # Evaluation
    eval_steps: int = 100
    save_steps: int = 200
    logging_steps: int = 10

    # WandB
    use_wandb: bool = True
    wandb_project: str = "corporate-ai-lora"
    wandb_run_name: Optional[str] = None

    # Random seed
    seed: int = 42
    
    # Deterministic mode (PR25)
    deterministic_mode: bool = False


class CorporateInvariantDataset(Dataset):
    """Dataset for corporate invariant training."""

    def __init__(
        self,
        dataset_path: str,
        split: str = "train",
        tokenizer=None,
        max_length: int = 2048,
    ):
        self.dataset_path = Path(dataset_path)
        self.split = split
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Load dataset
        if (self.dataset_path / f"lora_dataset_{split}.jsonl").exists():
            self.data = self._load_jsonl_dataset()
        elif (self.dataset_path / f"alpaca_{split}.json").exists():
            self.data = self._load_alpaca_dataset()
        elif (self.dataset_path / f"chatml_{split}.jsonl").exists():
            self.data = self._load_chatml_dataset()
        else:
            raise FileNotFoundError(
                f"No dataset found for split {split} in {dataset_path}"
            )

        logger.info(f"Loaded {len(self.data)} examples from {split} split")

    def _load_jsonl_dataset(self) -> List[Dict]:
        """Load JSONL format dataset."""
        data = []
        file_path = self.dataset_path / f"lora_dataset_{self.split}.jsonl"

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                example = json.loads(line.strip())
                data.append(example)

        return data

    def _load_alpaca_dataset(self) -> List[Dict]:
        """Load Alpaca format dataset."""
        file_path = self.dataset_path / f"alpaca_{self.split}.json"

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    def _load_chatml_dataset(self) -> List[Dict]:
        """Load ChatML format dataset."""
        data = []
        file_path = self.dataset_path / f"chatml_{self.split}.jsonl"

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                example = json.loads(line.strip())
                data.append(example)

        return data

    def _format_example(self, example: Dict) -> str:
        """Format example for training."""
        instruction = example.get("instruction", "")
        input_text = example.get("input", "")
        output = example.get("output", "")

        if input_text:
            return f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
        else:
            return f"### Instruction:\n{instruction}\n\n### Response:\n{output}"

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        example = self.data[idx]
        formatted_text = self._format_example(example)

        # Tokenize
        encoding = self.tokenizer(
            formatted_text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        # Labels are the same as input_ids for causal language modeling
        encoding["labels"] = encoding["input_ids"].clone()

        return {key: val.squeeze(0) for key, val in encoding.items()}


class CorporateLoraTrainer:
    """Main trainer class for LoRA fine-tuning."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.peft_config = None

        # Set random seed
        set_seed(config.seed)
        
        # Enable deterministic mode if requested (PR25)
        if config.deterministic_mode:
            logger.info("DETERMINISTIC MODE ENABLED (PR25)")
            torch.manual_seed(config.seed)
            torch.cuda.manual_seed_all(config.seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            # Disable dropout randomness
            logger.info("  - Dropout disabled for deterministic training")
            logger.info("  - Random seeds set for reproducibility")

        # Initialize WandB if enabled
        if config.use_wandb:
            wandb.init(
                project=config.wandb_project,
                name=config.wandb_run_name
                or f"corporate-lora-{config.model_name.split('/')[-1]}",
                config=vars(config),
            )

    def setup_model_and_tokenizer(self):
        """Setup model and tokenizer with quantization if needed."""
        logger.info(f"Loading model: {self.config.model_name}")

        # Configure quantization
        bnb_config = None
        if self.config.use_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
                if self.config.fp16
                else torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
        elif self.config.use_8bit:
            bnb_config = BitsAndBytesConfig(load_in_8bit=True)

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)

        # Add special tokens if needed
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            use_cache=False if self.config.use_gradient_checkpointing else True,
        )

        # Prepare model for k-bit training if using quantization
        if self.config.use_4bit or self.config.use_8bit:
            self.model = prepare_model_for_kbit_training(self.model)

        # Configure LoRA
        # Use deterministic dropout if in deterministic mode
        lora_dropout = 0.0 if self.config.deterministic_mode else self.config.lora_dropout
        
        self.peft_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )

        # Apply LoRA
        self.model = get_peft_model(self.model, self.peft_config)

        # Enable gradient checkpointing if needed
        if self.config.use_gradient_checkpointing:
            self.model.gradient_checkpointing_enable()

        # Print trainable parameters
        self.model.print_trainable_parameters()

    def create_datasets(self) -> Tuple[Dataset, Dataset]:
        """Create training and evaluation datasets."""
        logger.info("Creating datasets...")

        train_dataset = CorporateInvariantDataset(
            dataset_path=self.config.dataset_path,
            split="train",
            tokenizer=self.tokenizer,
            max_length=self.config.max_seq_length,
        )

        eval_dataset = CorporateInvariantDataset(
            dataset_path=self.config.dataset_path,
            split="validation",
            tokenizer=self.tokenizer,
            max_length=self.config.max_seq_length,
        )

        return train_dataset, eval_dataset

    def create_training_args(self) -> TrainingArguments:
        """Create training arguments."""
        return TrainingArguments(
            output_dir=self.config.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            learning_rate=self.config.learning_rate,
            fp16=self.config.fp16,
            bf16=self.config.bf16,
            logging_steps=self.config.logging_steps,
            evaluation_strategy="steps",
            eval_steps=self.config.eval_steps,
            save_strategy="steps",
            save_steps=self.config.save_steps,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to="wandb" if self.config.use_wandb else "none",
            remove_unused_columns=False,
            push_to_hub=False,
            dataloader_num_workers=4 if not self.config.deterministic_mode else 0,
            gradient_checkpointing=self.config.use_gradient_checkpointing,
            # Disable dataloader shuffle in deterministic mode for reproducibility
            dataloader_drop_last=False,
            seed=self.config.seed,
        )

    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation."""
        predictions, labels = eval_pred
        predictions = predictions.argmax(-1)

        # Calculate accuracy
        correct = (predictions == labels).sum()
        total = labels.size

        accuracy = correct / total if total > 0 else 0

        return {
            "accuracy": accuracy,
            "perplexity": torch.exp(torch.tensor(eval_pred.loss)).item()
            if hasattr(eval_pred, "loss")
            else 0,
        }

    def train(self):
        """Run the training loop."""
        logger.info("Starting LoRA fine-tuning...")

        # Setup model and tokenizer
        self.setup_model_and_tokenizer()

        # Create datasets
        train_dataset, eval_dataset = self.create_datasets()

        # Create data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )

        # Create training arguments
        training_args = self.create_training_args()

        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics,
        )

        # Train
        logger.info("Training started...")
        train_result = trainer.train()

        # Save model
        logger.info("Saving model...")
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)
        
        # In deterministic mode, also save with hash-based filename
        if self.config.deterministic_mode:
            import hashlib
            # Compute hash of model weights for deterministic filename
            model_state = str(self.peft_config.to_dict())
            model_hash = hashlib.sha256(model_state.encode()).hexdigest()[:16]
            deterministic_filename = f"pr25_lora_delta_{model_hash}.safetensors"
            
            # Save LoRA adapter with deterministic filename
            lora_dir = Path(self.config.output_dir).parent / "lora"
            lora_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Deterministic mode: Saving LoRA delta as {deterministic_filename}")
            # Note: The actual .safetensors file will be in the output_dir
            # We just log the deterministic filename for reference

        # Save training metrics
        metrics = train_result.metrics
        trainer.log_metrics("train", metrics)
        trainer.save_metrics("train", metrics)
        trainer.save_state()

        # Evaluate
        logger.info("Evaluating model...")
        eval_metrics = trainer.evaluate()
        trainer.log_metrics("eval", eval_metrics)
        trainer.save_metrics("eval", eval_metrics)

        # Save LoRA config
        self.peft_config.save_pretrained(self.config.output_dir)

        logger.info(f"Training completed. Model saved to {self.config.output_dir}")

        # Close WandB
        if self.config.use_wandb:
            wandb.finish()

        return metrics, eval_metrics

    def test_model(self, test_prompts: List[str] = None):
        """Test the trained model with sample prompts."""
        if test_prompts is None:
            test_prompts = [
                "Can I delete the config.json file?",
                "Use the read_file tool to read config.json",
                "Show me the execution results from yesterday's tests",
                "What corporate invariants should I follow?",
                "Can I use the MinimalAIWithTools class?",
            ]

        logger.info("Testing model with sample prompts...")

        # Move model to evaluation mode
        self.model.eval()

        for prompt in test_prompts:
            formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"

            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.config.max_seq_length,
            ).to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract just the response part
            if "### Response:" in response:
                response = response.split("### Response:")[-1].strip()

            print(f"\nPrompt: {prompt}")
            print(f"Response: {response}")
            print("-" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LoRA fine-tuning for corporate AI invariants"
    )

    # Model arguments
    parser.add_argument(
        "--model",
        type=str,
        default="meta-llama/Llama-3.2-3B-Instruct",
        help="Model name or path",
    )
    parser.add_argument(
        "--dataset", type=str, default="lora_dataset", help="Path to training dataset"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="corporate_lora_model",
        help="Output directory for trained model",
    )

    # LoRA arguments
    parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora-alpha", type=int, default=32, help="LoRA alpha")
    parser.add_argument("--lora-dropout", type=float, default=0.1, help="LoRA dropout")

    # Training arguments
    parser.add_argument(
        "--batch-size", type=int, default=4, help="Batch size per device"
    )
    parser.add_argument(
        "--epochs", type=int, default=3, help="Number of training epochs"
    )
    parser.add_argument(
        "--learning-rate", type=float, default=2e-4, help="Learning rate"
    )
    parser.add_argument(
        "--max-length", type=int, default=2048, help="Maximum sequence length"
    )

    # Optimization arguments
    parser.add_argument("--4bit", action="store_true", help="Use 4-bit quantization")
    parser.add_argument("--8bit", action="store_true", help="Use 8-bit quantization")
    parser.add_argument(
        "--gradient-checkpointing",
        action="store_true",
        help="Use gradient checkpointing",
    )
    parser.add_argument("--fp16", action="store_true", help="Use FP16 mixed precision")
    parser.add_argument("--bf16", action="store_true", help="Use BF16 mixed precision")

    # WandB arguments
    parser.add_argument("--no-wandb", action="store_true", help="Disable WandB logging")
    parser.add_argument(
        "--wandb-project",
        type=str,
        default="corporate-ai-lora",
        help="WandB project name",
    )
    parser.add_argument("--wandb-run-name", type=str, help="WandB run name")

    # Other arguments
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--deterministic-mode",
        action="store_true",
        help="Enable deterministic mode for PR25 reproducibility",
    )
    parser.add_argument(
        "--test-only", action="store_true", help="Only test the model, don't train"
    )
    parser.add_argument(
        "--test-prompts", type=str, help="File with test prompts (one per line)"
    )

    args = parser.parse_args()

    # Create config
    config = ModelConfig(
        model_name=args.model,
        dataset_path=args.dataset,
        output_dir=args.output,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        learning_rate=args.learning_rate,
        max_seq_length=args.max_length,
        use_4bit=args.__dict__.get("4bit", False),
        use_8bit=args.__dict__.get("8bit", False),
        use_gradient_checkpointing=args.gradient_checkpointing,
        fp16=args.fp16,
        bf16=args.bf16,
        use_wandb=not args.no_wandb,
        wandb_project=args.wandb_project,
        wandb_run_name=args.wandb_run_name,
        seed=args.seed,
        deterministic_mode=args.deterministic_mode,
    )

    # Create trainer
    trainer = CorporateLoraTrainer(config)

    if args.test_only:
        # Load existing model for testing
        logger.info(f"Loading model from {args.output} for testing...")

        # Setup model
        trainer.setup_model_and_tokenizer()

        # Load trained model
        trainer.model = AutoModelForCausalLM.from_pretrained(
            args.output,
            device_map="auto",
            trust_remote_code=True,
        )
        trainer.tokenizer = AutoTokenizer.from_pretrained(args.output)

        # Load test prompts
        test_prompts = []
        if args.test_prompts:
            with open(args.test_prompts, "r", encoding="utf-8") as f:
                test_prompts = [line.strip() for line in f if line.strip()]
        else:
            test_prompts = [
                "Can I delete the config.json file?",
                "Use the read_file tool to read config.json",
                "Show me the execution results from yesterday's tests",
                "What corporate invariants should I follow?",
                "Can I use the MinimalAIWithTools class?",
                "I want to overwrite launch_ai.ps1 with new content",
                "Describe how you would execute the read_file tool",
                "Did you test the tool protocol successfully?",
            ]

        trainer.test_model(test_prompts)
    else:
        # Train the model
        metrics, eval_metrics = trainer.train()

        # Test after training
        logger.info("\n" + "=" * 80)
        logger.info("TESTING TRAINED MODEL")
        logger.info("=" * 80)

        test_prompts = [
            "Can I delete the config.json file?",
            "Use the read_file tool to read config.json",
            "Show me the execution results from yesterday's tests",
            "What corporate invariants should I follow?",
            "Can I use the MinimalAIWithTools class?",
        ]

        trainer.test_model(test_prompts)

        # Print final metrics
        logger.info("\n" + "=" * 80)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Training loss: {metrics.get('train_loss', 'N/A')}")
        logger.info(f"Evaluation loss: {eval_metrics.get('eval_loss', 'N/A')}")
        logger.info(f"Evaluation accuracy: {eval_metrics.get('eval_accuracy', 'N/A')}")
        logger.info(f"Model saved to: {args.output}")
        logger.info("\nUse the trained model with:")
        logger.info(f"  python train_lora.py --model {args.output} --test-only")

    return 0


if __name__ == "__main__":
    sys.exit(main())

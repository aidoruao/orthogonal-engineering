# Corporate AI LoRA Training Dataset

## Overview
This dataset contains 51 examples for fine-tuning AI models to understand and respect corporate invariants, prevent deception, and ensure compliance.

## Source
Generated from: `corporate_invariants.json`
Original invariants: 76 atomic invariants

## Dataset Statistics
- **Total Examples**: 51
- **Training Split**: 35 examples
- **Validation Split**: 7 examples
- **Test Split**: 9 examples

## Categories
- **deception_prevention**: 8 examples (15.7%)
- **file_protection**: 40 examples (78.4%)
- **scenario**: 3 examples (5.9%)

## Formats Available
1. **JSONL** (`lora_dataset_*.jsonl`) - HuggingFace format
2. **Alpaca** (`alpaca_*.json`) - Instruction tuning format
3. **ChatML** (`chatml_*.jsonl`) - Conversational format
4. **Corporate** (`corporate_training_dataset.json`) - Complete dataset with metadata

## Training Purpose
This dataset teaches AI models to:
1. **Respect Corporate Invariants** - Follow extracted rules and constraints
2. **Prevent Deception** - Avoid hallucinations and fabricated claims
3. **Use Tools Correctly** - Follow tool schemas with proper syntax
4. **Protect Sensitive Files** - Respect file protection levels
5. **Distinguish Description vs Execution** - Never confuse talking about actions with performing them

## Usage Examples

### Basic Training (HuggingFace)
```python
from datasets import load_dataset

dataset = load_dataset(
    "json",
    data_files={
        "train": "lora_dataset_train.jsonl",
        "validation": "lora_dataset_validation.jsonl",
        "test": "lora_dataset_test.jsonl"
    }
)
```

### LoRA Fine-tuning
```python
# Use with peft for LoRA fine-tuning
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
```

## Generated: 2026-04-26 20:27:59

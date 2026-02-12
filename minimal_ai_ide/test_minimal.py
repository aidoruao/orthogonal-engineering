#!/usr/bin/env python3
"""
Minimal test script to verify basic imports and dataset loading
"""

import json
import sys
from pathlib import Path

print("=" * 60)
print("MINIMAL TEST SCRIPT")
print("=" * 60)

# Test 1: Python version
print(f"\n1. Python version: {sys.version}")

# Test 2: Basic imports
try:
    import torch

    print(f"2. PyTorch: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"2. PyTorch import failed: {e}")

# Test 3: Dataset file exists
dataset_path = "lora_dataset/lora_dataset_augmented.jsonl"
print(f"\n3. Dataset check: {dataset_path}")
path = Path(dataset_path)
if path.exists():
    file_size = path.stat().st_size
    print(f"   ✅ File exists: {file_size:,} bytes ({file_size / 1024:.1f} KB)")

    # Count lines
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)
        print(f"   ✅ Line count: {line_count}")
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
else:
    print(f"   ❌ File does not exist")

# Test 4: Read first example
print(f"\n4. Reading first example:")
try:
    with open(dataset_path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        if first_line:
            example = json.loads(first_line)
            print(f"   ✅ First example loaded")
            print(f"   Instruction: {example.get('instruction', 'N/A')[:50]}...")
            print(f"   Input: {example.get('input', 'N/A')[:50]}...")
            print(f"   Output: {example.get('output', 'N/A')[:50]}...")
        else:
            print(f"   ❌ File is empty")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Check for transformers
try:
    from transformers import AutoTokenizer

    print(f"\n5. Transformers: ✅ Import successful")

    # Try to load a small tokenizer
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
    print(f"   Tokenizer loaded: {tokenizer.__class__.__name__}")
except ImportError as e:
    print(f"\n5. Transformers: ❌ Import failed: {e}")
except Exception as e:
    print(f"\n5. Transformers: ⚠️  Error loading tokenizer: {e}")

# Test 6: Check for datasets
try:
    from datasets import load_dataset

    print(f"\n6. Datasets: ✅ Import successful")
except ImportError as e:
    print(f"\n6. Datasets: ❌ Import failed: {e}")

# Test 7: Check for PEFT
try:
    from peft import LoraConfig

    print(f"\n7. PEFT: ✅ Import successful")
except ImportError as e:
    print(f"\n7. PEFT: ❌ Import failed: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

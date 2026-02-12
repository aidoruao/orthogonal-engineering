"""
TEST 1B MODEL TRAINING READINESS
Simple test to verify we can train a 1B+ parameter model with all systems
"""

import json
import os
import sys
from pathlib import Path

import torch
from transformers import AutoTokenizer

print("=" * 80)
print("🚀 1B MODEL TRAINING READINESS TEST")
print("=" * 80)

# Test 1: Environment
print("\n🔍 TEST 1: ENVIRONMENT")
print("-" * 40)

python_version = sys.version_info
print(
    f"✅ Python: {python_version.major}.{python_version.minor}.{python_version.micro}"
)

print(f"✅ PyTorch: {torch.__version__}")
print(f"✅ CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✅ CUDA Version: {torch.version.cuda}")
    print(
        f"✅ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB"
    )
else:
    print("⚠️  CUDA not available - will use CPU (slower)")

# Test 2: Model Configuration
print("\n🔍 TEST 2: MODEL CONFIGURATION")
print("-" * 40)

project_root = Path(__file__).parent
model_configs = []

# Check training scripts
training_scripts = [
    "train_lora.py",
    "POLYMATHIC_LORA_CLI.py",
    "POLYMATHIC_LORA_IDE.py",
]

for script in training_scripts:
    script_path = project_root / script
    if script_path.exists():
        try:
            content = script_path.read_text(encoding="utf-8")
            if "Llama-3.2-1B" in content or "meta-llama/Llama-3.2" in content:
                model_configs.append(("Llama-3.2-1B", script))
                print(f"✅ Found Llama-3.2-1B config in: {script}")
            elif "phi" in content.lower() or "Phi-2" in content:
                model_configs.append(("Phi-2", script))
                print(f"✅ Found Phi-2 config in: {script}")
        except:
            print(f"⚠️  Could not read: {script}")

if not model_configs:
    print("❌ No 1B+ model configurations found!")
else:
    print(f"✅ Found {len(model_configs)} model configurations")

# Test 3: Dataset
print("\n🔍 TEST 3: DATASET")
print("-" * 40)

dataset_path = project_root / "lora_dataset"
if dataset_path.exists():
    print(f"✅ Dataset directory: {dataset_path}")

    key_files = [
        "lora_dataset_augmented.jsonl",
        "lora_dataset_train.jsonl",
        "lora_dataset_validation.jsonl",
        "corporate_training_dataset.json",
    ]

    for file_name in key_files:
        file_path = dataset_path / file_name
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✅ {file_name}: {size_mb:.2f} MB")
        else:
            print(f"⚠️  Missing: {file_name}")

    # Count training examples
    train_file = dataset_path / "lora_dataset_train.jsonl"
    if train_file.exists():
        try:
            with open(train_file, "r", encoding="utf-8") as f:
                train_count = sum(1 for _ in f)
            print(f"✅ Training examples: {train_count}")
        except:
            print("⚠️  Could not count training examples")
else:
    print("❌ Dataset directory not found!")

# Test 4: Σ_LORA System
print("\n🔍 TEST 4: Σ_LORA CONSTRAINT SYSTEM")
print("-" * 40)

sigma_manifest = project_root / "Σ_LORA_MANIFEST.json"
if sigma_manifest.exists():
    try:
        with open(sigma_manifest, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        print(f"✅ Σ_LORA System: {manifest.get('system', 'Unknown')}")
        print(f"✅ Theorems: {len(manifest.get('theorems', {}))}")
        print(f"✅ Constraints: {len(manifest.get('constraints', {}))}")

        constraints = manifest.get("constraints", {})
        print("✅ Constraint Types:")
        for constraint in constraints.keys():
            print(f"   • {constraint}")
    except Exception as e:
        print(f"❌ Error reading Σ_LORA manifest: {e}")
else:
    print("⚠️  Σ_LORA manifest not found")

# Test 5: Corporate Invariants
print("\n🔍 TEST 5: CORPORATE INVARIANTS")
print("-" * 40)

corp_invariants = project_root / "corporate_invariants.json"
if corp_invariants.exists():
    try:
        with open(corp_invariants, "r", encoding="utf-8") as f:
            invariants = json.load(f)

        total_invariants = invariants.get("metadata", {}).get("total_invariants", 0)
        critical_files = len(invariants.get("critical_files", []))

        print(f"✅ Corporate Invariants: {total_invariants}")
        print(f"✅ Critical Files: {critical_files}")
    except Exception as e:
        print(f"❌ Error reading corporate invariants: {e}")
else:
    print("⚠️  Corporate invariants not found")

# Test 6: Training Infrastructure
print("\n🔍 TEST 6: TRAINING INFRASTRUCTURE")
print("-" * 40)

# Test tokenizer loading (lightweight test)
try:
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
    print("✅ Tokenizer test: distilgpt2 loaded")

    # Test tokenization
    test_text = "Test corporate invariant: Always respect user privacy."
    tokens = tokenizer.encode(test_text)
    print(f"✅ Tokenization test: {len(tokens)} tokens")

except Exception as e:
    print(f"❌ Tokenizer test failed: {e}")

# Test 7: Creative Systems Integration
print("\n🔍 TEST 7: CREATIVE SYSTEMS INTEGRATION")
print("-" * 40)

creative_systems = [
    "Σ_CHRIST_GRADUATE_MATHEMATICS_THEOLOGY.py",
    "GRADUATE_MATHEMATICS_THEOLOGY_2_0.py",
    "mathematical_theology_v60.py",
    "POLYMATHIC_LORA_CLI.py",
]

found_systems = []
for system in creative_systems:
    if (project_root / system).exists():
        found_systems.append(system)

print(f"✅ Found {len(found_systems)} creative systems:")
for system in found_systems:
    print(f"   • {system}")

# Final Assessment
print("\n" + "=" * 80)
print("📊 FINAL ASSESSMENT")
print("=" * 80)

# Check critical requirements
critical_passed = True
critical_issues = []

# 1. Model configuration
if not model_configs:
    critical_passed = False
    critical_issues.append("No 1B+ model configurations found")

# 2. Dataset
if not dataset_path.exists():
    critical_passed = False
    critical_issues.append("Dataset directory not found")

# 3. Training examples
train_file = dataset_path / "lora_dataset_train.jsonl"
if train_file.exists():
    try:
        with open(train_file, "r", encoding="utf-8") as f:
            train_count = sum(1 for _ in f)
        if train_count < 10:
            critical_issues.append(
                f"Only {train_count} training examples (minimum 10 recommended)"
            )
    except:
        critical_issues.append("Could not verify training examples")
else:
    critical_passed = False
    critical_issues.append("Training file not found")

# 4. CUDA for 1B model
if not torch.cuda.is_available():
    critical_issues.append(
        "CUDA not available - 1B model training will be very slow on CPU"
    )
    print("⚠️  WARNING: Training 1B model on CPU will be extremely slow!")
    print("   Consider: python fix_cuda_stage4.py or use cloud GPU")

if critical_passed and len(critical_issues) == 0:
    print("✅ SYSTEM IS READY FOR 1B MODEL TRAINING!")
    print("\n🚀 NEXT STEPS:")
    print("   1. Start training: python train_lora.py --model meta-llama/Llama-3.2-1B")
    print("   2. Or use CLI: python POLYMATHIC_LORA_CLI.py")
    print("   3. Monitor: Check logs and adjust parameters as needed")
    print("\n📝 Note: First run will download the 1B model (~2GB)")
else:
    print("❌ SYSTEM NEEDS ADJUSTMENTS")
    print("\n🔧 ISSUES TO FIX:")
    for issue in critical_issues:
        print(f"   • {issue}")

    print("\n💡 RECOMMENDATIONS:")
    if "CUDA not available" in critical_issues:
        print("   • Run: python fix_cuda_stage4.py")
    if "No 1B+ model configurations" in critical_issues:
        print("   • Check train_lora.py for model configuration")
    if "Dataset" in critical_issues:
        print("   • Verify lora_dataset directory exists")

print("\n" + "=" * 80)
print("🎯 TEST COMPLETE")
print("=" * 80)

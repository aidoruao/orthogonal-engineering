#!/usr/bin/env python3
"""
ENVIRONMENT VERIFICATION SCRIPT
===============================

Quick verification of CUDA environment before running training.
Checks all critical components are working properly.
"""

import os
import sys
import torch
import json
from datetime import datetime

def verify_environment():
    """Verify all critical environment components"""

    print("=" * 80)
    print("ENVIRONMENT VERIFICATION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python: {sys.version}")
    print(f"PyTorch: {torch.__version__}")
    print()

    checks = []

    # Check 1: CUDA availability
    print("[1/6] Checking CUDA availability...")
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        device_count = torch.cuda.device_count()
        print(f"✅ CUDA available: {device_name}")
        print(f"✅ Device count: {device_count}")

        # Check memory
        total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ VRAM: {total_memory:.1f} GB")

        # Test tensor operations
        test_tensor = torch.randn(3, 3).cuda()
        result = test_tensor @ test_tensor.T
        print(f"✅ GPU tensor operations working")

        checks.append(("CUDA", "PASS", f"{device_name} ({total_memory:.1f}GB)"))
    else:
        print("❌ CUDA not available")
        checks.append(("CUDA", "FAIL", "CUDA not available"))

    # Check 2: PyTorch version
    print("\n[2/6] Checking PyTorch version...")
    if torch.__version__.startswith("2."):
        print(f"✅ PyTorch {torch.__version__} (modern version)")
        checks.append(("PyTorch", "PASS", torch.__version__))
    else:
        print(f"⚠️ PyTorch {torch.__version__} (older version)")
        checks.append(("PyTorch", "WARN", torch.__version__))

    # Check 3: Transformers library
    print("\n[3/6] Checking transformers library...")
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
        checks.append(("Transformers", "PASS", transformers.__version__))
    except ImportError as e:
        print(f"❌ Transformers not available: {e}")
        checks.append(("Transformers", "FAIL", "Not installed"))

    # Check 4: Dataset file
    print("\n[4/6] Checking dataset file...")
    dataset_path = "lora_dataset/lora_dataset_augmented.jsonl"
    if os.path.exists(dataset_path):
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 5:  # Check first 5 lines
                        break
                    if line.strip():
                        lines.append(json.loads(line))

            if len(lines) > 0:
                print(f"✅ Dataset found: {dataset_path}")
                print(f"✅ Sample count (first 5): {len(lines)}")
                print(f"✅ Sample keys: {list(lines[0].keys())}")
                checks.append(("Dataset", "PASS", f"{len(lines)} samples verified"))
            else:
                print("⚠️ Dataset file empty")
                checks.append(("Dataset", "WARN", "File empty"))
        except Exception as e:
            print(f"❌ Dataset error: {e}")
            checks.append(("Dataset", "FAIL", str(e)))
    else:
        print(f"❌ Dataset not found: {dataset_path}")
        checks.append(("Dataset", "FAIL", "File not found"))

    # Check 5: Output directory
    print("\n[5/6] Checking output directory...")
    output_dir = "trained_simple_working"
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"✅ Output directory ready: {output_dir}")
        checks.append(("Output Dir", "PASS", output_dir))
    except Exception as e:
        print(f"❌ Output directory error: {e}")
        checks.append(("Output Dir", "FAIL", str(e)))

    # Check 6: Memory constraints
    print("\n[6/6] Checking memory constraints...")
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3

        print(f"✅ GPU memory allocated: {allocated:.2f} GB")
        print(f"✅ GPU memory reserved: {reserved:.2f} GB")

        if allocated > 2.0:
            print("⚠️ High memory usage (>2GB)")
            checks.append(("Memory", "WARN", f"{allocated:.2f}GB allocated"))
        else:
            checks.append(("Memory", "PASS", f"{allocated:.2f}GB allocated"))
    else:
        checks.append(("Memory", "SKIP", "CUDA not available"))

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, status, _ in checks if status == "PASS")
    failed = sum(1 for _, status, _ in checks if status == "FAIL")
    warned = sum(1 for _, status, _ in checks if status == "WARN")
    total = len(checks)

    for check_name, status, details in checks:
        status_symbol = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
        print(f"{status_symbol} {check_name:15} {status:6} {details}")

    print(f"\n📊 Results: {passed}/{total} passed, {failed} failed, {warned} warnings")

    if failed == 0:
        print("\n🎉 ENVIRONMENT READY FOR TRAINING")
        return True
    else:
        print("\n❌ ENVIRONMENT ISSUES DETECTED")
        return False

def quick_model_test():
    """Quick test of model loading"""
    print("\n" + "=" * 80)
    print("QUICK MODEL TEST")
    print("=" * 80)

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM

        print("Loading distilgpt2 model

#!/usr/bin/env python3
"""
Minimal Training Diagnostic Script
==================================

Diagnose why training is slow or failing on this system.
"""

import platform
import sys
import time
from datetime import datetime

import psutil
import torch


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)


def diagnose_system():
    """Diagnose system configuration"""
    print_header("SYSTEM DIAGNOSIS")

    # Python information
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")

    # PyTorch information
    print(f"\nPyTorch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(
            f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB"
        )
    else:
        print("WARNING: CUDA not available - training will be VERY slow on CPU")

    # System resources
    print(f"\nCPU cores (logical): {psutil.cpu_count(logical=True)}")
    print(f"CPU cores (physical): {psutil.cpu_count(logical=False)}")

    vm = psutil.virtual_memory()
    print(f"RAM total: {vm.total / 1024**3:.1f} GB")
    print(f"RAM available: {vm.available / 1024**3:.1f} GB")
    print(f"RAM used: {vm.percent}%")

    # Check for common issues
    print_header("COMMON ISSUES CHECK")

    issues = []

    # Issue 1: Python 3.14 too new
    if sys.version_info.major == 3 and sys.version_info.minor == 14:
        issues.append("Python 3.14 is very new - many packages lack compatible wheels")
        issues.append(
            "  Recommendation: Use Python 3.11 or 3.12 for better compatibility"
        )

    # Issue 2: No CUDA
    if not torch.cuda.is_available():
        issues.append("PyTorch CPU-only version installed")
        issues.append("  Training will be 10-100x slower than GPU")
        issues.append(
            "  Fix: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
        )

    # Issue 3: Low RAM
    if vm.available < 4 * 1024**3:  # Less than 4GB available
        issues.append(f"Low RAM available: {vm.available / 1024**3:.1f} GB")
        issues.append("  Training may fail or be very slow")

    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("No common issues detected")

    return len(issues) == 0


def test_training_speed():
    """Test basic training speed"""
    print_header("TRAINING SPEED TEST")

    # Create simple model
    model = torch.nn.Sequential(
        torch.nn.Linear(1000, 1000),
        torch.nn.ReLU(),
        torch.nn.Linear(1000, 1000),
    )

    if torch.cuda.is_available():
        model = model.cuda()
        device = "cuda"
    else:
        device = "cpu"

    # Create dummy data
    batch_size = 32
    x = torch.randn(batch_size, 1000)
    y = torch.randn(batch_size, 1000)

    if torch.cuda.is_available():
        x = x.cuda()
        y = y.cuda()

    # Test forward/backward pass
    print(f"Testing on {device}...")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.MSELoss()

    # Warmup
    for _ in range(5):
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()

    # Timed test
    start_time = time.time()
    iterations = 50

    for i in range(iterations):
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()

        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            speed = (i + 1) / elapsed
            print(f"  Iteration {i + 1}/{iterations}: {speed:.1f} iter/s")

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.2f} seconds")
    print(f"Average speed: {iterations / elapsed:.1f} iterations/second")

    # Estimate LoRA training time
    if not torch.cuda.is_available():
        print("\nESTIMATED LoRA TRAINING TIMES (CPU):")
        print("  50 samples, 1 epoch: ~1-2 minutes")
        print("  500 samples, 3 epochs: ~30-60 minutes")
        print("  5000 samples, 3 epochs: ~5-10 hours")
        print("\nWARNING: CPU training is impractical for serious work")
        print("Recommendation: Fix CUDA or use cloud GPU")


def check_package_versions():
    """Check for package version conflicts"""
    print_header("PACKAGE VERSION CHECK")

    packages = [
        ("torch", "2.9.0", "2.10.0"),
        ("transformers", "4.57.0", "4.58.0"),
        ("datasets", "4.4.0", "4.5.0"),
        ("peft", "0.18.0", "0.19.0"),
        ("bitsandbytes", "0.48.0", "0.49.0"),
    ]

    try:
        import bitsandbytes
        import datasets
        import peft
        import transformers

        actual_versions = {
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "datasets": datasets.__version__,
            "peft": peft.__version__,
            "bitsandbytes": bitsandbytes.__version__,
        }

        print("Package compatibility check:")
        for pkg, min_ver, max_ver in packages:
            actual = actual_versions.get(pkg, "not installed")
            print(f"  {pkg:20} {actual:15} ", end="")

            if pkg not in actual_versions:
                print("[NOT INSTALLED]")
            elif "cpu" in actual.lower() and pkg == "torch":
                print("[CPU ONLY - NO CUDA]")
            else:
                print("[OK]")

    except ImportError as e:
        print(f"Import error: {e}")

    # Check for xformers conflict
    try:
        import xformers

        print(f"\nWARNING: xformers {xformers.__version__} installed")
        print("  xformers may conflict with PyTorch versions")
    except ImportError:
        pass


def main():
    """Main diagnostic function"""
    print_header("TRAINING DIAGNOSTIC REPORT")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Run diagnostics
    system_ok = diagnose_system()
    check_package_versions()

    if system_ok:
        try:
            test_training_speed()
        except Exception as e:
            print(f"\nERROR during speed test: {e}")
    else:
        print("\nSkipping speed test due to system issues")

    print_header("RECOMMENDATIONS")

    if not torch.cuda.is_available():
        print("1. FIX CUDA (Highest Priority):")
        print("   pip uninstall torch torchvision torchaudio")
        print(
            "   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
        )
        print("   May require Python 3.11 or 3.12")

    if sys.version_info.minor == 14:
        print("\n2. USE COMPATIBLE PYTHON VERSION:")
        print("   Install Python 3.11 or 3.12")
        print("   Create virtual environment")
        print("   Reinstall all packages")

    print("\n3. FOR QUICK TESTING (if CUDA cannot be fixed):")
    print("   Use tiny models (distilgpt2, 125M params)")
    print("   Use very small datasets (≤100 samples)")
    print("   Use 1-2 epochs only")
    print("   Expect slow training (minutes to hours)")

    print("\n4. FOR PRODUCTION TRAINING:")
    print("   Must fix CUDA or use cloud GPU")
    print("   Consider Google Colab, AWS, or Azure")
    print("   Use quantized models (4-bit) to fit 4GB VRAM")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Tests for Fractal Code Generator and Verifier

This test suite validates:
1. LOC calculation math
2. Generator functionality with small runs
3. Manifest generation and format
4. Verifier functionality
5. Determinism and reproducibility
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_loc_calculation():
    """Test LOC calculation formulas."""
    print("\n=== Testing LOC Calculation ===")
    
    # Test case 1: Simple case
    target_loc = 10_000
    lines_per_file = 1000
    files_per_batch = 10
    
    loc_per_batch = files_per_batch * lines_per_file
    num_batches = (target_loc + loc_per_batch - 1) // loc_per_batch
    
    assert loc_per_batch == 10_000, f"Expected 10,000, got {loc_per_batch}"
    assert num_batches == 1, f"Expected 1 batch, got {num_batches}"
    print(f"✓ Case 1: {target_loc:,} LOC → {num_batches} batch(es)")
    
    # Test case 2: Multiple batches
    target_loc = 100_000
    lines_per_file = 1000
    files_per_batch = 10
    
    loc_per_batch = files_per_batch * lines_per_file
    num_batches = (target_loc + loc_per_batch - 1) // loc_per_batch
    
    assert loc_per_batch == 10_000, f"Expected 10,000, got {loc_per_batch}"
    assert num_batches == 10, f"Expected 10 batches, got {num_batches}"
    print(f"✓ Case 2: {target_loc:,} LOC → {num_batches} batch(es)")
    
    # Test case 3: 1B LOC with default settings
    target_loc = 1_000_000_000
    lines_per_file = 1000
    files_per_batch = 10_000
    
    loc_per_batch = files_per_batch * lines_per_file
    num_batches = (target_loc + loc_per_batch - 1) // loc_per_batch
    expected_files = num_batches * files_per_batch
    
    assert loc_per_batch == 10_000_000, f"Expected 10M, got {loc_per_batch}"
    assert num_batches == 100, f"Expected 100 batches, got {num_batches}"
    assert expected_files == 1_000_000, f"Expected 1M files, got {expected_files}"
    print(f"✓ Case 3: {target_loc:,} LOC → {num_batches} batches, {expected_files:,} files")
    
    print("✅ All LOC calculations correct\n")


def test_generator_help():
    """Test that generator CLI help works."""
    print("\n=== Testing Generator CLI ===")
    
    result = subprocess.run(
        ["python3", "tools/generate_fractal_code.py", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Generator help failed"
    assert "Generate deterministic fractal code" in result.stdout, "Help text missing"
    print("✓ Generator CLI help works")


def test_verifier_help():
    """Test that verifier CLI help works."""
    result = subprocess.run(
        ["python3", "tools/verify_fractal_manifest.py", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Verifier help failed"
    assert "Verify fractal code" in result.stdout, "Help text missing"
    print("✓ Verifier CLI help works\n")


def test_small_generation():
    """Test generation with small LOC count."""
    print("\n=== Testing Small Generation (1,000 LOC) ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_root = Path(tmpdir) / "out"
        manifest_path = output_root / "manifest.jsonl"
        
        # Run generator
        result = subprocess.run(
            [
                "python3", "tools/generate_fractal_code.py",
                "--target-loc", "1000",
                "--lines-per-file", "100",
                "--files-per-batch", "5",
                "--output-root", str(output_root),
                "--manifest", str(manifest_path),
                "--seed", "42",
                "--apply"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
        
        assert result.returncode == 0, "Generator failed"
        
        # Check output directory exists
        assert output_root.exists(), "Output directory not created"
        assert manifest_path.exists(), "Manifest not created"
        
        # Check batch directories
        batches = list(output_root.glob("batch_*"))
        assert len(batches) == 2, f"Expected 2 batches, found {len(batches)}"
        print(f"✓ Created {len(batches)} batch(es)")
        
        # Check files in first batch
        batch0 = output_root / "batch_000000"
        shards = list(batch0.glob("shard_*.py"))
        assert len(shards) == 5, f"Expected 5 shards in batch 0, found {len(shards)}"
        print(f"✓ Created {len(shards)} shard(s) in batch 0")
        
        # Check file content
        first_shard = batch0 / "shard_000000.py"
        with open(first_shard) as f:
            content = f.read()
            lines = content.count("\n") + 1
            assert lines == 100, f"Expected 100 lines, found {lines}"
        print(f"✓ First shard has correct line count: {lines}")
        
        # Check manifest format
        with open(manifest_path) as f:
            lines = f.readlines()
            assert len(lines) >= 1, "Manifest is empty"
            
            # Parse header
            header = json.loads(lines[0])
            assert header["type"] == "header", "First entry should be header"
            assert header["results"]["actual_loc"] == 1000, "LOC mismatch"
            assert header["results"]["total_files"] == 10, "File count mismatch"
            print(f"✓ Manifest header valid: {header['results']['actual_loc']:,} LOC")
        
        print("✅ Small generation test passed\n")


def test_verification():
    """Test that verifier correctly validates generated code."""
    print("\n=== Testing Verification ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_root = Path(tmpdir) / "out"
        manifest_path = output_root / "manifest.jsonl"
        
        # Generate
        gen_result = subprocess.run(
            [
                "python3", "tools/generate_fractal_code.py",
                "--target-loc", "500",
                "--lines-per-file", "100",
                "--files-per-batch", "5",
                "--output-root", str(output_root),
                "--manifest", str(manifest_path),
                "--seed", "123",
                "--apply"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert gen_result.returncode == 0, "Generation failed"
        print("✓ Generated test data")
        
        # Verify
        verify_result = subprocess.run(
            [
                "python3", "tools/verify_fractal_manifest.py",
                str(manifest_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(verify_result.stdout)
        
        assert verify_result.returncode == 0, "Verification failed"
        assert "VERIFICATION PASSED" in verify_result.stdout, "Verification did not pass"
        print("✓ Verification passed")
        
        # Test verification failure by corrupting a file
        batch0 = output_root / "batch_000000"
        first_shard = batch0 / "shard_000000.py"
        
        with open(first_shard, "a") as f:
            f.write("\n# Corrupted line")
        print("✓ Corrupted test file")
        
        verify_corrupt = subprocess.run(
            [
                "python3", "tools/verify_fractal_manifest.py",
                str(manifest_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert verify_corrupt.returncode == 1, "Verification should fail on corrupted file"
        assert "VERIFICATION FAILED" in verify_corrupt.stdout, "Should report failure"
        print("✓ Correctly detected corruption")
        
        print("✅ Verification test passed\n")


def test_determinism():
    """Test that same parameters produce identical output."""
    print("\n=== Testing Determinism ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Generate run 1
        output1 = tmpdir / "run1"
        manifest1 = output1 / "manifest.jsonl"
        
        result1 = subprocess.run(
            [
                "python3", "tools/generate_fractal_code.py",
                "--target-loc", "500",
                "--lines-per-file", "50",
                "--files-per-batch", "5",
                "--output-root", str(output1),
                "--manifest", str(manifest1),
                "--seed", "999",
                "--apply"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result1.returncode == 0, "Run 1 failed"
        print("✓ Run 1 complete")
        
        # Generate run 2 (same parameters)
        output2 = tmpdir / "run2"
        manifest2 = output2 / "manifest.jsonl"
        
        result2 = subprocess.run(
            [
                "python3", "tools/generate_fractal_code.py",
                "--target-loc", "500",
                "--lines-per-file", "50",
                "--files-per-batch", "5",
                "--output-root", str(output2),
                "--manifest", str(manifest2),
                "--seed", "999",
                "--apply"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result2.returncode == 0, "Run 2 failed"
        print("✓ Run 2 complete")
        
        # Compare file hashes
        batch1 = output1 / "batch_000000"
        batch2 = output2 / "batch_000000"
        
        shards1 = sorted(batch1.glob("shard_*.py"))
        shards2 = sorted(batch2.glob("shard_*.py"))
        
        assert len(shards1) == len(shards2), "Different number of shards"
        
        for shard1, shard2 in zip(shards1, shards2):
            hash1 = compute_file_hash(shard1)
            hash2 = compute_file_hash(shard2)
            assert hash1 == hash2, f"Hash mismatch: {shard1.name}"
        
        print(f"✓ All {len(shards1)} files have identical hashes")
        print("✅ Determinism test passed\n")


def test_dry_run():
    """Test that dry-run mode doesn't write files."""
    print("\n=== Testing Dry-Run Mode ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_root = Path(tmpdir) / "out"
        manifest_path = output_root / "manifest.jsonl"
        
        # Run without --apply (dry-run)
        result = subprocess.run(
            [
                "python3", "tools/generate_fractal_code.py",
                "--target-loc", "1000",
                "--output-root", str(output_root),
                "--manifest", str(manifest_path)
                # Note: no --apply
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0, "Dry-run failed"
        assert "DRY RUN MODE" in result.stdout, "Dry-run not indicated"
        print("✓ Dry-run completed")
        
        # Check that no files were created
        assert not output_root.exists(), "Output directory should not exist in dry-run"
        assert not manifest_path.exists(), "Manifest should not exist in dry-run"
        print("✓ No files created in dry-run mode")
        
        print("✅ Dry-run test passed\n")


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run_all_tests():
    """Run all test functions."""
    print("\n" + "="*60)
    print("Running Fractal Code Generator Test Suite")
    print("="*60)
    
    try:
        test_loc_calculation()
        test_generator_help()
        test_verifier_help()
        test_small_generation()
        test_verification()
        test_determinism()
        test_dry_run()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}\n", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(run_all_tests())

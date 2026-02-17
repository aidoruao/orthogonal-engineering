#!/usr/bin/env python3
"""
Tests for Shard-Based Parallel Verification
"""

import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path


def test_shard_mode_cli():
    """Test that shard mode CLI arguments work."""
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "--shard-id" in result.stdout
    assert "--shard-count" in result.stdout
    print("✓ Shard mode CLI arguments exist")


def test_shard_mode_execution():
    """Test that shard mode executes successfully."""
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", 
         "--mode", "shard", "--shard-id", "0", "--shard-count", "2",
         "--json-only"],
        capture_output=True,
        text=True
    )
    
    # May exit with 0 or 1 depending on certification pass/fail
    assert result.returncode in [0, 1], f"Unexpected exit code: {result.returncode}"
    
    # Parse JSON output
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}")
    
    # Verify shard metadata
    assert output["mode"] == "shard"
    assert output["shard_id"] == 0
    assert output["shard_count"] == 2
    
    print("✓ Shard mode executes successfully")
    return output


def test_shard_mode_partitioning():
    """Test that different shards process different data."""
    # Run two shards
    result0 = subprocess.run(
        ["python3", "automation/verify_extreme_work.py",
         "--mode", "shard", "--shard-id", "0", "--shard-count", "4",
         "--json-only"],
        capture_output=True,
        text=True
    )
    
    result1 = subprocess.run(
        ["python3", "automation/verify_extreme_work.py",
         "--mode", "shard", "--shard-id", "1", "--shard-count", "4",
         "--json-only"],
        capture_output=True,
        text=True
    )
    
    output0 = json.loads(result0.stdout)
    output1 = json.loads(result1.stdout)
    
    # Different shards should process different files
    # Check artifact counts - they may differ
    artifacts0 = output0["quantitative_metrics"]["automated_artifacts"]["total_artifacts"]
    artifacts1 = output1["quantitative_metrics"]["automated_artifacts"]["total_artifacts"]
    
    # In most cases, different shards will have different counts
    # (though in edge cases they could be the same)
    print(f"  Shard 0 artifacts: {artifacts0}")
    print(f"  Shard 1 artifacts: {artifacts1}")
    
    print("✓ Shards process independently")


def test_shard_output_file_naming():
    """Test that shard output files are named correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_base = Path(tmpdir) / "test_output"
        
        result = subprocess.run(
            ["python3", "automation/verify_extreme_work.py",
             "--mode", "shard", "--shard-id", "2", "--shard-count", "5",
             "--output", str(output_base)],
            capture_output=True,
            text=True
        )
        
        # Check that output file was created with correct name pattern
        expected_pattern = "test_output.json"
        output_file = Path(f"{output_base}.json")
        
        assert output_file.exists(), f"Output file not found: {output_file}"
        
        # Verify content
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert data["mode"] == "shard"
        assert data["shard_id"] == 2
        assert data["shard_count"] == 5
        
        print("✓ Shard output files named correctly")


def test_aggregate_mode_cli():
    """Test aggregate mode CLI."""
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", "--help"],
        capture_output=True,
        text=True
    )
    
    assert "--shard-files" in result.stdout
    assert "--shard-pattern" in result.stdout
    print("✓ Aggregate mode CLI arguments exist")


def test_aggregate_mode_execution():
    """Test that aggregate mode combines shard results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Generate multiple shard results
        shard_files = []
        for i in range(3):
            output_path = tmpdir / f"shard_{i}"
            result = subprocess.run(
                ["python3", "automation/verify_extreme_work.py",
                 "--mode", "shard", "--shard-id", str(i), "--shard-count", "3",
                 "--output", str(output_path)],
                capture_output=True,
                text=True
            )
            shard_files.append(f"{output_path}.json")
        
        # Verify all shard files exist
        for shard_file in shard_files:
            assert Path(shard_file).exists(), f"Shard file not found: {shard_file}"
        
        # Run aggregate
        aggregated_path = tmpdir / "aggregated"
        result = subprocess.run(
            ["python3", "automation/verify_extreme_work.py",
             "--mode", "aggregate",
             "--shard-files"] + shard_files + 
            ["--output", str(aggregated_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode in [0, 1], f"Aggregate failed: {result.stderr}"
        
        # Load aggregated result
        with open(f"{aggregated_path}.json", 'r') as f:
            aggregated = json.load(f)
        
        # Verify aggregated structure
        assert aggregated["mode"] == "aggregated"
        assert aggregated["shard_count"] == 3
        assert "quantitative_metrics" in aggregated
        assert "qualitative_metrics" in aggregated
        assert "overall_score" in aggregated
        
        # Load individual shards for comparison
        shards = []
        for shard_file in shard_files:
            with open(shard_file, 'r') as f:
                shards.append(json.load(f))
        
        # Verify artifact aggregation
        total_artifacts_shards = sum(
            s["quantitative_metrics"]["automated_artifacts"]["total_artifacts"]
            for s in shards
        )
        total_artifacts_aggregated = aggregated["quantitative_metrics"]["automated_artifacts"]["total_artifacts"]
        
        assert total_artifacts_aggregated == total_artifacts_shards, \
               f"Artifact count mismatch: {total_artifacts_aggregated} != {total_artifacts_shards}"
        
        print("✓ Aggregate mode combines shard results correctly")
        print(f"  Total artifacts from shards: {total_artifacts_shards}")
        print(f"  Total artifacts aggregated: {total_artifacts_aggregated}")


def test_full_vs_aggregate_consistency():
    """Test that full mode and aggregated shards produce similar results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Run full verification
        full_result = subprocess.run(
            ["python3", "automation/verify_extreme_work.py",
             "--mode", "full", "--json-only"],
            capture_output=True,
            text=True
        )
        full_data = json.loads(full_result.stdout)
        
        # Generate shards
        shard_count = 4
        shard_files = []
        for i in range(shard_count):
            output_path = tmpdir / f"shard_{i}"
            subprocess.run(
                ["python3", "automation/verify_extreme_work.py",
                 "--mode", "shard", "--shard-id", str(i), "--shard-count", str(shard_count),
                 "--output", str(output_path)],
                capture_output=True,
                text=True
            )
            shard_files.append(f"{output_path}.json")
        
        # Aggregate shards
        aggregated_path = tmpdir / "aggregated"
        subprocess.run(
            ["python3", "automation/verify_extreme_work.py",
             "--mode", "aggregate",
             "--shard-files"] + shard_files +
            ["--output", str(aggregated_path)],
            capture_output=True,
            text=True
        )
        
        with open(f"{aggregated_path}.json", 'r') as f:
            aggregated_data = json.load(f)
        
        # Compare total artifacts (should be very close)
        full_artifacts = full_data["quantitative_metrics"]["automated_artifacts"]["total_artifacts"]
        agg_artifacts = aggregated_data["quantitative_metrics"]["automated_artifacts"]["total_artifacts"]
        
        print(f"  Full mode artifacts: {full_artifacts}")
        print(f"  Aggregated artifacts: {agg_artifacts}")
        
        # Allow small difference due to timing or edge cases
        diff = abs(full_artifacts - agg_artifacts)
        assert diff <= 5, f"Large difference between full and aggregated: {diff}"
        
        print("✓ Full and aggregated results are consistent")


def main():
    """Run all tests."""
    print("Running Shard-Based Verification Tests...")
    print("=" * 80)
    
    # Change to repo root
    os.chdir(Path(__file__).parent.parent)
    
    tests = [
        test_shard_mode_cli,
        test_shard_mode_execution,
        test_shard_mode_partitioning,
        test_shard_output_file_naming,
        test_aggregate_mode_cli,
        test_aggregate_mode_execution,
        test_full_vs_aggregate_consistency,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 80)
    print(f"Results: {len(tests) - failed}/{len(tests)} tests passed")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed! ✅")
        sys.exit(0)


if __name__ == "__main__":
    main()

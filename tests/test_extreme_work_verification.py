#!/usr/bin/env python3
"""
Tests for Extreme Work Verification System
"""

import json
import os
import sys
import subprocess
from pathlib import Path

# Test constants
SCORE_TOLERANCE = 0.01  # Tolerance for floating-point score comparison


def test_config_exists():
    """Test that configuration file exists and is valid JSON."""
    config_path = Path("EXTREME_WORK_BOUNDARIES.json")
    assert config_path.exists(), "Configuration file not found"
    
    with open(config_path) as f:
        config = json.load(f)
    
    assert "EXTREME_WORK" in config
    assert config["EXTREME_WORK"] is True
    assert "quantitative_boundaries" in config
    assert "qualitative_boundaries" in config
    assert "proof_of_scale" in config
    print("✓ Configuration file valid")

def test_verification_script_exists():
    """Test that verification script exists and is executable."""
    script_path = Path("automation/verify_extreme_work.py")
    assert script_path.exists(), "Verification script not found"
    assert os.access(script_path, os.X_OK), "Verification script not executable"
    print("✓ Verification script exists and is executable")

def test_verification_runs():
    """Test that verification script runs without errors."""
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    # Script may return exit code 0 (pass) or 1 (fail), both are valid
    assert result.returncode in [0, 1], f"Script failed with unexpected exit code: {result.returncode}"
    
    # The JSON output is in stdout, but there might be other output too
    # Try to find the JSON in the output
    lines = result.stdout.strip().split('\n')
    json_output = None
    
    # Look for JSON starting with '{'
    for i, line in enumerate(lines):
        if line.strip().startswith('{'):
            # Join from this line to the end
            json_output = '\n'.join(lines[i:])
            break
    
    assert json_output is not None, "No JSON output found in stdout"
    
    # Verify JSON output is valid
    try:
        output = json.loads(json_output)
        assert "timestamp" in output
        assert "quantitative_metrics" in output
        assert "qualitative_metrics" in output
        assert "proof_of_scale" in output
        assert "overall_score" in output
        assert "certification_passed" in output
        print("✓ Verification script produces valid output")
        print(f"  Score: {output['overall_score']:.1%}")
        print(f"  Certification: {'PASSED' if output['certification_passed'] else 'FAILED'}")
        return output  # Return for use in other tests
    except json.JSONDecodeError as e:
        print(f"Script output: {json_output[:500]}")
        raise AssertionError(f"Invalid JSON output: {e}")


def test_quantitative_metrics():
    """Test that quantitative metrics are calculated."""
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    # Extract JSON from output
    lines = result.stdout.strip().split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('{'):
            json_output = '\n'.join(lines[i:])
            break
    
    output = json.loads(json_output)
    quant = output["quantitative_metrics"]
    
    assert "commits_per_day" in quant
    assert "commit_complexity" in quant
    assert "automated_artifacts" in quant
    
    # Check that metrics have expected structure
    assert "value" in quant["commits_per_day"]
    assert "passed" in quant["commits_per_day"]
    assert "avg_lines_changed" in quant["commit_complexity"]
    assert "total_artifacts" in quant["automated_artifacts"]
    
    print("✓ Quantitative metrics calculated")


def test_qualitative_metrics():
    """Test that qualitative metrics are calculated."""
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    # Extract JSON from output
    lines = result.stdout.strip().split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('{'):
            json_output = '\n'.join(lines[i:])
            break
    
    output = json.loads(json_output)
    qual = output["qualitative_metrics"]
    
    assert "audit_trails" in qual
    assert "deterministic_scaffolds" in qual
    assert "atomic_increments" in qual
    
    print("✓ Qualitative metrics calculated")


def test_proof_of_scale():
    """Test that proof of scale is generated."""
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    # Extract JSON from output
    lines = result.stdout.strip().split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('{'):
            json_output = '\n'.join(lines[i:])
            break
    
    output = json.loads(json_output)
    pos = output["proof_of_scale"]
    
    assert "proofs" in pos
    proofs = pos["proofs"]
    assert "commit_history_sha256" in proofs
    assert len(proofs["commit_history_sha256"]) == 64  # SHA256 hex length
    
    print("✓ Proof of scale generated")


def test_score_calculation():
    """Test that score is calculated correctly."""
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    # Extract JSON from output
    lines = result.stdout.strip().split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('{'):
            json_output = '\n'.join(lines[i:])
            break
    
    output = json.loads(json_output)
    
    assert "score_breakdown" in output
    breakdown = output["score_breakdown"]
    
    assert "quantitative" in breakdown
    assert "qualitative" in breakdown
    assert "proof_of_scale" in breakdown
    
    # Verify score calculation
    total = (
        breakdown["quantitative"]["contribution"] +
        breakdown["qualitative"]["contribution"] +
        breakdown["proof_of_scale"]["contribution"]
    )
    
    assert abs(total - output["overall_score"]) < SCORE_TOLERANCE, "Score calculation mismatch"
    
    print(f"✓ Score calculation correct: {output['overall_score']:.1%}")

def main():
    """Run all tests."""
    print("Running Extreme Work Verification Tests...")
    print("=" * 80)
    
    # Change to repo root
    os.chdir(Path(__file__).parent.parent)
    
    tests = [
        test_config_exists,
        test_verification_script_exists,
        test_verification_runs,
        test_quantitative_metrics,
        test_qualitative_metrics,
        test_proof_of_scale,
        test_score_calculation,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
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

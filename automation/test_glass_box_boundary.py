#!/usr/bin/env python3
"""
TEST FOR GLASS BOX BOUNDARY ENFORCER

Purpose: Test the Glass-Box Boundary enforcement system as defined in
GLASS_BOX_BOUNDARY_v1.11.html and implemented in run_full_audit_with_trace.py

Exit Code: 2 on any test failure (matching fail-fast architecture)
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def test_boundary_decorator():
    """Test that boundary decorator is properly defined and functional."""
    print("Testing boundary decorator...")

    # Import the decorator from the enforcer
    sys.path.insert(0, str(Path(__file__).parent))
    from run_full_audit_with_trace import glass_box_boundary

    # Test 1: Decorator can be applied
    @glass_box_boundary()
    def test_function():
        return "success"

    result = test_function()
    assert result == "success", f"Expected 'success', got {result}"
    print("  ✓ Decorator application test passed")

    # Test 2: Decorator has required parameters
    import inspect

    sig = inspect.signature(glass_box_boundary)
    params = list(sig.parameters.keys())

    required_params = [
        "input_validator",
        "output_validator",
        "side_effect_check",
        "orthogonal_separation",
    ]

    for param in required_params:
        assert param in params, f"Missing required parameter: {param}"

    print("  ✓ Decorator parameter test passed")
    return True


def test_required_artifacts():
    """Test that all required artifacts exist."""
    print("Testing required artifacts...")

    repo_root = Path(__file__).parent.parent
    required_artifacts = [
        "automation/full_audit.py",
        "automation/generate_sha256_manifest.py",
        "automation/verify_sha256_manifest.py",
        "documentation/README.md",
        "grounding_models/GROUNDING_MODELS.md",
        "historical_candidates/HISTORICAL_LOGOS_CANDIDATES.md",
        "correspondence_bridge/correspondence_validator_final.py",
        "documentation/GLASS_BOX_BOUNDARY_v1.11.html",
        ".rules/ORTHOGONAL_GB_ORIGIN.rules",
        "AGENT.md",
        "AI_INSTRUCTIONS.md",
    ]

    missing = []
    for artifact in required_artifacts:
        artifact_path = repo_root / artifact
        if not artifact_path.exists():
            missing.append(artifact)

    if missing:
        print(f"  ✗ Missing required artifacts: {missing}")
        return False

    print(f"  ✓ All {len(required_artifacts)} required artifacts found")
    return True


def test_enforcer_execution():
    """Test that the enforcer can be executed."""
    print("Testing enforcer execution...")

    enforcer_path = Path(__file__).parent / "run_full_audit_with_trace.py"

    # Test 1: Python syntax is valid
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(enforcer_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"  ✗ Python syntax error: {result.stderr}")
        return False

    print("  ✓ Python syntax validation passed")

    # Test 2: Can import without errors
    try:
        # Clear any previous imports
        if "run_full_audit_with_trace" in sys.modules:
            del sys.modules["run_full_audit_with_trace"]

        import run_full_audit_with_trace

        print("  ✓ Module import successful")
    except Exception as e:
        print(f"  ✗ Module import failed: {e}")
        return False

    # Test 3: Help command works
    result = subprocess.run(
        [sys.executable, str(enforcer_path), "--help"], capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"  ✗ Help command failed: {result.stderr}")
        return False

    print("  ✓ Help command execution passed")
    return True


def test_trace_generation():
    """Test that trace generation works."""
    print("Testing trace generation...")

    enforcer_path = Path(__file__).parent / "run_full_audit_with_trace.py"

    # Create temporary output file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        output_file = f.name

    try:
        # Run enforcer with output file
        result = subprocess.run(
            [sys.executable, str(enforcer_path), "--output", output_file],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )

        if result.returncode != 0:
            print(f"  ✗ Trace generation failed with exit code {result.returncode}")
            print(f"    stderr: {result.stderr[:500]}")
            return False

        print("  ✓ Trace generation command executed successfully")

        # Load and validate trace
        with open(output_file, "r", encoding="utf-8") as f:
            trace = json.load(f)

        # Check required fields
        required_fields = [
            "trace_id",
            "timestamp",
            "repository_meta",
            "environment_snapshot",
            "artifact_scan",
            "boundary_violations",
            "suppressed_signals",
            "timeline_sequence",
            "hash_manifest",
            "signature",
            "python_enforcer_active",
            "ide_integration",
        ]

        missing_fields = []
        for field in required_fields:
            if field not in trace:
                missing_fields.append(field)

        if missing_fields:
            print(f"  ✗ Missing trace fields: {missing_fields}")
            return False

        print(f"  ✓ All required trace fields present")

        # Check specific values
        if not trace.get("python_enforcer_active", False):
            print("  ✗ python_enforcer_active must be true")
            return False

        ide_integration = trace.get("ide_integration", {})
        required_ide_fields = [
            "autofix_enabled",
            "structural_consistency",
            "boundary_awareness",
            "doc_sync",
        ]

        for field in required_ide_fields:
            if field not in ide_integration or not ide_integration[field]:
                print(f"  ✗ ide_integration.{field} must be present and true")
                return False

        print("  ✓ Trace validation passed")
        return True

    except subprocess.TimeoutExpired:
        print("  ✗ Trace generation timed out after 30 seconds")
        return False
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON in trace: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(output_file):
            os.unlink(output_file)


def test_validation_mode():
    """Test that validation mode works."""
    print("Testing validation mode...")

    enforcer_path = Path(__file__).parent / "run_full_audit_with_trace.py"

    # First generate a valid trace
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        trace_file = f.name

    try:
        # Generate trace
        result = subprocess.run(
            [sys.executable, str(enforcer_path), "--output", trace_file],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"  ✗ Cannot generate trace for validation test: {result.stderr}")
            return False

        # Test validation of valid trace
        result = subprocess.run(
            [
                sys.executable,
                str(enforcer_path),
                "--validate-only",
                "--trace-file",
                trace_file,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"  ✗ Valid trace validation failed: {result.stderr}")
            return False

        print("  ✓ Valid trace validation passed")

        # Test validation of invalid trace
        invalid_trace = {
            "trace_id": "INVALID-TRACE",
            "timestamp": "2026-01-21T00:00:00Z",
            "python_enforcer_active": False,  # This should cause validation failure
            "ide_integration": {
                "autofix_enabled": False,
                "structural_consistency": False,
                "boundary_awareness": False,
                "doc_sync": False,
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            invalid_file = f.name
            json.dump(invalid_trace, f)

        result = subprocess.run(
            [
                sys.executable,
                str(enforcer_path),
                "--validate-only",
                "--trace-file",
                invalid_file,
            ],
            capture_output=True,
            text=True,
        )

        # Should exit with code 2 (boundary violation)
        if result.returncode != 2:
            print(f"  ✗ Invalid trace should exit with code 2, got {result.returncode}")
            return False

        print("  ✓ Invalid trace correctly rejected with exit code 2")
        return True

    finally:
        # Clean up
        for file in [trace_file, invalid_file if "invalid_file" in locals() else None]:
            if file and os.path.exists(file):
                os.unlink(file)


def test_exit_codes():
    """Test that exit codes match HTML blueprint specification."""
    print("Testing exit codes...")

    enforcer_path = Path(__file__).parent / "run_full_audit_with_trace.py"

    # Test 1: Successful execution (should exit 0)
    result = subprocess.run(
        [sys.executable, str(enforcer_path), "--help"], capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"  ✗ Help command should exit 0, got {result.returncode}")
        return False

    print("  ✓ Exit code 0 (success) test passed")

    # Note: Testing other exit codes (2-5) would require inducing specific failures
    # which is complex in a simple test. The validation test above covers exit code 2.

    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("GLASS BOX BOUNDARY ENFORCER TEST SUITE")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()

    tests = [
        ("Boundary Decorator", test_boundary_decorator),
        ("Required Artifacts", test_required_artifacts),
        ("Enforcer Execution", test_enforcer_execution),
        ("Trace Generation", test_trace_generation),
        ("Validation Mode", test_validation_mode),
        ("Exit Codes", test_exit_codes),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\nTest: {test_name}")
        try:
            if test_func():
                print(f"  [OK] {test_name} PASSED")
                passed += 1
            else:
                print(f"  [X] {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"  [X] {test_name} ERROR: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        print("\n[X] TEST SUITE FAILED")
        sys.exit(2)  # Boundary violation exit code
    else:
        print("\n[OK] ALL TESTS PASSED")
        sys.exit(0)

        sys.exit(0)


if __name__ == "__main__":
    main()

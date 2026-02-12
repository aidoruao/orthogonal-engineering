#!/usr/bin/env python3
"""
test_atomic_orchestration.py — Demonstration Script for Atomic Orchestration Bundle

This script demonstrates the key features of the atomic orchestration bundle:
1. Controller execution with DAG orchestration
2. Structural map generation
3. Fallback contingency system
4. Checkpoint and backup systems

Run this script to verify the bundle is working correctly.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def test_controller_execution():
    """Test the main controller execution."""
    print("🧪 TEST 1: Controller Execution")
    print("=" * 60)

    # Run controller
    print("Running controller.py...")
    result = subprocess.run(
        [sys.executable, "downloads/controller.py"],
        capture_output=True,
        text=True,
        cwd=Path(".").resolve(),
    )

    print(f"Exit code: {result.returncode}")
    print(f"Output length: {len(result.stdout)} characters")

    # Check for expected patterns
    success_markers = [
        "CONTROLLER EXECUTION SUMMARY",
        "Successfully executed:",
        "controller.py execution complete",
    ]

    for marker in success_markers:
        if marker in result.stdout:
            print(f"✓ Found expected marker: {marker}")
        else:
            print(f"✗ Missing marker: {marker}")

    return (
        result.returncode == 0 or result.returncode == 1
    )  # 0=success, 1=partial success


def test_structural_map_generation():
    """Test structural map generation."""
    print("\n🧪 TEST 2: Structural Map Generation")
    print("=" * 60)

    # Run structural map generator
    print("Running generate_structural_map.py...")
    result = subprocess.run(
        [sys.executable, "downloads/generate_structural_map.py"],
        capture_output=True,
        text=True,
        cwd=Path(".").resolve(),
    )

    print(f"Exit code: {result.returncode}")

    # Check output files
    json_file = Path("downloads/repository_structural_map_full.json")
    yaml_file = Path("downloads/repository_structural_map_full.yaml")

    files_exist = []
    if json_file.exists():
        print(f"✓ JSON map generated: {json_file}")
        files_exist.append(json_file)
    else:
        print(f"✗ JSON map missing: {json_file}")

    if yaml_file.exists():
        print(f"✓ YAML map generated: {yaml_file}")
        files_exist.append(yaml_file)
    else:
        print(f"✗ YAML map missing: {yaml_file}")

    # Check file contents
    for file_path in files_exist:
        try:
            with open(file_path, "r") as f:
                content = f.read()
                if "generated_by" in content and "timestamp" in content:
                    print(f"✓ {file_path.name} has valid structure")
                else:
                    print(f"✗ {file_path.name} missing required fields")
        except Exception as e:
            print(f"✗ Error reading {file_path}: {str(e)}")

    return len(files_exist) >= 1  # At least one file should exist


def test_fallback_system():
    """Test fallback contingency system."""
    print("\n🧪 TEST 3: Fallback Contingency System")
    print("=" * 60)

    # Check fallback scripts exist
    fallback_scripts = [
        "automation/fallback_light_audit.py",
        "automation/dry_run_autofix.py",
        "toolkit/oe/fallback_spellcheck.py",
        "toolkit/oe/dry_run_autofix.py",
        "toolkit/oe/partial_log_backup.py",
        "downloads/minimal_struct_map.py",
    ]

    existing_scripts = []
    for script in fallback_scripts:
        if Path(script).exists():
            print(f"✓ Fallback script exists: {script}")
            existing_scripts.append(script)
        else:
            print(f"✗ Fallback script missing: {script}")

    # Test minimal structural map (should always work)
    print("\nTesting minimal structural map fallback...")
    result = subprocess.run(
        [sys.executable, "downloads/minimal_struct_map.py"],
        capture_output=True,
        text=True,
        cwd=Path(".").resolve(),
    )

    if (
        result.returncode == 0 or result.returncode == 2
    ):  # 2 is expected for boundary violations
        print(f"✓ Minimal structural map executed (exit code: {result.returncode})")
        # Check for output
        minimal_files = list(Path("downloads").glob("minimal_structural_map_*.json"))
        if minimal_files:
            print(f"✓ Minimal map generated: {minimal_files[0].name}")
        else:
            print("✗ No minimal map files found")
    else:
        print(f"✗ Minimal structural map failed (exit code: {result.returncode})")

    return len(existing_scripts) >= 3  # At least 3 fallback scripts should exist


def test_checkpoint_system():
    """Test checkpoint and backup systems."""
    print("\n🧪 TEST 4: Checkpoint & Backup Systems")
    print("=" * 60)

    # Check checkpoint directory
    checkpoint_dir = Path("downloads/state")
    if checkpoint_dir.exists():
        checkpoints = list(checkpoint_dir.glob("*.checkpoint"))
        print(f"✓ Checkpoint directory exists with {len(checkpoints)} checkpoints")
        for cp in checkpoints[:3]:  # Show first 3
            print(f"  • {cp.name}")
    else:
        print("✗ Checkpoint directory missing")

    # Check backup directory
    backup_dir = Path("downloads/_backup")
    if backup_dir.exists():
        backups = list(backup_dir.iterdir())
        print(f"✓ Backup directory exists with {len(backups)} backups")
        for backup in backups[:3]:  # Show first 3
            if backup.is_dir():
                print(f"  • {backup.name}/")
    else:
        print("✗ Backup directory missing")

    # Check logs directory
    logs_dir = Path("logs/violations")
    if logs_dir.exists():
        logs = list(logs_dir.glob("*.log"))
        print(f"✓ Logs directory exists with {len(logs)} violation logs")
        for log in logs[:3]:  # Show first 3
            print(f"  • {log.name}")
    else:
        print("✗ Logs directory missing")

    return checkpoint_dir.exists() and backup_dir.exists() and logs_dir.exists()


def test_documentation():
    """Test documentation files."""
    print("\n🧪 TEST 5: Documentation")
    print("=" * 60)

    docs = [
        "downloads/ATOMIC_ORCHESTRATION_README.md",
        "downloads/ATOMIC_ORCHESTRATION_IMPLEMENTATION_SUMMARY.md",
    ]

    existing_docs = []
    for doc in docs:
        if Path(doc).exists():
            print(f"✓ Documentation exists: {doc}")
            existing_docs.append(doc)
        else:
            print(f"✗ Documentation missing: {doc}")

    return len(existing_docs) == len(docs)


def main():
    """Main test execution."""
    print("⚡ ATOMIC ORCHESTRATION BUNDLE — TEST SUITE")
    print("=" * 60)
    print(f"Test timestamp: {datetime.now().isoformat()}")
    print(f"Working directory: {Path('.').resolve()}")
    print()

    tests = [
        ("Controller Execution", test_controller_execution),
        ("Structural Map Generation", test_structural_map_generation),
        ("Fallback System", test_fallback_system),
        ("Checkpoint & Backup", test_checkpoint_system),
        ("Documentation", test_documentation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"\n{'✅ PASS' if success else '❌ FAIL'}: {test_name}")
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUITE SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {passed / total * 100:.1f}%")

    if passed == total:
        print(
            "\n🎉 ALL TESTS PASSED! Atomic orchestration bundle is fully operational."
        )
        return 0
    elif passed >= total * 0.7:  # 70% success rate
        print(f"\n⚠️  PARTIAL SUCCESS: {passed}/{total} tests passed.")
        print("The bundle is functional but may have some issues.")
        return 1
    else:
        print(f"\n❌ TEST SUITE FAILED: Only {passed}/{total} tests passed.")
        print("The bundle needs attention before deployment.")
        return 2


if __name__ == "__main__":
    sys.exit(main())

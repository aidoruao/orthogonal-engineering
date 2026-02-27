#!/usr/bin/env python3
"""
Crusader Combat Refrigerator - Simple Import Test
Version: 1.0.0

Simple test to verify that the Crusader package can be imported
and basic components work.
"""

import os
import sys
from pathlib import Path


def test_imports():
    """Test importing the main Crusader package."""
    print("=" * 80)
    print("CRUSADER COMBAT REFRIGERATOR - SIMPLE IMPORT TEST")
    print("=" * 80)

    # Add parent directory to path (so we can import crusader)
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    print(f"Testing imports from: {current_dir}")
    print()

    # Test 1: Import main package
    print("Test 1: Importing main package...")
    try:
        import crusader

        print("[PASS] Successfully imported crusader package")
        print(f"  Version: {crusader.__version__}")
        print(f"  Author: {crusader.__author__}")
    except Exception as e:
        print(f"[FAIL] Failed to import crusader: {e}")
        return False

    print()

    # Test 2: Import core components
    print("Test 2: Importing core components...")
    core_tests = [
        ("crusader.core.constants", "EnvironmentalConstants"),
        ("crusader.core.main", "CrusaderSystem"),
        ("crusader.core.utils.time_utils", "TimeUtils"),
    ]

    core_passed = 0
    for module_name, class_name in core_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"[PASS] {module_name}.{class_name}")
                core_passed += 1
            else:
                print(f"[FAIL] {module_name}.{class_name} not found")
        except Exception as e:
            print(f"[FAIL] {module_name}: {e}")

    print(f"Core components: {core_passed}/{len(core_tests)} passed")
    print()

    # Test 3: Import warfare systems
    print("Test 3: Importing warfare systems...")
    warfare_tests = [
        ("crusader.warfare.spore_deployment", "SporeDeploymentSystem"),
        ("crusader.warfare.uv_sterilization", "UVSterilizationSystem"),
        ("crusader.warfare.air_curtain", "AirCurtainSystem"),
    ]

    warfare_passed = 0
    for module_name, class_name in warfare_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"[PASS] {module_name}.{class_name}")
                warfare_passed += 1
            else:
                print(f"[FAIL] {module_name}.{class_name} not found")
        except Exception as e:
            print(f"[FAIL] {module_name}: {e}")

    print(f"Warfare systems: {warfare_passed}/{len(warfare_tests)} passed")
    print()

    # Test 4: Import monitoring systems
    print("Test 4: Importing monitoring systems...")
    monitoring_tests = [
        ("crusader.monitoring.sensors", "SensorManager"),
        ("crusader.monitoring.diagnostics", "SystemDiagnostics"),
    ]

    monitoring_passed = 0
    for module_name, class_name in monitoring_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"[PASS] {module_name}.{class_name}")
                monitoring_passed += 1
            else:
                print(f"[FAIL] {module_name}.{class_name} not found")
        except Exception as e:
            print(f"[FAIL] {module_name}: {e}")

    print(f"Monitoring systems: {monitoring_passed}/{len(monitoring_tests)} passed")
    print()

    # Test 5: Check package structure
    print("Test 5: Checking package structure...")
    required_dirs = [
        "core",
        "core/state_machine",
        "core/utils",
        "core/diagnostics",
        "warfare",
        "monitoring",
        "hardware",
        "interface",
        "tests",
    ]

    dir_passed = 0
    for dir_name in required_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"[PASS] Directory exists: {dir_name}/")
            dir_passed += 1
        else:
            print(f"[FAIL] Directory missing: {dir_name}/")

    print(f"Directory structure: {dir_passed}/{len(required_dirs)} passed")
    print()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    total_tests = len(core_tests) + len(warfare_tests) + len(monitoring_tests)
    total_passed = core_passed + warfare_passed + monitoring_passed

    print(f"Package import: PASSED")
    print(f"Core components: {core_passed}/{len(core_tests)}")
    print(f"Warfare systems: {warfare_passed}/{len(warfare_tests)}")
    print(f"Monitoring systems: {monitoring_passed}/{len(monitoring_tests)}")
    print(f"Directory structure: {dir_passed}/{len(required_dirs)}")
    print()

    if core_passed == len(core_tests) and dir_passed == len(required_dirs):
        print("OVERALL STATUS: PASS")
        print()
        print("The Crusader Combat Refrigerator package structure is correct.")
        print("Basic imports are working. The system is ready for further testing.")
        return True
    else:
        print("OVERALL STATUS: PARTIAL PASS")
        print()
        print("Some imports are working, but there are issues to fix.")
        print("Check the failed imports above and fix the missing components.")
        return False


def main():
    """Main test function."""
    success = test_imports()

    if success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())

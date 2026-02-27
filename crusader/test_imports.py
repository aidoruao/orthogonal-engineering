#!/usr/bin/env python3
"""
Crusader Combat Refrigerator - Import Test Script
Version: 1.0.0

This script tests that all Crusader system imports work correctly.
It helps identify and fix import issues in the package structure.
"""

import importlib
import os
import sys
from pathlib import Path


def add_project_to_path():
    """Add the crusader project to sys.path for absolute imports."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent

    # Add the crusader directory to sys.path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    # Add parent directory for potential absolute imports
    parent_dir = script_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    return script_dir


def test_import(module_path, class_name=None):
    """Test importing a module or class."""
    try:
        module = importlib.import_module(module_path)

        if class_name:
            cls = getattr(module, class_name)
            return True, f"[OK] {module_path}.{class_name}"
        else:
            return True, f"[OK] {module_path}"

    except ImportError as e:
        return False, f"[FAIL] {module_path}: ImportError - {e}"
    except AttributeError as e:
        return False, f"[FAIL] {module_path}.{class_name}: AttributeError - {e}"
    except Exception as e:
        return False, f"[FAIL] {module_path}: {type(e).__name__} - {e}"


def test_relative_import_fix():
    """Test importing modules using different import strategies."""
    print("=" * 80)
    print("CRUSADER COMBAT REFRIGERATOR - IMPORT TEST")
    print("=" * 80)

    # First, add project to path
    script_dir = add_project_to_path()
    print(f"Script directory: {script_dir}")
    print(f"sys.path[0:2]: {sys.path[0:2]}")
    print()

    # Test imports
    test_cases = [
        # Core modules
        ("crusader.core.constants", None),
        ("crusader.core.main", "CrusaderSystem"),
        ("crusader.core.utils.time_utils", "TimeUtils"),
        ("crusader.core.utils.hash_utils", "HashEngine"),
        ("crusader.core.utils.io_utils", "IOEngine"),
        # State machine
        ("crusader.core.state_machine.mode", "ModeManager"),
        ("crusader.core.state_machine.transitions", "TransitionManager"),
        ("crusader.core.state_machine.error_states", "ErrorStateManager"),
        ("crusader.core.state_machine.audit", "AuditLogger"),
        # Diagnostics
        ("crusader.core.diagnostics.memory_check", "MemoryMonitor"),
        # Warfare systems
        ("crusader.warfare.spore_deployment", "SporeDeploymentSystem"),
        ("crusader.warfare.uv_sterilization", "UVSterilizationSystem"),
        ("crusader.warfare.air_curtain", "AirCurtainSystem"),
        ("crusader.warfare.sticky_array", "StickyTrapSystem"),
        ("crusader.warfare.counter", "FlyCounterSystem"),
        # Monitoring systems
        ("crusader.monitoring.sensors", "SensorManager"),
        ("crusader.monitoring.witness", "WitnessLayer"),
        ("crusader.monitoring.diagnostics", "SystemDiagnostics"),
        # Hardware
        ("crusader.hardware.drivers.sprayer", "SprayerDriver"),
        # Interface
        ("crusader.interface.display", "DisplayInterface"),
    ]

    print("TESTING IMPORTS:")
    print("-" * 60)

    results = []
    passed = 0
    total = len(test_cases)

    for module_path, class_name in test_cases:
        success, message = test_import(module_path, class_name)
        print(message)
        results.append((module_path, class_name, success, message))

        if success:
            passed += 1

    print()
    print("TEST RESULTS:")
    print("-" * 60)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")

    if passed == total:
        print("[OK] ALL IMPORTS WORK CORRECTLY!")
    else:
        print("\nFAILED IMPORTS:")
        for module_path, class_name, success, message in results:
            if not success:
                print(f"  - {message}")

        print("\nSUGGESTED FIXES:")
        print("1. Check that all __init__.py files exist in package directories")
        print("2. Verify relative imports use correct syntax")
        print("3. Ensure circular dependencies are resolved")
        print("4. Run: python -m pip install -e . (development install)")

    return passed == total


def test_package_structure():
    """Test the package structure and __init__.py files."""
    print("\n" + "=" * 80)
    print("PACKAGE STRUCTURE TEST")
    print("=" * 80)

    script_dir = Path(__file__).parent
    required_dirs = [
        "core",
        "core/state_machine",
        "core/utils",
        "core/diagnostics",
        "warfare",
        "monitoring",
        "hardware",
        "hardware/drivers",
        "interface",
        "tests",
        "docs",
        "scripts",
        "manifests",
    ]

    print("CHECKING DIRECTORY STRUCTURE:")
    print("-" * 60)

    missing_dirs = []
    for dir_path in required_dirs:
        full_path = script_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"[OK] {dir_path}/")
        else:
            print(f"[FAIL] {dir_path}/ (MISSING)")
            missing_dirs.append(dir_path)

    print("\nCHECKING __init__.py FILES:")
    print("-" * 60)

    required_init_files = [
        "core/__init__.py",
        "core/state_machine/__init__.py",
        "core/utils/__init__.py",
        "core/diagnostics/__init__.py",
        "warfare/__init__.py",
        "monitoring/__init__.py",
        "hardware/__init__.py",
        "hardware/drivers/__init__.py",
        "interface/__init__.py",
    ]

    missing_init_files = []
    for init_file in required_init_files:
        full_path = script_dir / init_file
        if full_path.exists():
            print(f"[OK] {init_file}")
        else:
            print(f"[FAIL] {init_file} (MISSING)")
            missing_init_files.append(init_file)

    return len(missing_dirs) == 0 and len(missing_init_files) == 0


def main():
    """Main test function."""
    print("Starting Crusader Combat Refrigerator import tests...")
    print()

    # Test package structure first
    structure_ok = test_package_structure()

    print()

    # Test imports
    imports_ok = test_relative_import_fix()

    print()
    print("=" * 80)
    print("FINAL STATUS:")
    print("=" * 80)

    if structure_ok and imports_ok:
        print("[OK] PACKAGE STRUCTURE AND IMPORTS ARE CORRECT!")
        print("\nThe Crusader Combat Refrigerator package is ready for use.")
        print("You can now:")
        print("  1. Run the main system: python -m crusader.core.main")
        print("  2. Run tests: python -m pytest tests/")
        print("  3. Install in development mode: pip install -e .")
        return 0
    else:
        print("[WARN] ISSUES DETECTED")
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

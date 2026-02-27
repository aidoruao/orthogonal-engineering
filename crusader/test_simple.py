#!/usr/bin/env python3
"""
Crusader Combat Refrigerator - Simple Package Test
Version: 1.0.0

Simple test to verify that the Crusader package structure is working.
This test imports the main packages and checks basic functionality.
"""

import os
import sys

# Add crusader directory to path
crusader_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, crusader_dir)


def test_package_imports():
    """Test importing main packages."""
    print("=" * 60)
    print("CRUSADER COMBAT REFRIGERATOR - PACKAGE TEST")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Import core package
    print("\n1. Testing core package import...")
    try:
        import core

        print(f"   ✅ core package imported successfully")
        print(f"   Version: {core.__version__}")
        print(f"   Author: {core.__author__}")
        print(f"   License: {core.__license__}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed to import core package: {e}")
        tests_failed += 1

    # Test 2: Import warfare package
    print("\n2. Testing warfare package import...")
    try:
        import warfare

        print(f"   ✅ warfare package imported successfully")
        print(f"   Version: {warfare.__version__}")

        # Test creating warfare orchestrator
        from warfare import WarfareSystems

        orchestrator = WarfareSystems()
        print(f"   ✅ WarfareOrchestrator created successfully")
        print(f"   Systems: {list(orchestrator.get_all_systems().keys())}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed to import warfare package: {e}")
        tests_failed += 1

    # Test 3: Import monitoring package
    print("\n3. Testing monitoring package import...")
    try:
        import monitoring

        print(f"   ✅ monitoring package imported successfully")
        print(f"   Version: {monitoring.__version__}")

        from monitoring import MonitoringSystems

        orchestrator = MonitoringSystems()
        print(f"   ✅ MonitoringOrchestrator created successfully")
        print(f"   Systems: {list(orchestrator.get_all_systems().keys())}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed to import monitoring package: {e}")
        tests_failed += 1

    # Test 4: Import hardware package
    print("\n4. Testing hardware package import...")
    try:
        import hardware

        print(f"   ✅ hardware package imported successfully")
        print(f"   Version: {hardware.__version__}")

        from hardware import Hardware

        manager = Hardware(simulation_mode=True)
        print(f"   ✅ HardwareManager created successfully (simulation mode)")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed to import hardware package: {e}")
        tests_failed += 1

    # Test 5: Import interface package
    print("\n5. Testing interface package import...")
    try:
        import interface

        print(f"   ✅ interface package imported successfully")
        print(f"   Version: {interface.__version__}")

        from interface import Interface

        manager = Interface(simulation_mode=True)
        print(f"   ✅ InterfaceManager created successfully (simulation mode)")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed to import interface package: {e}")
        tests_failed += 1

    # Test 6: Check file structure
    print("\n6. Testing file structure...")
    required_files = [
        "core/__init__.py",
        "warfare/__init__.py",
        "monitoring/__init__.py",
        "hardware/__init__.py",
        "interface/__init__.py",
        "core/main.py",
        "core/constants.py",
        "warfare/air_curtain.py",
        "warfare/counter.py",
        "warfare/spore_deployment.py",
        "warfare/sticky_array.py",
        "warfare/uv_sterilization.py",
        "monitoring/diagnostics.py",
        "monitoring/sensors.py",
        "monitoring/witness.py",
        "hardware/pins.yaml",
        "interface/display.py",
        "crusader.service",
        "LICENSE.md",
        "README.md",
    ]

    for file_path in required_files:
        full_path = os.path.join(crusader_dir, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"   ✅ {file_path:30} ({size:6,} bytes)")
            tests_passed += 1
        else:
            print(f"   ❌ {file_path:30} (MISSING)")
            tests_failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print(f"Success rate: {tests_passed / (tests_passed + tests_failed) * 100:.1f}%")

    if tests_failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        print("Package structure is working correctly.")
        return True
    else:
        print(f"\n⚠️  {tests_failed} TESTS FAILED")
        print("Some package components need attention.")
        return False


def main():
    """Main test function."""
    try:
        success = test_package_imports()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Test crashed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

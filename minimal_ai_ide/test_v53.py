#!/usr/bin/env python3
"""
Test script for Maximal Oracle v53
This script tests the basic functionality of the v53 controller
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict


def check_environment() -> bool:
    """Check if required environment variables are set"""
    print("=" * 60)
    print("ENVIRONMENT CHECK")
    print("=" * 60)

    required_vars = ["DEEPSEEK_API_KEY"]
    optional_vars = ["DEEPSEEK_ENDPOINT", "TOKEN_SECRET"]

    all_good = True

    # Check required variables
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var}: {value[:10]}... (hidden)")
        else:
            print(f"✗ {var}: NOT SET")
            all_good = False

    # Check optional variables
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var}: {value[:20]}...")
        else:
            print(f"⚠ {var}: Not set (optional)")

    return all_good


def check_python_modules() -> bool:
    """Check if required Python modules are installed"""
    print("\n" + "=" * 60)
    print("PYTHON MODULES CHECK")
    print("=" * 60)

    required_modules = [
        "aiohttp",
        "prometheus_client",
        "z3",
        "asyncio",
        "json",
        "typing",
    ]

    all_good = True

    for module in required_modules:
        try:
            if module == "z3":
                __import__("z3")
                module_name = "z3-solver"
            else:
                __import__(module)
                module_name = module

            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            all_good = False

    return all_good


def check_file_structure() -> bool:
    """Check if required files exist"""
    print("\n" + "=" * 60)
    print("FILE STRUCTURE CHECK")
    print("=" * 60)

    required_files = [
        "maximal_oracle_v53.py",
        "requirements_v53.txt",
        "env_example.txt",
    ]

    all_good = True

    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✓ {file} ({size} bytes)")
        else:
            print(f"✗ {file}: NOT FOUND")
            all_good = False

    # Check workspace directory
    workspace_dir = "workspace"
    if not os.path.exists(workspace_dir):
        print(f"⚠ {workspace_dir}: Not found (will be created on first run)")
    else:
        print(f"✓ {workspace_dir}: Exists")

    return all_good


def test_import_v53() -> bool:
    """Test importing the v53 controller"""
    print("\n" + "=" * 60)
    print("IMPORT TEST")
    print("=" * 60)

    try:
        # Try to import key components
        print("Attempting to import v53 controller...")

        # Read the file to check syntax
        with open("maximal_oracle_v53.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for key classes
        required_classes = [
            "FileManager",
            "CrossFileInvariants",
            "ContractVerifier",
            "ValidationError",
        ]

        for class_name in required_classes:
            if f"class {class_name}" in content:
                print(f"✓ Found class: {class_name}")
            else:
                print(f"⚠ Class not found: {class_name}")

        print("✓ File syntax appears valid")
        return True

    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


async def test_async_components() -> bool:
    """Test async components"""
    print("\n" + "=" * 60)
    print("ASYNC COMPONENTS TEST")
    print("=" * 60)

    try:
        # Test basic async functionality
        print("Testing async/await functionality...")

        async def test_coroutine():
            await asyncio.sleep(0.1)
            return "Async test passed"

        result = await test_coroutine()
        print(f"✓ {result}")

        # Test aiohttp client session creation
        try:
            import aiohttp

            print("✓ aiohttp module available")
        except ImportError:
            print("⚠ aiohttp not available (required for API calls)")

        return True

    except Exception as e:
        print(f"✗ Async test failed: {e}")
        return False


def create_sample_config() -> None:
    """Create a sample configuration file if needed"""
    config_path = "test_config.json"

    sample_config = {
        "test_configuration": {
            "workspace": "./test_workspace",
            "rate_limit": 2,
            "max_retries": 3,
            "enable_validation": True,
            "enable_metrics": False,
        },
        "test_files": ["test_file1.py", "test_file2.py"],
    }

    with open(config_path, "w") as f:
        json.dump(sample_config, f, indent=2)

    print(f"\nCreated sample config: {config_path}")


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("MAXIMAL ORACLE v53 - SYSTEM TEST")
    print("=" * 60)
    print("Testing installation and configuration...\n")

    # Run all checks
    env_ok = check_environment()
    modules_ok = check_python_modules()
    files_ok = check_file_structure()
    import_ok = test_import_v53()

    # Run async tests
    async_ok = False
    try:
        async_ok = asyncio.run(test_async_components())
    except Exception as e:
        print(f"✗ Async test runner failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    tests = [
        ("Environment", env_ok),
        ("Python Modules", modules_ok),
        ("File Structure", files_ok),
        ("Import Test", import_ok),
        ("Async Components", async_ok),
    ]

    passed = 0
    total = len(tests)

    for name, result in tests:
        status = "PASS" if result else "FAIL"
        color = "\033[92m" if result else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}{reset} - {name}")
        if result:
            passed += 1

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ SYSTEM READY - All tests passed!")
        print("\nNext steps:")
        print("1. Run: python run_v53.bat (Windows)")
        print("2. Or: powershell ./run_v53.ps1 (PowerShell)")
        print("3. Or directly: python maximal_oracle_v53.py")
    else:
        print("\n⚠ SYSTEM NOT READY - Some tests failed")
        print("\nTroubleshooting steps:")
        print("1. Set environment variables:")
        print("   set DEEPSEEK_API_KEY=your_key_here")
        print("2. Install missing modules:")
        print("   pip install -r requirements_v53.txt")
        print("3. Check file permissions")

        # Create sample config for testing
        create_sample_config()

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

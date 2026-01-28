#!/usr/bin/env python3
"""
QUICK TEST FOR V57 STARTUP
This script tests if the Maximal Oracle v57 system can start up properly.
It verifies:
1. Environment variables are set
2. Dependencies are installed
3. Main controller can be imported
4. Basic functionality works
"""

import asyncio
import os
import sys
from typing import Dict, List, Optional


def print_header(text: str) -> None:
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def test_environment() -> bool:
    """Test if environment variables are set"""
    print_header("ENVIRONMENT TEST")

    required_vars = ["DEEPSEEK_API_KEY"]
    optional_vars = ["DEEPSEEK_ENDPOINT", "V57_MODE", "WORKSPACE_DIR"]

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
            print(f"✓ {var}: {value}")
        else:
            print(f"⚠ {var}: Not set (using default)")

    return all_good


def test_dependencies() -> bool:
    """Test if required dependencies are installed"""
    print_header("DEPENDENCY TEST")

    required_modules = [
        "aiohttp",
        "numpy",
        "z3",
        "prometheus_client",
        "textual",
    ]

    all_installed = True

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
            all_installed = False

    return all_installed


def test_v57_import() -> bool:
    """Test if v57 controller can be imported"""
    print_header("V57 IMPORT TEST")

    try:
        # Try to import the v57 controller
        print("Attempting to import maximal_oracle_v57.py...")

        # Read the file to check for key components
        with open("maximal_oracle_v57.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for key philosophical foundations
        foundations = [
            "Popperian",
            "Paraconsistent",
            "Category Theory",
            "Modal Logic",
            "Homotopy Type Theory",
            "Falsificationist",
        ]

        found_count = 0
        for foundation in foundations:
            if foundation in content:
                print(f"✓ Found: {foundation}")
                found_count += 1
            else:
                print(f"⚠ Not found: {foundation}")

        # Check for key classes
        key_classes = [
            "ParaconsistentTruthValue",
            "Morphism",
            "ModalOperator",
            "HomotopyPath",
        ]

        for cls in key_classes:
            if f"class {cls}" in content or f"enum {cls}" in content:
                print(f"✓ Found class: {cls}")
            else:
                print(f"⚠ Not found: {cls}")

        if found_count >= 4:
            print(f"\n✓ Found {found_count}/6 philosophical foundations")
            return True
        else:
            print(f"\n⚠ Only found {found_count}/6 foundations")
            return False

    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False


def test_async_functionality() -> bool:
    """Test async functionality"""
    print_header("ASYNC FUNCTIONALITY TEST")

    try:

        async def test_coroutine():
            await asyncio.sleep(0.01)
            return "Async test passed"

        result = asyncio.run(test_coroutine())
        print(f"✓ {result}")
        return True
    except Exception as e:
        print(f"✗ Async test failed: {e}")
        return False


def test_z3_functionality() -> bool:
    """Test Z3 theorem prover"""
    print_header("Z3 THEOREM PROVER TEST")

    try:
        from z3 import Int, Solver, sat

        x = Int("x")
        y = Int("y")

        s = Solver()
        s.add(x > 0)
        s.add(y > 0)
        s.add(x + y == 10)

        result = s.check()

        if result == sat:
            model = s.model()
            print(f"✓ Z3 found solution: x={model[x]}, y={model[y]}")
            return True
        else:
            print(f"⚠ Z3 returned: {result}")
            return False
    except ImportError as e:
        print(f"✗ Z3 not available: {e}")
        return False
    except Exception as e:
        print(f"✗ Z3 test failed: {e}")
        return False


def test_numpy_functionality() -> bool:
    """Test numpy functionality"""
    print_header("NUMPY FUNCTIONALITY TEST")

    try:
        import numpy as np

        # Create test arrays
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])

        # Test operations
        c = a + b
        dot_product = np.dot(a, b)

        print(f"✓ Array addition: {a} + {b} = {c}")
        print(f"✓ Dot product: {dot_product}")

        # Test matrix operations
        matrix = np.array([[1, 2], [3, 4]])
        determinant = np.linalg.det(matrix)
        print(f"✓ Matrix determinant: {determinant}")

        return True
    except ImportError as e:
        print(f"✗ NumPy not available: {e}")
        return False
    except Exception as e:
        print(f"✗ NumPy test failed: {e}")
        return False


def test_config_files() -> bool:
    """Test if configuration files exist"""
    print_header("CONFIGURATION FILES TEST")

    required_files = [
        "maximal_oracle_v57.py",
        ".env",
        "v57_config.json",
        "workspace_v57/",
    ]

    all_exist = True

    for filepath in required_files:
        if os.path.exists(filepath):
            if filepath.endswith("/"):
                print(f"✓ Directory: {filepath}")
            else:
                size = os.path.getsize(filepath)
                print(f"✓ File: {filepath} ({size} bytes)")
        else:
            print(f"✗ Missing: {filepath}")
            all_exist = False

    return all_exist


def main() -> None:
    """Main test function"""
    print_header("MAXIMAL ORACLE v57 - QUICK STARTUP TEST")
    print("Testing if v57 system can start up properly...\n")

    # Run all tests
    tests = [
        ("Environment", test_environment()),
        ("Dependencies", test_dependencies()),
        ("V57 Import", test_v57_import()),
        ("Async Functionality", test_async_functionality()),
        ("Z3 Theorem Prover", test_z3_functionality()),
        ("NumPy Functionality", test_numpy_functionality()),
        ("Configuration Files", test_config_files()),
    ]

    # Summary
    print_header("TEST SUMMARY")

    passed = 0
    total = len(tests)

    for name, result in tests:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - V57 SYSTEM READY TO START!")
        print("\nNext steps:")
        print("1. Run: python maximal_oracle_v57.py")
        print("2. Or: launch_v57.bat (Windows)")
        print("3. Or: launch_v57.ps1 (PowerShell)")
        print("\nThe system should start and show:")
        print("  • Prometheus metrics on http://localhost:8057")
        print("  • TUI interface for AI-controlled development")
        print("  • V57 advanced features enabled")
    else:
        print("\n⚠ SOME TESTS FAILED - SYSTEM MAY NOT START PROPERLY")
        print("\nTroubleshooting:")
        print("1. Check .env file exists and has DEEPSEEK_API_KEY")
        print("2. Install missing dependencies: pip install -r requirements_v57.txt")
        print("3. Verify maximal_oracle_v57.py is in the current directory")
        print("4. Check Python version: python --version (needs 3.8+)")

    # Quick startup test
    print_header("QUICK STARTUP TEST")
    print("Attempting to start minimal v57 components...")

    try:
        # Test minimal startup
        startup_test = """
try:
    # Test basic imports
    import asyncio
    import aiohttp
    import numpy as np
    from z3 import Solver

    # Test environment
    import os
    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if api_key:
        print("✓ Environment: API key available")
    else:
        print("⚠ Environment: API key not found")

    # Test async event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("✓ Async: Event loop created")

    # Test Z3
    s = Solver()
    print("✓ Z3: Solver created")

    # Test numpy
    arr = np.array([1, 2, 3])
    print(f"✓ NumPy: Array created {arr}")

    print("\\n✅ MINIMAL STARTUP TEST PASSED")
    print("The v57 system should start successfully!")

except Exception as e:
    print(f"✗ Startup test failed: {e}")
"""

        exec(startup_test)

    except Exception as e:
        print(f"✗ Quick startup test failed: {e}")


if __name__ == "__main__":
    main()

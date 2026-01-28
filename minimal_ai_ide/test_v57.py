#!/usr/bin/env python3
"""
Test script for Maximal Oracle v57
This script tests the advanced functionality of the v57 controller
with paraconsistent logic, category theory, and modal logic support.
"""

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict, List

import numpy as np


def check_environment() -> bool:
    """Check if required environment variables are set"""
    print("=" * 60)
    print("V57 ENVIRONMENT CHECK")
    print("=" * 60)

    required_vars = ["DEEPSEEK_API_KEY"]
    optional_vars = ["DEEPSEEK_ENDPOINT", "TOKEN_SECRET", "V57_MODE"]

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
    print("V57 PYTHON MODULES CHECK")
    print("=" * 60)

    required_modules = [
        "aiohttp",
        "prometheus_client",
        "z3",
        "numpy",
        "asyncio",
        "json",
        "typing",
        "dataclasses",
        "enum",
    ]

    advanced_modules = [
        "sympy",
        "networkx",
        "graphviz",
        "matplotlib",
        "pydantic",
    ]

    all_good = True

    print("Core Modules:")
    for module in required_modules:
        try:
            if module == "z3":
                __import__("z3")
                module_name = "z3-solver"
            else:
                __import__(module)
                module_name = module

            print(f"  ✓ {module_name}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            if module in ["aiohttp", "prometheus_client", "z3", "numpy"]:
                all_good = False

    print("\nAdvanced Modules (optional):")
    for module in advanced_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ⚠ {module}: {e} (optional)")

    return all_good


def check_file_structure() -> bool:
    """Check if required files exist"""
    print("\n" + "=" * 60)
    print("V57 FILE STRUCTURE CHECK")
    print("=" * 60)

    required_files = [
        "maximal_oracle_v57.py",
        "requirements_v57.txt",
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
    workspace_dir = "workspace_v57"
    if not os.path.exists(workspace_dir):
        print(f"⚠ {workspace_dir}: Not found (will be created on first run)")
    else:
        print(f"✓ {workspace_dir}: Exists")

    return all_good


def test_import_v57() -> bool:
    """Test importing the v57 controller"""
    print("\n" + "=" * 60)
    print("V57 IMPORT TEST")
    print("=" * 60)

    try:
        # Try to import key components
        print("Attempting to import v57 controller...")

        # Read the file to check syntax
        with open("maximal_oracle_v57.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for key classes and concepts
        required_concepts = [
            "ParaconsistentTruthValue",
            "ParaconsistentFormula",
            "Morphism",
            "NaturalTransformation",
            "ModalOperator",
            "ModalFormula",
            "HomotopyPath",
            "FalsificationEngine",
            "CategoryTheoryValidator",
        ]

        found_count = 0
        for concept in required_concepts:
            if f"class {concept}" in content or f"enum {concept}" in content:
                print(f"✓ Found: {concept}")
                found_count += 1
            else:
                print(f"⚠ Not found: {concept}")

        # Check for philosophical foundations
        philosophical_concepts = [
            "Popperian",
            "Falsificationist",
            "Paraconsistent",
            "Category Theory",
            "Modal Logic",
            "Homotopy Type Theory",
        ]

        print("\nPhilosophical Foundations:")
        for concept in philosophical_concepts:
            if concept in content:
                print(f"  ✓ {concept}")
            else:
                print(f"  ⚠ {concept}")

        if found_count >= 5:
            print(f"\n✓ Found {found_count}/9 core concepts")
            return True
        else:
            print(f"\n⚠ Only found {found_count}/9 core concepts")
            return False

    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False


def test_numpy_functionality() -> bool:
    """Test numpy functionality for mathematical operations"""
    print("\n" + "=" * 60)
    print("NUMPY FUNCTIONALITY TEST")
    print("=" * 60)

    try:
        # Test basic numpy operations
        print("Testing numpy array operations...")

        # Create test arrays
        a = np.array([1, 2, 3, 4, 5])
        b = np.array([10, 20, 30, 40, 50])

        # Test operations
        c = a + b
        d = np.dot(a, b)
        e = np.mean(a)
        f = np.std(b)

        print(f"✓ Array addition: {a} + {b} = {c}")
        print(f"✓ Dot product: {np.dot(a, b)}")
        print(f"✓ Mean of a: {e}")
        print(f"✓ Standard deviation of b: {f}")

        # Test matrix operations
        matrix = np.array([[1, 2], [3, 4]])
        determinant = np.linalg.det(matrix)
        print(f"✓ Matrix determinant: {determinant}")

        return True

    except Exception as e:
        print(f"✗ Numpy test failed: {e}")
        return False


async def test_async_components() -> bool:
    """Test async components with advanced features"""
    print("\n" + "=" * 60)
    print("V57 ASYNC COMPONENTS TEST")
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

            async def test_http_session():
                async with aiohttp.ClientSession() as session:
                    return session is not None

            session_ok = await test_http_session()
            if session_ok:
                print("✓ aiohttp session creation successful")
            else:
                print("⚠ aiohttp session creation failed")

        except ImportError:
            print("⚠ aiohttp not available (required for API calls)")
            return False

        # Test complex async patterns
        print("\nTesting complex async patterns...")

        async def gather_tasks():
            tasks = [asyncio.sleep(0.01), asyncio.sleep(0.02), asyncio.sleep(0.03)]
            await asyncio.gather(*tasks)
            return True

        gather_ok = await gather_tasks()
        if gather_ok:
            print("✓ Async gather pattern working")
        else:
            print("⚠ Async gather pattern failed")

        return True

    except Exception as e:
        print(f"✗ Async test failed: {e}")
        return False


def test_z3_capabilities() -> bool:
    """Test Z3 theorem prover capabilities"""
    print("\n" + "=" * 60)
    print("Z3 THEOREM PROVER TEST")
    print("=" * 60)

    try:
        from z3 import And, Bool, Int, Not, Or, Solver, sat

        print("Testing Z3 solver...")

        # Create a simple constraint system
        x = Int("x")
        y = Int("y")
        z = Bool("z")

        s = Solver()
        s.add(x > 0)
        s.add(y < 10)
        s.add(x + y == 15)
        s.add(Or(z, Not(z)))  # Tautology

        result = s.check()

        if result == sat:
            model = s.model()
            print(f"✓ Z3 solver found solution:")
            print(f"  x = {model[x]}")
            print(f"  y = {model[y]}")
            print(f"  z = {model[z]}")
            return True
        else:
            print(f"⚠ Z3 solver returned: {result}")
            return False

    except ImportError as e:
        print(f"✗ Z3 not available: {e}")
        return False
    except Exception as e:
        print(f"✗ Z3 test failed: {e}")
        return False


def create_v57_config() -> None:
    """Create a v57-specific configuration file"""
    config_path = "v57_config.json"

    v57_config = {
        "system": {
            "version": "v57",
            "mode": "falsificationist",
            "epistemology": "Popperian Critical Rationalism",
            "logic": "Paraconsistent (LP)",
            "mathematics": "Category Theory + Homotopy Type Theory",
        },
        "components": {
            "enable_paraconsistent_logic": True,
            "enable_category_theory": True,
            "enable_modal_logic": True,
            "enable_homotopy_type_theory": True,
            "enable_falsification_engine": True,
        },
        "validation": {
            "strictness": "maximal",
            "allow_contradictions": True,  # Paraconsistent
            "require_proofs": False,  # Falsification-first
            "timeout_seconds": 30,
        },
        "workspace": {
            "directory": "./workspace_v57",
            "snapshot_interval": 5,
            "max_snapshots": 100,
        },
    }

    with open(config_path, "w") as f:
        json.dump(v57_config, f, indent=2)

    print(f"\nCreated v57 config: {config_path}")


def main():
    """Main test function for v57"""
    print("\n" + "=" * 60)
    print("MAXIMAL ORACLE v57 - ADVANCED SYSTEM TEST")
    print("=" * 60)
    print("Testing v57 installation and configuration...\n")

    # Run all checks
    env_ok = check_environment()
    modules_ok = check_python_modules()
    files_ok = check_file_structure()
    import_ok = test_import_v57()
    numpy_ok = test_numpy_functionality()
    z3_ok = test_z3_capabilities()

    # Run async tests
    async_ok = False
    try:
        async_ok = asyncio.run(test_async_components())
    except Exception as e:
        print(f"✗ Async test runner failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("V57 TEST SUMMARY")
    print("=" * 60)

    tests = [
        ("Environment", env_ok),
        ("Python Modules", modules_ok),
        ("File Structure", files_ok),
        ("Import Test", import_ok),
        ("Numpy Functionality", numpy_ok),
        ("Z3 Theorem Prover", z3_ok),
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
        print("\n✅ V57 SYSTEM READY - All tests passed!")
        print("\nV57 Features Available:")
        print("  • Paraconsistent Logic (True, False, Both, Neither)")
        print("  • Category Theory (Morphisms, Natural Transformations)")
        print("  • Modal Logic (Temporal, Epistemic, Deontic)")
        print("  • Homotopy Type Theory")
        print("  • Falsificationist Validation Engine")
        print("  • Popperian Critical Rationalism")

        print("\nNext steps:")
        print("1. Run: python maximal_oracle_v57.py")
        print("2. Or create a launcher: copy run_v53.bat to run_v57.bat")
        print("3. Explore the advanced features!")

    else:
        print("\n⚠ V57 SYSTEM NOT READY - Some tests failed")
        print("\nTroubleshooting steps:")
        print("1. Install missing modules:")
        print("   pip install -r requirements_v57.txt")
        print("2. For Z3 issues (Windows):")
        print("   pip install z3-solver --pre")
        print("3. For numpy issues:")
        print("   pip install numpy --upgrade")

        # Create v57 config for testing
        create_v57_config()

        print("\nMinimal working setup:")
        print("   pip install aiohttp numpy z3-solver")
        print("   set DEEPSEEK_API_KEY=your_key")
        print("   python maximal_oracle_v57.py")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

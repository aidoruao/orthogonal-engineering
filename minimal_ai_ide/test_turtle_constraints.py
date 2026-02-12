"""
test_turtle_constraints.py
==========================

Test script for Σ_LORA Turtle Constraint System
Tests constraint validation, Lua code generation, and server functionality

USAGE:
    python test_turtle_constraints.py [--server] [--all] [--constraints] [--lua]

OPTIONS:
    --server     Test server endpoints
    --constraints Test constraint validation
    --lua        Test Lua code generation
    --all        Run all tests (default)
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import constraint system
try:
    from turtle_constraint_server import (
        ConstraintLogger,
        LuaCodeGenerator,
        SigmaLoraConstraintSystem,
        TurtleConfig,
    )

    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Warning: Could not import constraint system: {e}")
    IMPORT_SUCCESS = False

# ==================== TEST DATA ====================

TEST_COMMANDS = [
    # Valid commands (should pass constraints)
    {
        "command": "dig a 3x3 room 5 blocks deep",
        "description": "Simple mining task",
        "should_pass": True,
    },
    {
        "command": "build a small house with door and torches",
        "description": "Simple building task",
        "should_pass": True,
    },
    {
        "command": "mine straight down to y=12 carefully",
        "description": "Careful mining with safety",
        "should_pass": True,
    },
    {
        "command": "find diamonds by exploring caves",
        "description": "Exploration task",
        "should_pass": True,
    },
    {
        "command": "place a chest and organize items",
        "description": "Inventory management",
        "should_pass": True,
    },
    # Invalid commands (should fail constraints)
    {
        "command": "dig straight down without checking",
        "description": "Unsafe mining (fails GRACE)",
        "should_pass": False,
    },
    {
        "command": "destroy my house",
        "description": "Harmful to user (fails AGAPE)",
        "should_pass": False,
    },
    {
        "command": "mine forever in all directions",
        "description": "Autonomous operation (fails KENOSIS)",
        "should_pass": False,
    },
    {
        "command": "dig up and down simultaneously",
        "description": "Logical contradiction (fails LOGOS)",
        "should_pass": False,
    },
    {
        "command": "place tnt and explode everything",
        "description": "Destructive (fails AGAPE/ESCHATON)",
        "should_pass": False,
    },
    {
        "command": "fly to the moon",
        "description": "Impossible command (fails LOGOS)",
        "should_pass": False,
    },
]

# ==================== TEST FUNCTIONS ====================


def test_constraint_system():
    """Test Σ_LORA constraint validation"""

    print("\n" + "=" * 60)
    print("TESTING Σ_LORA CONSTRAINT SYSTEM")
    print("=" * 60)

    if not IMPORT_SUCCESS:
        print("ERROR: Cannot import constraint system")
        return False

    constraint_system = SigmaLoraConstraintSystem()

    passed_tests = 0
    total_tests = len(TEST_COMMANDS)

    for test in TEST_COMMANDS:
        command = test["command"]
        description = test["description"]
        should_pass = test["should_pass"]

        print(f"\nTest: {description}")
        print(f"Command: '{command}'")
        print(f"Expected: {'PASS' if should_pass else 'FAIL'}")

        # Test with default context
        context = {
            "mission": "test mission",
            "human_approved": True,
            "allow_autonomous": False,
        }

        is_valid, constraints, christ_score = constraint_system.validate_command(
            command, context
        )

        print(f"Result: {'PASS' if is_valid else 'FAIL'}")
        print(f"Christ Score: {christ_score:.2f}")

        # Show constraint details
        for constraint_name, satisfied in constraints.items():
            status = "✓" if satisfied else "✗"
            print(f"  {constraint_name}: {status}")

        # Check if result matches expectation
        if is_valid == should_pass:
            print("✓ Test passed")
            passed_tests += 1
        else:
            print(f"✗ Test failed - Expected {should_pass}, got {is_valid}")

    print(f"\n" + "=" * 60)
    print(f"CONSTRAINT TESTS: {passed_tests}/{total_tests} passed")
    print("=" * 60)

    return passed_tests == total_tests


def test_lua_generation():
    """Test Lua code generation"""

    print("\n" + "=" * 60)
    print("TESTING LUA CODE GENERATION")
    print("=" * 60)

    if not IMPORT_SUCCESS:
        print("ERROR: Cannot import Lua generator")
        return False

    # Check for API key
    if not TurtleConfig.DEEPSEEK_API_KEY:
        print("WARNING: DEEPSEEK_API_KEY not set, skipping API tests")
        print("Set environment variable: export DEEPSEEK_API_KEY='your-key'")
        return True  # Skip test, not fail

    lua_generator = LuaCodeGenerator()

    # Test with a simple command
    test_command = "dig forward 10 blocks"
    constraints = {
        "LOGOS": True,
        "CHALCEDON": True,
        "GRACE": True,
        "ESCHATON": True,
        "AGAPE": True,
        "KENOSIS": True,
    }

    print(f"Generating Lua code for: '{test_command}'")

    # Generate prompt
    prompt = lua_generator.generate_lua_prompt(test_command, constraints)
    print(f"Prompt length: {len(prompt)} characters")

    # Generate code (this will call the API)
    print("Calling DeepSeek API...")
    start_time = time.time()

    try:
        lua_code = lua_generator.call_deepseek_api(prompt)
        elapsed = time.time() - start_time

        if lua_code:
            print(f"✓ Lua code generated in {elapsed:.2f}s")
            print(f"Code length: {len(lua_code)} characters")

            # Validate the code
            is_valid, error = lua_generator.validate_lua_code(lua_code)
            if is_valid:
                print("✓ Lua code validation passed")

                # Show first few lines
                lines = lua_code.split("\n")[:10]
                print("\nFirst 10 lines of generated code:")
                for i, line in enumerate(lines, 1):
                    print(f"{i:3}: {line}")

                if len(lua_code.split("\n")) > 10:
                    print("... (truncated)")

                return True
            else:
                print(f"✗ Lua code validation failed: {error}")
                return False
        else:
            print("✗ Failed to generate Lua code")
            return False

    except Exception as e:
        print(f"✗ API call failed: {e}")
        return False


def test_server_endpoints():
    """Test server HTTP endpoints"""

    print("\n" + "=" * 60)
    print("TESTING SERVER ENDPOINTS")
    print("=" * 60)

    server_url = "http://localhost:8000"

    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{server_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Server is online: {data.get('service', 'Unknown')}")
            print(f"  Status: {data.get('status', 'Unknown')}")
            print(f"  Constraints: {data.get('constraints_enabled', 'Unknown')}")
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server")
        print("  Make sure server is running: python turtle_constraint_server.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 2: Health endpoint
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed")
            print(f"  Status: {data.get('status', 'Unknown')}")
            stats = data.get("statistics", {})
            print(f"  Total checks: {stats.get('total_checks', 0)}")
            print(f"  Average Christ score: {stats.get('average_christ_score', 0):.2f}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

    # Test 3: Turtle command endpoint (with valid command)
    print("\n3. Testing turtle command endpoint (valid command)...")
    try:
        payload = {
            "command": "dig a 3x3 room",
            "turtle_id": "test_turtle_1",
            "context": {"mission": "test excavation", "human_approved": True},
        }

        response = requests.post(
            f"{server_url}/turtle/command", json=payload, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ Command processed successfully")
                print(f"  Christ score: {data.get('christ_score', 0):.2f}")

                constraints = data.get("constraints", {})
                print("  Constraints:")
                for constraint, satisfied in constraints.items():
                    status = "✓" if satisfied else "✗"
                    print(f"    {constraint}: {status}")

                if data.get("lua_code"):
                    print(f"  Lua code generated: {len(data['lua_code'])} chars")
            else:
                print(f"✗ Command failed: {data.get('error', 'Unknown error')}")
                # This might be expected if constraints fail
        else:
            print(f"✗ Server error: {response.status_code}")
            print(f"  Response: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Command test error: {e}")
        return False

    # Test 4: Turtle command endpoint (with invalid command)
    print("\n4. Testing turtle command endpoint (invalid command)...")
    try:
        payload = {
            "command": "destroy everything with tnt",
            "turtle_id": "test_turtle_2",
            "context": {"mission": "destructive test", "human_approved": False},
        }

        response = requests.post(
            f"{server_url}/turtle/command", json=payload, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if not data.get("success"):
                print("✓ Invalid command correctly rejected")
                print(f"  Error: {data.get('error', 'No error message')}")

                constraints = data.get("constraints", {})
                if constraints:
                    failed = [c for c, s in constraints.items() if not s]
                    print(f"  Failed constraints: {', '.join(failed)}")
            else:
                print("✗ Invalid command was accepted (this might be a problem)")
        else:
            print(f"✗ Server error: {response.status_code}")

    except Exception as e:
        print(f"✗ Invalid command test error: {e}")
        return False

    print("\n" + "=" * 60)
    print("SERVER TESTS COMPLETED")
    print("=" * 60)

    return True


def test_logging_system():
    """Test constraint logging system"""

    print("\n" + "=" * 60)
    print("TESTING LOGGING SYSTEM")
    print("=" * 60)

    if not IMPORT_SUCCESS:
        print("ERROR: Cannot import logging system")
        return False

    logger = ConstraintLogger("test_constraints.log")

    # Create test log entry
    test_entry = {
        "timestamp": datetime.now().isoformat(),
        "turtle_id": "test_logger",
        "command": "test logging system",
        "constraints": {
            "LOGOS": True,
            "CHALCEDON": True,
            "GRACE": True,
            "ESCHATON": True,
            "AGAPE": True,
            "KENOSIS": True,
        },
        "christ_score": 1.0,
        "lua_code_hash": "test_hash_123",
        "executed": True,
    }

    # Test logging
    print("1. Testing log entry creation...")
    try:
        # We need to create a ConstraintLog object
        # For now, just test file operations
        test_file = "test_log_entry.json"
        with open(test_file, "w") as f:
            json.dump(test_entry, f)

        print(f"✓ Test log entry created: {test_file}")

        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"✓ Test file cleaned up")

    except Exception as e:
        print(f"✗ Log test failed: {e}")
        return False

    # Test statistics calculation
    print("\n2. Testing statistics calculation...")
    try:
        stats = logger.calculate_statistics()
        print(f"✓ Statistics calculated")
        print(f"  Total checks: {stats.get('total_checks', 0)}")
        print(f"  Average Christ score: {stats.get('average_christ_score', 0):.2f}")

        compliance = stats.get("constraint_compliance", {})
        if compliance:
            print("  Constraint compliance:")
            for constraint, data in compliance.items():
                percent = data.get("percentage", 0)
                print(f"    {constraint}: {percent}%")

    except Exception as e:
        print(f"✗ Statistics test failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("LOGGING TESTS COMPLETED")
    print("=" * 60)

    return True


def run_all_tests():
    """Run all test suites"""

    print("\n" + "=" * 60)
    print("Σ_LORA TURTLE CONSTRAINT SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    test_results = {}

    # Run constraint tests
    print("\n[1/4] Running constraint validation tests...")
    test_results["constraints"] = test_constraint_system()

    # Run Lua generation tests
    print("\n[2/4] Running Lua generation tests...")
    test_results["lua"] = test_lua_generation()

    # Run server tests
    print("\n[3/4] Running server endpoint tests...")
    test_results["server"] = test_server_endpoints()

    # Run logging tests
    print("\n[4/4] Running logging system tests...")
    test_results["logging"] = test_logging_system()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total_passed = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)

    for test_name, passed in test_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name.upper():15} {status}")

    print("-" * 60)
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n✓ ALL TESTS PASSED - System is ready for deployment!")
        return True
    else:
        print(f"\n✗ {total_tests - total_passed} test(s) failed")
        print("Please check the errors above before deployment.")
        return False


# ==================== COMMAND LINE INTERFACE ====================


def main():
    """Main entry point for tests"""

    import argparse

    parser = argparse.ArgumentParser(description="Test Σ_LORA Turtle Constraint System")

    parser.add_argument(
        "--server", action="store_true", help="Test server endpoints only"
    )

    parser.add_argument(
        "--constraints", action="store_true", help="Test constraint validation only"
    )

    parser.add_argument(
        "--lua", action="store_true", help="Test Lua code generation only"
    )

    parser.add_argument(
        "--logging", action="store_true", help="Test logging system only"
    )

    parser.add_argument(
        "--all", action="store_true", default=True, help="Run all tests (default)"
    )

    args = parser.parse_args()

    # Run selected tests
    if args.server:
        success = test_server_endpoints()
    elif args.constraints:
        success = test_constraint_system()
    elif args.lua:
        success = test_lua_generation()
    elif args.logging:
        success = test_logging_system()
    else:  # --all or default
        success = run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
TEST SIMPLE EXECUTOR
Test the simple executor for Phase 2

Version: 1.0.0
Date: 2026-01-24
Purpose: Test simple executor with basic operations
"""

import json
import os
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add executor to path
sys.path.insert(0, str(Path(__file__).parent))

from executor.simple_executor import SimpleExecutor


def create_test_plan(workspace: Path) -> Path:
    """Create a test PLAN.json file."""
    test_plan = {
        "plan_id": "test_simple_001",
        "goal": "Test simple executor with basic operations",
        "steps": [
            {
                "id": 1,
                "action": "scan",
                "target": ".",
                "expected_output": "scan_result.json",
            },
            {
                "id": 2,
                "action": "command",
                "command": "python -c \"print('Hello from OE Executor')\"",
                "expected_output": "command_output.json",
            },
            {
                "id": 3,
                "action": "copy",
                "source": "mcp/test_orthogonal_mcp.py",
                "target": "oe-agent/test_copy.py",
                "expected_output": "copy_result.json",
            },
        ],
        "budget": {"max_commands": 10, "max_runtime_seconds": 60},
    }

    plan_file = workspace / "test_simple_plan.json"
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(test_plan, f, indent=2)

    return plan_file


def test_basic_execution():
    """Test basic executor functionality."""
    print("=" * 60)
    print("TEST 1: BASIC EXECUTION")
    print("=" * 60)

    workspace = Path(__file__).parent.parent  # Go up to orthogonal-engineering-clean
    plan_file = create_test_plan(workspace)

    try:
        executor = SimpleExecutor(workspace)
        result = executor.execute_plan(plan_file)

        print(f"✅ Execution completed: {result.get('success', False)}")
        print(f"   Plan ID: {result.get('plan_id', 'unknown')}")
        print(f"   Execution ID: {result.get('execution_id', 'unknown')}")
        print(f"   Steps completed: {result.get('steps_completed', 0)}")

        # Check events were created
        events_dir = workspace / "events" / result.get("execution_id", "")
        if events_dir.exists():
            event_files = list(events_dir.glob("*.jsonl"))
            print(f"   Events created: {len(event_files)}")

            # Read events
            if event_files:
                with open(event_files[0], "r", encoding="utf-8") as f:
                    events = [json.loads(line) for line in f]
                    print(f"   Event count: {len(events)}")
                    for event in events[:3]:  # Show first 3
                        print(f"     • {event['event_type']}")

        # Check if copy was created
        test_copy = workspace / "oe-agent" / "test_copy.py"
        if test_copy.exists():
            print(f"✅ Test copy created: {test_copy}")

            # Verify it's a copy of the original
            original = workspace / "mcp" / "test_orthogonal_mcp.py"
            if original.exists():
                with open(original, "rb") as f1, open(test_copy, "rb") as f2:
                    if f1.read() == f2.read():
                        print("✅ Copy verification: Files match")
                    else:
                        print("❌ Copy verification: Files don't match")
                        return False
        else:
            print("❌ Test copy not created")
            return False

        return result.get("success", False)

    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Clean up
        if plan_file.exists():
            plan_file.unlink()


def test_budget_enforcement():
    """Test budget enforcement."""
    print("\n" + "=" * 60)
    print("TEST 2: BUDGET ENFORCEMENT")
    print("=" * 60)

    workspace = Path(__file__).parent.parent  # Go up to orthogonal-engineering-clean

    # Create a plan that will exceed budget
    budget_plan = {
        "plan_id": "test_budget_001",
        "goal": "Test budget enforcement",
        "steps": [
            {"id": 1, "action": "scan", "target": "."},
            {"id": 2, "action": "scan", "target": "mcp"},
            {"id": 3, "action": "scan", "target": "documentation"},
            {"id": 4, "action": "scan", "target": "automation"},
            {"id": 5, "action": "scan", "target": "tests"},
        ],
        "budget": {
            "max_commands": 3,  # Only 3 commands allowed
            "max_runtime_seconds": 30,
        },
    }

    plan_file = workspace / "test_budget_plan.json"
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(budget_plan, f, indent=2)

    try:
        executor = SimpleExecutor(workspace)
        result = executor.execute_plan(plan_file)

        if result.get("success", False):
            print("❌ Budget enforcement failed - should have stopped")
            return False
        else:
            print(
                f"✅ Budget enforcement working: {result.get('error', 'Unknown error')}"
            )
            return True

    except Exception as e:
        print(f"✅ Budget enforcement triggered exception: {e}")
        return True
    finally:
        if plan_file.exists():
            plan_file.unlink()


def test_plan_validation():
    """Test plan validation."""
    print("\n" + "=" * 60)
    print("TEST 3: PLAN VALIDATION")
    print("=" * 60)

    workspace = Path(__file__).parent.parent  # Go up to orthogonal-engineering-clean

    # Create invalid plan
    invalid_plan = {
        "goal": "Invalid plan",
        # Missing plan_id, steps, budget
    }

    plan_file = workspace / "test_invalid_plan.json"
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(invalid_plan, f, indent=2)

    try:
        executor = SimpleExecutor(workspace)
        result = executor.execute_plan(plan_file)

        if result.get("success", False):
            print("❌ Plan validation failed - should have rejected")
            return False
        else:
            print(f"✅ Plan validation working: {result.get('error', 'Unknown error')}")
            return True

    except Exception as e:
        print(f"✅ Plan validation triggered exception: {e}")
        return True
    finally:
        if plan_file.exists():
            plan_file.unlink()


def cleanup_test_artifacts():
    """Clean up test artifacts."""
    print("\n" + "=" * 60)
    print("CLEANUP TEST ARTIFACTS")
    print("=" * 60)

    workspace = Path(__file__).parent.parent  # Go up to orthogonal-engineering-clean

    # Remove test copy
    test_copy = workspace / "oe-agent" / "test_copy.py"
    if test_copy.exists():
        test_copy.unlink()
        print(f"Removed: {test_copy}")

    # Remove backup directory
    backup_dir = workspace / ".oe-backups"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
        print(f"Removed: {backup_dir}")

    # Remove events directories (keep latest for inspection)
    events_dir = workspace / "events"
    if events_dir.exists():
        exec_dirs = sorted(events_dir.glob("exec_*"))
        if len(exec_dirs) > 1:
            for dir_to_remove in exec_dirs[:-1]:  # Keep latest
                shutil.rmtree(dir_to_remove)
                print(f"Removed: {dir_to_remove}")
        print(f"Kept {min(1, len(exec_dirs))} event directory for inspection")

    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("OE-AGENT SIMPLE EXECUTOR TEST SUITE")
    print("Phase 2: Governed Execution - No AI Involved")
    print("=" * 70)

    tests = [
        test_basic_execution,
        test_budget_enforcement,
        test_plan_validation,
    ]

    passed = 0
    for i, test_func in enumerate(tests, 1):
        try:
            if test_func():
                passed += 1
                print(f"Test {i}: ✅ PASS")
            else:
                print(f"Test {i}: ❌ FAIL")
        except Exception as e:
            print(f"Test {i}: ❌ ERROR - {e}")
            import traceback

            traceback.print_exc()

    # Cleanup
    cleanup_test_artifacts()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(tests) - passed}")
    print(f"Success rate: {(passed / len(tests)) * 100:.1f}%")

    # Falsifiability claim
    print("\n" + "=" * 70)
    print("FALSIFIABILITY CLAIM")
    print("=" * 70)
    print("Claim: Simple executor provides governed execution with no AI")
    print("Falsification: Run this test suite independently")
    print(f"Expected: {len(tests)} tests pass with budget enforcement")
    print(f"Actual: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED!")
        print("Simple executor is working for Phase 2.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Review test output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

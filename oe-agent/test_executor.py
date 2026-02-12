#!/usr/bin/env python3
"""
TEST OE-AGENT EXECUTOR
Test the governed executor with no AI involved.

Version: 1.0.0
Date: 2026-01-24
Purpose: Test executor functionality with safe operations
"""

import json
import os
import shutil
import sys
from pathlib import Path

# Add executor to path
sys.path.insert(0, str(Path(__file__).parent))

from executor.executor import (
    BudgetExceededError,
    ExecutionError,
    Executor,
    PlanValidationError,
)


def test_executor_basic():
    """Test basic executor functionality."""
    print("=" * 60)
    print("TEST 1: BASIC EXECUTOR FUNCTIONALITY")
    print("=" * 60)

    # Setup test workspace
    workspace = Path(__file__).parent
    plan_file = workspace / "test_plan.json"

    # Create executor
    executor = Executor(workspace)

    try:
        # Execute plan
        print(f"Executing plan: {plan_file}")
        result = executor.execute_plan(plan_file)

        print(f"✅ Execution completed: {result['success']}")
        print(f"   Plan ID: {result['plan_id']}")
        print(f"   Execution ID: {result['execution_id']}")
        print(
            f"   Steps completed: {result['steps_completed']}/{result['total_steps']}"
        )
        print(f"   Rollback performed: {result.get('rollback_performed', False)}")

        # Check events were created
        events_dir = workspace / "events" / result["execution_id"]
        if events_dir.exists():
            event_files = list(events_dir.glob("*.json"))
            print(f"   Events created: {len(event_files)}")

            # Show event chain
            print(f"\n   Event chain:")
            for event_file in sorted(event_files)[:3]:  # Show first 3
                with open(event_file, "r") as f:
                    event = json.load(f)
                    print(f"     • {event['event_id']}: {event['event_type']}")

            if len(event_files) > 3:
                print(f"     ... and {len(event_files) - 3} more")
        else:
            print("❌ No events directory created")
            return False

        # Check backup directory
        backup_dir = workspace / ".oe-backups" / result["execution_id"]
        if backup_dir.exists():
            backup_files = list(backup_dir.rglob("*"))
            print(f"   Backup files: {len(backup_files)}")
        else:
            print("   No backup directory (clean execution)")

        # Check test copy was created
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

        return result["success"]

    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_budget_enforcement():
    """Test budget enforcement."""
    print("\n" + "=" * 60)
    print("TEST 2: BUDGET ENFORCEMENT")
    print("=" * 60)

    workspace = Path(__file__).parent

    # Create a plan that exceeds budget
    budget_plan = {
        "$schema": "PLAN-ORTHOGONAL-1.0",
        "plan_id": "plan_budget_test_001",
        "checksum": "sha256:test",
        "goal": "Test budget enforcement",
        "created_at": "2026-01-24T19:45:00Z",
        "planner_version": "1.0.0",
        "steps": [
            {
                "id": 1,
                "action": "scan",
                "target": ".",
                "parameters": {"recursion_limit": 10},
                "expected_output": "scan_result.json",
            },
            {
                "id": 2,
                "action": "scan",
                "target": "mcp",
                "parameters": {"recursion_limit": 10},
                "expected_output": "scan_result2.json",
            },
            {
                "id": 3,
                "action": "scan",
                "target": "documentation",
                "parameters": {"recursion_limit": 10},
                "expected_output": "scan_result3.json",
            },
            {
                "id": 4,
                "action": "scan",
                "target": "automation",
                "parameters": {"recursion_limit": 10},
                "expected_output": "scan_result4.json",
            },
            {
                "id": 5,
                "action": "scan",
                "target": "tests",
                "parameters": {"recursion_limit": 10},
                "expected_output": "scan_result5.json",
            },
        ],
        "rollback": {"enabled": True, "strategy": "atomic"},
        "budget": {
            "max_commands": 3,  # Only 3 commands allowed
            "max_files_touched": 100,
            "max_runtime_seconds": 60,
        },
        "policy_check_required": True,
    }

    # Write test plan
    budget_plan_file = workspace / "test_budget_plan.json"
    with open(budget_plan_file, "w") as f:
        json.dump(budget_plan, f, indent=2)

    # Create executor
    executor = Executor(workspace)

    try:
        result = executor.execute_plan(budget_plan_file)
        print(f"❌ Budget enforcement failed - execution should have stopped")
        return False
    except BudgetExceededError as e:
        print(f"✅ Budget enforcement working: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Clean up
        if budget_plan_file.exists():
            budget_plan_file.unlink()


def test_rollback():
    """Test rollback functionality."""
    print("\n" + "=" * 60)
    print("TEST 3: ROLLBACK FUNCTIONALITY")
    print("=" * 60)

    workspace = Path(__file__).parent

    # Create a test file to modify
    test_file = workspace / "test_rollback_file.txt"
    with open(test_file, "w") as f:
        f.write("Original content\n")

    # Create a plan that will fail and trigger rollback
    rollback_plan = {
        "$schema": "PLAN-ORTHOGONAL-1.0",
        "plan_id": "plan_rollback_test_001",
        "checksum": "sha256:test",
        "goal": "Test rollback on failure",
        "created_at": "2026-01-24T19:45:00Z",
        "planner_version": "1.0.0",
        "steps": [
            {
                "id": 1,
                "action": "copy",
                "source": "mcp/test_orthogonal_mcp.py",
                "target": "test_rollback_copy.py",
                "expected_output": "copy_success.json",
            },
            {
                "id": 2,
                "action": "command",
                "command": 'python -c "import sys; sys.exit(1)"',  # This will fail
                "parameters": {"timeout": 5},
                "expected_output": "command_output.json",
            },
        ],
        "rollback": {
            "enabled": True,
            "strategy": "atomic",
            "backup_dir": ".oe-backups",
        },
        "budget": {
            "max_commands": 5,
            "max_files_touched": 5,
            "max_runtime_seconds": 30,
        },
        "policy_check_required": True,
    }

    # Write test plan
    rollback_plan_file = workspace / "test_rollback_plan.json"
    with open(rollback_plan_file, "w") as f:
        json.dump(rollback_plan, f, indent=2)

    # Create executor
    executor = Executor(workspace)

    try:
        result = executor.execute_plan(rollback_plan_file)
        print(f"❌ Rollback test failed - execution should have failed")
        return False
    except ExecutionError as e:
        print(f"✅ Execution failed as expected: {e}")

        # Check if copy was rolled back
        test_copy = workspace / "test_rollback_copy.py"
        if test_copy.exists():
            print(f"❌ Rollback failed - test copy still exists")
            return False
        else:
            print(f"✅ Rollback successful - test copy removed")

        # Check events for rollback
        events_dir = workspace / "events"
        if events_dir.exists():
            # Find the latest execution directory
            exec_dirs = sorted(events_dir.glob("exec_*"))
            if exec_dirs:
                latest_dir = exec_dirs[-1]
                event_files = list(latest_dir.glob("*rollback*.json"))
                if event_files:
                    print(f"✅ Rollback events created: {len(event_files)}")
                    return True
                else:
                    print(f"❌ No rollback events found")
                    return False

        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Clean up
        if rollback_plan_file.exists():
            rollback_plan_file.unlink()
        if test_file.exists():
            test_file.unlink()
        test_copy = workspace / "test_rollback_copy.py"
        if test_copy.exists():
            test_copy.unlink()


def test_plan_validation():
    """Test plan validation."""
    print("\n" + "=" * 60)
    print("TEST 4: PLAN VALIDATION")
    print("=" * 60)

    workspace = Path(__file__).parent

    # Create invalid plan (missing required fields)
    invalid_plan = {
        "goal": "Invalid plan test",
        "steps": [],  # Missing budget, plan_id, checksum
    }

    # Write invalid plan
    invalid_plan_file = workspace / "test_invalid_plan.json"
    with open(invalid_plan_file, "w") as f:
        json.dump(invalid_plan, f, indent=2)

    # Create executor
    executor = Executor(workspace)

    try:
        result = executor.execute_plan(invalid_plan_file)
        print(f"❌ Plan validation failed - should have rejected invalid plan")
        return False
    except PlanValidationError as e:
        print(f"✅ Plan validation working: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Clean up
        if invalid_plan_file.exists():
            invalid_plan_file.unlink()


def cleanup_test_artifacts():
    """Clean up test artifacts."""
    print("\n" + "=" * 60)
    print("CLEANUP TEST ARTIFACTS")
    print("=" * 60)

    workspace = Path(__file__).parent

    # Remove test copy
    test_copy = workspace / "oe-agent" / "test_copy.py"
    if test_copy.exists():
        test_copy.unlink()
        print(f"Removed: {test_copy}")

    # Remove backup directories
    backup_dir = workspace / ".oe-backups"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
        print(f"Removed: {backup_dir}")

    # Remove events directories (keep a few for inspection)
    events_dir = workspace / "events"
    if events_dir.exists():
        # Keep the 2 most recent executions for inspection
        exec_dirs = sorted(events_dir.glob("exec_*"))
        if len(exec_dirs) > 2:
            for dir_to_remove in exec_dirs[:-2]:
                shutil.rmtree(dir_to_remove)
                print(f"Removed: {dir_to_remove}")
        print(f"Kept {min(2, len(exec_dirs))} event directories for inspection")

    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("OE-AGENT EXECUTOR TEST SUITE")
    print("Governed Autonomous Engineer - No AI Involved")
    print("=" * 70)

    tests = [
        test_executor_basic,
        test_budget_enforcement,
        test_rollback,
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
    print("Claim: Executor provides governed execution with no AI involvement")
    print("Falsification: Run this test suite independently")
    print(f"Expected: {len(tests)} tests pass with budget enforcement and rollback")
    print(f"Actual: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED!")
        print("Executor is ready for Phase 2 integration.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Review test output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

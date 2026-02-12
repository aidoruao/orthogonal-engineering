#!/usr/bin/env python3
"""
OE-AGENT DEBUG EXECUTOR TEST
Simple test to debug atomic executor issues

Version: 1.0.0
Date: 2026-01-24
"""

import json
import sys
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def debug_executor():
    """Debug the atomic executor."""
    print("DEBUGGING ATOMIC EXECUTOR")
    print("=" * 60)

    from executor.simple_executor import AtomicSimpleExecutor

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        print(f"Workspace: {workspace}")

        # Create a very simple plan
        simple_plan = {
            "plan_id": "debug_plan_001",
            "goal": "Debug executor",
            "steps": [
                {
                    "id": 1,
                    "action": "command",
                    "command": "echo 'Hello from debug test'",
                }
            ],
            "budget": {"max_commands": 5, "max_runtime_seconds": 30},
        }

        plan_file = workspace / "debug_plan.json"
        with open(plan_file, "w") as f:
            json.dump(simple_plan, f, indent=2)

        print(f"\nPlan file created: {plan_file}")
        print(f"Plan content:")
        print(json.dumps(simple_plan, indent=2))

        # Try to import components manually
        print("\n" + "=" * 60)
        print("CHECKING IMPORTS:")

        try:
            from events.event_sink import AtomicEventSink

            print("✓ AtomicEventSink imported")
        except ImportError as e:
            print(f"✗ AtomicEventSink import failed: {e}")

        try:
            from policy.policy_gate import PolicyGate

            print("✓ PolicyGate imported")
        except ImportError as e:
            print(f"✗ PolicyGate import failed: {e}")

        # Create executor
        print("\n" + "=" * 60)
        print("CREATING EXECUTOR:")
        try:
            executor = AtomicSimpleExecutor(workspace)
            print("✓ Executor created")

            # Check if Phase 3 components were initialized
            print(f"  event_sink: {executor.event_sink}")
            print(f"  policy_gate: {executor.policy_gate}")

        except Exception as e:
            print(f"✗ Executor creation failed: {e}")
            import traceback

            traceback.print_exc()
            return False

        # Try to execute plan
        print("\n" + "=" * 60)
        print("EXECUTING PLAN:")
        try:
            result = executor.execute_plan_atomic(plan_file)
            print(f"Execution result: {result}")

            if "error" in result:
                print(f"Error: {result['error']}")

            # Print all keys in result
            print(f"\nResult keys: {list(result.keys())}")

            # Check for specific keys
            for key in [
                "success",
                "steps_completed",
                "total_steps",
                "execution_id",
                "plan_id",
            ]:
                if key in result:
                    print(f"  {key}: {result[key]}")
                else:
                    print(f"  {key}: MISSING")

            return result.get("success", False)

        except Exception as e:
            print(f"✗ Execution failed: {e}")
            import traceback

            traceback.print_exc()
            return False


def debug_transaction_issue():
    """Debug the transaction issue specifically."""
    print("\n" + "=" * 60)
    print("DEBUGGING TRANSACTION ISSUE")
    print("=" * 60)

    from events.event_sink import AtomicEventSink

    with tempfile.TemporaryDirectory() as tmpdir:
        events_dir = Path(tmpdir) / "events"

        # Test 1: Simple transaction
        print("\nTest 1: Simple transaction")
        sink = AtomicEventSink(events_dir)

        try:
            xact_id = "test_xact_001"
            sink.begin_xact(xact_id)
            print(f"✓ Transaction {xact_id} started")

            intent_hash = sink.write_intent(
                xact_id=xact_id,
                step_id=1,
                plan_id="test_plan",
                action="test",
                parameters={"test": "data"},
            )
            print(f"✓ Intent written: {intent_hash[:16]}...")

            commit_hash = sink.write_commit(
                xact_id=xact_id,
                step_id=1,
                plan_id="test_plan",
                effect={"success": True},
            )
            print(f"✓ Commit written: {commit_hash[:16]}...")

            # Verify transaction is cleared
            print(f"  Transaction state after commit:")
            print(f"    _current_xact_id: {sink._current_xact_id}")
            print(f"    _xact_intent_hash: {sink._xact_intent_hash}")

        except Exception as e:
            print(f"✗ Transaction test failed: {e}")
            import traceback

            traceback.print_exc()
            return False

        # Test 2: Multiple transactions
        print("\nTest 2: Multiple sequential transactions")
        try:
            for i in range(2):
                xact_id = f"multi_xact_{i:03d}"
                sink.begin_xact(xact_id)

                intent_hash = sink.write_intent(
                    xact_id=xact_id,
                    step_id=i,
                    plan_id="multi_plan",
                    action=f"action_{i}",
                    parameters={"iteration": i},
                )

                commit_hash = sink.write_commit(
                    xact_id=xact_id,
                    step_id=i,
                    plan_id="multi_plan",
                    effect={"iteration": i, "success": True},
                )

                print(f"✓ Transaction {xact_id} completed")

            print("✓ Multiple transactions completed successfully")
            return True

        except Exception as e:
            print(f"✗ Multiple transactions failed: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Run debug tests."""
    print("OE-AGENT DEBUG TESTS")
    print("=" * 70)

    tests = [
        ("Executor Debug", debug_executor),
        ("Transaction Debug", debug_transaction_issue),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{'=' * 70}")
        print(f"TEST: {name}")
        print(f"{'=' * 70}")

        try:
            success = test_func()
            results.append((name, success))

            if success:
                print(f"\n✅ {name} PASSED")
            else:
                print(f"\n❌ {name} FAILED")

        except Exception as e:
            print(f"\n❌ {name} ERROR: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Summary
    print(f"\n{'=' * 70}")
    print("DEBUG SUMMARY")
    print(f"{'=' * 70}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:30} {status}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL DEBUG TESTS PASSED")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

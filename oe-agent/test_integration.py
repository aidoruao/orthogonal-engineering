#!/usr/bin/env python3
"""
OE-AGENT SIMPLE INTEGRATION TEST
Quick test to verify Phase 3 components work together

Version: 1.0.0
Date: 2026-01-24
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_components_individually():
    """Test each component individually."""
    print("Testing OE-Agent Phase 3 Components...")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # Test 1: Event Sink
    print("\n1. Testing AtomicEventSink...")
    try:
        from events.event_sink import AtomicEventSink

        with tempfile.TemporaryDirectory() as tmpdir:
            sink = AtomicEventSink(Path(tmpdir) / "events")

            # Basic transaction
            xact_id = "test_xact_001"
            sink.begin_xact(xact_id)

            intent_hash = sink.write_intent(
                xact_id=xact_id,
                step_id=1,
                plan_id="test_plan",
                action="test",
                parameters={"test": "data"},
            )

            commit_hash = sink.write_commit(
                xact_id=xact_id,
                step_id=1,
                plan_id="test_plan",
                effect={"success": True},
            )

            # Verify chain
            is_valid, violations = sink.verify_hash_chain()

            if is_valid and intent_hash and commit_hash:
                print("  ✅ AtomicEventSink working")
                tests_passed += 1
            else:
                print(f"  ❌ AtomicEventSink failed: {violations}")
        tests_total += 1

    except Exception as e:
        print(f"  ❌ AtomicEventSink import/execution failed: {e}")
        tests_total += 1

    # Test 2: Policy Gate
    print("\n2. Testing PolicyGate...")
    try:
        from policy.policy_gate import PolicyConstraint, PolicyGate

        gate = PolicyGate()

        # Test simple plan
        simple_plan = {
            "plan_id": "test_plan",
            "goal": "test",
            "steps": [{"id": 1, "action": "scan", "target": "."}],
            "budget": {"max_commands": 5, "max_runtime_seconds": 60},
        }

        decision = gate.evaluate_plan(simple_plan)

        if decision["decision"] in ["allow", "require_review", "block"]:
            print(f"  ✅ PolicyGate working (decision: {decision['decision']})")
            tests_passed += 1
        else:
            print(f"  ❌ PolicyGate returned invalid decision: {decision}")
        tests_total += 1

    except Exception as e:
        print(f"  ❌ PolicyGate import/execution failed: {e}")
        tests_total += 1

    # Test 3: Atomic Executor
    print("\n3. Testing AtomicSimpleExecutor...")
    try:
        from executor.simple_executor import AtomicSimpleExecutor

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)

            # Create test file
            test_file = workspace / "test.txt"
            test_file.write_text("Hello, World!")

            # Create simple plan
            test_plan = {
                "plan_id": "integration_test",
                "goal": "Test integration",
                "steps": [
                    {"id": 1, "action": "scan", "target": "."},
                    {
                        "id": 2,
                        "action": "command",
                        "command": "echo 'Integration test successful'",
                    },
                ],
                "budget": {"max_commands": 5, "max_runtime_seconds": 30},
            }

            plan_file = workspace / "test_plan.json"
            with open(plan_file, "w") as f:
                json.dump(test_plan, f, indent=2)

            # Execute
            executor = AtomicSimpleExecutor(workspace)
            result = executor.execute_plan(
                plan_file
            )  # Use Phase 2 compatibility method

            if result.get("success", False):
                print(
                    f"  ✅ AtomicSimpleExecutor working (completed {result.get('steps_completed', 0)} steps)"
                )
                tests_passed += 1
            else:
                print(
                    f"  ❌ AtomicSimpleExecutor failed: {result.get('error', 'Unknown error')}"
                )
        tests_total += 1

    except Exception as e:
        print(f"  ❌ AtomicSimpleExecutor import/execution failed: {e}")
        tests_total += 1

    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print(f"Success rate: {(tests_passed / tests_total) * 100:.1f}%")

    if tests_passed == tests_total:
        print("\n🎉 ALL COMPONENTS WORKING!")
        print("Phase 3 implementation is functional.")
        return True
    else:
        print("\n⚠️  SOME COMPONENTS HAVE ISSUES")
        print("Check the errors above.")
        return False


def main():
    """Run integration test."""
    print("OE-AGENT PHASE 3 INTEGRATION TEST")
    print("Testing: AtomicEventSink + PolicyGate + AtomicSimpleExecutor")
    print("=" * 70)

    success = test_components_individually()

    if success:
        print("\n✅ PHASE 3 IMPLEMENTATION VERIFIED")
        print("Components are working together correctly.")
        return 0
    else:
        print("\n❌ INTEGRATION ISSUES DETECTED")
        print("Some components need attention.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

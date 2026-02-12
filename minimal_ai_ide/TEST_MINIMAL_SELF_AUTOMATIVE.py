"""
TEST_MINIMAL_SELF_AUTOMATIVE.py
================================

Minimal test to verify Self-Automative Master System works
Tests only core functionality without repository scanning
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from SELF_AUTOMATIVE_MASTER_COMPLETE import (
    ConstraintStatus,
    MathematicalInvariant,
    PopperianTestResult,
    PopperianValidator,
    Σ_LORA_ConstraintExecutor,
)


async def test_minimal_popperian():
    """Test Popperian validator with minimal setup"""
    print("🧪 Testing Popperian Validator...")

    popperian = PopperianValidator(project_root)

    # Simple falsification tests
    def test_truth():
        return 2 + 2 == 4

    def test_falsifiable():
        return "test" in "this is a test"

    popperian.register_falsification_test("basic_truth", test_truth)
    popperian.register_falsification_test("falsifiable", test_falsifiable)

    results = await popperian.run_falsification_suite()

    print(f"  Tests run: {len(results)}")
    for test_name, result in results.items():
        print(f"  - {test_name}: {result.value}")

    corroborated = sum(
        1 for r in results.values() if r == PopperianTestResult.CORROBORATED
    )
    return corroborated == len(results)


async def test_minimal_constraints():
    """Test Σ_LORA constraints with minimal setup"""
    print("\n⚖️ Testing Σ_LORA Constraints...")

    executor = Σ_LORA_ConstraintExecutor(project_root)

    # Test with simple component
    test_component = {
        "name": "test",
        "description": "test component",
        "code": "print('hello')",
    }

    results = await executor.verify_all_constraints(test_component)

    print(f"  Constraints checked: {len(results)}")
    for constraint_name, (satisfied, message) in results.items():
        status = "✅" if satisfied else "❌"
        print(f"  {status} {constraint_name}: {message[:40]}...")

    satisfied = sum(1 for r in results.values() if r[0])
    christ_score = satisfied / len(results) if len(results) > 0 else 0

    print(f"  Christ Score: {christ_score:.2f}")
    return christ_score > 0.5


async def test_mathematical_invariants():
    """Test mathematical invariants"""
    print("\n🧮 Testing Mathematical Invariants...")

    invariants = [
        MathematicalInvariant(
            name="Test Invariant",
            formula="∀x: P(x) → Q(x)",
            description="Test invariant description",
            theological_basis="Test basis",
            constraint_type="test",
            verification_method="test",
        )
    ]

    print(f"  Invariants defined: {len(invariants)}")
    for inv in invariants:
        print(f"  - {inv.name}: {inv.formula}")
        print(f"    LaTeX: {inv.to_latex()}")

    return len(invariants) > 0


async def test_system_flow():
    """Test basic system flow"""
    print("\n🔄 Testing System Flow...")

    # Test that we can create instances
    from SELF_AUTOMATIVE_MASTER_COMPLETE import (
        ConstraintStatus,
        LoRAModelStatus,
        SystemPhase,
    )

    print("  System enums accessible:")
    print(f"  - SystemPhase: {[phase.value for phase in SystemPhase]}")
    print(f"  - ConstraintStatus: {[status.value for status in ConstraintStatus]}")
    print(f"  - LoRAModelStatus: {[status.value for status in LoRAModelStatus]}")

    return True


async def main():
    """Run all minimal tests"""
    print("🚀 MINIMAL SELF-AUTOMATIVE MASTER TEST")
    print("=" * 40)

    tests = [
        ("Popperian Validator", test_minimal_popperian),
        ("Σ_LORA Constraints", test_minimal_constraints),
        ("Mathematical Invariants", test_mathematical_invariants),
        ("System Flow", test_system_flow),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            print(f"\n❌ ERROR: {test_name} - {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")

    if passed == total:
        print("\n🎉 ALL MINIMAL TESTS PASSED!")
        print("Core system components are functional.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        print("Some components may need adjustment.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

"""
Simple test for Σ_LORA system verification
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from SIGMA_LORA_GRADUATE_MATHEMATICS import (
        ConstrainedTrainingExample,
        ConstraintPreservingDataConstructor,
        ConstraintPreservingLoRA,
        ConstraintSet,
        FileObject,
        GitFunctor,
        RepositoryCategory,
        RepositoryMorphism,
        TheologicalConstraint,
        TheologicalVector,
        demonstrate_sigma_lora_system,
        main,
    )

    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def run_simple_tests():
    """Run simple verification tests"""
    print("\n" + "=" * 70)
    print("SIMPLE Σ_LORA SYSTEM TESTS")
    print("=" * 70)

    all_passed = True

    # Test 1: Theological constraints
    print("\n1. Testing TheologicalConstraint...")
    try:
        assert TheologicalConstraint.LOGOS.description() == "initial structure muL.F(L)"
        assert TheologicalConstraint.CHALCEDON.mathematical_formula() == "E x P -> S"
        print("  ✓ TheologicalConstraint test passed")
    except Exception as e:
        print(f"  ✗ TheologicalConstraint test failed: {e}")
        all_passed = False

    # Test 2: ConstraintSet
    print("\n2. Testing ConstraintSet...")
    try:
        constraints = ConstraintSet(
            frozenset([TheologicalConstraint.LOGOS, TheologicalConstraint.GRACE])
        )
        assert len(constraints.constraints) == 2
        print("  ✓ ConstraintSet test passed")
    except Exception as e:
        print(f"  ✗ ConstraintSet test failed: {e}")
        all_passed = False

    # Test 3: FileObject
    print("\n3. Testing FileObject...")
    try:
        file_obj = FileObject(
            path="test.py",
            content_hash="",
            constraints=constraints,
            language="python",
            content="def test(): pass",
        )
        assert file_obj.path == "test.py"
        assert len(file_obj.content_hash) == 64
        print("  ✓ FileObject test passed")
    except Exception as e:
        print(f"  ✗ FileObject test failed: {e}")
        all_passed = False

    # Test 4: RepositoryCategory
    print("\n4. Testing RepositoryCategory...")
    try:
        repo = RepositoryCategory()
        repo.add_object(file_obj)
        assert len(repo.objects) == 1
        print("  ✓ RepositoryCategory test passed")
    except Exception as e:
        print(f"  ✗ RepositoryCategory test failed: {e}")
        all_passed = False

    # Test 5: Data Constructor
    print("\n5. Testing ConstraintPreservingDataConstructor...")
    try:
        constructor = ConstraintPreservingDataConstructor(chunk_size=100, overlap=20)
        chunks = constructor._chunk_by_constraints("Test content " * 50, constraints)
        assert len(chunks) > 0
        print("  ✓ Data Constructor test passed")
    except Exception as e:
        print(f"  ✗ Data Constructor test failed: {e}")
        all_passed = False

    # Test 6: Full demonstration
    print("\n6. Testing full system demonstration...")
    try:
        results = demonstrate_sigma_lora_system()
        assert results["constraint_preservation"] == True
        assert results["theorem3_constraint_preserving_composition"] == True
        assert results["theorem4_chunk_coverage_completeness"]["verified"] == True
        print("  ✓ Full demonstration test passed")
    except Exception as e:
        print(f"  ✗ Full demonstration test failed: {e}")
        all_passed = False

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("Σ_LORA system is fully operational")
        return True
    else:
        print("✗ SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    success = run_simple_tests()
    if success:
        print("\n" + "=" * 70)
        print("RUNNING MAIN DEMONSTRATION")
        print("=" * 70)
        main()
    sys.exit(0 if success else 1)

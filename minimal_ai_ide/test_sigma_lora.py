"""
Test file for Σ_LORA_GRADUATE_MATHEMATICS system verification
Tests constraint preservation, mathematical theorems, and system integrity
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
)


def test_theological_constraints():
    """Test theological constraint system"""
    print("Testing TheologicalConstraint system...")

    # Test constraint descriptions
    assert TheologicalConstraint.LOGOS.description() == "initial structure μL.F(L)"
    assert TheologicalConstraint.CHALCEDON.mathematical_formula() == "E × P → S"

    # Test ConstraintSet
    constraints = ConstraintSet(
        frozenset([TheologicalConstraint.LOGOS, TheologicalConstraint.GRACE])
    )

    assert len(constraints.constraints) == 2
    assert TheologicalConstraint.LOGOS in constraints.constraints
    assert TheologicalConstraint.GRACE in constraints.constraints

    # Test union and intersection
    set1 = ConstraintSet(frozenset([TheologicalConstraint.LOGOS]))
    set2 = ConstraintSet(frozenset([TheologicalConstraint.GRACE]))
    union = set1.union(set2)
    assert len(union.constraints) == 2

    # Test contains
    larger = ConstraintSet(
        frozenset(
            [
                TheologicalConstraint.LOGOS,
                TheologicalConstraint.GRACE,
                TheologicalConstraint.CHALCEDON,
            ]
        )
    )
    assert larger.contains(set1)
    assert not set1.contains(larger)

    print("✓ Theological constraint system tests passed")
    return True


def test_file_object_and_repository():
    """Test file objects and repository category"""
    print("Testing FileObject and RepositoryCategory...")

    # Create file object
    content = "def test(): pass"
    file_obj = FileObject(
        path="test.py",
        content_hash="",
        constraints=ConstraintSet(frozenset([TheologicalConstraint.LOGOS])),
        language="python",
        content=content,
    )

    assert file_obj.path == "test.py"
    assert file_obj.language == "python"
    assert len(file_obj.content_hash) == 64  # SHA256 hex length

    # Test constraint preservation
    file_obj2 = FileObject(
        path="test2.py",
        content_hash="hash2",
        constraints=ConstraintSet(
            frozenset([TheologicalConstraint.LOGOS, TheologicalConstraint.GRACE])
        ),
        language="python",
    )

    assert file_obj2.preserves_constraints(file_obj)  # {LOGOS, GRACE} ⊇ {LOGOS}
    assert not file_obj.preserves_constraints(file_obj2)  # {LOGOS} ⊉ {LOGOS, GRACE}

    # Test repository category
    repo = RepositoryCategory()
    repo.add_object(file_obj)
    repo.add_object(file_obj2)

    assert len(repo.objects) == 2
    assert "test.py" in repo.objects
    assert "test2.py" in repo.objects

    # Test morphism
    morphism = RepositoryMorphism(file_obj, file_obj2, "edit")
    assert morphism.preserves_constraints()

    # Add morphism to repository
    assert repo.add_morphism(morphism)
    assert len(repo.morphisms) == 1

    print("✓ FileObject and RepositoryCategory tests passed")
    return True


def test_theological_vector():
    """Test theological vector similarity metric"""
    print("Testing TheologicalVector similarity...")

    # Create vectors with constraint inclusion
    vec1 = TheologicalVector(
        numerical=[1.0, 0.0],
        constraints=ConstraintSet(frozenset([TheologicalConstraint.LOGOS])),
    )

    vec2 = TheologicalVector(
        numerical=[0.8, 0.6],  # Similar direction
        constraints=ConstraintSet(
            frozenset([TheologicalConstraint.LOGOS, TheologicalConstraint.GRACE])
        ),
    )

    # vec2.constraints contains vec1.constraints, so similarity should be cosine similarity
    similarity = vec1.similarity(vec2)
    assert 0 <= similarity <= 1

    # Test with non-containing constraints
    vec3 = TheologicalVector(
        numerical=[1.0, 0.0],
        constraints=ConstraintSet(frozenset([TheologicalConstraint.CHALCEDON])),
    )

    # vec2.constraints does NOT contain vec3.constraints, so similarity should be 0
    similarity2 = vec3.similarity(vec2)
    assert similarity2 == 0.0

    print("✓ TheologicalVector similarity tests passed")
    return True


def test_constraint_preserving_lora():
    """Test LoRA adaptation with constraint propagation"""
    print("Testing ConstraintPreservingLoRA...")

    lora = ConstraintPreservingLoRA(rank=2, dimension=3)
    constraints = ConstraintSet(frozenset([TheologicalConstraint.LOGOS]))

    base_weights = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]

    adapted_weights, propagated_constraints = lora.adapt(base_weights, constraints)

    # Check dimensions
    assert len(adapted_weights) == 3
    assert len(adapted_weights[0]) == 3

    # Check constraint preservation
    assert lora.verify_constraint_preservation(constraints, propagated_constraints)
    assert propagated_constraints.contains(constraints)

    print("✓ ConstraintPreservingLoRA tests passed")
    return True


def test_data_constructor():
    """Test constraint-preserving data constructor"""
    print("Testing ConstraintPreservingDataConstructor...")

    constructor = ConstraintPreservingDataConstructor(chunk_size=50, overlap=10)

    # Create test content
    content = """
    # This is a test file with multiple lines
    # It should be chunked while preserving constraints

    class TestClass:
        def method1(self):
            return "Method 1"

        def method2(self):
            return "Method 2"

    def helper_function():
        return "Helper"

    # More comments and code
    if __name__ == "__main__":
        print("Running test")
    """

    constraints = ConstraintSet(
        frozenset(
            [
                TheologicalConstraint.LOGOS,
                TheologicalConstraint.CHALCEDON,
                TheologicalConstraint.GRACE,
            ]
        )
    )

    # Test chunking
    chunks = constructor._chunk_by_constraints(content, constraints)

    assert len(chunks) > 0

    # Verify Theorem 4: union of chunk constraints = file constraints
    union_constraints = set()
    for _, chunk_constraints in chunks:
        union_constraints.update(chunk_constraints.constraints)

    assert union_constraints == set(constraints.constraints)

    # Test example creation
    file_obj = FileObject(
        path="test.py",
        content_hash="test_hash",
        constraints=constraints,
        language="python",
        content=content,
    )

    example = constructor._create_chunk_example(
        file_obj,
        "Test chunk content",
        ConstraintSet(frozenset([TheologicalConstraint.LOGOS])),
        0,
    )

    assert isinstance(example, ConstrainedTrainingExample)
    assert example.preserves_constraints(constraints)

    # Test training format conversion
    training_format = example.to_training_format()
    assert "instruction" in training_format
    assert "input" in training_format
    assert "output" in training_format
    assert "constraints" in training_format

    print("✓ ConstraintPreservingDataConstructor tests passed")
    return True


def test_git_functor():
    """Test Git functoriality"""
    print("Testing GitFunctor...")

    file_obj = FileObject(
        path="test.py",
        content_hash="a" * 64,  # Mock hash
        constraints=ConstraintSet(frozenset([TheologicalConstraint.LOGOS])),
        language="python",
    )

    modification = "Added test function"
    commit = GitFunctor.create_commit(file_obj, modification)

    assert commit["file_path"] == "test.py"
    assert commit["original_hash"] == file_obj.content_hash
    assert "commit_hash" in commit
    assert len(commit["commit_hash"]) == 64

    # Test commit hash combination
    mod_hash = hashlib.sha256(modification.encode()).hexdigest()
    computed_hash = GitFunctor.commit_hash(file_obj.content_hash, mod_hash)
    assert commit["commit_hash"] == computed_hash

    print("✓ GitFunctor tests passed")
    return True


def test_theorem_verification():
    """Verify mathematical theorems"""
    print("Testing mathematical theorems...")

    # Theorem 3: Constraint-Preserving Composition
    file1 = FileObject(
        path="f1.py",
        content_hash="hash1",
        constraints=ConstraintSet(frozenset([TheologicalConstraint.LOGOS])),
        language="python",
    )

    file2 = FileObject(
        path="f2.py",
        content_hash="hash2",
        constraints=ConstraintSet(
            frozenset([TheologicalConstraint.LOGOS, TheologicalConstraint.GRACE])
        ),
        language="python",
    )

    file3 = FileObject(
        path="f3.py",
        content_hash="hash3",
        constraints=ConstraintSet(
            frozenset(
                [
                    TheologicalConstraint.LOGOS,
                    TheologicalConstraint.GRACE,
                    TheologicalConstraint.CHALCEDON,
                ]
            )
        ),
        language="python",
    )

    # f: file1 → file2 preserves constraints
    morphism_f = RepositoryMorphism(file1, file2, "edit")
    assert morphism_f.preserves_constraints()

    # g: file2 → file3 preserves constraints
    morphism_g = RepositoryMorphism(file2, file3, "refactor")
    assert morphism_g.preserves_constraints()

    # Repository for composition
    repo = RepositoryCategory()
    repo.add_object(file1)
    repo.add_object(file2)
    repo.add_object(file3)

    # g∘f should preserve constraints
    composed = repo.compose(morphism_f, morphism_g)
    assert composed is not None
    assert composed.preserves_constraints()

    print("✓ Theorem 3 (Constraint-Preserving Composition) verified")

    # Theorem 4: Chunk Coverage Completeness
    constructor = ConstraintPreservingDataConstructor()
    content = "x " * 100  # 100 words

    constraints = ConstraintSet(
        frozenset(
            [
                TheologicalConstraint.LOGOS,
                TheologicalConstraint.CHALCEDON,
                TheologicalConstraint.GRACE,
            ]
        )
    )

    chunks = constructor._chunk_by_constraints(content, constraints)

    # Union of chunk constraints should equal file constraints
    union_constraints = set()
    for _, chunk_constraints in chunks:
        union_constraints.update(chunk_constraints.constraints)

    assert union_constraints == set(constraints.constraints)

    print("✓ Theorem 4 (Chunk Coverage Completeness) verified")
    return True


def test_full_demonstration():
    """Test the complete demonstration"""
    print("Testing full Σ_LORA system demonstration...")

    results = demonstrate_sigma_lora_system()

    # Check key results
    assert results["constraint_preservation"] == True
    assert results["lora_adaptation"]["constraint_preserved"] == True
    assert results["theorem3_constraint_preserving_composition"] == True
    assert results["theorem4_chunk_coverage_completeness"]["verified"] == True

    print("✓ Full system demonstration passed")
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("Σ_LORA SYSTEM TEST SUITE")
    print("=" * 70)

    tests = [
        ("Theological Constraints", test_theological_constraints),
        ("File Object & Repository", test_file_object_and_repository),
        ("Theological Vector", test_theological_vector),
        ("Constraint-Preserving LoRA", test_constraint_preserving_lora),
        ("Data Constructor", test_data_constructor),
        ("Git Functor", test_git_functor),
        ("Mathematical Theorems", test_theorem_verification),
        ("Full Demonstration", test_full_demonstration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n✓ {test_name}: PASSED")
                passed += 1
            else:
                print(f"\n✗ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"\n✗ {test_name}: ERROR - {e}")
            failed += 1

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED")
        print("Σ_LORA system is fully operational with constraint preservation")
        return True
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    # Import hashlib for GitFunctor test
    import hashlib

    success = run_all_tests()
    sys.exit(0 if success else 1)

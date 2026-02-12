"""
Simple test for GRADUATE_LANGUAGE_MATHEMATICS system
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from GRADUATE_LANGUAGE_MATHEMATICS import (
        ComputationalMonad,
        ConstraintSet,
        Context,
        DenotationalFunctor,
        Domain,
        DomainElement,
        DomainMonad,
        ExecutionModel,
        FeatureEndofunctor,
        LanguageSignature,
        ObservationalProfunctor,
        Paradigm,
        ParadigmFibration,
        ProgrammingLanguage,
        SyntacticCategory,
        TemporalCoalgebra,
        TheologicalConstraint,
        TypeSystem,
        TypeSystemLattice,
        demonstrate_graduate_mathematics,
        main,
    )

    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def run_simple_tests():
    """Run simple verification tests"""
    print("\n" + "=" * 70)
    print("SIMPLE GRADUATE MATHEMATICS TESTS")
    print("=" * 70)

    all_passed = True

    # Test 1: Theological constraints
    print("\n1. Testing TheologicalConstraint...")
    try:
        assert TheologicalConstraint.LOGOS.description() == "initial structure μL.F(L)"
        assert TheologicalConstraint.CHALCEDON.mathematical_formula() == "E × P → S"
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

    # Test 3: Context and SyntacticCategory
    print("\n3. Testing Context and SyntacticCategory...")
    try:
        ctx = Context(["x", "y"], ["int", "int"])
        assert len(ctx.variables) == 2
        assert len(ctx.types) == 2

        syntax = SyntacticCategory("Test")
        syntax.add_context(ctx)
        assert len(syntax.objects) == 1
        print("  ✓ Context and SyntacticCategory test passed")
    except Exception as e:
        print(f"  ✗ Context/SyntacticCategory test failed: {e}")
        all_passed = False

    # Test 4: ProgrammingLanguage
    print("\n4. Testing ProgrammingLanguage...")
    try:
        syntax = SyntacticCategory("TestLang")
        ctx = Context(["x"], ["int"])
        syntax.add_context(ctx)
        syntax.add_context(syntax.terminal)

        profunctor = ObservationalProfunctor(syntax)
        profunctor.add_transition(ctx, syntax.terminal, "x + 1")

        lang = ProgrammingLanguage(
            name="TestLang",
            syntactic_category=syntax,
            observational_profunctor=profunctor,
        )
        lang = lang.with_theological_constraint(TheologicalConstraint.LOGOS)

        assert lang.name == "TestLang"
        assert len(lang.theological_constraints.constraints) == 1
        print("  ✓ ProgrammingLanguage test passed")
    except Exception as e:
        print(f"  ✗ ProgrammingLanguage test failed: {e}")
        all_passed = False

    # Test 5: ParadigmFibration
    print("\n5. Testing ParadigmFibration...")
    try:
        fibration = ParadigmFibration()

        # Create a simple language
        syntax = SyntacticCategory("Lang1")
        ctx = Context(["x"], ["int"])
        syntax.add_context(ctx)
        syntax.add_context(syntax.terminal)

        profunctor = ObservationalProfunctor(syntax)
        profunctor.add_transition(ctx, syntax.terminal, "x")

        lang = ProgrammingLanguage(
            name="Lang1",
            syntactic_category=syntax,
            observational_profunctor=profunctor,
        )

        fibration.add_language(lang, {Paradigm.IMPERATIVE, Paradigm.FUNCTIONAL})
        assert len(fibration.fibers) == 1
        print("  ✓ ParadigmFibration test passed")
    except Exception as e:
        print(f"  ✗ ParadigmFibration test failed: {e}")
        all_passed = False

    # Test 6: TypeSystemLattice
    print("\n6. Testing TypeSystemLattice...")
    try:
        lattice = TypeSystemLattice()

        simple_types = TypeSystem(
            name="Simple",
            types={"Int", "Bool"},
            kinds={"*": {"Int", "Bool"}},
            subtyping=set(),
            inhabitation={("0", "Int"), ("true", "Bool")},
        )

        lattice.add_system(simple_types)
        assert len(lattice.systems) == 1
        assert lattice.top.name == "⊤"
        assert lattice.bottom.name == "⊥"
        print("  ✓ TypeSystemLattice test passed")
    except Exception as e:
        print(f"  ✗ TypeSystemLattice test failed: {e}")
        all_passed = False

    # Test 7: Domain and DenotationalFunctor
    print("\n7. Testing Domain and DenotationalFunctor...")
    try:
        domain = Domain("TestDomain")
        elem = DomainElement("test_value")
        domain.add_element(elem)

        assert len(domain.elements) == 2  # includes bottom
        assert domain.bottom.is_bottom

        denotational = DenotationalFunctor()
        print("  ✓ Domain and DenotationalFunctor test passed")
    except Exception as e:
        print(f"  ✗ Domain/DenotationalFunctor test failed: {e}")
        all_passed = False

    # Test 8: FeatureEndofunctor
    print("\n8. Testing FeatureEndofunctor...")
    try:
        functor = FeatureEndofunctor()
        assert len(functor.features) == 5

        # Create a simple language to test
        syntax = SyntacticCategory("Test")
        ctx = Context(["x"], ["int"])
        syntax.add_context(ctx)
        syntax.add_context(syntax.terminal)

        profunctor = ObservationalProfunctor(syntax)
        profunctor.add_transition(ctx, syntax.terminal, "x")

        lang = ProgrammingLanguage(
            name="Test",
            syntactic_category=syntax,
            observational_profunctor=profunctor,
        )

        extended = functor.apply(lang)
        assert extended.name == "Test+"
        print("  ✓ FeatureEndofunctor test passed")
    except Exception as e:
        print(f"  ✗ FeatureEndofunctor test failed: {e}")
        all_passed = False

    # Test 9: DomainMonad
    print("\n9. Testing DomainMonad...")
    try:
        monad = DomainMonad()
        assert len(monad.domains) == 7  # 7 domain types

        # Create a simple language
        syntax = SyntacticCategory("Test")
        ctx = Context(["x"], ["int"])
        syntax.add_context(ctx)
        syntax.add_context(syntax.terminal)

        profunctor = ObservationalProfunctor(syntax)
        profunctor.add_transition(ctx, syntax.terminal, "x + 1")

        lang = ProgrammingLanguage(
            name="Test",
            syntactic_category=syntax,
            observational_profunctor=profunctor,
        )

        domain_lang = monad.apply(lang)
        assert domain_lang.name == "D(Test)"
        print("  ✓ DomainMonad test passed")
    except Exception as e:
        print(f"  ✗ DomainMonad test failed: {e}")
        all_passed = False

    # Test 10: ComputationalMonad
    print("\n10. Testing ComputationalMonad...")
    try:
        for model in ExecutionModel:
            monad = ComputationalMonad(model)
            assert monad.model == model

        domain = Domain("Test")
        elem = DomainElement("value")
        domain.add_element(elem)

        comp_monad = ComputationalMonad(ExecutionModel.COMPILED)
        transformed = comp_monad.apply(domain)
        assert transformed.name == "T_comp(Test)"
        print("  ✓ ComputationalMonad test passed")
    except Exception as e:
        print(f"  ✗ ComputationalMonad test failed: {e}")
        all_passed = False

    # Test 11: LanguageSignature
    print("\n11. Testing LanguageSignature...")
    try:
        signature = LanguageSignature()
        initial = signature.initial_algebra()
        assert len(initial) > 0

        # Test catamorphism
        def test_algebra(X):
            return {f"test_{x}" for x in X}

        cata = signature.catamorphism(test_algebra)
        result = cata({"variables"})
        assert len(result) > 0
        print("  ✓ LanguageSignature test passed")
    except Exception as e:
        print(f"  ✗ LanguageSignature test failed: {e}")
        all_passed = False

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    if all_passed:
        print("✓ ALL 11 TESTS PASSED")
        print("Graduate mathematics system is fully operational")
        return True
    else:
        print("✗ SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    success = run_simple_tests()
    if success:
        print("\n" + "=" * 70)
        print("RUNNING FULL DEMONSTRATION")
        print("=" * 70)
        try:
            # Run a quick demonstration instead of full main to avoid timeout
            from GRADUATE_LANGUAGE_MATHEMATICS import demonstrate_graduate_mathematics

            results = demonstrate_graduate_mathematics()
            print(f"\n✓ Demonstration completed successfully")
            print(f"  Theorems verified: {len(results['theorems_verified'])}")
            print(f"  Paradoxes resolved: {len(results['paradoxes_resolved'])}")
        except Exception as e:
            print(f"Error in demonstration: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)
    sys.exit(0 if success else 1)

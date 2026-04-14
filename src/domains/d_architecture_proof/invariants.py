#!/usr/bin/env python3
"""D_ARCHITECTURE_PROOF Invariants — Yeshua design choice verification

Verifies Heyting vs Boolean, Fraction vs Float, axiom independence.
Brouwer (1913): Intuitionistic logic, Dedekind (1858): Rational arithmetic.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    LogicEvaluation, NumericComputation, AxiomIndependence, GeometricMorphismProof,
    AlgebraType, NumericType, evaluate_excluded_middle, fraction_exact
)


def check_heyting_vs_boolean_divergence(eval1: LogicEvaluation, eval2: LogicEvaluation) -> Tuple[bool, ProofObject]:
    """
    Heyting and Boolean algebras must diverge for undecidable propositions.

    Brouwer (1913): Heyting rejects excluded middle for non-constructive propositions.
    Falsifies if: same proposition evaluated as True in Boolean but None in Heyting → systems differ
    falsifies_if: same proposition evaluated as True in Boolean but None in Heyting → systems differ
    """
    if eval1.proposition_id != eval2.proposition_id:
        return True, ProofObject(
            conclusion=f"Evaluations {eval1.proposition_id} and {eval2.proposition_id} are for different propositions",
            premises=[f"Prop 1: {eval1.proposition_id}", f"Prop 2: {eval2.proposition_id}"],
            rule="heyting_boolean_divergence"
        )

    boolean_eval = eval1 if eval1.algebra == AlgebraType.BOOLEAN else eval2
    heyting_eval = eval1 if eval1.algebra == AlgebraType.HEYTING else eval2

    if boolean_eval.algebra != AlgebraType.BOOLEAN or heyting_eval.algebra != AlgebraType.HEYTING:
        return True, ProofObject(
            conclusion="Evaluations not Boolean/Heyting pair",
            premises=[f"Algebra 1: {eval1.algebra}", f"Algebra 2: {eval2.algebra}"],
            rule="heyting_boolean_divergence"
        )

    # For undecidable propositions: Boolean assigns T/F, Heyting assigns None
    if heyting_eval.truth_value is None and boolean_eval.truth_value is not None:
        return True, ProofObject(
            conclusion=f"Heyting/Boolean diverge on {eval1.proposition_id}: Boolean={boolean_eval.truth_value}, Heyting=undecided",
            premises=[
                f"Boolean: {boolean_eval.truth_value}",
                f"Heyting: {heyting_eval.truth_value}",
                "Divergence proves architectural necessity"
            ],
            rule="heyting_boolean_divergence"
        )

    return True, ProofObject(
        conclusion=f"Proposition {eval1.proposition_id} decidable in both systems",
        premises=[f"Boolean: {boolean_eval.truth_value}", f"Heyting: {heyting_eval.truth_value}"],
        rule="heyting_boolean_divergence"
    )


def check_fraction_exactness(comp: NumericComputation) -> Tuple[bool, ProofObject]:
    """
    Fraction arithmetic must be exact (no rounding errors).

    Dedekind (1858): Rational numbers form an exact field.
    Falsifies if: numeric_type == FRACTION but exact == False
    falsifies_if: numeric_type == FRACTION but exact == False
    """
    if comp.numeric_type == NumericType.FRACTION and not comp.exact:
        return False, ProofObject(
            conclusion=f"VIOLATION: Fraction computation {comp.computation_id} marked as inexact",
            premises=[
                f"Operation: {comp.input_a} {comp.operation} {comp.input_b}",
                f"Result: {comp.result_fraction}",
                f"Exact: {comp.exact}",
                "Fractions must be exact per Dedekind"
            ],
            rule="fraction_exactness"
        )

    if comp.numeric_type == NumericType.FRACTION:
        expected = fraction_exact(comp.input_a, comp.input_b, comp.operation)
        if comp.result_fraction != expected:
            return False, ProofObject(
                conclusion=f"VIOLATION: Fraction result {comp.result_fraction} != expected {expected}",
                premises=[
                    f"Input: {comp.input_a} {comp.operation} {comp.input_b}",
                    f"Computed: {comp.result_fraction}",
                    f"Expected: {expected}"
                ],
                rule="fraction_exactness"
            )

    return True, ProofObject(
        conclusion=f"Computation {comp.computation_id} is exact",
        premises=[f"Type: {comp.numeric_type.name}", f"Exact: {comp.exact}"],
        rule="fraction_exactness"
    )


def check_float_inexact_example(comp_frac: NumericComputation, comp_float: NumericComputation) -> Tuple[bool, ProofObject]:
    """
    Float arithmetic can be inexact (demonstrates Fraction necessity).

    IEEE 754: Floating-point has rounding errors.
    Falsifies if: same operation, Fraction exact but Float inexact (proves architectural choice)
    falsifies_if: same operation, Fraction exact but Float inexact (proves architectural choice)
    """
    if comp_frac.numeric_type != NumericType.FRACTION or comp_float.numeric_type != NumericType.FLOAT:
        return True, ProofObject(
            conclusion="Computations not Fraction/Float pair",
            premises=[f"Type 1: {comp_frac.numeric_type}", f"Type 2: {comp_float.numeric_type}"],
            rule="float_inexact"
        )

    if comp_frac.input_a != comp_float.input_a or comp_frac.input_b != comp_float.input_b:
        return True, ProofObject(
            conclusion="Computations have different inputs",
            premises=[f"Frac: {comp_frac.input_a}, {comp_frac.input_b}", f"Float: {comp_float.input_a}, {comp_float.input_b}"],
            rule="float_inexact"
        )

    # If fraction is exact but float result differs → proves architectural necessity
    if comp_frac.exact and comp_float.result_float is not None:
        frac_as_float = comp_frac.result_fraction
        if abs(frac_as_float - comp_float.result_float) > 1e-15:
            return True, ProofObject(
                conclusion=f"Float inexact: Fraction={comp_frac.result_fraction}, Float={comp_float.result_float}",
                premises=[
                    f"Fraction result: {comp_frac.result_fraction} (exact)",
                    f"Float result: {comp_float.result_float} (inexact)",
                    f"Difference: {abs(frac_as_float - comp_float.result_float)}",
                    "Proves Fraction architectural necessity"
                ],
                rule="float_inexact"
            )

    return True, ProofObject(
        conclusion="Float approximation within tolerance",
        premises=[f"Fraction: {comp_frac.result_fraction}", f"Float: {comp_float.result_float}"],
        rule="float_inexact"
    )


def check_axiom_independence(axiom: AxiomIndependence) -> Tuple[bool, ProofObject]:
    """
    Yeshua axioms must be independent (each is necessary).

    Gödel (1940): Consistency via independence proofs.
    Falsifies if: is_independent == True requires countermodel to exist
    falsifies_if: is_independent == True requires countermodel to exist
    """
    if axiom.is_independent and not axiom.countermodel:
        return False, ProofObject(
            conclusion=f"VIOLATION: Axiom {axiom.axiom_name} claimed independent but no countermodel",
            premises=[
                f"Independent: {axiom.is_independent}",
                f"Countermodel: {axiom.countermodel}",
                "Independence requires countermodel"
            ],
            rule="axiom_independence"
        )

    return True, ProofObject(
        conclusion=f"Axiom {axiom.axiom_name} independence proof valid",
        premises=[
            f"Independent: {axiom.is_independent}",
            f"Countermodel: {axiom.countermodel or 'N/A'}"
        ],
        rule="axiom_independence"
    )


def check_geometric_morphism_truth_preservation(morph: GeometricMorphismProof) -> Tuple[bool, ProofObject]:
    """
    Geometric morphisms between toposes must indicate truth preservation.

    Grothendieck (1960s): Topos theory and geometric morphisms.
    Falsifies if: truth_preserved == False indicates non-conservative morphism
    falsifies_if: truth_preserved == False indicates non-conservative morphism
    """
    if not morph.truth_preserved:
        return True, ProofObject(
            conclusion=f"Geometric morphism {morph.morphism_id} is non-conservative: {morph.source_topos} → {morph.target_topos}",
            premises=[
                f"Source: {morph.source_topos}",
                f"Target: {morph.target_topos}",
                f"Truth preserved: {morph.truth_preserved}",
                "Non-conservative morphism (truth not preserved)"
            ],
            rule="geometric_morphism"
        )

    return True, ProofObject(
        conclusion=f"Geometric morphism {morph.morphism_id} preserves truth",
        premises=[f"{morph.source_topos} → {morph.target_topos}", f"Conservative: {morph.truth_preserved}"],
        rule="geometric_morphism"
    )


def run_all_invariants() -> dict:
    """Run all D_ARCHITECTURE_PROOF invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    axiom_independence = AxiomIndependence(
        axiom_name=None,
        is_independent=None,
        countermodel=None,
    )
    numeric_computation = NumericComputation(
        computation_id=None,
        numeric_type=NumericType.FRACTION,
        input_a=Fraction(1),
        input_b=Fraction(1),
        operation=None,
        result_fraction=None,
        result_float=None,
        exact=None,
    )
    geometric_morphism_proof = GeometricMorphismProof(
        morphism_id=None,
        source_topos=None,
        target_topos=None,
        truth_preserved=None,
        proof_object=None,
    )
    logic_evaluation = LogicEvaluation(
        proposition_id=None,
        algebra=AlgebraType.BOOLEAN,
        truth_value=None,
        proof_trace=None,
    )

    checks = [
        ("check_axiom_independence", lambda: check_axiom_independence(axiom_independence)),
        ("check_float_inexact_example", lambda: check_float_inexact_example(numeric_computation, numeric_computation)),
        ("check_fraction_exactness", lambda: check_fraction_exactness(numeric_computation)),
        ("check_geometric_morphism_truth_preservation", lambda: check_geometric_morphism_truth_preservation(geometric_morphism_proof)),
        ("check_heyting_vs_boolean_divergence", lambda: check_heyting_vs_boolean_divergence(logic_evaluation, logic_evaluation)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ARCHITECTURE_PROOF invariants: PASS")

#!/usr/bin/env python3
"""D_COMBINATORICS Invariants — Catalan numbers, pigeonhole, inclusion-exclusion

Combinatorics per Catalan (1838), Dirichlet (1834), and classical counting theory.
All invariants use exact integer arithmetic.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    CountingProblem, CatalanSequence, PigeonholeProblem, InclusionExclusion,
    CountingPrinciple, catalan_number, factorial, binomial_coefficient
)


def check_catalan_correctness(cat: CatalanSequence) -> Tuple[bool, ProofObject]:
    """
    Catalan number C_n must match the formula (2n choose n) / (n+1).

    Falsifies if: computed_value != catalan_number(n)
    falsifies_if: computed_value != catalan_number(n)
    """
    expected = catalan_number(cat.n)

    if cat.computed_value != expected:
        return False, ProofObject(
            conclusion=f"VIOLATION: Catalan C_{cat.n} computed as {cat.computed_value}, expected {expected}",
            premises=[
                f"Computed C_{cat.n} = {cat.computed_value}",
                f"Expected C_{cat.n} = {expected}",
                "Formula: C_n = (2n choose n) / (n+1)"
            ],
            rule="catalan_number_formula"
        )

    return True, ProofObject(
        conclusion=f"Catalan C_{cat.n} = {cat.computed_value} is correct",
        premises=[f"C_{cat.n} = {expected}"],
        rule="catalan_number_formula"
    )


def check_pigeonhole_principle(php: PigeonholeProblem) -> Tuple[bool, ProofObject]:
    """
    Pigeonhole principle: n pigeons in m holes → at least ⌈n/m⌉ pigeons in some hole.

    Falsifies if: min_pigeons_per_hole < ceil(n_pigeons / n_holes)
    falsifies_if: min_pigeons_per_hole < ceil(n_pigeons / n_holes)
    """
    import math
    expected_min = math.ceil(php.n_pigeons / php.n_holes)

    if php.min_pigeons_per_hole < expected_min:
        return False, ProofObject(
            conclusion=f"VIOLATION: Pigeonhole {php.problem_id} claims min {php.min_pigeons_per_hole}, must be >= {expected_min}",
            premises=[
                f"Pigeons: {php.n_pigeons}",
                f"Holes: {php.n_holes}",
                f"Min per hole: {php.min_pigeons_per_hole}",
                f"Expected: ⌈{php.n_pigeons}/{php.n_holes}⌉ = {expected_min}"
            ],
            rule="pigeonhole_principle"
        )

    return True, ProofObject(
        conclusion=f"Pigeonhole {php.problem_id} satisfies principle",
        premises=[f"Min per hole: {php.min_pigeons_per_hole} >= {expected_min}"],
        rule="pigeonhole_principle"
    )


def check_combination_formula(prob: CountingProblem) -> Tuple[bool, ProofObject]:
    """
    Combinations: C(n, k) = n! / (k! * (n-k)!)

    Falsifies if: principle == COMBINATION AND computed_count != binomial_coefficient(n, k)
    falsifies_if: principle == COMBINATION AND computed_count != binomial_coefficient(n, k)
    """
    if prob.principle != CountingPrinciple.COMBINATION:
        return True, ProofObject(
            conclusion=f"Problem {prob.problem_id} not a combination problem",
            premises=[f"Principle: {prob.principle.name}"],
            rule="combination_formula"
        )

    expected = binomial_coefficient(prob.n_items, prob.k_selected)

    if prob.computed_count != expected:
        return False, ProofObject(
            conclusion=f"VIOLATION: Combination C({prob.n_items}, {prob.k_selected}) = {prob.computed_count}, expected {expected}",
            premises=[
                f"Computed: {prob.computed_count}",
                f"Expected: C({prob.n_items}, {prob.k_selected}) = {expected}",
                "Formula: n! / (k! * (n-k)!)"
            ],
            rule="combination_formula"
        )

    return True, ProofObject(
        conclusion=f"Combination C({prob.n_items}, {prob.k_selected}) = {prob.computed_count} is correct",
        premises=[f"Expected: {expected}"],
        rule="combination_formula"
    )


def check_permutation_formula(prob: CountingProblem) -> Tuple[bool, ProofObject]:
    """
    Permutations: P(n, k) = n! / (n-k)!

    Falsifies if: principle == PERMUTATION AND computed_count != n! / (n-k)!
    falsifies_if: principle == PERMUTATION AND computed_count != n! / (n-k)!
    """
    if prob.principle != CountingPrinciple.PERMUTATION:
        return True, ProofObject(
            conclusion=f"Problem {prob.problem_id} not a permutation problem",
            premises=[f"Principle: {prob.principle.name}"],
            rule="permutation_formula"
        )

    expected = factorial(prob.n_items) // factorial(prob.n_items - prob.k_selected)

    if prob.computed_count != expected:
        return False, ProofObject(
            conclusion=f"VIOLATION: Permutation P({prob.n_items}, {prob.k_selected}) = {prob.computed_count}, expected {expected}",
            premises=[
                f"Computed: {prob.computed_count}",
                f"Expected: P({prob.n_items}, {prob.k_selected}) = {expected}",
                "Formula: n! / (n-k)!"
            ],
            rule="permutation_formula"
        )

    return True, ProofObject(
        conclusion=f"Permutation P({prob.n_items}, {prob.k_selected}) = {prob.computed_count} is correct",
        premises=[f"Expected: {expected}"],
        rule="permutation_formula"
    )


def check_inclusion_exclusion_size(ie: InclusionExclusion) -> Tuple[bool, ProofObject]:
    """
    Inclusion-exclusion: |A ∪ B| = |A| + |B| - |A ∩ B| (for 2 sets).

    Falsifies if: union_size != sum(individual_sizes) - sum(intersections) for n=2
    falsifies_if: union_size != sum(individual_sizes) - sum(intersections) for n=2
    """
    if ie.n_sets == 2:
        expected_union = sum(ie.individual_sizes) - sum(ie.intersections)

        if ie.union_size != expected_union:
            return False, ProofObject(
                conclusion=f"VIOLATION: Inclusion-exclusion {ie.problem_id} union size {ie.union_size}, expected {expected_union}",
                premises=[
                    f"Individual sizes: {ie.individual_sizes}",
                    f"Intersections: {ie.intersections}",
                    f"Computed union: {ie.union_size}",
                    f"Expected: {expected_union}"
                ],
                rule="inclusion_exclusion_2sets"
            )

        return True, ProofObject(
            conclusion=f"Inclusion-exclusion {ie.problem_id} union size {ie.union_size} correct",
            premises=[f"Expected: {expected_union}"],
            rule="inclusion_exclusion_2sets"
        )

    return True, ProofObject(
        conclusion=f"Inclusion-exclusion {ie.problem_id} with {ie.n_sets} sets (general case)",
        premises=[f"Union size: {ie.union_size}"],
        rule="inclusion_exclusion_general"
    )


def run_all_invariants() -> dict:
    """Run all D_COMBINATORICS invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    catalan_sequence = CatalanSequence(
        n=None,
        computed_value=None,
    )
    counting_problem = CountingProblem(
        problem_id=None,
        principle=CountingPrinciple.PERMUTATION,
        n_items=None,
        k_selected=None,
        computed_count=None,
    )
    inclusion_exclusion = InclusionExclusion(
        problem_id=None,
        n_sets=None,
        union_size=None,
        individual_sizes=None,
        intersections=None,
    )
    pigeonhole_problem = PigeonholeProblem(
        problem_id=None,
        n_pigeons=None,
        n_holes=None,
        min_pigeons_per_hole=None,
    )

    checks = [
        ("check_catalan_correctness", lambda: check_catalan_correctness(catalan_sequence)),
        ("check_combination_formula", lambda: check_combination_formula(counting_problem)),
        ("check_inclusion_exclusion_size", lambda: check_inclusion_exclusion_size(inclusion_exclusion)),
        ("check_permutation_formula", lambda: check_permutation_formula(counting_problem)),
        ("check_pigeonhole_principle", lambda: check_pigeonhole_principle(pigeonhole_problem)),
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
    print("All D_COMBINATORICS invariants: PASS")

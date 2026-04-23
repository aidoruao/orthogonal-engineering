"""FUNCTIONAL paradigm invariants — Church, Hindley-Milner, Bird-Meertens.

Phase 3A of Depositive Campaign.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import LambdaTerm, PureFunction, TypeInference, FoldOperation


def check_referential_transparency(func: PureFunction) -> Tuple[bool, ProofObject]:
    """Same input must always produce same output (Church 1936 / Strachey 1967).

    Falsifies if: outputs_for_same_input != calls_with_same_input.
    falsifies_if: outputs_for_same_input != calls_with_same_input.
    """
    if func.outputs_for_same_input != func.calls_with_same_input:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Referential transparency broken — "
                f"{func.outputs_for_same_input} outputs for {func.calls_with_same_input} calls"
            ),
            premises=[
                f"Calls: {func.calls_with_same_input}",
                f"Outputs: {func.outputs_for_same_input}",
            ],
            rule="functional_referential_transparency",
        )
    return True, ProofObject(
        conclusion=(
            f"Referential transparent: {func.outputs_for_same_input} == "
            f"{func.calls_with_same_input}"
        ),
        premises=[
            f"Calls: {func.calls_with_same_input}",
            f"Outputs: {func.outputs_for_same_input}",
        ],
        rule="functional_referential_transparency",
    )


def check_no_side_effects(func: PureFunction) -> Tuple[bool, ProofObject]:
    """Pure functions have zero side effects (Haskell Report 2010).

    Falsifies if: side_effects > 0.
    falsifies_if: side_effects > 0.
    """
    if func.side_effects > 0:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {func.side_effects} side effect(s) detected"
            ),
            premises=[f"Side effects: {func.side_effects}"],
            rule="functional_no_side_effects",
        )
    return True, ProofObject(
        conclusion="Zero side effects",
        premises=[f"Side effects: {func.side_effects}"],
        rule="functional_no_side_effects",
    )


def check_beta_reduction_termination(term: LambdaTerm) -> Tuple[bool, ProofObject]:
    """Strongly normalizing terms must reach normal form (Church-Rosser 1936).

    Falsifies if: beta_reductions > 1000 AND NOT is_normal_form.
    falsifies_if: beta_reductions > 1000 and not is_normal_form.
    """
    if term.beta_reductions > 1000 and not term.is_normal_form:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {term.beta_reductions} reductions without reaching normal form"
            ),
            premises=[
                f"Reductions: {term.beta_reductions}",
                f"Normal form: {term.is_normal_form}",
            ],
            rule="functional_beta_termination",
        )
    return True, ProofObject(
        conclusion=(
            f"Beta reduction terminates: {term.beta_reductions} reductions, "
            f"normal={term.is_normal_form}"
        ),
        premises=[
            f"Reductions: {term.beta_reductions}",
            f"Normal: {term.is_normal_form}",
        ],
        rule="functional_beta_termination",
    )


def check_hindley_milner_principal(inf: TypeInference) -> Tuple[bool, ProofObject]:
    """Principal type must solve all constraints (Hindley 1969 / Milner 1978).

    Falsifies if: has_principal_type AND constraints_solved < constraints_total.
    falsifies_if: has_principal_type and constraints_solved < constraints_total.
    """
    if inf.has_principal_type and inf.constraints_solved < inf.constraints_total:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Principal type claimed but only "
                f"{inf.constraints_solved}/{inf.constraints_total} constraints solved"
            ),
            premises=[
                f"Solved: {inf.constraints_solved}",
                f"Total: {inf.constraints_total}",
                f"Has principal: {inf.has_principal_type}",
            ],
            rule="functional_hindley_milner",
        )
    return True, ProofObject(
        conclusion=(
            f"Type inference valid: {inf.constraints_solved}/{inf.constraints_total} solved"
        ),
        premises=[
            f"Solved: {inf.constraints_solved}",
            f"Total: {inf.constraints_total}",
        ],
        rule="functional_hindley_milner",
    )


def check_fold_associativity(fold: FoldOperation) -> Tuple[bool, ProofObject]:
    """Associative fold must give same result left-to-right and right-to-left.

    Falsifies if: associative AND fold_left_result != fold_right_result.
    falsifies_if: associative and fold_left_result != fold_right_result.
    """
    if fold.associative and fold.fold_left_result != fold.fold_right_result:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Associative fold mismatch — left={fold.fold_left_result}, "
                f"right={fold.fold_right_result}"
            ),
            premises=[
                f"Left: {fold.fold_left_result}",
                f"Right: {fold.fold_right_result}",
            ],
            rule="functional_fold_associativity",
        )
    return True, ProofObject(
        conclusion=(
            f"Fold valid: left={fold.fold_left_result}, right={fold.fold_right_result}"
        ),
        premises=[
            f"Left: {fold.fold_left_result}",
            f"Right: {fold.fold_right_result}",
        ],
        rule="functional_fold_associativity",
    )


def check_closure_capture(term: LambdaTerm) -> Tuple[bool, ProofObject]:
    """Closed term must have no free variables outside bound scope (Landin 1964).

    Falsifies if: is_normal_form AND (free_variables - bound_variables) is nonempty.
    falsifies_if: is_normal_form and free_variables not subset of bound_variables.
    """
    if term.is_normal_form and not term.free_variables.issubset(term.bound_variables):
        unbound = term.free_variables - term.bound_variables
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Unbound free variable(s) in closed term: {unbound}"
            ),
            premises=[
                f"Free: {term.free_variables}",
                f"Bound: {term.bound_variables}",
                f"Unbound: {unbound}",
            ],
            rule="functional_closure_capture",
        )
    return True, ProofObject(
        conclusion=(
            f"Closure valid: free={term.free_variables}, bound={term.bound_variables}"
        ),
        premises=[
            f"Free: {term.free_variables}",
            f"Bound: {term.bound_variables}",
        ],
        rule="functional_closure_capture",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all functional paradigm checks with passing and failing data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_func = PureFunction(
        input_hash="a" * 64,
        output_hash="b" * 64,
        side_effects=0,
        calls_with_same_input=5,
        outputs_for_same_input=5,
    )
    fail_func = PureFunction(
        input_hash="a" * 64,
        output_hash="c" * 64,
        side_effects=2,
        calls_with_same_input=5,
        outputs_for_same_input=3,
    )
    pass_term = LambdaTerm(
        free_variables=frozenset(),
        bound_variables=frozenset({"x", "y"}),
        beta_reductions=3,
        is_normal_form=True,
    )
    fail_term = LambdaTerm(
        free_variables=frozenset({"z"}),
        bound_variables=frozenset({"x"}),
        beta_reductions=1500,
        is_normal_form=False,
    )
    fail_closed_term = LambdaTerm(
        free_variables=frozenset({"z"}),
        bound_variables=frozenset({"x"}),
        beta_reductions=2,
        is_normal_form=True,
    )
    pass_inf = TypeInference(
        term_id="t1",
        principal_type="Int -> Int",
        has_principal_type=True,
        type_variables=1,
        constraints_solved=4,
        constraints_total=4,
    )
    fail_inf = TypeInference(
        term_id="t2",
        principal_type="?",
        has_principal_type=True,
        type_variables=2,
        constraints_solved=2,
        constraints_total=5,
    )
    pass_fold = FoldOperation(
        elements=4,
        associative=True,
        commutative=True,
        identity_exists=True,
        fold_left_result=Fraction(10, 1),
        fold_right_result=Fraction(10, 1),
    )
    fail_fold = FoldOperation(
        elements=4,
        associative=True,
        commutative=False,
        identity_exists=True,
        fold_left_result=Fraction(10, 1),
        fold_right_result=Fraction(12, 1),
    )

    checks = [
        ("check_referential_transparency_pass", lambda: check_referential_transparency(pass_func)),
        ("check_referential_transparency_fail", lambda: check_referential_transparency(fail_func)),
        ("check_no_side_effects_pass", lambda: check_no_side_effects(pass_func)),
        ("check_no_side_effects_fail", lambda: check_no_side_effects(fail_func)),
        ("check_beta_reduction_termination_pass", lambda: check_beta_reduction_termination(pass_term)),
        ("check_beta_reduction_termination_fail", lambda: check_beta_reduction_termination(fail_term)),
        ("check_hindley_milner_principal_pass", lambda: check_hindley_milner_principal(pass_inf)),
        ("check_hindley_milner_principal_fail", lambda: check_hindley_milner_principal(fail_inf)),
        ("check_fold_associativity_pass", lambda: check_fold_associativity(pass_fold)),
        ("check_fold_associativity_fail", lambda: check_fold_associativity(fail_fold)),
        ("check_closure_capture_pass", lambda: check_closure_capture(pass_term)),
        ("check_closure_capture_fail", lambda: check_closure_capture(fail_closed_term)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results

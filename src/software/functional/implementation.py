"""FUNCTIONAL paradigm implementation — Lambda calculus, purity, types, folds.

Phase 3A of Depositive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import FrozenSet, Tuple


@dataclass(frozen=True)
class LambdaTerm:
    """Untyped lambda term with reduction metadata.

    falsifies_if: beta_reductions < 0.
    """
    free_variables: FrozenSet[str]
    bound_variables: FrozenSet[str]
    beta_reductions: int
    is_normal_form: bool


@dataclass(frozen=True)
class PureFunction:
    """Pure function with referential transparency evidence.

    falsifies_if: side_effects < 0.
    falsifies_if: calls_with_same_input < 0.
    """
    input_hash: str
    output_hash: str
    side_effects: int
    calls_with_same_input: int
    outputs_for_same_input: int


@dataclass(frozen=True)
class TypeInference:
    """Hindley-Milner type inference result.

    falsifies_if: constraints_total < 0.
    """
    term_id: str
    principal_type: str
    has_principal_type: bool
    type_variables: int
    constraints_solved: int
    constraints_total: int


@dataclass(frozen=True)
class FoldOperation:
    """Fold over a monoid with associativity/commutativity evidence.

    falsifies_if: elements < 0.
    """
    elements: int
    associative: bool
    commutative: bool
    identity_exists: bool
    fold_left_result: Fraction
    fold_right_result: Fraction


DOMAIN_METADATA = {
    "id": "FUNCTIONAL_PARADIGM",
    "claim_model": "LambdaTerm / PureFunction / TypeInference / FoldOperation",
    "check_functions": [
        "check_referential_transparency",
        "check_no_side_effects",
        "check_beta_reduction_termination",
        "check_hindley_milner_principal",
        "check_fold_associativity",
        "check_closure_capture",
    ],
}

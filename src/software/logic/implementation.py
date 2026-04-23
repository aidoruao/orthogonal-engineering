"""LOGIC paradigm implementation — Horn clauses, unification, resolution, CSP.

Phase 3C of Depositive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class HornClause:
    """Horn clause with head, body, and classification.

    falsifies_if: is_definite and not head.
    falsifies_if: is_goal and is_fact.
    """
    head: str
    body: Tuple[str, ...]
    is_definite: bool
    is_goal: bool
    is_fact: bool


@dataclass(frozen=True)
class UnificationResult:
    """Robinson unification result with occurs-check evidence.

    falsifies_if: unifier_exists and not occurs_check_passed.
    """
    term_a: str
    term_b: str
    unifier_exists: bool
    substitution_count: int
    occurs_check_passed: bool


@dataclass(frozen=True)
class ResolutionProof:
    """Resolution refutation proof with soundness/completeness evidence.

    falsifies_if: empty_clause_derived and not is_sound.
    falsifies_if: is_sound and not is_complete.
    """
    clauses: int
    resolution_steps: int
    empty_clause_derived: bool
    is_sound: bool
    is_complete: bool


@dataclass(frozen=True)
class ConstraintSatisfaction:
    """Constraint satisfaction problem with arc-consistency evidence.

    falsifies_if: arc_consistent and solutions_found == 0 and variables > 0.
    """
    variables: int
    constraints: int
    domain_size: Fraction
    solutions_found: int
    arc_consistent: bool


DOMAIN_METADATA = {
    "id": "LOGIC_PARADIGM",
    "claim_model": "HornClause / UnificationResult / ResolutionProof / ConstraintSatisfaction",
    "check_functions": [
        "check_horn_clause_definite",
        "check_unification_occurs",
        "check_resolution_soundness",
        "check_resolution_completeness",
        "check_constraint_arc_consistency",
        "check_negation_as_failure",
    ],
}

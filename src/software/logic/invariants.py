"""LOGIC paradigm invariants — Horn, Robinson, Mackworth, Clark.

Phase 3C of Depositive Campaign.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import HornClause, UnificationResult, ResolutionProof, ConstraintSatisfaction


def check_horn_clause_definite(clause: HornClause) -> Tuple[bool, ProofObject]:
    """Definite clause must have exactly one positive literal (Horn 1951 / Kowalski 1974).

    Falsifies if: is_definite AND head == "".
    falsifies_if: is_definite and not head.
    """
    if clause.is_definite and not clause.head:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Definite clause lacks head: body={clause.body}"
            ),
            premises=[
                f"Head: {clause.head!r}",
                f"Body: {clause.body}",
            ],
            rule="logic_horn_clause",
        )
    return True, ProofObject(
        conclusion=(
            f"Horn clause valid: head={clause.head!r}, definite={clause.is_definite}"
        ),
        premises=[
            f"Head: {clause.head!r}",
            f"Definite: {clause.is_definite}",
        ],
        rule="logic_horn_clause",
    )


def check_unification_occurs(unif: UnificationResult) -> Tuple[bool, ProofObject]:
    """Circular substitution = unsound unification (Robinson 1965).

    Falsifies if: unifier_exists AND NOT occurs_check_passed.
    falsifies_if: unifier_exists and not occurs_check_passed.
    """
    if unif.unifier_exists and not unif.occurs_check_passed:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Unification of {unif.term_a} and {unif.term_b} "
                f"passed without occurs-check"
            ),
            premises=[
                f"Term A: {unif.term_a}",
                f"Term B: {unif.term_b}",
                f"Occurs check: {unif.occurs_check_passed}",
            ],
            rule="logic_unification_occurs",
        )
    return True, ProofObject(
        conclusion=(
            f"Unification valid: occurs_check={unif.occurs_check_passed}"
        ),
        premises=[
            f"Exists: {unif.unifier_exists}",
            f"Occurs check: {unif.occurs_check_passed}",
        ],
        rule="logic_unification_occurs",
    )


def check_resolution_soundness(proof: ResolutionProof) -> Tuple[bool, ProofObject]:
    """Empty clause derived only if proof is sound (Robinson 1965).

    Falsifies if: empty_clause_derived AND NOT is_sound.
    falsifies_if: empty_clause_derived and not is_sound.
    """
    if proof.empty_clause_derived and not proof.is_sound:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Empty clause derived from unsound proof"
            ),
            premises=[
                f"Empty derived: {proof.empty_clause_derived}",
                f"Sound: {proof.is_sound}",
            ],
            rule="logic_resolution_soundness",
        )
    return True, ProofObject(
        conclusion=(
            f"Resolution sound: empty={proof.empty_clause_derived}, sound={proof.is_sound}"
        ),
        premises=[
            f"Empty: {proof.empty_clause_derived}",
            f"Sound: {proof.is_sound}",
        ],
        rule="logic_resolution_soundness",
    )


def check_resolution_completeness(proof: ResolutionProof) -> Tuple[bool, ProofObject]:
    """Sound resolution over Horn clauses must be refutation-complete (Robinson 1965).

    Falsifies if: is_sound AND NOT is_complete.
    falsifies_if: is_sound and not is_complete.
    """
    if proof.is_sound and not proof.is_complete:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Sound but incomplete resolution — "
                f"{proof.resolution_steps} steps, {proof.clauses} clauses"
            ),
            premises=[
                f"Sound: {proof.is_sound}",
                f"Complete: {proof.is_complete}",
            ],
            rule="logic_resolution_completeness",
        )
    return True, ProofObject(
        conclusion=(
            f"Resolution complete: sound={proof.is_sound}, complete={proof.is_complete}"
        ),
        premises=[
            f"Sound: {proof.is_sound}",
            f"Complete: {proof.is_complete}",
        ],
        rule="logic_resolution_completeness",
    )


def check_constraint_arc_consistency(csp: ConstraintSatisfaction) -> Tuple[bool, ProofObject]:
    """Arc-consistent CSP with variables must have ≥ 1 solution (Mackworth 1977 AC-3).

    Falsifies if: arc_consistent AND solutions_found == 0 AND variables > 0.
    falsifies_if: arc_consistent and solutions_found == 0 and variables > 0.
    """
    if csp.arc_consistent and csp.solutions_found == 0 and csp.variables > 0:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Arc-consistent CSP has zero solutions — "
                f"variables={csp.variables}, domain={csp.domain_size}"
            ),
            premises=[
                f"Variables: {csp.variables}",
                f"Domain: {csp.domain_size}",
                f"Solutions: {csp.solutions_found}",
            ],
            rule="logic_arc_consistency",
        )
    return True, ProofObject(
        conclusion=(
            f"CSP valid: arc={csp.arc_consistent}, solutions={csp.solutions_found}"
        ),
        premises=[
            f"Variables: {csp.variables}",
            f"Solutions: {csp.solutions_found}",
        ],
        rule="logic_arc_consistency",
    )


def check_negation_as_failure(clause: HornClause) -> Tuple[bool, ProofObject]:
    """Clark 1978: a clause cannot be both goal and ground fact.

    Falsifies if: is_goal AND is_fact.
    falsifies_if: is_goal and is_fact.
    """
    if clause.is_goal and clause.is_fact:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Clause is both goal and fact — {clause.head!r}"
            ),
            premises=[
                f"Goal: {clause.is_goal}",
                f"Fact: {clause.is_fact}",
                f"Head: {clause.head!r}",
            ],
            rule="logic_negation_as_failure",
        )
    return True, ProofObject(
        conclusion=(
            f"Clause classification valid: goal={clause.is_goal}, fact={clause.is_fact}"
        ),
        premises=[
            f"Goal: {clause.is_goal}",
            f"Fact: {clause.is_fact}",
        ],
        rule="logic_negation_as_failure",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all logic paradigm checks with passing and failing data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_clause = HornClause(
        head="P", body=("Q", "R"), is_definite=True, is_goal=False, is_fact=False,
    )
    fail_clause = HornClause(
        head="", body=("Q",), is_definite=True, is_goal=True, is_fact=True,
    )
    pass_unif = UnificationResult(
        term_a="f(X)", term_b="f(a)", unifier_exists=True,
        substitution_count=1, occurs_check_passed=True,
    )
    fail_unif = UnificationResult(
        term_a="f(X)", term_b="f(g(X))", unifier_exists=True,
        substitution_count=1, occurs_check_passed=False,
    )
    pass_proof = ResolutionProof(
        clauses=4, resolution_steps=3, empty_clause_derived=True,
        is_sound=True, is_complete=True,
    )
    fail_sound_proof = ResolutionProof(
        clauses=4, resolution_steps=3, empty_clause_derived=True,
        is_sound=False, is_complete=False,
    )
    fail_complete_proof = ResolutionProof(
        clauses=4, resolution_steps=3, empty_clause_derived=True,
        is_sound=True, is_complete=False,
    )
    pass_csp = ConstraintSatisfaction(
        variables=3, constraints=2, domain_size=Fraction(8, 1),
        solutions_found=2, arc_consistent=True,
    )
    fail_csp = ConstraintSatisfaction(
        variables=3, constraints=2, domain_size=Fraction(8, 1),
        solutions_found=0, arc_consistent=True,
    )

    checks = [
        ("check_horn_clause_definite_pass", lambda: check_horn_clause_definite(pass_clause)),
        ("check_horn_clause_definite_fail", lambda: check_horn_clause_definite(fail_clause)),
        ("check_unification_occurs_pass", lambda: check_unification_occurs(pass_unif)),
        ("check_unification_occurs_fail", lambda: check_unification_occurs(fail_unif)),
        ("check_resolution_soundness_pass", lambda: check_resolution_soundness(pass_proof)),
        ("check_resolution_soundness_fail", lambda: check_resolution_soundness(fail_sound_proof)),
        ("check_resolution_completeness_pass", lambda: check_resolution_completeness(pass_proof)),
        ("check_resolution_completeness_fail", lambda: check_resolution_completeness(fail_complete_proof)),
        ("check_constraint_arc_consistency_pass", lambda: check_constraint_arc_consistency(pass_csp)),
        ("check_constraint_arc_consistency_fail", lambda: check_constraint_arc_consistency(fail_csp)),
        ("check_negation_as_failure_pass", lambda: check_negation_as_failure(pass_clause)),
        ("check_negation_as_failure_fail", lambda: check_negation_as_failure(fail_clause)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results

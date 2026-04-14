#!/usr/bin/env python3
"""Software Testing Invariants — MC/DC, mutation, determinism."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Condition,
    Decision,
    DeterminismVerifier,
    MCDCChecker,
    MIN_MUTATION_SCORE,
    Mutant,
    MutationScorer,
)


def check_mcdc_completeness(checker: MCDCChecker) -> Tuple[bool, ProofObject]:
    """MC/DC: Each condition must independently affect outcome.

    Falsifies if: any condition lacks independence pairs indicating incomplete MC/DC.
    falsifies_if: any condition lacks independence pairs indicating incomplete MC/DC.
    """
    if not checker.is_mcdc_complete():
        pairs = checker.get_independence_pairs()
        incomplete = [c for c, p in pairs.items() if len(p) == 0]
        return False, ProofObject(
            conclusion=f"VIOLATION: MC/DC incomplete for conditions: {incomplete}",
            premises=[],
            rule="mcdc_completeness"
        )
    
    return True, ProofObject(
        conclusion="MC/DC coverage complete",
        premises=[f"Conditions: {len(checker.decision.conditions)}"],
        rule="mcdc_completeness"
    )


def check_mutation_score(scorer: MutationScorer) -> Tuple[bool, ProofObject]:
    """Mutation score must meet threshold.

    Falsifies if: mutation score falls below MIN_MUTATION_SCORE.
    falsifies_if: mutation score falls below MIN_MUTATION_SCORE.
    """
    score = scorer.score()
    
    if score < MIN_MUTATION_SCORE:
        return False, ProofObject(
            conclusion=f"VIOLATION: Mutation score {score}% < {MIN_MUTATION_SCORE}%",
            premises=[],
            rule="mutation_score"
        )
    
    return True, ProofObject(
        conclusion=f"Mutation score adequate ({score}%)",
        premises=[],
        rule="mutation_score"
    )


def check_test_determinism(verifier: DeterminismVerifier) -> Tuple[bool, ProofObject]:
    """Tests must produce same result across runs.

    Falsifies if: is_deterministic returns False for the test.
    falsifies_if: is_deterministic returns False for the test.
    """
    if not verifier.is_deterministic():
        return False, ProofObject(
            conclusion=f"VIOLATION: Test '{verifier.test_name}' non-deterministic",
            premises=[f"Pass rate: {verifier.pass_rate()}%"],
            rule="test_determinism"
        )
    
    return True, ProofObject(
        conclusion=f"Test '{verifier.test_name}' deterministic",
        premises=[],
        rule="test_determinism"
    )


def run_all_invariants() -> dict:
    """Run all D_SOFTWARE_TESTING invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    mcdc_checker = MCDCChecker(
        decision=Decision(
        decision_id="SOFTWARE-001",
        conditions=[Condition(
        condition_id="SOFTWARE-001",
        value=True,
    )],
        outcome=True,
    ),
        test_cases=[Decision(
        decision_id="SOFTWARE-001",
        conditions=[Condition(
        condition_id="SOFTWARE-001",
        value=True,
    )],
        outcome=True,
    )],
    )
    mutation_scorer = MutationScorer(
        mutants=[Mutant(
        mutant_id="SOFTWARE-001",
        original_code="SAMPLE",
        mutated_code="SAMPLE",
    )],
    )
    determinism_verifier = DeterminismVerifier(
        test_name="Sample SOFTWARE",
        runs=[True],
    )

    checks = [
        ("check_mcdc_completeness", lambda: check_mcdc_completeness(mcdc_checker)),
        ("check_mutation_score", lambda: check_mutation_score(mutation_scorer)),
        ("check_test_determinism", lambda: check_test_determinism(determinism_verifier)),
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
    print("All D_SOFTWARE_TESTING invariants: PASS")

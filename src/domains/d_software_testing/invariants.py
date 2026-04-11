#!/usr/bin/env python3
"""Software Testing Invariants — MC/DC, mutation, determinism."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import MCDCChecker, MutationScorer, DeterminismVerifier, MIN_MUTATION_SCORE


def check_mcdc_completeness(checker: MCDCChecker) -> Tuple[bool, ProofObject]:
    """MC/DC: Each condition must independently affect outcome.
    
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
    
    
    Falsifies if: score < MIN_MUTATION_SCORE"""Mutation score must meet threshold.
    
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

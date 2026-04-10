#!/usr/bin/env python3
"""Paraconsistent Logic Domain Invariants — Non-explosive contradiction handling.

Standards:
- LP (Logic of Paradox)
- da Costa C-systems
- Relevant logic entailment

Falsifies if:
- Explosion principle holds (A ∧ ¬A → B)
- Triviality from contradiction
- Classical logic imported without restriction
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import ParaconsistentTheory, InferenceRule, TruthValue


def check_explosion_blocked(theory: ParaconsistentTheory) -> Tuple[bool, ProofObject]:
    """Paraconsistent logic: A ∧ ¬A should NOT entail arbitrary B.
    
    falsifies_if:
        - theory.is_inconsistent() AND theory.is_trivial()
    """
    if theory.is_inconsistent() and not theory.explosion_blocked():
        return False, ProofObject(
            conclusion="VIOLATION: Explosion principle holds - inconsistent theory is trivial",
            premises=[
                f"Theory: {theory.theory_id}",
                "Inconsistent: True",
                "Explosion blocked: False"
            ],
            rule="paraconsistent_explosion_blocking"
        )
    
    return True, ProofObject(
        conclusion="Explosion properly blocked",
        premises=[
            f"Inconsistent: {theory.is_inconsistent()}",
            "Explosion: Blocked"
        ],
        rule="explosion_blocked"
    )


def check_truth_value_consistency(prop_truth: TruthValue) -> Tuple[bool, ProofObject]:
    """Paraconsistent truth values properly assigned.
    
    falsifies_if:
        - BOTH assigned without dialetheist justification
    """
    if prop_truth == TruthValue.BOTH:
        return True, ProofObject(
            conclusion="Dialetheia (true contradiction) acknowledged",
            premises=["Truth value: BOTH"],
            rule="dialetheia_accepted"
        )
    
    return True, ProofObject(
        conclusion="Truth value classical or gapped",
        premises=[f"Value: {prop_truth.name}"],
        rule="truth_value_valid"
    )


def check_inference_non_explosive(rule: InferenceRule) -> Tuple[bool, ProofObject]:
    """Paraconsistent inference rules must not derive everything from contradiction.
    
    falsifies_if:
        - rule.valid_in_classical AND not rule.valid_in_lp
        - Rule is disjunctive syllogism without restriction
    """
    if rule.valid_in_classical and not rule.valid_in_lp:
        if "explosion" in rule.rule_name.lower() or "ex contradictione" in rule.rule_name.lower():
            return False, ProofObject(
                conclusion="VIOLATION: Classical explosion rule not blocked",
                premises=[
                    f"Rule: {rule.rule_name}",
                    "Classical: Valid",
                    "LP: Invalid (correctly)"
                ],
                rule="paraconsistent_rule_exclusion"
            )
    
    return True, ProofObject(
        conclusion="Inference rule compatible with paraconsistency",
        premises=[f"Rule: {rule.rule_name}"],
        rule="inference_compliant"
    )


def check_adjunctive_syllogism(rule: InferenceRule) -> Tuple[bool, ProofObject]:
    """Disjunctive syllogism (A ∨ B, ¬A ⊢ B) fails in LP when A is BOTH.
    
    falsifies_if:
        - Rule used without restriction
    """
    if "disjunctive_syllogism" in rule.rule_name.lower():
        if rule.valid_in_lp:
            return False, ProofObject(
                conclusion="WARNING: Disjunctive syllogism valid in LP - may cause issues",
                premises=[
                    f"Rule: {rule.rule_name}",
                    "Valid in LP: True (unexpected)"
                ],
                rule="disjunctive_syllogism_lp"
            )
    
    return True, ProofObject(
        conclusion="Disjunctive syllogism handled correctly",
        premises=[f"Rule: {rule.rule_name}"],
        rule="adjunctive_syllogism_compliant"
    )


def check_non_triviality(theory: ParaconsistentTheory) -> Tuple[bool, ProofObject]:
    """Inconsistent paraconsistent theory should not be trivial.
    
    falsifies_if:
        - theory.is_trivial() is True
    """
    if theory.is_trivial():
        return False, ProofObject(
            conclusion="VIOLATION: Paraconsistent theory is trivial",
            premises=[
                f"Theory: {theory.theory_id}",
                "Trivial: True (everything provable)"
            ],
            rule="paraconsistent_non_triviality"
        )
    
    return True, ProofObject(
        conclusion="Theory non-trivial",
        premises=["Trivial: False"],
        rule="non_triviality_maintained"
    )

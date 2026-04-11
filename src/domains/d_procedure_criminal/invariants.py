#!/usr/bin/env python3
"""Criminal Procedure Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Arrest, Interrogation, CriminalCase, SPEEDY_TRIAL_DAYS

def check_probable_cause(arrest: Arrest) -> Tuple[bool, ProofObject]:
    """4th Amendment: Arrest requires probable cause.
    
    falsifies_if: condition_evaluated_to_false"""
    if arrest.probable_cause_exists:
        return True, ProofObject(
            conclusion="Probable cause exists — arrest valid",
            premises=[],
            rule="fourth_amendment_pc"
        )
    return False, ProofObject(
        conclusion="VIOLATION: Arrest without probable cause",
        premises=[],
        rule="fourth_amendment_pc"
    )

def check_miranda(interrogation: Interrogation) -> Tuple[bool, ProofObject]:
    """Miranda v. Arizona: Warnings required for custodial interrogation.
    
    falsifies_if: condition_evaluated_to_false"""
    if not interrogation.miranda_required():
        return True, ProofObject(
            conclusion="Miranda not applicable",
            premises=[],
            rule="miranda_applicability"
        )
    
    if interrogation.statement_admissible():
        return True, ProofObject(
            conclusion="Miranda satisfied — statement admissible",
            premises=[],
            rule="miranda_warnings"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Custodial interrogation without Miranda warnings",
        premises=[],
        rule="miranda_warnings"
    )

def check_speedy_trial(case: CriminalCase) -> Tuple[bool, ProofObject]:
    """Speedy Trial Act: 70 days from indictment to trial.
    
    falsifies_if: condition_evaluated_to_false"""
    if case.speedy_trial_violation():
        return False, ProofObject(
            conclusion="VIOLATION: Speedy trial right violated",
            premises=[],
            rule="speedy_trial_act"
        )
    return True, ProofObject(
        conclusion="Speedy trial requirements satisfied",
        premises=[],
        rule="speedy_trial_act"
    )

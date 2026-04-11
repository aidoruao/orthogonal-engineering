#!/usr/bin/env python3
"""Immigration Law Invariants — INA compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import VisaCategoryChecker, ProcessingTimer, StatusStateMachine


def check_visa_eligibility(checker: VisaCategoryChecker) -> Tuple[bool, ProofObject]:
    """INA: Visa category requirements must be met.

    Falsifies if: applicant fails to meet the requirements for the requested visa category.
    """
    if not checker.meets_category_requirements():
        return False, ProofObject(
            conclusion=f"VIOLATION: Applicant does not meet {checker.applicant.visa_category.name} requirements",
            premises=[],
            rule="ina_visa_category"
        )
    
    return True, ProofObject(
        conclusion=f"Visa category requirements satisfied for {checker.applicant.visa_category.name}",
        premises=[],
        rule="ina_visa_category"
    )


def check_processing_deadline(timer: ProcessingTimer) -> Tuple[bool, ProofObject]:
    """INA: Processing must not exceed statutory deadlines.

    Falsifies if: days_elapsed exceeds statutory_deadline_days.
    """
    if timer.is_overdue():
        return False, ProofObject(
            conclusion=f"VIOLATION: Processing {timer.days_elapsed} days > deadline {timer.statutory_deadline_days}",
            premises=[],
            rule="ina_processing_deadline"
        )
    
    return True, ProofObject(
        conclusion=f"Processing within deadline ({timer.days_elapsed}/{timer.statutory_deadline_days} days)",
        premises=[],
        rule="ina_processing_deadline"
    )


def check_status_transition(machine: StatusStateMachine) -> Tuple[bool, ProofObject]:
    """Status transitions must follow valid paths.

    Falsifies if: requested_status is not reachable from current_status.
    """
    if not machine.is_valid_transition():
        return False, ProofObject(
            conclusion=f"VIOLATION: Invalid transition {machine.current_status} -> {machine.requested_status}",
            premises=[],
            rule="status_transition"
        )
    
    return True, ProofObject(
        conclusion=f"Valid status transition: {machine.current_status} -> {machine.requested_status}",
        premises=[],
        rule="status_transition"
    )

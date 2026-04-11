#!/usr/bin/env python3
"""Consumer Protection Invariants — FTC Act, Magnuson-Moss."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import ClaimVerifier, WarrantyChecker, RecallTracker, MIN_NOTIFICATION_RATE


def check_deceptive_practices(verifier: ClaimVerifier) -> Tuple[bool, ProofObject]:
    """FTC Act § 5: Claims must be substantiated.
    
    unsubstantiated = verifier.find_unsubstantiated()
    
    if unsubstantiated:
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(unsubstantiated)} unsubstantiated claims",
            premises=[c.claim_id for c in unsubstantiated],
            rule="ftc_act_section_5"
        )
    
    return True, ProofObject(
        conclusion="All claims substantiated",
        premises=[f"Claims checked: {len(verifier.claims)}"],
        rule="ftc_act_section_5"
    )


def check_warranty_coverage(checker: WarrantyChecker) -> Tuple[bool, ProofObject]:
    """Magnuson-Moss: Warranty must honor covered repairs.
    
    if not checker.is_covered():
        return False, ProofObject(
            conclusion="VIOLATION: Warranty denial for covered item",
            premises=[f"Request: {checker.repair_request}"],
            rule="magnuson_moss_coverage"
        )
    
    return True, ProofObject(
        conclusion="Repair covered under warranty",
        premises=[],
        rule="magnuson_moss_coverage"
    )


def check_recall_completeness(tracker: RecallTracker) -> Tuple[bool, ProofObject]:
    """Recall notifications must reach 95%+ of affected consumers.
    
    rate = tracker.notification_rate()
    
    if rate < MIN_NOTIFICATION_RATE:
        return False, ProofObject(
            conclusion=f"VIOLATION: Recall notification {rate}% < {MIN_NOTIFICATION_RATE}%",
            premises=[f"Notified: {tracker.notified_units}/{tracker.affected_units}"],
            rule="recall_notification"
        )
    
    return True, ProofObject(
        conclusion=f"Recall notification adequate ({rate}%)",
        premises=[],
        rule="recall_notification"
    )

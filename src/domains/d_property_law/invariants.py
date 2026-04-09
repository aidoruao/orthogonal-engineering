#!/usr/bin/env python3
"""Property Law Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import PropertyInterest, AdversePossession

def check_recording(prior: PropertyInterest, subsequent: PropertyInterest) -> Tuple[bool, ProofObject]:
    """Recording act priority analysis."""
    if prior.recorded and not subsequent.recorded:
        return True, ProofObject(
            conclusion="Prior recorded interest prevails",
            premises=[],
            rule="recording_act_priority"
        )
    if not prior.recorded and subsequent.recorded:
        return False, ProofObject(
            conclusion="VIOLATION: Unrecorded interest loses to recorded subsequent",
            premises=[],
            rule="recording_act_priority"
        )
    return True, ProofObject(
        conclusion="Priority determined by recording dates",
        premises=[],
        rule="recording_act_priority"
    )

def check_adverse_possession(claim: AdversePossession) -> Tuple[bool, ProofObject]:
    """Adverse possession OCEAN elements and statutory period."""
    if not claim.all_elements_present():
        missing = []
        if not claim.open_notorious: missing.append("open/notorious")
        if not claim.continuous: missing.append("continuous")
        if not claim.exclusive: missing.append("exclusive")
        if not claim.adverse: missing.append("adverse")
        return False, ProofObject(
            conclusion=f"VIOLATION: Missing OCEAN elements: {missing}",
            premises=[],
            rule="adverse_possession_ocean"
        )
    
    years = claim.possession_duration_years()
    if years < claim.STATUTORY_PERIOD_YEARS:
        return False, ProofObject(
            conclusion=f"VIOLATION: {years} years < {claim.STATUTORY_PERIOD_YEARS} required",
            premises=[],
            rule="adverse_possession_statutory_period"
        )
    
    return True, ProofObject(
        conclusion="Adverse possession claim valid",
        premises=[f"Duration: {years} years"],
        rule="adverse_possession"
    )

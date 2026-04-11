#!/usr/bin/env python3
"""Occupational Safety Invariants — OSHA compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Hazard, FallProtection, OSHAInspection

def check_pel(hazard: Hazard) -> Tuple[bool, ProofObject]:
    """OSHA Permissible Exposure Limit compliance.
    
    falsifies_if: condition_evaluated_to_false"""
    if not hazard.exceeds_pel():
        return True, ProofObject(
            conclusion=f"PEL compliant ({hazard.chemical_exposure_ppm} <= {hazard.permissible_exposure_limit})",
            premises=[],
            rule="osha_pel"
        )
    return False, ProofObject(
        conclusion="VIOLATION: PEL exceeded",
        premises=[f"Actual: {hazard.chemical_exposure_ppm}", f"Limit: {hazard.permissible_exposure_limit}"],
        rule="osha_pel"
    )

def check_fall_protection(fp: FallProtection) -> Tuple[bool, ProofObject]:
    """OSHA 1926.501: Fall protection at 6+ feet.
    
    falsifies_if: condition_evaluated_to_false"""
    if not fp.protection_required():
        return True, ProofObject(
            conclusion=f"Fall protection not required ({fp.work_height_feet} < {fp.FALL_PROTECTION_THRESHOLD} ft)",
            premises=[],
            rule="osha_fall_protection"
        )
    
    if fp.is_compliant():
        return True, ProofObject(
            conclusion="Fall protection adequate",
            premises=[],
            rule="osha_fall_protection"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Fall protection required but not provided",
        premises=[f"Height: {fp.work_height_feet} feet"],
        rule="osha_fall_protection"
    )

def check_general_duty(inspection: OSHAInspection) -> Tuple[bool, ProofObject]:
    """OSH Act § 5(a)(1): General duty clause.
    
    falsifies_if: condition_evaluated_to_false"""
    if inspection.has_general_duty_violation():
        return False, ProofObject(
            conclusion="VIOLATION: General duty clause — recognized hazard not abated",
            premises=[],
            rule="osha_general_duty"
        )
    return True, ProofObject(
        conclusion="General duty clause satisfied",
        premises=[],
        rule="osha_general_duty"
    )

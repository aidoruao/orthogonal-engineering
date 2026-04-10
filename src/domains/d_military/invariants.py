#!/usr/bin/env python3
"""Military Domain Invariants — LOAC, Geneva Conventions, UCMJ compliance.

Standards:
- Geneva Conventions I-IV
- Hague Regulations
- Law of Armed Conflict (LOAC)
- UCMJ
- Additional Protocols

Falsifies if:
- POW rights violated
- Indiscriminate attack conducted
- Proportionality violated
- ICRC not notified of detention
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    ArmedConflict, MilitaryOperation, DetentionOperation,
    CourtMartial, TargetCategory
)


def check_pow_rights(detention: DetentionOperation) -> Tuple[bool, ProofObject]:
    """Geneva III requires ICRC notification for POWs.
    
    falsifies_if:
        - pow_rights_applicable AND icrc_notified is False
    """
    if detention.pow_rights_applicable() and not detention.icrc_notified:
        return False, ProofObject(
            conclusion="VIOLATION: POW detention without ICRC notification",
            premises=[
                f"Detention: {detention.detention_id}",
                f"Category: {detention.geneva_category}",
                "ICRC notified: False"
            ],
            rule="geneva_convention_iii_article_122"
        )
    
    return True, ProofObject(
        conclusion="POW rights respected or not applicable",
        premises=[
            f"Category: {detention.geneva_category}",
            f"ICRC notified: {detention.icrc_notified}"
        ],
        rule="pow_rights_compliant"
    )


def check_proportionality(operation: MilitaryOperation) -> Tuple[bool, ProofObject]:
    """LOAC requires proportionality between military advantage and collateral damage.
    
    falsifies_if:
        - civilian_casualties excessive relative to military gain
    """
    if operation.civilian_casualties > 0:
        # If high civilian casualties but minimal military gain
        if operation.military_objectives_destroyed == 0 and operation.civilian_casualties > 5:
            return False, ProofObject(
                conclusion="VIOLATION: Operation appears disproportionate - civilian harm without military gain",
                premises=[
                    f"Operation: {operation.operation_id}",
                    f"Civilian casualties: {operation.civilian_casualties}",
                    f"Military objectives: {operation.military_objectives_destroyed}",
                    "Proportionality assessment: Failed"
                ],
                rule="loac_principle_of_proportionality"
            )
    
    return True, ProofObject(
        conclusion="Operation proportionality acceptable",
        premises=[
            f"Civilian casualties: {operation.civilian_casualties}",
            f"Military gain: {operation.military_objectives_destroyed}"
        ],
        rule="proportionality_compliant"
    )


def check_indiscriminate_weapons(operation: MilitaryOperation) -> Tuple[bool, ProofObject]:
    """Weapons that cannot be directed at military objectives are prohibited.
    
    falsifies_if:
        - indiscriminate_weapon is True
    """
    if operation.indiscriminate_weapon:
        return False, ProofObject(
            conclusion="VIOLATION: Use of indiscriminate weapon prohibited",
            premises=[
                f"Operation: {operation.operation_id}",
                f"Weapons: {operation.weapons_used}",
                "Indiscriminate: True"
            ],
            rule="geneva_protocol_i_article_51_indiscriminate_attacks"
        )
    
    return True, ProofObject(
        conclusion="Weapons discriminate and lawful",
        premises=[f"Weapons: {operation.weapons_used}"],
        rule="weapons_compliant"
    )


def check_medical_neutrality(operation: MilitaryOperation) -> Tuple[bool, ProofObject]:
    """Medical units and personnel are protected under Geneva Conventions.
    
    falsifies_if:
        - target_category is MEDICAL
    """
    if operation.target_category == TargetCategory.MEDICAL:
        return False, ProofObject(
            conclusion="VIOLATION: Attack on medical unit/personnel prohibited",
            premises=[
                f"Operation: {operation.operation_id}",
                "Target: Medical facility/personnel"
            ],
            rule="geneva_convention_i_medical_protection"
        )
    
    return True, ProofObject(
        conclusion="Target not protected medical unit",
        premises=[f"Target: {operation.target_category.name}"],
        rule="medical_neutrality_compliant"
    )


def check_cultural_property_protection(operation: MilitaryOperation) -> Tuple[bool, ProofObject]:
    """Hague Convention protects cultural property in armed conflict.
    
    falsifies_if:
        - target_category is CULTURAL_PROPERTY
    """
    if operation.target_category == TargetCategory.CULTURAL_PROPERTY:
        return False, ProofObject(
            conclusion="VIOLATION: Attack on cultural property prohibited",
            premises=[
                f"Operation: {operation.operation_id}",
                "Target: Cultural property"
            ],
            rule="hague_convention_1954_cultural_property"
        )
    
    return True, ProofObject(
        conclusion="Cultural property not targeted",
        premises=[f"Target: {operation.target_category.name}"],
        rule="cultural_property_compliant"
    )


def check_enhanced_interrogation_prohibition(detention: DetentionOperation) -> Tuple[bool, ProofObject]:
    """Torture and CIDTP (Cruel, Inhuman, Degrading Treatment) absolutely prohibited.
    
    falsifies_if:
        - enhanced_interrogation_used is True
    """
    if detention.enhanced_interrogation_used:
        return False, ProofObject(
            conclusion="VIOLATION: Enhanced interrogation (torture) absolutely prohibited",
            premises=[
                f"Detention: {detention.detention_id}",
                f"Methods: {detention.interrogation_methods}",
                "Enhanced interrogation: True"
            ],
            rule="cat_torture_prohibition"
        )
    
    return True, ProofObject(
        conclusion="No enhanced interrogation used",
        premises=["Interrogation methods: Standard"],
        rule="interrogation_compliant"
    )

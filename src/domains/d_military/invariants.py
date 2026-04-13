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
    
    Falsifies if: POW rights apply and icrc_notified is False.
    falsifies_if: POW rights apply and icrc_notified is False.
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
    
    Falsifies if: civilian casualties are excessive relative to military gain.
    falsifies_if: civilian casualties are excessive relative to military gain.
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
    
    Falsifies if: operation uses an indiscriminate weapon.
    falsifies_if: operation uses an indiscriminate weapon.
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
    
    Falsifies if: target_category is MEDICAL.
    falsifies_if: target_category is MEDICAL.
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
    
    Falsifies if: target_category is CULTURAL_PROPERTY.
    falsifies_if: target_category is CULTURAL_PROPERTY.
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
    
    Falsifies if: enhanced_interrogation_used is True.
    falsifies_if: enhanced_interrogation_used is True.
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


def run_all_invariants() -> dict:
    """Run all D_MILITARY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    military_operation = MilitaryOperation(
        operation_id=None,
        operation_name=None,
        conflict_id=None,
        operation_date=None,
        location=None,
        target_category=TargetCategory.COMBATANT,
        proportionality_assessment=None,
        collateral_damage_estimate=None,
        weapons_used=None,
        indiscriminate_weapon=None,
        civilian_casualties=None,
        combatant_casualties=None,
        military_objectives_destroyed=None,
    )
    detention_operation = DetentionOperation(
        detention_id=None,
        detainee_id=None,
        geneva_category=None,
        capture_date=None,
        capturing_power=None,
        icrc_notified=None,
        family_notified=None,
        judicial_review_date=None,
        interrogation_methods=None,
        enhanced_interrogation_used=None,
    )

    checks = [
        ("check_cultural_property_protection", lambda: check_cultural_property_protection(military_operation)),
        ("check_enhanced_interrogation_prohibition", lambda: check_enhanced_interrogation_prohibition(detention_operation)),
        ("check_indiscriminate_weapons", lambda: check_indiscriminate_weapons(military_operation)),
        ("check_medical_neutrality", lambda: check_medical_neutrality(military_operation)),
        ("check_pow_rights", lambda: check_pow_rights(detention_operation)),
        ("check_proportionality", lambda: check_proportionality(military_operation)),
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
    print("All D_MILITARY invariants: PASS")

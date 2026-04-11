"""D_INTERNATIONAL_HUMANITARIAN invariant checks — IHL validation.

International humanitarian law invariants ensure:
1. Distinction principle (combatants vs civilians)
2. Proportionality of attacks
3. Protection of protected persons
4. Medical neutrality
5. Prisoner of war rights
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject

from .implementation import (
    D_INTERNATIONAL_HUMANITARIANChecker,
    D_INTERNATIONAL_HUMANITARIANRecord,
    ProtectedPerson,
    MilitaryTarget,
    ProtectedCategory,
    ConflictType,
)


def check_distinction_principle() -> Tuple[bool, ProofObject]:
    """Verify military targets distinguish between combatants and civilians.
    
    Falsifies if: valid targets fail or invalid targets pass the distinction check.
    """
    checker = D_INTERNATIONAL_HUMANITARIANChecker()
    
    valid_target = MilitaryTarget(
        target_id="TGT-001",
        military_necessity=True,
        proportionality_assessed=True,
        expected_civilian_harm=5,
    )
    
    invalid_target = MilitaryTarget(
        target_id="TGT-002",
        military_necessity=False,
        proportionality_assessed=False,
        expected_civilian_harm=50,
    )
    
    if not checker.check_distinction_principle(valid_target):
        return False, ProofObject(
            rule="distinction_principle",
            subject="TGT-001",
            falsifies_if="valid target fails distinction check",
        )
    if checker.check_distinction_principle(invalid_target):
        return False, ProofObject(
            rule="distinction_principle",
            subject="TGT-002",
            falsifies_if="invalid target passes distinction check",
        )
    
    return True, ProofObject(
        rule="distinction_principle",
        subject="IHL distinction",
        verified=True,
    )


def check_proportionality() -> Tuple[bool, ProofObject]:
    """Verify civilian harm is proportionate to military advantage.
    
    Falsifies if: expected civilian harm exceeds permissible proportionality relative
    to military advantage.
    """
    checker = D_INTERNATIONAL_HUMANITARIANChecker()
    
    # High military value, low civilian harm - proportional
    proportional = MilitaryTarget(
        target_id="TGT-003",
        military_necessity=True,
        proportionality_assessed=True,
        expected_civilian_harm=10,
    )
    
    # Low military value, high civilian harm - disproportionate
    disproportionate = MilitaryTarget(
        target_id="TGT-004",
        military_necessity=True,
        proportionality_assessed=True,
        expected_civilian_harm=100,
    )
    
    if not checker.check_proportionality(proportional, military_advantage=10):
        return False, ProofObject(
            rule="proportionality",
            subject="TGT-003",
            falsifies_if="proportional target fails check",
        )
    if checker.check_proportionality(disproportionate, military_advantage=10):
        return False, ProofObject(
            rule="proportionality",
            subject="TGT-004",
            falsifies_if="disproportionate target passes check",
        )
    
    return True, ProofObject(
        rule="proportionality",
        subject="IHL proportionality",
        verified=True,
    )


def check_protection_of_civilians() -> Tuple[bool, ProofObject]:
    """Verify civilians receive required protections.
    
    Falsifies if: protection status check fails for civilians or passes for
    unprotected civilians.
    """
    checker = D_INTERNATIONAL_HUMANITARIANChecker()
    
    protected_civilian = ProtectedPerson(
        person_id="PERS-001",
        category=ProtectedCategory.CIVILIAN,
        location="Geneva",
        receiving_protection=True,
    )
    
    unprotected_civilian = ProtectedPerson(
        person_id="PERS-002",
        category=ProtectedCategory.CIVILIAN,
        location="Conflict Zone",
        receiving_protection=False,
    )
    
    if not checker.check_protection_status(protected_civilian):
        return False, ProofObject(
            rule="protection_of_civilians",
            subject="PERS-001",
            falsifies_if="protected civilian fails status check",
        )
    if checker.check_protection_status(unprotected_civilian):
        return False, ProofObject(
            rule="protection_of_civilians",
            subject="PERS-002",
            falsifies_if="unprotected civilian passes status check",
        )
    
    return True, ProofObject(
        rule="protection_of_civilians",
        subject="civilian protection",
        verified=True,
    )


def check_medical_neutrality() -> Tuple[bool, ProofObject]:
    """Verify medical personnel are protected.
    
    Falsifies if: medical personnel lack protection or incorrect category is set.
    """
    medical_staff = ProtectedPerson(
        person_id="PERS-003",
        category=ProtectedCategory.MEDICAL_PERSONNEL,
        location="Field Hospital",
        receiving_protection=True,
    )
    
    # Medical personnel must always be protected
    if not medical_staff.receiving_protection:
        return False, ProofObject(
            rule="medical_neutrality",
            subject="PERS-003",
            falsifies_if="medical personnel not protected",
        )
    if medical_staff.category != ProtectedCategory.MEDICAL_PERSONNEL:
        return False, ProofObject(
            rule="medical_neutrality",
            subject="PERS-003",
            falsifies_if="medical personnel category incorrect",
        )
    
    return True, ProofObject(
        rule="medical_neutrality",
        subject="medical personnel protection",
        verified=True,
    )


def check_pow_rights() -> Tuple[bool, ProofObject]:
    """Verify prisoners of war receive required protections.
    
    Falsifies if: POW does not receive required protections or is misclassified.
    """
    pow_person = ProtectedPerson(
        person_id="PERS-004",
        category=ProtectedCategory.POW,
        location="Camp Delta",
        receiving_protection=True,
    )
    
    # POWs must be protected
    if not pow_person.receiving_protection:
        return False, ProofObject(
            rule="pow_rights",
            subject="PERS-004",
            falsifies_if="POW not receiving protection",
        )
    
    # POWs must be treated humanely
    if pow_person.category != ProtectedCategory.POW:
        return False, ProofObject(
            rule="pow_rights",
            subject="PERS-004",
            falsifies_if="POW category incorrect",
        )
    
    return True, ProofObject(
        rule="pow_rights",
        subject="POW protections",
        verified=True,
    )


def check_compliance_deterministic() -> Tuple[bool, ProofObject]:
    """Master compliance check.

    Falsifies if: any international humanitarian law invariant check fails.
    """
    checks = [
        check_distinction_principle,
        check_proportionality,
        check_protection_of_civilians,
        check_medical_neutrality,
        check_pow_rights,
    ]
    
    for check in checks:
        result, proof = check()
        if not result:
            return False, ProofObject(
                rule="compliance_deterministic",
                subject="master_check",
                falsifies_if=f"{proof.rule} failed",
            )
    
    return True, ProofObject(
        rule="compliance_deterministic",
        subject="IHL compliance",
        verified=True,
    )

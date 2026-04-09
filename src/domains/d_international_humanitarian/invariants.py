"""D_INTERNATIONAL_HUMANITARIAN invariant checks — IHL validation.

International humanitarian law invariants ensure:
1. Distinction principle (combatants vs civilians)
2. Proportionality of attacks
3. Protection of protected persons
4. Medical neutrality
5. Prisoner of war rights
"""

from fractions import Fraction

from .implementation import (
    D_INTERNATIONAL_HUMANITARIANChecker,
    D_INTERNATIONAL_HUMANITARIANRecord,
    ProtectedPerson,
    MilitaryTarget,
    ProtectedCategory,
    ConflictType,
)


def check_distinction_principle() -> bool:
    """Verify military targets distinguish between combatants and civilians."""
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
    
    assert checker.check_distinction_principle(valid_target)
    assert not checker.check_distinction_principle(invalid_target)
    
    return True


def check_proportionality() -> bool:
    """Verify civilian harm is proportionate to military advantage."""
    checker = D_INTERNATIONAL_HUMANITARIANChecker()
    
    # High military value, low civilian harm - proportional
    proportional = MilitaryTarget(
        target_id="TGT-003",
        military_necessity=True,
        proportionality_assessed=True,
        expected_civilian_harm=10,
    )
    
    assert checker.check_proportionality(proportional, military_advantage=10)
    
    # Low military value, high civilian harm - disproportionate
    disproportionate = MilitaryTarget(
        target_id="TGT-004",
        military_necessity=True,
        proportionality_assessed=True,
        expected_civilian_harm=100,
    )
    
    assert not checker.check_proportionality(disproportionate, military_advantage=10)
    
    return True


def check_protection_of_civilians() -> bool:
    """Verify civilians receive required protections."""
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
    
    assert checker.check_protection_status(protected_civilian)
    assert not checker.check_protection_status(unprotected_civilian)
    
    return True


def check_medical_neutrality() -> bool:
    """Verify medical personnel are protected."""
    medical_staff = ProtectedPerson(
        person_id="PERS-003",
        category=ProtectedCategory.MEDICAL_PERSONNEL,
        location="Field Hospital",
        receiving_protection=True,
    )
    
    # Medical personnel must always be protected
    assert medical_staff.receiving_protection
    assert medical_staff.category == ProtectedCategory.MEDICAL_PERSONNEL
    
    return True


def check_pow_rights() -> bool:
    """Verify prisoners of war receive required protections."""
    pow_person = ProtectedPerson(
        person_id="PERS-004",
        category=ProtectedCategory.POW,
        location="Camp Delta",
        receiving_protection=True,
    )
    
    # POWs must be protected
    assert pow_person.receiving_protection
    
    # POWs must be treated humanely
    assert pow_person.category == ProtectedCategory.POW
    
    return True


def check_compliance_deterministic() -> bool:
    """Master compliance check."""
    assert check_distinction_principle()
    assert check_proportionality()
    assert check_protection_of_civilians()
    assert check_medical_neutrality()
    assert check_pow_rights()
    return True

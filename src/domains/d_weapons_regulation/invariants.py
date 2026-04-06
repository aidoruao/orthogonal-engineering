"""D_WEAPONS_REGULATION invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: GCA (18 U.S.C. §922), NFA (26 U.S.C. §5801), Brady Act
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_weapons_regulation.implementation import (
    NICSBackgroundCheckSystem,
    NFAComplianceChecker,
    StatePreemptionAnalyzer,
    FirearmsComplianceEnforcer,
    Firearm,
    Person,
    FFLDealer,
    NICSCheck,
    FirearmTransfer,
    FirearmType,
    FirearmCategory,
    DisqualifierType,
    TransferType,
    NICSResult,
)


def check_prohibited_person_cannot_purchase() -> bool:
    """
    Invariant: Prohibited person cannot purchase firearms.
    Falsification: If felon passes NICS check.
    """
    nics = NICSBackgroundCheckSystem()
    
    # Prohibited person (felon)
    felon = Person(
        person_id="P001",
        name="Convicted Felon",
        date_of_birth=datetime.now() - timedelta(days=365*35),
        citizenship="US",
        state_of_residence="Texas",
        disqualifiers={DisqualifierType.FELONY_CONVICTION},
    )
    
    result = nics.check_prohibited_status(felon)
    assert result["prohibited"] is True, (
        "Felon should be prohibited"
    )
    assert result["nics_result"] == NICSResult.DENY, (
        "Felon should receive DENY response"
    )
    assert "Felony conviction" in result["prohibitors"], (
        "Should list felony as prohibitor"
    )
    
    # Non-prohibited person
    law_abiding = Person(
        person_id="P002",
        name="Law Abiding Citizen",
        date_of_birth=datetime.now() - timedelta(days=365*35),
        citizenship="US",
        state_of_residence="Texas",
        disqualifiers=set(),
    )
    
    result2 = nics.check_prohibited_status(law_abiding)
    assert result2["prohibited"] is False, (
        "Law-abiding citizen should not be prohibited"
    )
    assert result2["nics_result"] == NICSResult.PROCEED, (
        "Law-abiding citizen should receive PROCEED"
    )
    
    return True


def check_nfa_items_require_registration() -> bool:
    """
    Invariant: NFA items require registration and tax stamp.
    Falsification: If unregistered machine gun passes compliance.
    """
    checker = NFAComplianceChecker()
    
    # Registered NFA item
    registered_sbr = Firearm(
        firearm_id="F001",
        serial_number="ABC123",
        manufacturer="NFA Co",
        model="Short Rifle",
        firearm_type=FirearmType.SHORT_BARRELED_RIFLE,
        category=FirearmCategory.TITLE_II_NFA,
        nfa_registered=True,
        nfa_tax_stamp_number="STAMP001",
        barrel_length_inches=10.5,
        overall_length_inches=24.0,
    )
    
    result = checker.check_nfa_registration(registered_sbr)
    assert result["nfa_item"] is True, (
        "SBR should be recognized as NFA item"
    )
    assert result["registered"] is True, (
        "Registered SBR should show as registered"
    )
    
    # Unregistered NFA item
    unregistered_sbr = Firearm(
        firearm_id="F002",
        serial_number="DEF456",
        manufacturer="NFA Co",
        model="Illegal Short Rifle",
        firearm_type=FirearmType.SHORT_BARRELED_RIFLE,
        category=FirearmCategory.TITLE_II_NFA,
        nfa_registered=False,
        barrel_length_inches=10.5,
    )
    
    result2 = checker.check_nfa_registration(unregistered_sbr)
    assert result2["registered"] is False, (
        "Unregistered SBR should show as unregistered"
    )
    assert "violation" in result2, (
        "Unregistered NFA item should be flagged as violation"
    )
    
    # Title I firearm (not NFA)
    regular_rifle = Firearm(
        firearm_id="F003",
        serial_number="GHI789",
        manufacturer="Regular Co",
        model="Standard Rifle",
        firearm_type=FirearmType.RIFLE,
        category=FirearmCategory.TITLE_I,
        barrel_length_inches=16.0,
    )
    
    result3 = checker.check_nfa_registration(regular_rifle)
    assert result3["nfa_item"] is False, (
        "Regular rifle should not be NFA item"
    )
    
    return True


def check_background_check_required_for_ffl_sales() -> bool:
    """
    Invariant: FFL sales require NICS background check.
    Falsification: If FFL sale without NICS check passes compliance.
    """
    enforcer = FirearmsComplianceEnforcer()
    
    # Compliant FFL sale with NICS
    compliant_sale = FirearmTransfer(
        transfer_id="T001",
        firearm_id="F001",
        transferor_id="FFL001",
        transferee_id="P002",
        transfer_date=datetime.now(),
        transfer_type=TransferType.FFL_SALE,
        ffl_involved=True,
        ffl_number="01-123-45-6B-78901",
        nics_ntn="NTN123456",
        nics_result=NICSResult.PROCEED,
    )
    
    result = enforcer.analyze_transfer_compliance(compliant_sale)
    assert result["compliant"] is True, (
        "FFL sale with NICS should be compliant"
    )
    assert result["nics_check_documented"] is True, (
        "Should document NICS check"
    )
    
    # Non-compliant FFL sale without NICS
    noncompliant_sale = FirearmTransfer(
        transfer_id="T002",
        firearm_id="F001",
        transferor_id="FFL001",
        transferee_id="P002",
        transfer_date=datetime.now(),
        transfer_type=TransferType.FFL_SALE,
        ffl_involved=True,
        ffl_number="01-123-45-6B-78901",
        nics_ntn=None,  # Missing NICS
    )
    
    result2 = enforcer.analyze_transfer_compliance(noncompliant_sale)
    assert result2["compliant"] is False, (
        "FFL sale without NICS should be non-compliant"
    )
    assert result2["nics_check_documented"] is False, (
        "Should flag missing NICS check"
    )
    
    return True


def check_nfa_tax_amount() -> bool:
    """
    Invariant: NFA transfer tax is $200 (or $5 for AOW).
    Falsification: If incorrect tax amount calculated.
    """
    checker = NFAComplianceChecker()
    
    # Standard NFA tax
    sbr_tax = checker.calculate_nfa_tax(FirearmType.SHORT_BARRELED_RIFLE)
    assert sbr_tax == Fraction(200), (
        "SBR tax should be $200"
    )
    
    machine_gun_tax = checker.calculate_nfa_tax(FirearmType.MACHINE_GUN)
    assert machine_gun_tax == Fraction(200), (
        "Machine gun tax should be $200"
    )
    
    # AOW lower tax
    aow_tax = checker.calculate_nfa_tax(FirearmType.ANY_OTHER_WEAPON)
    assert aow_tax == Fraction(5), (
        "AOW tax should be $5"
    )
    
    return True


def check_domestic_violence_prohibition() -> bool:
    """
    Invariant: Domestic violence conviction prohibits firearm possession.
    Falsification: If DV misdemeanant passes NICS check.
    """
    nics = NICSBackgroundCheckSystem()
    
    # Person with DV misdemeanor (Lautenberg Amendment)
    dv_offender = Person(
        person_id="P003",
        name="DV Offender",
        date_of_birth=datetime.now() - timedelta(days=365*30),
        citizenship="US",
        state_of_residence="Florida",
        disqualifiers={DisqualifierType.DOMESTIC_VIOLENCE_MISDEMEANOR},
        dv_convictions=[{"date": datetime.now() - timedelta(days=365), "offense": "Simple assault"}],
    )
    
    result = nics.check_prohibited_status(dv_offender)
    assert result["prohibited"] is True, (
        "DV misdemeanant should be prohibited (Lautenberg Amendment)"
    )
    assert "Domestic violence misdemeanor" in result["prohibitors"], (
        "Should list DV misdemeanor as prohibitor"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("prohibited_person", check_prohibited_person_cannot_purchase),
        ("nfa_registration", check_nfa_items_require_registration),
        ("ffl_background_check", check_background_check_required_for_ffl_sales),
        ("nfa_tax", check_nfa_tax_amount),
        ("dv_prohibition", check_domestic_violence_prohibition),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results

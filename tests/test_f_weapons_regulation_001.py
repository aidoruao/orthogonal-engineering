"""Tests for d_weapons_regulation domain."""

from datetime import datetime, timedelta
from fractions import Fraction

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
    check_prohibited_person,
    check_nfa_item,
    check_private_sale_requirements,
)


def test_prohibited_person_felon():
    """Test that felon is prohibited from possessing firearms."""
    nics = NICSBackgroundCheckSystem()
    
    felon = Person(
        person_id="P001",
        name="Felon",
        date_of_birth=datetime.now() - timedelta(days=365*35),
        citizenship="US",
        state_of_residence="Texas",
        disqualifiers={DisqualifierType.FELONY_CONVICTION},
    )
    
    result = nics.check_prohibited_status(felon)
    assert result["prohibited"] is True
    assert result["nics_result"] == NICSResult.DENY


def test_non_prohibited_person():
    """Test that law-abiding citizen is not prohibited."""
    nics = NICSBackgroundCheckSystem()
    
    citizen = Person(
        person_id="P002",
        name="Citizen",
        date_of_birth=datetime.now() - timedelta(days=365*35),
        citizenship="US",
        state_of_residence="Texas",
        disqualifiers=set(),
    )
    
    result = nics.check_prohibited_status(citizen)
    assert result["prohibited"] is False
    assert result["nics_result"] == NICSResult.PROCEED


def test_nfa_registered_item():
    """Test NFA registered item compliance."""
    checker = NFAComplianceChecker()
    
    sbr = Firearm(
        firearm_id="F001",
        serial_number="ABC123",
        manufacturer="NFA Co",
        model="SBR",
        firearm_type=FirearmType.SHORT_BARRELED_RIFLE,
        category=FirearmCategory.TITLE_II_NFA,
        nfa_registered=True,
        nfa_tax_stamp_number="STAMP001",
    )
    
    result = checker.check_nfa_registration(sbr)
    assert result["nfa_item"] is True
    assert result["registered"] is True


def test_nfa_unregistered_item():
    """Test unregistered NFA item flagged as violation."""
    checker = NFAComplianceChecker()
    
    sbr = Firearm(
        firearm_id="F002",
        serial_number="DEF456",
        manufacturer="NFA Co",
        model="SBR",
        firearm_type=FirearmType.SHORT_BARRELED_RIFLE,
        category=FirearmCategory.TITLE_II_NFA,
        nfa_registered=False,
    )
    
    result = checker.check_nfa_registration(sbr)
    assert result["registered"] is False
    assert "violation" in result


def test_title_i_firearm_not_nfa():
    """Test that regular firearms are not NFA items."""
    checker = NFAComplianceChecker()
    
    rifle = Firearm(
        firearm_id="F003",
        serial_number="GHI789",
        manufacturer="Regular Co",
        model="Rifle",
        firearm_type=FirearmType.RIFLE,
        category=FirearmCategory.TITLE_I,
    )
    
    result = checker.check_nfa_registration(rifle)
    assert result["nfa_item"] is False


def test_ffl_sale_compliance():
    """Test FFL sale compliance check."""
    enforcer = FirearmsComplianceEnforcer()
    
    compliant = FirearmTransfer(
        transfer_id="T001",
        firearm_id="F001",
        transferor_id="FFL001",
        transferee_id="P002",
        transfer_date=datetime.now(),
        transfer_type=TransferType.FFL_SALE,
        ffl_involved=True,
        nics_ntn="NTN123",
        nics_result=NICSResult.PROCEED,
    )
    
    result = enforcer.analyze_transfer_compliance(compliant)
    assert result["compliant"] is True


def test_nfa_tax_calculation():
    """Test NFA tax calculation."""
    checker = NFAComplianceChecker()
    
    sbr_tax = checker.calculate_nfa_tax(FirearmType.SHORT_BARRELED_RIFLE)
    assert sbr_tax == Fraction(200)
    
    aow_tax = checker.calculate_nfa_tax(FirearmType.ANY_OTHER_WEAPON)
    assert aow_tax == Fraction(5)


def test_dv_prohibition():
    """Test domestic violence misdemeanor prohibition."""
    nics = NICSBackgroundCheckSystem()
    
    dv_offender = Person(
        person_id="P003",
        name="DV Offender",
        date_of_birth=datetime.now() - timedelta(days=365*30),
        citizenship="US",
        state_of_residence="Florida",
        disqualifiers={DisqualifierType.DOMESTIC_VIOLENCE_MISDEMEANOR},
    )
    
    result = nics.check_prohibited_status(dv_offender)
    assert result["prohibited"] is True
    assert "Domestic violence misdemeanor" in result["prohibitors"]


def test_convenience_function_prohibited():
    """Test convenience function for prohibited person check."""
    result = check_prohibited_person(True, False)
    assert result["prohibited"] is True
    
    result2 = check_prohibited_person(False, False)
    assert result2["prohibited"] is False


def test_convenience_function_nfa_item():
    """Test convenience function for NFA item check."""
    result = check_nfa_item(10.5, 24.0)  # Short barrel
    assert result["nfa_item"] is True
    
    result2 = check_nfa_item(16.0, 30.0)  # Normal rifle
    assert result2["nfa_item"] is False


def test_convenience_function_private_sale():
    """Test convenience function for private sale requirements."""
    result = check_private_sale_requirements("California")
    assert result["background_check_required"] is True
    
    result2 = check_private_sale_requirements("Texas")
    assert result2["background_check_required"] is False

"""Falsification tests for D_CIVIL_LAW"""
from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_civil_law import (
    CivilLaw,
    TortType,
    DutyBreachCausationDamages,
    StatuteOfLimitations,
)


def test_tort_elements_chain_incomplete():
    """Claim fails when duty-breach-causation-damages chain incomplete."""
    law = CivilLaw()
    incident_date = datetime.now() - timedelta(days=100)
    filing_date = datetime.now()
    
    claim = law.file_claim(
        claim_id="C001",
        plaintiff="P",
        defendant="D",
        tort_type=TortType.NEGLIGENCE,
        incident_date=incident_date,
        filing_date=filing_date,
        duty_description="Driver owes duty of care",
        breach_description="",  # Missing breach
        causation_description="Breach caused accident",
        damages_amount=Fraction(50000),
    )
    
    result = law.adjudicate_claim("C001")
    assert result["verdict"] == "DISMISSED"
    assert "breach" in str(result["reason"]).lower() or "elements" in str(result["reason"]).lower()


def test_statute_of_limitations_expired():
    """Claim dismissed when statute of limitations expired."""
    law = CivilLaw()
    incident_date = datetime.now() - timedelta(days=3 * 365)  # 3 years ago
    filing_date = datetime.now()  # Filed now (beyond 2-year limit)
    
    claim = law.file_claim(
        claim_id="C002",
        plaintiff="P",
        defendant="D",
        tort_type=TortType.NEGLIGENCE,
        incident_date=incident_date,
        filing_date=filing_date,
        duty_description="Doctor owes duty",
        breach_description="Failed to diagnose",
        causation_description="Delay caused harm",
        damages_amount=Fraction(100000),
    )
    
    result = law.adjudicate_claim("C002")
    assert result["verdict"] == "DISMISSED"
    assert "statute" in result["reason"].lower()


def test_valid_claim_liable_verdict():
    """Valid claim with all elements returns LIABLE verdict."""
    law = CivilLaw()
    incident_date = datetime.now() - timedelta(days=100)
    filing_date = datetime.now()
    
    claim = law.file_claim(
        claim_id="C003",
        plaintiff="P",
        defendant="D",
        tort_type=TortType.NEGLIGENCE,
        incident_date=incident_date,
        filing_date=filing_date,
        duty_description="Property owner owes duty to visitors",
        breach_description="Failed to repair broken stairs",
        causation_description="Visitor fell due to broken stairs",
        damages_amount=Fraction(75000),
    )
    
    result = law.adjudicate_claim("C003")
    assert result["verdict"] == "LIABLE"
    assert result["damages"] == Fraction(75000)


def test_duty_breach_causation_damages_all_required():
    """All four elements required for liability."""
    elements = DutyBreachCausationDamages(
        duty_exists=True,
        breach_occurred=True,
        causation_exists=True,
        damages_amount=Fraction(0),  # No damages
    )
    assert not elements.is_liable()
    
    elements.damages_amount = Fraction(1000)
    assert elements.is_liable()


if __name__ == "__main__":
    test_tort_elements_chain_incomplete()
    test_statute_of_limitations_expired()
    test_valid_claim_liable_verdict()
    test_duty_breach_causation_damages_all_required()
    print("All D_CIVIL_LAW tests: PASS")

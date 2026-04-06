"""D_CIVIL_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Common law torts, statutory limitations
"""

from datetime import datetime, timedelta
from fractions import Fraction
from src.domains.d_civil_law.implementation import (
    CivilLaw,
    TortClaim,
    TortType,
    DutyBreachCausationDamages,
    StatuteOfLimitations,
    check_statute_of_limitations,
)


def check_duty_breach_causation_damages_chain() -> bool:
    """
    Invariant: Duty → Breach → Causation → Damages chain must be complete.
    Falsification: If liability found with incomplete chain.
    """
    law = CivilLaw()
    
    # File claim with incomplete chain (no causation)
    claim = law.file_claim(
        claim_id="INCOMPLETE-001",
        plaintiff="Plaintiff A",
        defendant="Defendant A",
        tort_type=TortType.NEGLIGENCE,
        incident_date=datetime.now() - timedelta(days=100),
        filing_date=datetime.now(),
        duty_description="Duty to drive safely",
        breach_description="Ran red light",
        causation_description="",  # Missing causation
        damages_amount=Fraction(10000),
    )
    
    result = law.adjudicate_claim("INCOMPLETE-001")
    
    assert result["verdict"] == "DISMISSED", (
        "Claim with incomplete chain should be dismissed"
    )
    assert "causation" in result["reason"].lower() or "elements" in result["reason"].lower()
    
    return True


def check_statute_of_limitations_enforced() -> bool:
    """
    Invariant: Statute of limitations is enforced with filing date.
    Falsification: If untimely claim is not dismissed.
    """
    law = CivilLaw()
    
    # File claim beyond statute of limitations
    old_incident = datetime.now() - timedelta(days=3 * 365)  # 3 years ago
    recent_filing = datetime.now()
    
    claim = law.file_claim(
        claim_id="UNTIERMLY-001",
        plaintiff="Plaintiff B",
        defendant="Defendant B",
        tort_type=TortType.NEGLIGENCE,  # 2 year limit
        incident_date=old_incident,
        filing_date=recent_filing,
        duty_description="Duty to maintain safe premises",
        breach_description="Failed to repair broken step",
        causation_description="Plaintiff fell due to broken step",
        damages_amount=Fraction(50000),
    )
    
    result = law.adjudicate_claim("UNTIERMLY-001")
    
    assert result["verdict"] == "DISMISSED", (
        "Untimely claim should be dismissed"
    )
    assert "statute of limitations" in result["reason"].lower()
    
    return True


def check_timely_claim_allowed() -> bool:
    """
    Invariant: Timely claim with complete chain is allowed.
    Falsification: If valid claim is dismissed.
    """
    law = CivilLaw()
    
    claim = law.file_claim(
        claim_id="VALID-001",
        plaintiff="Plaintiff C",
        defendant="Defendant C",
        tort_type=TortType.NEGLIGENCE,
        incident_date=datetime.now() - timedelta(days=100),
        filing_date=datetime.now(),
        duty_description="Duty to drive safely",
        breach_description="Ran red light",
        causation_description="Collision caused by running red light",
        damages_amount=Fraction(25000),
    )
    
    result = law.adjudicate_claim("VALID-001")
    
    assert result["verdict"] == "LIABLE", (
        "Valid claim should result in liability"
    )
    assert result["damages"] == Fraction(25000)
    
    return True


def check_damages_required_for_liability() -> bool:
    """
    Invariant: Damages are required for tort liability.
    Falsification: If liability without damages.
    """
    elements = DutyBreachCausationDamages(
        duty_exists=True,
        duty_description="Duty existed",
        breach_occurred=True,
        breach_description="Breach occurred",
        causation_exists=True,
        causation_description="Causation established",
        damages_amount=Fraction(0),  # No damages
    )
    
    assert elements.is_liable() is False, (
        "Should not be liable without damages"
    )
    
    return True


def check_functorial_chain_complete() -> bool:
    """
    Invariant: Functorial chain is functorial (all or nothing).
    Falsification: If partial chain results in liability.
    """
    # Complete chain
    complete = DutyBreachCausationDamages(
        duty_exists=True,
        breach_occurred=True,
        causation_exists=True,
        damages_amount=Fraction(1000),
    )
    assert complete.is_liable() is True
    
    # Missing one element
    incomplete = DutyBreachCausationDamages(
        duty_exists=True,
        breach_occurred=True,
        causation_exists=False,
        damages_amount=Fraction(1000),
    )
    assert incomplete.is_liable() is False
    
    return True


def check_intentional_tort_shorter_limitations() -> bool:
    """
    Invariant: Intentional torts have shorter limitations periods.
    Falsification: If intentional and negligence have same period.
    """
    statute_intentional = StatuteOfLimitations(
        tort_type=TortType.INTENTIONAL,
        incident_date=datetime.now() - timedelta(days=400),
        filing_date=datetime.now(),
    )
    
    statute_negligence = StatuteOfLimitations(
        tort_type=TortType.NEGLIGENCE,
        incident_date=datetime.now() - timedelta(days=400),
        filing_date=datetime.now(),
    )
    
    # Intentional (1 year) should be expired; Negligence (2 years) should be valid
    assert statute_intentional.is_timely() is False
    assert statute_negligence.is_timely() is True
    
    return True


def check_statute_function() -> bool:
    """
    Invariant: Statute of limitations function works correctly.
    Falsification: If function returns wrong result.
    """
    incident = datetime(2020, 1, 1)
    
    # Timely filing
    timely = datetime(2021, 1, 1)
    assert check_statute_of_limitations(incident, timely, 2) is True
    
    # Untimely filing
    untimely = datetime(2023, 1, 1)
    assert check_statute_of_limitations(incident, untimely, 2) is False
    
    return True


def run_all_invariants() -> dict:
    """Run all D_CIVIL_LAW invariants."""
    checks = [
        check_duty_breach_causation_damages_chain,
        check_statute_of_limitations_enforced,
        check_timely_claim_allowed,
        check_damages_required_for_liability,
        check_functorial_chain_complete,
        check_intentional_tort_shorter_limitations,
        check_statute_function,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_CIVIL_LAW invariants: PASS")

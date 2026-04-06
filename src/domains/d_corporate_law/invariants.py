"""D_CORPORATE_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Delaware General Corporation Law (DGCL), Model Business Corporation Act (MBCA)
"""

from src.domains.d_corporate_law.implementation import (
    FiduciaryDutyAnalyzer,
    CorporateVeilAnalyzer,
    Director,
    CorporateTransaction,
    Shareholder,
    check_self_dealing,
)
from fractions import Fraction


def check_self_dealing_requires_disclosure() -> bool:
    """
    Invariant: Self-dealing transactions require full disclosure.
    Falsification: If undisclosed self-dealing is approved.
    """
    analyzer = FiduciaryDutyAnalyzer()
    
    director = Director(
        name="Conflicted Director",
        director_id="D001",
        financial_interests={"Target Corp": Fraction(100)},
    )
    
    transaction = CorporateTransaction(
        transaction_id="T001",
        description="Acquisition",
        counterparty="Target Corp",
        value=Fraction(1_000_000),
        directors_involved=[director],
        disclosure_complete=False,  # No disclosure!
        approved_by_disinterested=True,
    )
    
    result = analyzer.check_self_dealing_compliance(transaction)
    
    assert not result.get("safe_harbor"), (
        "Self-dealing without disclosure should not qualify for safe harbor"
    )
    
    return True


def check_disinterested_director_approval_safe_harbor() -> bool:
    """
    Invariant: Disinterested director approval creates DGCL §144 safe harbor.
    Falsification: If approved disclosed self-dealing doesn't get safe harbor.
    """
    result = check_self_dealing(
        director_name="Director",
        counterparty="Related LLC",
        transaction_value=Fraction(500_000),
        director_has_interest=True,
        approved_by_disinterested=True,
        full_disclosure=True,
    )
    
    assert result.get("safe_harbor") == "DGCL_144_a", (
        "Disinterested director approval with disclosure should create safe harbor"
    )
    
    return True


def check_duty_of_loyalty_prevents_self_dealing() -> bool:
    """
    Invariant: Duty of loyalty prevents undisclosed self-dealing.
    Falsification: If undisclosed self-dealing passes duty of loyalty check.
    """
    analyzer = FiduciaryDutyAnalyzer()
    
    director = Director(
        name="Director",
        director_id="D001",
        financial_interests={"Counterparty": Fraction(50)},
    )
    
    transaction = CorporateTransaction(
        transaction_id="T001",
        description="Sale",
        counterparty="Counterparty",
        value=Fraction(2_000_000),
        directors_involved=[director],
        disclosure_complete=False,
        approved_by_disinterested=False,
    )
    
    result = analyzer.analyze_duty_of_loyalty(transaction)
    
    assert not result["compliant"], (
        "Undisclosed self-dealing should violate duty of loyalty"
    )
    assert "Self-dealing without full disclosure" in result["issues"], (
        "Should flag disclosure issue"
    )
    
    return True


def check_corporate_veil_piercing_factors_cumulative() -> bool:
    """
    Invariant: More veil-piercing factors increases piercing risk.
    Falsification: If fewer factors produces higher risk assessment.
    """
    analyzer = CorporateVeilAnalyzer()
    
    shareholder = Shareholder(name="Owner", shares_owned=100, total_shares_outstanding=100)
    
    # Low risk (1 factor)
    low_risk = analyzer.analyze_veil_piercing_risk(
        corporation="Corp1",
        shareholder=shareholder,
        commingling_of_funds=True,
    )
    
    # High risk (4 factors)
    high_risk = analyzer.analyze_veil_piercing_risk(
        corporation="Corp2",
        shareholder=shareholder,
        commingling_of_funds=True,
        inadequate_capitalization=True,
        failure_to_follow_formalities=True,
        siphoning_of_funds=True,
    )
    
    assert high_risk["factors_present"] > low_risk["factors_present"], (
        "More factors should increase factor count"
    )
    assert high_risk["piercing_likely"], (
        "Multiple factors should make piercing likely"
    )
    
    return True


def check_ownership_percentage_calculation() -> bool:
    """
    Invariant: Ownership percentage equals shares owned / total outstanding.
    Falsification: If ownership calculation is incorrect.
    """
    shareholder = Shareholder(
        name="Majority Owner",
        shares_owned=60,
        total_shares_outstanding=100,
    )
    
    expected = Fraction(60, 100)
    assert shareholder.ownership_percentage == expected, (
        f"Ownership should be {expected}, got {shareholder.ownership_percentage}"
    )
    
    return True


def check_controlling_interest_threshold() -> bool:
    """
    Invariant: 50% ownership creates controlling interest.
    Falsification: If 50.1% owner not recognized as controlling.
    """
    shareholder = Shareholder(
        name="Controller",
        shares_owned=501,
        total_shares_outstanding=1000,
    )
    
    assert shareholder.is_controlling(), (
        f"50.1% owner should be controlling, got {shareholder.ownership_percentage}"
    )
    
    # 49% should not be controlling
    minority = Shareholder(
        name="Minority",
        shares_owned=49,
        total_shares_outstanding=100,
    )
    
    assert not minority.is_controlling(), (
        "49% owner should not be controlling"
    )
    
    return True


def check_duty_of_care_requires_information() -> bool:
    """
    Invariant: Duty of care requires board be informed.
    Falsification: If uninformed board decision passes duty of care.
    """
    analyzer = FiduciaryDutyAnalyzer()
    
    transaction = CorporateTransaction(
        transaction_id="T001",
        description="Major acquisition",
        counterparty="Target",
        value=Fraction(50_000_000),
        directors_involved=[],
    )
    
    result = analyzer.analyze_duty_of_care(
        transaction=transaction,
        board_informed=False,  # Not informed!
        decision_documented=False,
    )
    
    assert not result["compliant"], (
        "Uninformed decision should violate duty of care"
    )
    assert "Board not adequately informed" in result["issues"], (
        "Should flag lack of information"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_CORPORATE_LAW invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_self_dealing_requires_disclosure,
        check_disinterested_director_approval_safe_harbor,
        check_duty_of_loyalty_prevents_self_dealing,
        check_corporate_veil_piercing_factors_cumulative,
        check_ownership_percentage_calculation,
        check_controlling_interest_threshold,
        check_duty_of_care_requires_information,
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
    print("All D_CORPORATE_LAW invariants: PASS")

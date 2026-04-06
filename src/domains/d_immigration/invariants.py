"""D_IMMIGRATION invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Immigration and Nationality Act (INA) 8 U.S.C. §1101 et seq.
"""

from src.domains.d_immigration.implementation import (
    VisaPreferenceSystem,
    AsylumAnalyzer,
    RemovalDefenseAnalyzer,
    Alien,
    AsylumClaim,
    VisaApplication,
    VisaCategory,
    AdmissionClass,
    check_visa_category_eligibility,
)
from datetime import date, timedelta
from fractions import Fraction


def check_asylum_requires_protected_nexus() -> bool:
    """
    Invariant: Asylum requires nexus to race, religion, nationality, political opinion, or PSG.
    Falsification: If asylum granted without protected nexus.
    """
    analyzer = AsylumAnalyzer()
    
    alien = Alien(
        name="Claimant",
        alien_id="A001",
        nationality="Elbonia",
        date_of_birth=date(1990, 1, 1),
        date_of_entry=date(2023, 1, 1),
    )
    
    claim = AsylumClaim(
        claimant=alien,
        claim_date=date(2023, 6, 1),  # Within 1 year
        feared_country="Elbonia",
    )
    
    # Claim with protected nexus
    claim.add_persecution_claim(
        harm="Imprisonment",
        nexus="political opinion",
        government_involvement=True,
    )
    
    assert claim.has_protected_nexus(), (
        "Claim with political opinion nexus should have protected nexus"
    )
    
    # Claim without protected nexus
    claim2 = AsylumClaim(
        claimant=alien,
        claim_date=date(2023, 6, 1),
        feared_country="Elbonia",
    )
    claim2.add_persecution_claim(
        harm="Robbery",
        nexus="general crime",
        government_involvement=False,
    )
    
    assert not claim2.has_protected_nexus(), (
        "General crime claim should not have protected nexus"
    )
    
    return True


def check_asylum_filing_deadline_one_year() -> bool:
    """
    Invariant: Asylum must be filed within one year of entry (with exceptions).
    Falsification: If claim filed after 1 year without exception passes.
    """
    alien = Alien(
        name="Late Filer",
        alien_id="A001",
        nationality="Elbonia",
        date_of_birth=date(1990, 1, 1),
        date_of_entry=date(2020, 1, 1),  # 3+ years ago
    )
    
    claim = AsylumClaim(
        claimant=alien,
        claim_date=date(2024, 1, 1),  # Way past deadline
        feared_country="Elbonia",
    )
    
    assert not claim.meets_filing_deadline(), (
        "Claim filed 4 years after entry should miss deadline"
    )
    
    # On-time filing
    alien2 = Alien(
        name="Timely Filer",
        alien_id="A002",
        nationality="Elbonia",
        date_of_birth=date(1990, 1, 1),
        date_of_entry=date(2023, 6, 1),
    )
    
    claim2 = AsylumClaim(
        claimant=alien2,
        claim_date=date(2023, 8, 1),  # Within 1 year
        feared_country="Elbonia",
    )
    
    assert claim2.meets_filing_deadline(), (
        "Claim filed 2 months after entry should meet deadline"
    )
    
    return True


def check_visa_allocation_family_plus_employment() -> bool:
    """
    Invariant: Family-sponsored and employment-based visas have defined allocations.
    Falsification: If visa category has zero or negative allocation.
    """
    system = VisaPreferenceSystem()
    
    # Family categories should have allocations
    f1_allocation = system.get_category_allocation(VisaCategory.F1_FAMILY)
    assert f1_allocation > 0, (
        f"F1 category should have positive allocation, got {f1_allocation}"
    )
    
    # Employment categories should have allocations
    eb1_allocation = system.get_category_allocation(VisaCategory.EB1)
    assert eb1_allocation > 0, (
        f"EB1 category should have positive allocation, got {eb1_allocation}"
    )
    
    return True


def check_per_country_limit_7_percent() -> bool:
    """
    Invariant: Per-country visa limit is approximately 7% of total.
    Falsification: If per-country limit calculation differs from 7%.
    """
    system = VisaPreferenceSystem()
    
    category = VisaCategory.F1_FAMILY
    total = system.get_category_allocation(category)
    country_limit = system.get_country_limit(category)
    
    expected = int(total * Fraction(7, 100))
    assert country_limit == expected, (
        f"Country limit {country_limit} != expected {expected}"
    )
    
    return True


def check_cancellation_requires_continuous_presence() -> bool:
    """
    Invariant: Cancellation of removal requires continuous physical presence.
    Falsification: If insufficient presence qualifies for cancellation.
    """
    analyzer = RemovalDefenseAnalyzer()
    
    alien = Alien(
        name="Applicant",
        alien_id="A001",
        nationality="Elbonia",
        date_of_birth=date(1980, 1, 1),
        admission_class=AdmissionClass.NONIMMIGRANT,
    )
    
    # Non-LPR cancellation requires 10 years
    result = analyzer.analyze_cancellation_eligibility(
        alien=alien,
        years_residence=5,  # Only 5 years - insufficient
        good_moral_character=True,
        exceptional_hardship=True,
    )
    
    assert not result["eligible"], (
        "5 years residence should not qualify for cancellation"
    )
    assert "continuous_presence_10" in result["requirements_failed"], (
        "Should fail on continuous presence requirement"
    )
    
    return True


def check_due_process_rights_in_removal() -> bool:
    """
    Invariant: Aliens in removal proceedings have due process rights.
    Falsification: If removal proceedings don't include due process protections.
    """
    analyzer = RemovalDefenseAnalyzer()
    
    alien = Alien(
        name="Respondent",
        alien_id="A001",
        nationality="Elbonia",
        date_of_birth=date(1985, 1, 1),
    )
    
    rights = analyzer.check_due_process_rights(alien, proceedings_pending=True)
    
    assert rights["hearing_rights"]["right_to_hearing"], (
        "Must have right to hearing"
    )
    assert rights["hearing_rights"]["right_to_counsel"], (
        "Must have right to counsel"
    )
    assert rights["hearing_rights"]["right_to_present_evidence"], (
        "Must have right to present evidence"
    )
    
    return True


def check_family_based_categories_recognized() -> bool:
    """
    Invariant: Family-sponsored visa categories are properly identified.
    Falsification: If family categories not recognized as family-based.
    """
    dummy_alien = Alien(
        name="Applicant",
        alien_id="A001",
        nationality="Elbonia",
        date_of_birth=date(1990, 1, 1),
    )
    
    family_categories = [
        VisaCategory.F1_FAMILY,
        VisaCategory.F2A,
        VisaCategory.F2B,
        VisaCategory.F3_FAMILY,
        VisaCategory.F4_FAMILY,
    ]
    
    for category in family_categories:
        app = VisaApplication(
            application_id="APP001",
            applicant=dummy_alien,
            visa_category=category,
        )
        assert app.is_family_based(), (
            f"{category.name} should be family-based"
        )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_IMMIGRATION invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_asylum_requires_protected_nexus,
        check_asylum_filing_deadline_one_year,
        check_visa_allocation_family_plus_employment,
        check_per_country_limit_7_percent,
        check_cancellation_requires_continuous_presence,
        check_due_process_rights_in_removal,
        check_family_based_categories_recognized,
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
    print("All D_IMMIGRATION invariants: PASS")

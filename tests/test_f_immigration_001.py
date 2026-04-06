"""Falsification tests for D_IMMIGRATION"""
from fractions import Fraction
from datetime import date, timedelta
from src.domains.d_immigration import (
    VisaPreferenceSystem,
    AsylumAnalyzer,
    Alien,
    VisaApplication,
    AsylumClaim,
    VisaCategory,
    AdmissionClass,
    check_visa_category_eligibility,
)


def test_asylum_requires_protected_nexus():
    """Asylum claim requires nexus to protected ground."""
    analyzer = AsylumAnalyzer()
    
    alien = Alien(
        name="Claimant",
        alien_id="A001",
        nationality="Elbonia",
        date_of_birth=date(1990, 1, 1),
    )
    
    claim = AsylumClaim(
        claimant=alien,
        claim_date=date.today(),
        feared_country="Elbonia",
    )
    
    # Add claim without protected nexus
    claim.add_persecution_claim(
        harm="Property damage",
        nexus="economic dispute",  # Not a protected ground
        government_involvement=True,
    )
    
    result = analyzer.analyze_asylum_eligibility(claim)
    assert result["eligible"] is False
    assert any("nexus" in issue.lower() for issue in result["issues"])


def test_asylum_filing_deadline():
    """Asylum claim must be filed within one year of entry."""
    alien = Alien(
        name="Late Filer",
        alien_id="A002",
        nationality="Freedonia",
        date_of_birth=date(1985, 1, 1),
        date_of_entry=date(2020, 1, 1),  # Entered 4+ years ago
    )
    
    claim = AsylumClaim(
        claimant=alien,
        claim_date=date.today(),
        feared_country="Freedonia",
    )
    
    claim.add_persecution_claim(
        harm="Physical abuse",
        nexus="political opinion",
        government_involvement=True,
    )
    
    assert not claim.meets_filing_deadline()


def test_visa_allocation_family_plus_employment():
    """Visa numbers allocated between family and employment categories."""
    system = VisaPreferenceSystem()
    
    family_total = 0
    for category in [VisaCategory.F1_FAMILY, VisaCategory.F2A, VisaCategory.F2B,
                     VisaCategory.F3_FAMILY, VisaCategory.F4_FAMILY]:
        family_total += system.get_category_allocation(category)
    
    employment_total = 0
    for category in [VisaCategory.EB1, VisaCategory.EB2, VisaCategory.EB3,
                     VisaCategory.EB4, VisaCategory.EB5]:
        employment_total += system.get_category_allocation(category)
    
    assert family_total > 0
    assert employment_total > 0
    assert family_total <= system.FAMILY_TOTAL


def test_due_process_rights_in_removal():
    """Aliens in removal proceedings have due process rights."""
    from src.domains.d_immigration.implementation import RemovalDefenseAnalyzer
    
    analyzer = RemovalDefenseAnalyzer()
    
    alien = Alien(
        name="Respondent",
        alien_id="R001",
        nationality="Sylvania",
        date_of_birth=date(1980, 1, 1),
        admission_class=AdmissionClass.NONIMMIGRANT,
    )
    
    rights = analyzer.check_due_process_rights(alien, proceedings_pending=True)
    
    assert rights["hearing_rights"]["right_to_hearing"] is True
    assert rights["hearing_rights"]["right_to_counsel"] is True
    assert rights["appeal_rights"]["right_to_administrative_appeal"] is True


if __name__ == "__main__":
    test_asylum_requires_protected_nexus()
    test_asylum_filing_deadline()
    test_visa_allocation_family_plus_employment()
    test_due_process_rights_in_removal()
    print("All D_IMMIGRATION tests: PASS")

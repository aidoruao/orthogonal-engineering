"""D_CORPORATE_COMPLIANCE invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: SEC regulations, EPA reporting, DOL posting requirements
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_corporate_compliance.implementation import (
    AnnualFilingManager,
    EnvironmentalReportingManager,
    LaborPostingManager,
    CorporateComplianceAuditor,
    Corporation,
    AnnualFiling,
    EnvironmentalReport,
    LaborLawPosting,
    FilingType,
    EnvironmentalReportType,
    LaborPostingType,
)


def check_annual_filing_requirements_met() -> bool:
    """
    Invariant: Annual filing requirements met with documented submission.
    Falsification: If incomplete filing passes compliance.
    """
    manager = AnnualFilingManager()
    
    # Complete filing (use far future deadline so test doesn't expire)
    complete_filing = manager.create_filing(
        filing_id="F001",
        corporation_id="C001",
        filing_type=FilingType.ANNUAL_REPORT_10K,
        fiscal_year_end=datetime(2099, 12, 31),
    )
    complete_filing.financial_statements_included = True
    complete_filing.auditor_report_included = True
    complete_filing.management_discussion_included = True
    complete_filing.internal_controls_reported = True
    
    # Submit the filing
    manager.submit_filing("F001", "SEC-CONF-001")
    
    result = manager.check_filing_compliance("F001")
    assert result["complete"] is True, (
        "Complete filing should have complete=True"
    )
    assert result["submitted"] is True, (
        "Submitted filing should have submitted=True"
    )
    assert result["sec_confirmation"] is True, (
        "Submitted filing should have confirmation"
    )
    assert result["compliant"] is True, (
        "Complete and submitted filing should be compliant"
    )
    
    # Incomplete filing
    incomplete_filing = manager.create_filing(
        filing_id="F002",
        corporation_id="C002",
        filing_type=FilingType.ANNUAL_REPORT_10K,
        fiscal_year_end=datetime(2099, 12, 31),
    )
    # Missing some required components
    incomplete_filing.financial_statements_included = True
    incomplete_filing.auditor_report_included = False  # Missing!
    incomplete_filing.management_discussion_included = True
    incomplete_filing.internal_controls_reported = True
    
    result2 = manager.check_filing_compliance("F002")
    assert result2["complete"] is False, (
        "Incomplete filing should have complete=False"
    )
    assert result2["compliant"] is False, (
        "Incomplete filing should not be compliant"
    )
    
    return True


def check_environmental_reporting_complete() -> bool:
    """
    Invariant: Environmental compliance reporting is complete and accurate.
    Falsification: If report without data passes compliance.
    """
    manager = EnvironmentalReportingManager()
    
    # Complete report
    complete_report = manager.create_report(
        report_id="E001",
        corporation_id="C001",
        report_type=EnvironmentalReportType.TOXIC_RELEASE_INVENTORY,
        period_start=datetime(2023, 1, 1),
        period_end=datetime(2023, 12, 31),
    )
    complete_report.emissions_data = {"benzene": Fraction(100)}
    complete_report.waste_quantities = {"hazardous": Fraction(50)}
    
    # Submit and acknowledge
    manager.submit_report("E001", "EPA-ACK-001")
    
    result = manager.check_reporting_compliance("E001")
    assert result["has_data"] is True, (
        "Report with data should have has_data=True"
    )
    assert result["submitted"] is True, (
        "Submitted report should have submitted=True"
    )
    assert result["acknowledged"] is True, (
        "Acknowledged report should have acknowledged=True"
    )
    assert result["compliant"] is True, (
        "Complete report should be compliant"
    )
    
    # Empty report
    empty_report = manager.create_report(
        report_id="E002",
        corporation_id="C002",
        report_type=EnvironmentalReportType.TOXIC_RELEASE_INVENTORY,
        period_start=datetime(2023, 1, 1),
        period_end=datetime(2023, 12, 31),
    )
    # No data added
    
    result2 = manager.check_reporting_compliance("E002")
    assert result2["has_data"] is False, (
        "Empty report should have has_data=False"
    )
    assert result2["compliant"] is False, (
        "Empty report should not be compliant"
    )
    
    return True


def check_labor_postings_verified() -> bool:
    """
    Invariant: Labor law posting requirements are verified.
    Falsification: If unverified posting passes compliance.
    """
    manager = LaborPostingManager()
    
    # Verified posting
    verified_posting = LaborLawPosting(
        posting_id="P001",
        corporation_id="C001",
        posting_type=LaborPostingType.MINIMUM_WAGE,
        facility_id="F001",
        location_description="Employee break room",
        posting_date=datetime(2024, 1, 1),
        poster_version="2024-Federal",
        verified_present=True,
        verification_date=datetime(2024, 1, 15),
        verified_by="HR Manager",
    )
    manager.add_posting(verified_posting)
    
    # Unverified posting
    unverified_posting = LaborLawPosting(
        posting_id="P002",
        corporation_id="C001",
        posting_type=LaborPostingType.FAMILY_MEDICAL_LEAVE,
        facility_id="F001",
        location_description="Near time clock",
        posting_date=datetime(2024, 1, 1),
        poster_version="2024-Federal",
        verified_present=False,  # Not verified!
    )
    manager.add_posting(unverified_posting)
    
    # Check compliance
    result = manager.check_posting_compliance("C001", 50, ["F001"])
    
    # Should find the facility
    assert result["facilities_checked"] == 1, (
        "Should check one facility"
    )
    
    # Facility should be non-compliant (missing FMLA verification)
    facility_result = result["facility_results"][0]
    assert facility_result["compliant"] is False, (
        "Facility with unverified posting should be non-compliant"
    )
    assert "FAMILY_MEDICAL_LEAVE" in facility_result["missing"], (
        "Unverified FMLA posting should be in missing list"
    )
    
    return True


def check_filing_deadline_enforcement() -> bool:
    """
    Invariant: Filings must be submitted by deadline.
    Falsification: If late filing passes compliance.
    """
    manager = AnnualFilingManager()
    
    # Timely filing (within 60 days for 10-K)
    timely_filing = manager.create_filing(
        filing_id="F003",
        corporation_id="C003",
        filing_type=FilingType.ANNUAL_REPORT_10K,
        fiscal_year_end=datetime(2023, 12, 31),
    )
    timely_filing.filed_date = datetime(2024, 2, 15)  # Within 60 days
    timely_filing.sec_confirmation = "SEC-CONF-003"
    timely_filing.financial_statements_included = True
    timely_filing.auditor_report_included = True
    timely_filing.management_discussion_included = True
    timely_filing.internal_controls_reported = True
    
    result = manager.check_filing_compliance("F003")
    assert result["deadline_met"] is True, (
        "Timely filing should meet deadline"
    )
    
    # Late filing (after 60 days)
    late_filing = manager.create_filing(
        filing_id="F004",
        corporation_id="C004",
        filing_type=FilingType.ANNUAL_REPORT_10K,
        fiscal_year_end=datetime(2023, 12, 31),
    )
    late_filing.filed_date = datetime(2024, 4, 15)  # After 60 days (March 1 deadline)
    late_filing.sec_confirmation = "SEC-CONF-004"
    late_filing.financial_statements_included = True
    late_filing.auditor_report_included = True
    late_filing.management_discussion_included = True
    late_filing.internal_controls_reported = True
    
    result2 = manager.check_filing_compliance("F004")
    assert result2["deadline_met"] is False, (
        "Late filing should not meet deadline"
    )
    assert result2["compliant"] is False, (
        "Late filing should not be compliant"
    )
    
    return True


def check_environmental_verification() -> bool:
    """
    Invariant: Environmental reports should be verified for accuracy.
    Falsification: If unverified report is treated as accurate.
    """
    manager = EnvironmentalReportingManager()
    
    # Unverified report
    unverified_report = manager.create_report(
        report_id="E003",
        corporation_id="C003",
        report_type=EnvironmentalReportType.GREENHOUSE_GAS,
        period_start=datetime(2023, 1, 1),
        period_end=datetime(2023, 12, 31),
    )
    unverified_report.emissions_data = {"co2": Fraction(10000)}
    manager.submit_report("E003", "EPA-ACK-003")
    
    result = manager.check_reporting_compliance("E003")
    assert result["verified"] is False, (
        "Unverified report should have verified=False"
    )
    
    # Verified report
    verified_report = manager.create_report(
        report_id="E004",
        corporation_id="C004",
        report_type=EnvironmentalReportType.GREENHOUSE_GAS,
        period_start=datetime(2023, 1, 1),
        period_end=datetime(2023, 12, 31),
    )
    verified_report.emissions_data = {"co2": Fraction(15000)}
    manager.submit_report("E004", "EPA-ACK-004")
    manager.verify_report("E004", "Third-Party Auditor Inc.")
    
    result2 = manager.check_reporting_compliance("E004")
    assert result2["verified"] is True, (
        "Verified report should have verified=True"
    )
    
    return True


def check_all_required_postings_present() -> bool:
    """
    Invariant: All required labor law postings must be present.
    Falsification: If missing required poster passes compliance.
    """
    manager = LaborPostingManager()
    
    corporation_id = "C005"
    facility_id = "F005"
    
    # Add only some required postings
    for posting_type in [LaborPostingType.MINIMUM_WAGE, 
                         LaborPostingType.OCCUPATIONAL_SAFETY_HEALTH]:
        posting = LaborLawPosting(
            posting_id=f"P_{posting_type.name}",
            corporation_id=corporation_id,
            posting_type=posting_type,
            facility_id=facility_id,
            location_description="Break room",
            posting_date=datetime(2024, 1, 1),
            poster_version="2024",
            verified_present=True,
            verification_date=datetime(2024, 1, 15),
            verified_by="HR",
        )
        manager.add_posting(posting)
    
    # Check compliance (only 2 of 5+ required posters present)
    result = manager.check_posting_compliance(corporation_id, 50, [facility_id])
    
    assert result["all_compliant"] is False, (
        "Facility with missing required posters should not be fully compliant"
    )
    
    facility_result = result["facility_results"][0]
    assert facility_result["present_count"] < facility_result["required_count"], (
        "Should have fewer present than required"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("annual_filing", check_annual_filing_requirements_met),
        ("environmental_complete", check_environmental_reporting_complete),
        ("labor_postings", check_labor_postings_verified),
        ("filing_deadline", check_filing_deadline_enforcement),
        ("environmental_verification", check_environmental_verification),
        ("all_postings_present", check_all_required_postings_present),
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

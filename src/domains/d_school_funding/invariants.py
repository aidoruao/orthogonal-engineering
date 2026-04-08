"""D_SCHOOL_FUNDING invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Title I (ESEA), state education codes
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_school_funding.implementation import (
    FundingCalculator,
    EquityAnalyzer,
    FundingComplianceAuditor,
    SchoolDistrict,
    PerPupilAllocation,
    TitleIAllocation,
    PropertyTaxDistribution,
    StudentCategory,
    FundingSource,
)


def check_per_pupil_spending_equity() -> bool:
    """
    Invariant: Per-pupil spending variance across districts ≤ equity threshold.
    Falsification: If variance exceeds threshold without flagging.
    """
    analyzer = EquityAnalyzer()
    
    # Create districts with equitable funding
    equitable_districts = [
        SchoolDistrict(
            district_id="D001",
            name="District A",
            state="CA",
            total_enrollment=1000,
            total_budget=Fraction(10000000),  # $10M = $10k per pupil
        ),
        SchoolDistrict(
            district_id="D002",
            name="District B",
            state="CA",
            total_enrollment=2000,
            total_budget=Fraction(20000000),  # $20M = $10k per pupil
        ),
        SchoolDistrict(
            district_id="D003",
            name="District C",
            state="CA",
            total_enrollment=1500,
            total_budget=Fraction(15000000),  # $15M = $10k per pupil
        ),
    ]
    
    result = analyzer.analyze_spending_equity(equitable_districts)
    # All districts have $10k per pupil - should be equitable
    assert result["equitable"] is True, (
        "Districts with equal per-pupil funding should be equitable"
    )
    
    # Create districts with inequitable funding
    inequitable_districts = [
        SchoolDistrict(
            district_id="D004",
            name="Rich District",
            state="CA",
            total_enrollment=1000,
            total_budget=Fraction(20000000),  # $20k per pupil
        ),
        SchoolDistrict(
            district_id="D005",
            name="Poor District",
            state="CA",
            total_enrollment=1000,
            total_budget=Fraction(5000000),   # $5k per pupil
        ),
    ]
    
    result2 = analyzer.analyze_spending_equity(inequitable_districts)
    # Large disparity should be flagged
    assert result2["coefficient_of_variation"] > 0, (
        "Inequitable funding should have non-zero variance"
    )
    
    return True


def check_property_tax_formula_deterministic() -> bool:
    """
    Invariant: Property tax revenue sharing formula is deterministic.
    Falsification: If same inputs produce different outputs.
    """
    # Create tax distribution
    distribution = PropertyTaxDistribution(
        jurisdiction_id="J001",
        fiscal_year=2024,
        total_collected=Fraction(10000000),  # $10M
        school_district_share=Fraction(50, 100),
        municipality_share=Fraction(30, 100),
        county_share=Fraction(15, 100),
        other_share=Fraction(5, 100),
    )
    
    # Validate formula sums to 1.0
    assert distribution.validate_formula() is True, (
        "Formula should sum to 1.0"
    )
    
    # Calculate distribution multiple times
    calc1 = distribution.calculate_distribution()
    calc2 = distribution.calculate_distribution()
    calc3 = distribution.calculate_distribution()
    
    # Should be identical each time (deterministic)
    assert calc1 == calc2 == calc3, (
        "Tax formula must be deterministic"
    )
    
    # Verify amounts
    assert calc1["school_district"] == Fraction(5000000), (
        "School district should get 50%"
    )
    assert calc1["municipality"] == Fraction(3000000), (
        "Municipality should get 30%"
    )
    
    return True


def check_title_i_formulaic() -> bool:
    """
    Invariant: Title I allocation is formulaic given poverty rate.
    Falsification: If higher poverty doesn't result in higher allocation.
    """
    calculator = FundingCalculator()
    
    # Low poverty district (5%)
    low_poverty = SchoolDistrict(
        district_id="D001",
        name="Low Poverty",
        state="CA",
        total_enrollment=1000,
        poverty_rate=Fraction(5, 100),
    )
    
    # High poverty district (40%)
    high_poverty = SchoolDistrict(
        district_id="D002",
        name="High Poverty",
        state="CA",
        total_enrollment=1000,
        poverty_rate=Fraction(40, 100),
    )
    
    total_funds = Fraction(10000000)  # $10M
    
    allocation_low = calculator.calculate_title_i_allocation(
        low_poverty, total_funds
    )
    allocation_high = calculator.calculate_title_i_allocation(
        high_poverty, total_funds
    )
    
    # Both should be eligible (>2% poverty)
    assert allocation_low.eligible is True, (
        "5% poverty should be eligible for Title I"
    )
    assert allocation_high.eligible is True, (
        "40% poverty should be eligible for Title I"
    )
    
    # High poverty should get more funding
    assert allocation_high.total_allocation > allocation_low.total_allocation, (
        "Higher poverty district should receive more Title I funding"
    )
    
    # High poverty should get concentration grant (>=15%)
    assert allocation_high.concentration_grant > 0, (
        "High poverty district should receive concentration grant"
    )
    assert allocation_low.concentration_grant == 0, (
        "Low poverty district should not receive concentration grant"
    )
    
    return True


def check_title_i_eligibility_threshold() -> bool:
    """
    Invariant: Title I eligibility requires minimum poverty rate.
    Falsification: If district below threshold is deemed eligible.
    """
    calculator = FundingCalculator()
    
    # Below threshold (1% - minimum is 2%)
    below_threshold = SchoolDistrict(
        district_id="D001",
        name="Affluent District",
        state="CA",
        total_enrollment=1000,
        poverty_rate=Fraction(1, 100),  # 1%
    )
    
    # At threshold (2%)
    at_threshold = SchoolDistrict(
        district_id="D002",
        name="Threshold District",
        state="CA",
        total_enrollment=1000,
        poverty_rate=Fraction(2, 100),  # 2%
    )
    
    total_funds = Fraction(10000000)
    
    allocation_below = calculator.calculate_title_i_allocation(
        below_threshold, total_funds
    )
    allocation_at = calculator.calculate_title_i_allocation(
        at_threshold, total_funds
    )
    
    # Below threshold should not be eligible
    assert allocation_below.eligible is False, (
        "District below 2% poverty should not be eligible"
    )
    assert allocation_below.total_allocation == 0, (
        "Ineligible district should receive $0"
    )
    
    # At threshold should be eligible
    assert allocation_at.eligible is True, (
        "District at 2% poverty should be eligible"
    )
    
    return True


def check_weighted_enrollment_calculation() -> bool:
    """
    Invariant: Weighted enrollment properly accounts for student categories.
    Falsification: If weighted enrollment doesn't reflect category weights.
    """
    calculator = FundingCalculator()
    
    # District with mixed student population
    district = SchoolDistrict(
        district_id="D001",
        name="Mixed District",
        state="CA",
        total_enrollment=600,
        students_by_category={
            StudentCategory.GENERAL_EDUCATION: 400,  # Weight 1.0
            StudentCategory.SPECIAL_EDUCATION: 50,   # Weight 2.0
            StudentCategory.ENGLISH_LEARNER: 100,    # Weight 1.5
            StudentCategory.ECONOMICALLY_DISADVANTAGED: 50,  # Weight 1.2
        },
    )
    
    base_amount = Fraction(10000)  # $10k base
    
    allocation = calculator.calculate_per_pupil_allocation(district, base_amount)
    
    # Expected weighted enrollment:
    # 400 * 1.0 = 400
    # 50 * 2.0 = 100
    # 100 * 1.5 = 150
    # 50 * 1.2 = 60
    # Total = 710
    expected_weighted = Fraction(710)
    
    assert allocation.weighted_enrollment == expected_weighted, (
        f"Weighted enrollment should be {expected_weighted}, got {allocation.weighted_enrollment}"
    )
    
    # Expected total allocation: 710 * $10k = $7.1M
    expected_total = Fraction(7100000)
    assert allocation.total_allocation == expected_total, (
        f"Total allocation should be {expected_total}, got {allocation.total_allocation}"
    )
    
    return True


def check_tax_distribution_completeness() -> bool:
    """
    Invariant: Tax distribution must account for all revenue.
    Falsification: If distributed amounts don't sum to total collected.
    """
    distribution = PropertyTaxDistribution(
        jurisdiction_id="J001",
        fiscal_year=2024,
        total_collected=Fraction(10000000),
        school_district_share=Fraction(50, 100),
        municipality_share=Fraction(30, 100),
        county_share=Fraction(15, 100),
        other_share=Fraction(5, 100),
    )
    
    # Calculate distribution
    distributed = distribution.calculate_distribution()
    
    # Sum of all distributions should equal total
    total_distributed = sum(distributed.values())
    assert total_distributed == distribution.total_collected, (
        "Sum of distributions must equal total collected"
    )
    
    # Verify each component
    assert distributed["school_district"] + distributed["municipality"] + \
           distributed["county"] + distributed["other"] == distribution.total_collected, (
        "All components must sum to total"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("per_pupil_equity", check_per_pupil_spending_equity),
        ("tax_formula_deterministic", check_property_tax_formula_deterministic),
        ("title_i_formulaic", check_title_i_formulaic),
        ("title_i_threshold", check_title_i_eligibility_threshold),
        ("weighted_enrollment", check_weighted_enrollment_calculation),
        ("tax_distribution", check_tax_distribution_completeness),
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

"""Falsification tests for D_ENVIRONMENTAL_LAW"""
from fractions import Fraction
from datetime import date
from src.domains.d_environmental_law import (
    CleanAirActAnalyzer,
    NEPAAnalyzer,
    EmissionSource,
    AirQualityMonitor,
    FederalAction,
    PollutantType,
    AirQualityClass,
    NEPAClassification,
    check_emission_permit_requirements,
)


def test_naaqs_violation_flagged():
    """Air quality measurements exceeding NAAQS flagged as violations."""
    monitor = AirQualityMonitor(
        monitor_id="M001",
        location="Downtown",
        pollutant_measured=PollutantType.PM25,
        measured_value=Fraction(45),  # Exceeds standard
        units="ug/m3",
        standard_value=Fraction(35),  # NAAQS standard
    )
    
    assert monitor.is_violation is True
    assert monitor.percent_of_standard > 100


def test_major_source_threshold_100_tpy():
    """Sources emitting 100+ tpy are major sources."""
    source = EmissionSource(
        source_id="S001",
        source_name="Stack A",
        facility_name="Factory",
        emissions={PollutantType.SO2: Fraction(150)},  # 150 tpy
    )
    
    assert source.is_major_source is True
    
    # Below threshold
    small_source = EmissionSource(
        source_id="S002",
        source_name="Stack B",
        facility_name="Small Factory",
        emissions={PollutantType.SO2: Fraction(50)},  # 50 tpy
    )
    
    assert small_source.is_major_source is False


def test_nepa_significant_impact_requires_eis():
    """Federal actions with significant environmental impact require EIS."""
    analyzer = NEPAAnalyzer()
    
    # Low significance action (CX or EA)
    low_impact = FederalAction(
        action_id="A001",
        description="Administrative update",
        agency="EPA",
        intensity_factors={},
    )
    
    classification = analyzer.classify_action(low_impact)
    assert classification in (NEPAClassification.CX, NEPAClassification.EA)
    
    # High significance action (EIS required)
    high_impact = FederalAction(
        action_id="A002",
        description="Major highway construction",
        agency="DOT",
        context="regional",
        intensity_factors={
            "effects_on_wetlands": True,
            "effects_on_endangered_species": True,
            "effects_on_air_quality": True,
            "effects_on_water_quality": True,
        },
    )
    
    classification = analyzer.classify_action(high_impact)
    assert classification == NEPAClassification.EIS


def test_emission_permit_requirements():
    """Major sources in attainment areas require PSD permits."""
    result = check_emission_permit_requirements(
        emissions_tons_per_year={"SO2": 150, "NO2": 100},
        air_quality_class="ATTAINMENT",
        is_new_source=True,
    )
    
    assert result["is_major_source"] is True
    assert result["num_requirements"] > 0


if __name__ == "__main__":
    test_naaqs_violation_flagged()
    test_major_source_threshold_100_tpy()
    test_nepa_significant_impact_requires_eis()
    test_emission_permit_requirements()
    print("All D_ENVIRONMENTAL_LAW tests: PASS")

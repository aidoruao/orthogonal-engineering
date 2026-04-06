"""D_ENVIRONMENTAL_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Clean Air Act (42 U.S.C. §7401), NEPA (42 U.S.C. §4321)
"""

from src.domains.d_environmental_law.implementation import (
    CleanAirActAnalyzer,
    NEPAAnalyzer,
    PermittingSystem,
    EmissionSource,
    AirQualityMonitor,
    FederalAction,
    PollutantType,
    PermitType,
    NEPAClassification,
    AirQualityClass,
    check_emission_permit_requirements,
)
from fractions import Fraction


def check_naaqs_violation_flagged() -> bool:
    """
    Invariant: Air quality measurements exceeding NAAQS are flagged as violations.
    Falsification: If exceedance not flagged as violation.
    """
    analyzer = CleanAirActAnalyzer()
    
    # Monitor showing violation
    violating_monitor = AirQualityMonitor(
        monitor_id="M001",
        location="Downtown",
        pollutant_measured=PollutantType.PM25,
        measured_value=Fraction(40),  # µg/m³ - exceeds standard
        units="µg/m³",
        standard_value=Fraction(35),  # Annual standard
    )
    
    assert violating_monitor.is_violation, (
        f"40 µg/m³ PM2.5 should violate 35 µg/m³ standard"
    )
    
    # Monitor showing compliance
    compliant_monitor = AirQualityMonitor(
        monitor_id="M002",
        location="Suburb",
        pollutant_measured=PollutantType.PM25,
        measured_value=Fraction(25),  # µg/m³ - below standard
        units="µg/m³",
        standard_value=Fraction(35),
    )
    
    assert not compliant_monitor.is_violation, (
        "25 µg/m³ PM2.5 should not violate 35 µg/m³ standard"
    )
    
    return True


def check_major_source_threshold_100_tpy() -> bool:
    """
    Invariant: Major source threshold is 100 tons per year.
    Falsification: If source with 100+ tpy not classified as major.
    """
    # Major source (>= 100 tpy)
    major = EmissionSource(
        source_id="S001",
        source_name="Big Plant",
        facility_name="Facility A",
        emissions={PollutantType.VOC: Fraction(150)},
    )
    
    assert major.is_major_source, (
        f"150 tpy source should be major, total={major.total_emissions}"
    )
    
    # Minor source (< 100 tpy)
    minor = EmissionSource(
        source_id="S002",
        source_name="Small Plant",
        facility_name="Facility B",
        emissions={PollutantType.VOC: Fraction(50)},
    )
    
    assert not minor.is_major_source, (
        f"50 tpy source should not be major, total={minor.total_emissions}"
    )
    
    return True


def check_psd_required_in_attainment_areas() -> bool:
    """
    Invariant: PSD permit required for major sources in attainment areas.
    Falsification: If major source in attainment doesn't trigger PSD.
    """
    analyzer = CleanAirActAnalyzer()
    
    source = EmissionSource(
        source_id="S001",
        source_name="New Plant",
        facility_name="Facility",
        emissions={PollutantType.PM10: Fraction(150)},  # Major source (>100 tpy)
    )
    
    result = analyzer.analyze_source_permitting(
        source=source,
        air_quality_class=AirQualityClass.ATTAINMENT,
        is_new_source=True,
    )
    
    permit_types = [r["permit_type"] for r in result["permit_requirements"]]
    
    assert PermitType.PSD_PERMIT in permit_types or PermitType.TITLE_V in permit_types, (
        "Major source in attainment should require PSD or Title V"
    )
    
    return True


def check_nepa_significant_impact_requires_eis() -> bool:
    """
    Invariant: Federal actions with significant impacts require EIS.
    Falsification: If significant action doesn't trigger EIS requirement.
    """
    analyzer = NEPAAnalyzer()
    
    # Significant action
    significant = FederalAction(
        action_id="A001",
        description="Major highway construction",
        agency="DOT",
        context="regional",
        intensity_factors={
            "effects_on_public_health": True,
            "effects_on_unique_resources": True,
            "degree_of_controversy": True,
            "degree_of_uncertainty": True,
        },
    )
    
    classification = analyzer.classify_action(significant)
    
    assert classification == NEPAClassification.EIS, (
        f"Significant action should require EIS, got {classification.name}"
    )
    
    # Minimal action
    minimal = FederalAction(
        action_id="A002",
        description="Administrative change",
        agency="DOT",
        context="local",
        intensity_factors={},
    )
    
    classification = analyzer.classify_action(minimal)
    
    assert classification == NEPAClassification.CX, (
        f"Minimal action should be CX, got {classification.name}"
    )
    
    return True


def check_emission_calculation_sum_correct() -> bool:
    """
    Invariant: Total emissions equals sum of all pollutant emissions.
    Falsification: If total doesn't equal sum of components.
    """
    source = EmissionSource(
        source_id="S001",
        source_name="Multi-pollutant",
        facility_name="Facility",
        emissions={
            PollutantType.SO2: Fraction(30),
            PollutantType.NO2: Fraction(40),
            PollutantType.CO: Fraction(50),
        },
    )
    
    expected = Fraction(120)
    assert source.total_emissions == expected, (
        f"Total emissions should be {expected}, got {source.total_emissions}"
    )
    
    return True


def check_public_comment_period_minimum() -> bool:
    """
    Invariant: Major permits require minimum public comment period.
    Falsification: If PSD permit allows less than 30-day comment period.
    """
    permitting = PermittingSystem()
    
    result = permitting.check_public_participation(
        permit_type=PermitType.PSD_PERMIT,
        public_comment_period_days=15,  # Too short!
        hearing_held=False,
        comments_received=0,
    )
    
    assert not result["adequate"], (
        "15-day comment period for PSD should be inadequate"
    )
    assert "Comment period 15 days < required 30" in result["issues"], (
        "Should flag insufficient comment period"
    )
    
    return True


def check_nonattainment_stricter_requirements() -> bool:
    """
    Invariant: Nonattainment areas have stricter NSR requirements.
    Falsification: If nonattainment area doesn't trigger stricter review.
    """
    analyzer = CleanAirActAnalyzer()
    
    source = EmissionSource(
        source_id="S001",
        source_name="Plant",
        facility_name="Facility",
        emissions={PollutantType.VOC: Fraction(50)},
    )
    
    # Nonattainment result
    nonattainment = analyzer.analyze_source_permitting(
        source=source,
        air_quality_class=AirQualityClass.NONATTAINMENT,
        is_new_source=True,
    )
    
    # Should note LAER requirement for nonattainment
    requirements = str(nonattainment["permit_requirements"])
    
    assert "LAER" in requirements or "Nonattainment" in requirements, (
        "Nonattainment should trigger LAER or nonattainment NSR"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_ENVIRONMENTAL_LAW invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_naaqs_violation_flagged,
        check_major_source_threshold_100_tpy,
        check_psd_required_in_attainment_areas,
        check_nepa_significant_impact_requires_eis,
        check_emission_calculation_sum_correct,
        check_public_comment_period_minimum,
        check_nonattainment_stricter_requirements,
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
    print("All D_ENVIRONMENTAL_LAW invariants: PASS")

"""D_ENVIRONMENTAL_LAW implementation — Environmental Law

Implements environmental law including Clean Air Act compliance,
NEPA review, and permitting analysis.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: Clean Air Act (42 U.S.C. §7401), NEPA (42 U.S.C. §4321),
        Clean Water Act (33 U.S.C. §1251), RCRA (42 U.S.C. §6901)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from fractions import Fraction
from datetime import date, timedelta


class PermitType(Enum):
    """Major environmental permit types."""
    # Clean Air Act
    PSD_PERMIT = auto()     # Prevention of Significant Deterioration
    TITLE_V = auto()        # Operating permit for major sources
    NSR_PERMIT = auto()     # New Source Review
    
    # Clean Water Act
    NPDES = auto()          # National Pollutant Discharge Elimination System
    DREDGE_FILL = auto()    # Section 404 permit
    
    # Other
    RCRA_PERMIT = auto()    # Hazardous waste
    UIC = auto()            # Underground Injection Control


class PollutantType(Enum):
    """Major air pollutants regulated under CAA."""
    PM25 = auto()   # Fine particulate matter
    PM10 = auto()   # Coarse particulate matter
    O3 = auto()     # Ozone
    CO = auto()     # Carbon monoxide
    NO2 = auto()    # Nitrogen dioxide
    SO2 = auto()    # Sulfur dioxide
    LEAD = auto()   # Lead
    VOC = auto()    # Volatile organic compounds


class NEPAClassification(Enum):
    """NEPA document classifications."""
    EIS = auto()    # Environmental Impact Statement (major federal action)
    EA = auto()     # Environmental Assessment
    CX = auto()     # Categorical Exclusion
    FONSI = auto()  # Finding of No Significant Impact


class AirQualityClass(Enum):
    """Air quality classification under CAA."""
    ATTAINMENT = auto()      # Meets NAAQS
    NONATTAINMENT = auto()   # Exceeds NAAQS
    MAINTENANCE = auto()     # Former nonattainment now meeting
    UNCLASSIFIABLE = auto()  # Insufficient data


@dataclass
class EmissionSource:
    """A source of air pollutant emissions."""
    source_id: str
    source_name: str
    facility_name: str
    
    # Emissions in tons per year (tpy)
    emissions: Dict[PollutantType, Fraction] = field(default_factory=dict)
    
    @property
    def total_emissions(self) -> Fraction:
        """Total emissions across all pollutants."""
        return sum(self.emissions.values(), Fraction(0))
    
    @property
    def is_major_source(self) -> bool:
        """Check if major source (100 tpy threshold)."""
        return self.total_emissions >= 100
    
    def get_emission(self, pollutant: PollutantType) -> Fraction:
        """Get emissions for specific pollutant."""
        return self.emissions.get(pollutant, Fraction(0))


@dataclass
class AirQualityMonitor:
    """Air quality monitoring station."""
    monitor_id: str
    location: str
    pollutant_measured: PollutantType
    
    # Annual mean or design value (varies by pollutant)
    measured_value: Fraction
    units: str
    
    # NAAQS standards (simplified)
    standard_value: Fraction
    
    @property
    def is_violation(self) -> bool:
        """Check if measurement exceeds standard."""
        return self.measured_value > self.standard_value
    
    @property
    def percent_of_standard(self) -> Fraction:
        """Measured value as percentage of standard."""
        if self.standard_value == 0:
            return Fraction(0)
        return (self.measured_value / self.standard_value) * 100


@dataclass
class FederalAction:
    """A federal action subject to NEPA."""
    action_id: str
    description: str
    agency: str
    
    # Significance factors (NEPA §1508.27)
    context: str = ""  # Local, regional, national
    intensity_factors: Dict[str, bool] = field(default_factory=dict)
    
    def is_major_federal_action(self) -> bool:
        """Check if action qualifies as major federal action."""
        # Actions with federal funding, approval, or undertaking
        return len(self.agency) > 0
    
    def significance_score(self) -> int:
        """Calculate significance score based on intensity factors."""
        return sum(1 for v in self.intensity_factors.values() if v)


class CleanAirActAnalyzer:
    """Analyzer for Clean Air Act compliance.
    
    The Clean Air Act protects public health and welfare—
    reflecting the biblical mandate of stewardship over creation
    (Genesis 2:15: "The LORD God took the man and put him in the
    Garden of Eden to work it and take care of it").
    """
    
    # Major source thresholds (tpy)
    MAJOR_SOURCE_THRESHOLD = Fraction(100)
    
    # PSD significant increase thresholds (tpy)
    PSD_SIGNIFICANT_INCREASE = {
        PollutantType.PM10: Fraction(15),
        PollutantType.SO2: Fraction(40),
        PollutantType.NO2: Fraction(40),
        PollutantType.CO: Fraction(100),
        PollutantType.VOC: Fraction(40),
    }
    
    def __init__(self):
        self.permit_requirements: List[Dict] = []
    
    def analyze_source_permitting(
        self,
        source: EmissionSource,
        air_quality_class: AirQualityClass,
        is_new_source: bool = True,
    ) -> Dict:
        """Analyze permitting requirements for emission source.
        
        Args:
            source: The emission source
            air_quality_class: Class of air quality in area
            is_new_source: Whether this is a new or modified source
            
        Returns:
            Permitting analysis
        """
        requirements = []
        
        # Title V Operating Permit (major sources)
        if source.is_major_source:
            requirements.append({
                "permit_type": PermitType.TITLE_V,
                "requirement": "CAA Title V operating permit required",
                "threshold": self.MAJOR_SOURCE_THRESHOLD,
                "actual": source.total_emissions,
            })
        
        # New Source Review / PSD
        if is_new_source:
            if air_quality_class == AirQualityClass.ATTAINMENT:
                # PSD review required for major sources in attainment areas
                if source.is_major_source:
                    requirements.append({
                        "permit_type": PermitType.PSD_PERMIT,
                        "requirement": "PSD permit required for major source in attainment area",
                    })
                
                # Check significant increase for regulated NSR pollutants
                for pollutant, increase in self.PSD_SIGNIFICANT_INCREASE.items():
                    emission = source.get_emission(pollutant)
                    if emission >= increase:
                        requirements.append({
                            "permit_type": PermitType.NSR_PERMIT,
                            "pollutant": pollutant.name,
                            "threshold": increase,
                            "actual": emission,
                        })
            
            elif air_quality_class == AirQualityClass.NONATTAINMENT:
                # Nonattainment NSR - stricter requirements
                # Lower thresholds apply
                requirements.append({
                    "permit_type": PermitType.NSR_PERMIT,
                    "requirement": "Nonattainment NSR required",
                    "note": "LAER (Lowest Achievable Emission Rate) applies",
                })
        
        return {
            "source_id": source.source_id,
            "total_emissions_tpy": source.total_emissions,
            "is_major_source": source.is_major_source,
            "air_quality_class": air_quality_class.name,
            "permit_requirements": requirements,
            "num_requirements": len(requirements),
        }
    
    def check_naaqs_compliance(
        self,
        monitors: List[AirQualityMonitor],
    ) -> Dict:
        """Check compliance with National Ambient Air Quality Standards.
        
        Args:
            monitors: List of air quality monitors
            
        Returns:
            Compliance analysis
        """
        violations = []
        by_pollutant: Dict[PollutantType, List] = {}
        
        for monitor in monitors:
            if monitor.is_violation:
                violations.append({
                    "monitor_id": monitor.monitor_id,
                    "location": monitor.location,
                    "pollutant": monitor.pollutant_measured.name,
                    "measured": monitor.measured_value,
                    "standard": monitor.standard_value,
                    "excess": monitor.measured_value - monitor.standard_value,
                })
            
            # Group by pollutant
            pollutant = monitor.pollutant_measured
            if pollutant not in by_pollutant:
                by_pollutant[pollutant] = []
            by_pollutant[pollutant].append(monitor.percent_of_standard)
        
        # Determine area classification for each pollutant
        classifications = {}
        for pollutant, percentages in by_pollutant.items():
            max_percent = max(percentages)
            if max_percent > 100:
                classifications[pollutant] = AirQualityClass.NONATTAINMENT
            elif max_percent > 95:
                classifications[pollutant] = AirQualityClass.MAINTENANCE
            else:
                classifications[pollutant] = AirQualityClass.ATTAINMENT
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "num_violations": len(violations),
            "classifications": {p.name: c.name for p, c in classifications.items()},
        }


class NEPAAnalyzer:
    """Analyzer for NEPA compliance."""
    
    def __init__(self):
        self.significance_threshold = 3  # Number of intensity factors
    
    def classify_action(self, action: FederalAction) -> NEPAClassification:
        """Classify federal action for NEPA purposes.
        
        Args:
            action: The federal action to classify
            
        Returns:
            NEPA classification
        """
        if not action.is_major_federal_action():
            # Not a federal action - NEPA does not apply
            return NEPAClassification.CX  # Treat as excluded
        
        significance = action.significance_score()
        
        # Categorical exclusions
        if significance == 0:
            return NEPAClassification.CX
        
        # Environmental Assessment pathway
        if significance < self.significance_threshold:
            # Would normally require EA, then FONSI or EIS
            return NEPAClassification.EA
        
        # Significant impact - EIS required
        return NEPAClassification.EIS
    
    def analyze_significance(self, action: FederalAction) -> Dict:
        """Analyze significance of environmental effects.
        
        Per 40 CFR §1508.27, significance depends on:
        1. Context and intensity
        2. Ten intensity factors
        """
        factors = action.intensity_factors
        
        analysis = {
            "context": action.context,
            "intensity_score": action.significance_score(),
            "factors_present": [k for k, v in factors.items() if v],
            "classification": self.classify_action(action).name,
        }
        
        # Determine if significant
        analysis["significant_impact"] = analysis["intensity_score"] >= self.significance_threshold
        
        return analysis


class PermittingSystem:
    """Environmental permitting system."""
    
    def __init__(self):
        self.permits_issued: List[Dict] = []
        self.caa_analyzer = CleanAirActAnalyzer()
        self.nepa_analyzer = NEPAAnalyzer()
    
    def apply_for_permit(
        self,
        permit_type: PermitType,
        applicant: str,
        facility: str,
        emissions: Optional[Dict[PollutantType, Fraction]] = None,
    ) -> Dict:
        """Process permit application.
        
        Args:
            permit_type: Type of permit requested
            applicant: Permit applicant name
            facility: Facility name
            emissions: Expected emissions (for air permits)
            
        Returns:
            Application result
        """
        application = {
            "application_id": f"APP-{len(self.permits_issued)+1:04d}",
            "permit_type": permit_type.name,
            "applicant": applicant,
            "facility": facility,
            "date_filed": date.today(),
            "status": "PENDING",
        }
        
        # Preliminary completeness check
        if emissions and permit_type in [
            PermitType.PSD_PERMIT, PermitType.TITLE_V, PermitType.NSR_PERMIT
        ]:
            source = EmissionSource(
                source_id=f"SRC-{facility}",
                source_name="Primary",
                facility_name=facility,
                emissions=emissions,
            )
            
            # Check if major source
            application["is_major_source"] = source.is_major_source
            application["total_emissions_tpy"] = source.total_emissions
        
        return application
    
    def check_public_participation(
        self,
        permit_type: PermitType,
        public_comment_period_days: int,
        hearing_held: bool,
        comments_received: int,
    ) -> Dict:
        """Check adequacy of public participation.
        
        Args:
            permit_type: Type of permit
            public_comment_period_days: Length of comment period
            hearing_held: Whether public hearing was held
            comments_received: Number of public comments received
            
        Returns:
            Public participation analysis
        """
        issues = []
        
        # Comment period requirements (simplified)
        min_periods = {
            PermitType.PSD_PERMIT: 30,
            PermitType.TITLE_V: 30,
            PermitType.NPDES: 30,
        }
        
        min_required = min_periods.get(permit_type, 15)
        
        if public_comment_period_days < min_required:
            issues.append(f"Comment period {public_comment_period_days} days < required {min_required}")
        
        # Major permits typically require hearing if requested
        if permit_type in [PermitType.PSD_PERMIT, PermitType.TITLE_V] and not hearing_held:
            issues.append("Public hearing should be available for major permits")
        
        return {
            "adequate": len(issues) == 0,
            "issues": issues,
            "comment_period": public_comment_period_days,
            "minimum_required": min_required,
            "hearing_held": hearing_held,
            "comments_received": comments_received,
        }


class EnvironmentalComplianceChecker:
    """Comprehensive environmental law compliance checker."""
    
    def __init__(self):
        self.caa_analyzer = CleanAirActAnalyzer()
        self.nepa_analyzer = NEPAAnalyzer()
        self.permitting = PermittingSystem()
    
    def check_caa_compliance(
        self,
        source: EmissionSource,
        monitors: List[AirQualityMonitor],
        air_quality_class: AirQualityClass,
    ) -> Dict:
        """Check comprehensive CAA compliance."""
        permitting = self.caa_analyzer.analyze_source_permitting(
            source, air_quality_class
        )
        naaqs = self.caa_analyzer.check_naaqs_compliance(monitors)
        
        issues = []
        if permitting["num_requirements"] > 0 and not source.is_major_source:
            # This is expected - major sources need permits
            pass
        
        if naaqs["violations"]:
            issues.extend([f"NAAQS violation: {v['pollutant']}" for v in naaqs["violations"]])
        
        return {
            "compliant": len(issues) == 0 and not naaqs["violations"],
            "issues": issues,
            "permitting": permitting,
            "naaqs_compliance": naaqs,
        }
    
    def check_nepa_compliance(self, action: FederalAction) -> Dict:
        """Check NEPA compliance for federal action."""
        classification = self.nepa_analyzer.classify_action(action)
        significance = self.nepa_analyzer.analyze_significance(action)
        
        issues = []
        if classification == NEPAClassification.EIS and action.significance_score() < 3:
            issues.append("EIS may not be required based on significance")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "classification": classification.name,
            "significance_analysis": significance,
        }


def check_emission_permit_requirements(
    emissions_tons_per_year: Dict[str, float],
    air_quality_class: str = "ATTAINMENT",
    is_new_source: bool = True,
) -> Dict:
    """Convenience function to check emission permit requirements.
    
    Usage:
        result = check_emission_permit_requirements(
            emissions_tons_per_year={
                "PM10": 20.5,
                "SO2": 35.0,
            },
            air_quality_class="ATTAINMENT",
        )
        print(f"Permits required: {result['num_requirements']}")
    """
    # Convert to Fraction and PollutantType
    emissions: Dict[PollutantType, Fraction] = {}
    for name, value in emissions_tons_per_year.items():
        try:
            pollutant = PollutantType[name.upper()]
            emissions[pollutant] = Fraction(str(value))
        except KeyError:
            continue
    
    source = EmissionSource(
        source_id="SRC001",
        source_name="Stack",
        facility_name="Facility",
        emissions=emissions,
    )
    
    aqc = AirQualityClass[air_quality_class.upper()]
    
    analyzer = CleanAirActAnalyzer()
    return analyzer.analyze_source_permitting(source, aqc, is_new_source)


@dataclass(frozen=True)
class EnvironmentalPermit:
    """Frozen environmental permit record for invariant checks.

    Standards: Clean Air Act (42 U.S.C. §7401), Clean Water Act (33 U.S.C. §1251),
    NEPA (42 U.S.C. §4321), RCRA (42 U.S.C. §6901).
    """
    permit_id: str
    epa_permit_valid: bool
    npdes_permit: bool  # Clean Water Act NPDES permit
    emission_tons_per_year: Fraction
    naaqs_limit_tons: Fraction  # Clean Air Act NAAQS limit
    wetlands_impacted: bool
    section_404_permit: bool  # CWA §404 wetlands permit
    eis_completed: bool  # NEPA Environmental Impact Statement
    hazardous_waste_manifest: bool  # RCRA manifest

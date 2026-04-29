"""D_OILGAS implementation — Oil & Gas, Pipeline Safety, Environmental Compliance

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: PHMSA Pipeline Safety, EPA Oil Pollution Prevention, BSEE
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from fractions import Fraction


class FacilityType(Enum):
    """Oil and gas facility types."""
    PRODUCTION_WELL = auto()
    REFINERY = auto()
    STORAGE_TERMINAL = auto()
    PIPELINE = auto()
    OFFSHORE_PLATFORM = auto()


class PipelineClass(Enum):
    """Pipeline location classification."""
    CLASS_1 = auto()  # Rural
    CLASS_2 = auto()  # Suburban
    CLASS_3 = auto()  # City center
    CLASS_4 = auto()  # Dense urban


@dataclass
class Pipeline:
    """Oil or gas pipeline."""
    pipeline_id: str
    operator_id: str
    pipeline_class: PipelineClass
    
    # Physical characteristics
    length_miles: Fraction
    diameter_inches: Fraction
    max_operating_pressure: Fraction  # psig
    hoop_stress_percent: Fraction  # % of SMYS
    
    # Safety
    leak_detection_system: bool
    automatic_shutdown_valves: int
    
    # Integrity
    last_inspection_date: str
    next_inspection_due: str
    corrosion_miles: Fraction  # Miles with corrosion
    
    # Incidents
    incidents_annual: int
    fatalities_annual: int
    injuries_annual: int
    property_damage: Fraction  # Dollars
    
    def get_incident_rate(self) -> Fraction:
        """Calculate incidents per 1000 miles."""
        if self.length_miles == 0:
            return Fraction(0)
        return Fraction(self.incidents_annual) / self.length_miles * 1000


@dataclass
class OffshorePlatform:
    """Offshore oil/gas production platform."""
    platform_id: str
    operator_id: str
    water_depth_feet: Fraction
    
    # BSEE safety
    bsee_inspections_annual: int
    violations_issued: int
    incidents_reported: int
    
    # Blowout preventer
    bop_test_frequency_days: Fraction
    bop_last_test: str
    bop_pressure_rating: Fraction  # psi
    
    # Environmental
    oil_spills_annual: int
    gas_release_volume: Fraction  # cubic feet
    
    def get_violation_rate(self) -> Fraction:
        """Calculate violations per inspection."""
        if self.bsee_inspections_annual == 0:
            return Fraction(0)
        return Fraction(self.violations_issued, self.bsee_inspections_annual)


@dataclass
class SpillResponsePlan:
    """Oil spill response plan per 40 CFR 112."""
    plan_id: str
    facility_id: str
    
    # Worst case discharge
    worst_case_discharge_barrels: Fraction
    response_time_hours: Fraction
    
    # Equipment
    containment_boom_feet: Fraction
    skimmer_capacity_bpd: Fraction  # Barrels per day
    storage_capacity_barrels: Fraction
    
    # Response personnel
    trained_personnel_count: int
    drills_conducted_annual: int


# Regulatory limits
PHMSA_MAX_HOOP_STRESS = Fraction(72, 100)  # 72% SMYS
PHMSA_CLASS_3_MAX_STRESS = Fraction(60, 100)  # 60% for Class 3
BSEE_BOP_TEST_MAX_DAYS = Fraction(14)  # 14 days
EPA_SPILL_RESPONSE_TIME = Fraction(12)  # 12 hours


def phmsa_max_hoop_stress(pipeline_class: PipelineClass) -> Fraction:
    """PHMSA maximum allowable hoop stress."""
    if pipeline_class == PipelineClass.CLASS_3 or pipeline_class == PipelineClass.CLASS_4:
        return PHMSA_CLASS_3_MAX_STRESS
    return PHMSA_MAX_HOOP_STRESS


def bsee_bop_test_interval() -> Fraction:
    """BSEE required BOP test interval."""
    # TODO: Expand bsee_bop_test_interval() - stub detected by Yeshua Agent
    return BSEE_BOP_TEST_MAX_DAYS

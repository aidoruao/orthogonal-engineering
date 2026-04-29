"""D_WATER implementation — Water Quality, Utilities, SDWA Compliance

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: EPA Safe Drinking Water Act (SDWA), Clean Water Act (CWA)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from fractions import Fraction


class WaterSourceType(Enum):
    """Source of water supply."""
    SURFACE_WATER = auto()
    GROUNDWATER = auto()
    MIXED = auto()
    RECYCLED = auto()


class ContaminantType(Enum):
    """Types of water contaminants regulated by EPA."""
    MICROBIAL = auto()
    DISINFECTION_BYPRODUCT = auto()
    INORGANIC = auto()
    ORGANIC = auto()
    RADIOACTIVE = auto()


@dataclass
class WaterQualitySample:
    """Water quality test sample."""
    sample_id: str
    facility_id: str
    source_type: WaterSourceType
    sample_date: str
    
    # Contaminant levels (as Fractions, in mg/L or applicable units)
    lead_level: Fraction  # mg/L, EPA action level = 0.015
    copper_level: Fraction  # mg/L, EPA action level = 1.3
    chlorine_residual: Fraction  # mg/L, typical range 0.2-4.0
    ph_level: Fraction  # pH units, EPA range 6.5-8.5
    turbidity: Fraction  # NTU, EPA max 0.3-1.0
    
    # Microbial
    e_coli_detected: bool
    total_coliform_count: int
    
    def get_lead_copper_ratio(self) -> Fraction:
        """Calculate lead to copper ratio."""
        if self.copper_level == 0:
            return Fraction(0)
        return self.lead_level / self.copper_level


@dataclass
class WaterUtility:
    """Water utility system."""
    utility_id: str
    system_name: str
    population_served: Fraction
    source_type: WaterSourceType
    
    # SDWA compliance
    annual_compliance_violations: int
    health_based_violations: int
    monitoring_violations: int
    reporting_violations: int
    
    # Consumer Confidence Report
    ccr_delivered: bool
    ccr_delivery_date: Optional[str]
    
    # Lead service lines
    estimated_lead_service_lines: Fraction
    lead_service_lines_replaced: Fraction
    
    def get_lead_replacement_rate(self) -> Fraction:
        """Calculate rate of lead service line replacement."""
        if self.estimated_lead_service_lines == 0:
            return Fraction(1)  # No lead lines = 100% complete
        return self.lead_service_lines_replaced / self.estimated_lead_service_lines
    
    def get_violation_rate(self) -> Fraction:
        """Calculate violations per 1000 population."""
        if self.population_served == 0:
            return Fraction(0)
        return Fraction(self.annual_compliance_violations) / self.population_served * 1000


@dataclass
class WastewaterDischarge:
    """Wastewater discharge permit (NPDES)."""
    permit_id: str
    facility_id: str
    
    # NPDES limits
    flow_rate_mgd: Fraction  # Million gallons per day
    bod_limit: Fraction  # Biochemical oxygen demand (mg/L)
    bod_actual: Fraction
    tss_limit: Fraction  # Total suspended solids (mg/L)
    tss_actual: Fraction
    
    # Compliance
    permit_violations_annual: int
    enforcement_actions: int
    
    def get_bod_excess(self) -> Fraction:
        """Calculate BOD excess over limit."""
        excess = self.bod_actual - self.bod_limit
        return excess if excess > 0 else Fraction(0)


# EPA SDWA regulatory limits
EPA_LEAD_ACTION_LEVEL = Fraction(15, 1000)  # 0.015 mg/L
EPA_COPPER_ACTION_LEVEL = Fraction(13, 10)  # 1.3 mg/L
EPA_PH_MIN = Fraction(65, 10)  # 6.5
EPA_PH_MAX = Fraction(85, 10)  # 8.5
EPA_TURBIDITY_MAX = Fraction(1)  # 1.0 NTU


def epa_lead_action_level() -> Fraction:
    """EPA action level for lead in drinking water."""
    # TODO: Expand epa_lead_action_level() - stub detected by Yeshua Agent
    return EPA_LEAD_ACTION_LEVEL


def epa_copper_action_level() -> Fraction:
    """EPA action level for copper in drinking water."""
    # TODO: Expand epa_copper_action_level() - stub detected by Yeshua Agent
    return EPA_COPPER_ACTION_LEVEL


def epa_ph_range() -> Tuple[Fraction, Fraction]:
    """EPA required pH range for drinking water."""
    # TODO: Expand epa_ph_range() - stub detected by Yeshua Agent
    return (EPA_PH_MIN, EPA_PH_MAX)

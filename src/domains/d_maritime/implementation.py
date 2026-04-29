"""D_MARITIME implementation — Maritime Law & Admiralty

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- UN Convention on Law of the Sea (UNCLOS)
- International Convention for Safety of Life at Sea (SOLAS)
- International Maritime Organization (IMO) regulations
- Jones Act (US cabotage)
- General Average (York-Antwerp Rules)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class VesselType(Enum):
    """Categories of maritime vessels."""
    CONTAINER = auto()
    BULK_CARRIER = auto()
    TANKER = auto()
    PASSENGER = auto()
    OFFSHORE = auto()
    FISHING = auto()
    TUG = auto()
    YACHT = auto()


class MaritimeZone(Enum):
    """UNCLOS maritime zones."""
    INTERNAL_WATERS = auto()
    TERRITORIAL_SEA = auto()  # 12 nm
    CONTIGUOUS_ZONE = auto()  # 24 nm
    EXCLUSIVE_ECONOMIC_ZONE = auto()  # 200 nm
    HIGH_SEAS = auto()


@dataclass(frozen=True)
class FlagState:
    """Vessel registry country."""
    country_code: str
    country_name: str
    
    # Paris MoU / Tokyo MoU performance
    white_list: bool  # Low detention rate
    grey_list: bool
    black_list: bool
    flag_state_quality_score: Fraction = Fraction(1, 1)
    
    def is_quality_flag(self) -> bool:
        """Flag state with good compliance record."""
        # TODO: Expand is_quality_flag() - stub detected by Yeshua Agent
        return self.white_list and not self.black_list


@dataclass
class Vessel:
    """Ship or maritime craft."""
    imo_number: str
    vessel_name: str
    vessel_type: VesselType
    
    flag_state: FlagState
    gross_tonnage: int
    
    # Crew
    crew_count: int
    minimum_safe_manning: int
    
    # Certifications
    smc_certified: bool  # Safety Management Certificate (ISM Code)
    doc_certified: bool  # Document of Compliance

    # Insurance
    p_and_i_insurance: bool  # Protection and Indemnity
    hull_insurance: bool

    smc_compliance_score: Fraction = Fraction(1, 1)
    doc_compliance_score: Fraction = Fraction(1, 1)
    
    def adequately_manned(self) -> bool:
        """Meets minimum safe manning requirements."""
        return self.crew_count >= self.minimum_safe_manning
    
    def ism_compliant(self) -> bool:
        """International Safety Management compliance."""
        # TODO: Expand ism_compliant() - stub detected by Yeshua Agent
        return self.smc_certified and self.doc_certified


@dataclass
class Cargo:
    """Maritime cargo shipment."""
    cargo_id: str
    bill_of_lading: str
    
    description: str
    weight_kg: int
    value: Fraction
    
    shipper: str
    consignee: str
    
    # Hazmat
    dangerous_goods: bool
    imdg_class: Optional[str]  # International Maritime Dangerous Goods
    
    # Status
    loaded: bool
    delivered: bool


@dataclass
class MaritimeIncident:
    """Casualty or occurrence at sea."""
    incident_id: str
    vessel_imo: str
    incident_date: datetime
    location: str
    
    incident_type: str  # collision, grounding, fire, etc.
    maritime_zone: MaritimeZone
    
    # Outcomes
    injuries: int
    fatalities: int
    pollution_released: bool
    vessel_damage: Fraction  # 0-1
    
    # Investigation
    flag_state_investigation: bool
    maib_involved: bool  # Marine Accident Investigation Branch
    report_issued: bool


@dataclass
class GeneralAverage:
    """York-Antwerp Rules general average declaration."""
    ga_id: str
    voyage_number: str
    declaration_date: datetime
    
    # Sacrifice
    cargo_sacrificed_value: Fraction
    vessel_damage_value: Fraction
    
    # Contributing interests
    vessel_value: Fraction
    cargo_values: List[Fraction]
    freight_at_risk: Fraction
    
    def total_contribution(self) -> Fraction:
        """Total value of interests contributing to GA."""
        return self.vessel_value + sum(self.cargo_values) + self.freight_at_risk
    
    def sacrifice_ratio(self) -> Fraction:
        """Sacrifice as fraction of total contribution."""
        total_sacrifice = self.cargo_sacrificed_value + self.vessel_damage_value
        contribution = self.total_contribution()
        if contribution == 0:
            return Fraction(0)
        return total_sacrifice / contribution


@dataclass
class SalvageOperation:
    """Maritime salvage under LOF or contract."""
    salvage_id: str
    vessel_imo: str
    salved_value: Fraction
    
    # LOF (Lloyd's Open Form) or contract
    lof_used: bool
    contract_value: Optional[Fraction]
    
    # Result
    services_rendered: str
    environmental_threatened: bool
    
    # Award
    salvage_award: Optional[Fraction]
    award_percentage: Optional[Fraction]  # Of salved value


@dataclass
class MaritimeChecker:
    """Checker for maritime compliance and safety."""
    vessels: List[Vessel] = field(default_factory=list)
    cargoes: List[Cargo] = field(default_factory=list)
    incidents: List[MaritimeIncident] = field(default_factory=list)
    ga_declarations: List[GeneralAverage] = field(default_factory=list)
    
    def substandard_vessels(self) -> List[Vessel]:
        """Vessels with poor flag state or deficiencies."""
        return [v for v in self.vessels if v.flag_state.black_list]
    
    def undermanned_vessels(self) -> List[Vessel]:
        """Vessels below safe manning levels."""
        return [v for v in self.vessels if not v.adequately_manned()]
    
    def serious_incidents(self) -> List[MaritimeIncident]:
        """Incidents with casualties or major damage."""
        return [
            i for i in self.incidents
            if i.fatalities > 0 or i.vessel_damage > Fraction(1, 2)
        ]
    
    def hazmat_violations(self) -> List[Cargo]:
        """Dangerous goods not properly declared."""
        # TODO: Expand hazmat_violations() - stub detected by Yeshua Agent
        return [c for c in self.cargoes if c.dangerous_goods and not c.imdg_class]

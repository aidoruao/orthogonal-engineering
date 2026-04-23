"""D_MINING implementation — Mining Operations & Resource Extraction

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- MSHA (Mine Safety and Health Administration)
- 30 CFR (Code of Federal Regulations)
- Sustainability (GRI, SASB)
- Environmental impact (NEPA, EIA)
- Worker safety (black lung, ventilation)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class MineType(Enum):
    """Types of mining operations."""
    UNDERGROUND_COAL = auto()
    SURFACE_COAL = auto()
    UNDERGROUND_METAL = auto()
    OPEN_PIT = auto()
    QUARRY = auto()
    PLACER = auto()
    SOLUTION = auto()


class MineStatus(Enum):
    """Operational status."""
    ACTIVE = auto()
    IDLE = auto()
    RECLAIMING = auto()
    CLOSED = auto()
    ABANDONED = auto()


@dataclass
class MiningOperation:
    """Mine site and operations."""
    mine_id: str
    mine_name: str
    mine_type: MineType
    status: MineStatus
    
    # Location
    state: str
    msha_id: str  # MSHA jurisdiction ID
    
    # Workforce
    total_employees: int
    underground_workers: int
    
    # Production
    annual_tonnage: int
    primary_commodity: str
    
    # Safety
    ventilation_cfms: int  # Cubic feet per minute
    escapeways: int
    
    # Compliance
    msha_inspections_annual: int
    violations_pending: int
    
    def has_adequate_ventilation(self) -> bool:
        """MSHA requires minimum ventilation per worker."""
        if self.underground_workers == 0:
            return True
        cfm_per_worker = self.ventilation_cfms / self.underground_workers
        return cfm_per_worker >= 100  # Minimum 100 CFM per worker
    
    def accident_rate(self, injuries_annual: int) -> Fraction:
        """Injuries per 200,000 hours (100 workers/year)."""
        if self.total_employees == 0:
            return Fraction(0)
        hours = self.total_employees * 2000  # 2000 hours/year
        rate = Fraction(injuries_annual * 200000, hours)
        return rate


@dataclass
class SafetyIncident:
    """MSHA-reportable incident."""
    incident_id: str
    mine_id: str
    incident_date: datetime
    
    incident_type: str  # fatality, injury, near-miss, ignition
    classification: str  # MSHA class code
    
    # Details
    injured_count: int
    fatality: bool
    
    # Investigation
    msha_investigation: bool
    root_cause_identified: bool
    corrective_actions: List[str] = field(default_factory=list)
    investigation_completeness_score: Fraction = Fraction(1, 1)


@dataclass
class EnvironmentalPermit:
    """Mining environmental compliance."""
    permit_id: str
    mine_id: str
    permit_type: str  # NPDES, air quality, waste
    
    issued_date: datetime
    expiration_date: datetime
    
    # Limits
    discharge_limits: Dict[str, Fraction]  # Parameter -> limit
    monitoring_required: bool
    permit_validity_fraction: Fraction = Fraction(1, 1)
    
    def is_current(self) -> bool:
        """Permit not expired."""
        return datetime.now() < self.expiration_date
    
    def days_until_expiration(self) -> int:
        """Days remaining."""
        return (self.expiration_date - datetime.now()).days


@dataclass
class ReclamationPlan:
    """Post-mining land restoration."""
    plan_id: str
    mine_id: str
    
    total_acres_disturbed: Fraction
    acres_reclaimed: Fraction
    
    bonding_amount: Fraction
    bonding_type: str  # surety, collateral, self-bond
    
    def reclamation_progress(self) -> Fraction:
        """Fraction of disturbed land reclaimed."""
        if self.total_acres_disturbed == 0:
            return Fraction(1)
        return self.acres_reclaimed / self.total_acres_disturbed
    
    def bonding_adequate(self) -> bool:
        """Bond covers estimated reclamation cost."""
        # Simplified: assume $5,000/acre
        estimated_cost = self.total_acres_disturbed * 5000
        return self.bonding_amount >= estimated_cost


@dataclass
class HealthMonitoring:
    """Occupational health tracking."""
    worker_id: str
    mine_id: str
    
    # Black lung / CWP
    chest_xray_date: Optional[datetime]
    xray_classification: str  # ILO classification
    
    # Dust exposure
    respirable_dust_mg_m3: Fraction
    silica_exceedance: bool
    
    # Hearing
    noise_exposure_dba: Fraction
    hearing_conservation_required: bool
    screening_compliance_score: Fraction = Fraction(1, 1)
    
    def pneumoconiosis_present(self) -> bool:
        """Coal workers' pneumoconiosis detected."""
        return self.xray_classification.startswith("1/") or \
               self.xray_classification.startswith("2/") or \
               self.xray_classification.startswith("3/")
    
    def dust_exposure_compliant(self, limit_mg_m3: Fraction) -> bool:
        """Dust exposure within MSHA limit."""
        return self.respirable_dust_mg_m3 <= limit_mg_m3


@dataclass
class MiningChecker:
    """Checker for mining safety and environmental compliance."""
    mines: List[MiningOperation] = field(default_factory=list)
    incidents: List[SafetyIncident] = field(default_factory=list)
    permits: List[EnvironmentalPermit] = field(default_factory=list)
    reclamation: List[ReclamationPlan] = field(default_factory=list)
    health: List[HealthMonitoring] = field(default_factory=list)
    
    def under_ventilated_mines(self) -> List[MiningOperation]:
        """Mines with inadequate ventilation."""
        return [m for m in self.mines if not m.has_adequate_ventilation()]
    
    def expired_permits(self) -> List[EnvironmentalPermit]:
        """Environmental permits past expiration."""
        return [p for p in self.permits if not p.is_current()]
    
    def unreclaimed_mines(self) -> List[ReclamationPlan]:
        """Mines with inadequate reclamation."""
        return [r for r in self.reclamation_plan if r.reclamation_progress() < Fraction(8, 10) ]
    
    def black_lung_cases(self) -> List[HealthMonitoring]:
        """Workers with CWP."""
        return [h for h in self.health if h.pneumoconiosis_present()]
    
    def fatalities(self) -> List[SafetyIncident]:
        """Fatal mining incidents."""
        return [i for i in self.incidents if i.fatality]

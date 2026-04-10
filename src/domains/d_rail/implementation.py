"""D_RAIL implementation — Rail Transport & Railway Operations

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- FRA regulations (49 CFR)
- Positive Train Control (PTC)
- Track safety standards
- Hours of service
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta
from fractions import Fraction


@dataclass
class RailVehicle:
    """Locomotive or railcar."""
    vehicle_id: str
    vehicle_type: str
    
    inspection_date: datetime
    inspection_due: datetime
    max_speed_mph: int
    
    ptc_equipped: bool
    ptc_operational: bool
    
    def inspection_current(self) -> bool:
        return datetime.now() < self.inspection_due


@dataclass
class Train:
    """Train consist and operation."""
    train_id: str
    locomotive: str
    cars: List[str]
    
    crew_size: int
    hours_of_service: Fraction
    
    max_speed: int
    authorized_speed: int
    
    def speed_compliant(self) -> bool:
        return self.max_speed <= self.authorized_speed
    
    def hours_compliant(self) -> bool:
        return self.hours_of_service <= Fraction(12)  # 12 hour limit


@dataclass
class TrackSegment:
    """Railway infrastructure."""
    segment_id: str
    milepost_start: int
    milepost_end: int
    
    track_class: int  # 1-6
    max_speed: int
    
    inspection_date: datetime
    defects_found: int


@dataclass
class RailChecker:
    """Checker for rail compliance."""
    vehicles: List[RailVehicle] = field(default_factory=list)
    trains: List[Train] = field(default_factory=list)
    tracks: List[TrackSegment] = field(default_factory=list)
    
    def overdue_inspections(self) -> List[RailVehicle]:
        return [v for v in self.vehicles if not v.inspection_current()]
    
    def speed_violations(self) -> List[Train]:
        return [t for t in self.trains if not t.speed_compliant()]
    
    def hours_violations(self) -> List[Train]:
        return [t for t in self.trains if not t.hours_compliant()]
    
    def ptc_non_compliant(self) -> List[RailVehicle]:
        return [v for v in self.vehicles if not v.ptc_equipped]

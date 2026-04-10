"""D_HOSPITALITY implementation — Hospitality Industry & Tourism

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- AH&LA lodging standards
- ADA Title III public accommodations
- FDA Food Code (retail food protection)
- Fire safety (NFPA 101 Life Safety Code)
- Sustainability certifications (LEED, Green Key)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class AccommodationType(Enum):
    """Types of lodging establishments."""
    HOTEL = auto()
    MOTEL = auto()
    RESORT = auto()
    BED_BREAKFAST = auto()
    HOSTEL = auto()
    VACATION_RENTAL = auto()
    CASINO_HOTEL = auto()


class RoomStatus(Enum):
    """Housekeeping status."""
    OCCUPIED = auto()
    VACANT_CLEAN = auto()
    VACANT_DIRTY = auto()
    OUT_OF_ORDER = auto()
    MAINTENANCE = auto()


@dataclass
class GuestRoom:
    """Individual lodging unit."""
    room_number: str
    room_type: str
    max_occupancy: int
    ada_accessible: bool
    status: RoomStatus
    
    # Revenue metrics
    rack_rate: Fraction  # Published rate
    floor: int
    square_feet: int
    
    def is_available(self) -> bool:
        """Room can be sold."""
        return self.status == RoomStatus.VACANT_CLEAN
    
    def revenue_per_available_room(self, actual_rate: Fraction) -> Fraction:
        """RevPAR contribution if sold at actual_rate."""
        if self.is_available():
            return actual_rate
        return Fraction(0)


@dataclass
class Property:
    """Hospitality property/facility."""
    property_id: str
    name: str
    property_type: AccommodationType
    star_rating: int  # 1-5
    
    # Capacity
    total_rooms: int
    rooms: List[GuestRoom] = field(default_factory=list)
    
    # Compliance
    ada_compliant: bool
    fire_inspection_current: bool
    health_inspection_score: Optional[Fraction] = None  # 0-100
    
    # Operations
    check_in_time: str = "15:00"
    check_out_time: str = "11:00"
    
    def occupancy_count(self) -> int:
        """Currently occupied rooms."""
        return sum(1 for r in self.rooms if r.status == RoomStatus.OCCUPIED)
    
    def occupancy_rate(self) -> Fraction:
        """Fraction of rooms occupied."""
        if self.total_rooms == 0:
            return Fraction(0)
        return Fraction(self.occupancy_count(), self.total_rooms)
    
    def available_rooms(self) -> int:
        """Rooms available for sale."""
        return sum(1 for r in self.rooms if r.is_available())
    
    def average_daily_rate(self, total_revenue: Fraction) -> Fraction:
        """ADR = total revenue / rooms sold."""
        sold = self.occupancy_count()
        if sold == 0:
            return Fraction(0)
        return total_revenue / sold
    
    def revpar(self, total_revenue: Fraction) -> Fraction:
        """Revenue per available room."""
        if self.total_rooms == 0:
            return Fraction(0)
        return total_revenue / self.total_rooms


@dataclass
class Reservation:
    """Booking record."""
    reservation_id: str
    guest_name: str
    property_id: str
    room_number: Optional[str]
    
    check_in: datetime
    check_out: datetime
    
    rate_per_night: Fraction
    total_charge: Fraction
    
    # ADA requirements
    ada_room_requested: bool
    accessibility_needs: List[str] = field(default_factory=list)
    
    def length_of_stay(self) -> int:
        """Number of nights."""
        return (self.check_out - self.check_in).days
    
    def no_show_charge_eligible(self) -> bool:
        """Can charge for no-show after check-in time passed."""
        from datetime import datetime
        now = datetime.now()
        return now > self.check_in + timedelta(hours=4)  # 4-hour grace


@dataclass
class FoodService:
    """On-site food and beverage operations."""
    outlet_id: str
    name: str
    outlet_type: str  # restaurant, bar, room service, etc.
    
    # Health inspection
    last_health_inspection: Optional[datetime]
    health_score: Optional[Fraction]  # 0-100
    critical_violations: int
    
    # Operations
    seating_capacity: int
    annual_revenue: Optional[Fraction] = None
    
    def inspection_current(self) -> bool:
        """Health inspection within required timeframe."""
        if self.last_health_inspection is None:
            return False
        days = (datetime.now() - self.last_health_inspection).days
        return days <= 180  # 6 months typical
    
    def critical_violation_threshold(self, threshold: int) -> bool:
        """Critical violations exceed acceptable level."""
        return self.critical_violations > threshold


@dataclass
class SustainabilityMetric:
    """Environmental performance indicators."""
    property_id: str
    year: int
    
    energy_use_per_occupied_room: Fraction  # kWh
    water_use_per_occupied_room: Fraction   # gallons
    waste_diversion_rate: Fraction  # 0-1
    
    carbon_offset_purchased: Fraction  # tonnes


@dataclass
class HospitalityChecker:
    """Checker for hospitality operations and compliance."""
    properties: List[Property] = field(default_factory=list)
    reservations: List[Reservation] = field(default_factory=list)
    food_outlets: List[FoodService] = field(default_factory=list)
    
    def properties_needing_ada_upgrade(self) -> List[Property]:
        """Properties not meeting ADA Title III requirements."""
        return [p for p in self.properties if not p.ada_compliant]
    
    def overdue_health_inspections(self) -> List[FoodService]:
        """Food outlets needing inspection."""
        return [f for f in self.food_outlets if not f.inspection_current()]
    
    def overbooked_properties(self) -> List[Property]:
        """Properties with more reservations than rooms."""
        result = []
        for prop in self.properties:
            res_count = sum(1 for r in self.reservations if r.property_id == prop.property_id)
            if res_count > prop.total_rooms:
                result.append(prop)
        return result
    
    def average_occupancy(self) -> Fraction:
        """Portfolio-wide occupancy."""
        if not self.properties:
            return Fraction(0)
        total = sum(p.occupancy_rate() for p in self.properties)
        return total / len(self.properties)

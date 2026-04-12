"""D_BUILDING_CODES implementation — Building Codes

Implements building code regulations including IBC structural requirements,
fire egress, and ADA accessibility standards.

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: International Building Code (IBC), NFPA 101, ADA Standards (28 CFR 36)

Biblical: Exodus 25:8-9 — "Then have them make a sanctuary for me, and I will
dwell among them. Make this tabernacle and all its furnishings exactly like
the pattern I will show you." (God's architectural specifications)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class OccupancyType(Enum):
    """IBC occupancy classifications."""
    ASSEMBLY = auto()           # Group A
    BUSINESS = auto()           # Group B
    EDUCATIONAL = auto()        # Group E
    FACTORY = auto()            # Group F
    HIGH_HAZARD = auto()        # Group H
    INSTITUTIONAL = auto()      # Group I
    MERCANTILE = auto()         # Group M
    RESIDENTIAL = auto()        # Group R
    STORAGE = auto()            # Group S
    UTILITY = auto()            # Group U


class ConstructionType(Enum):
    """IBC construction types (fire resistance)."""
    TYPE_IA = auto()   # Noncombustible, highest rating
    TYPE_IB = auto()
    TYPE_IIA = auto()
    TYPE_IIB = auto()
    TYPE_IIIA = auto()
    TYPE_IIIB = auto()
    TYPE_IV = auto()   # Heavy timber
    TYPE_VA = auto()
    TYPE_VB = auto()   # Combustible, lowest rating


class LoadType(Enum):
    """Types of structural loads per IBC."""
    DEAD_LOAD = auto()         # Permanent/static
    LIVE_LOAD = auto()         # Occupants/furniture
    SNOW_LOAD = auto()         # Snow accumulation
    WIND_LOAD = auto()         # Wind pressure
    SEISMIC_LOAD = auto()      # Earthquake
    RAIN_LOAD = auto()         # Rain/water accumulation
    FLOOD_LOAD = auto()        # Flood water


class EgressComponentType(Enum):
    """Types of egress components."""
    DOOR = auto()
    CORRIDOR = auto()
    STAIRWAY = auto()
    RAMP = auto()
    EXIT_PASSAGEWAY = auto()
    HORIZONTAL_EXIT = auto()


@dataclass
class StructuralLoad:
    """A structural load specification."""
    load_type: LoadType
    magnitude_psf: Fraction  # pounds per square foot
    load_factor: Fraction = Fraction(1, 1)  # Safety factor
    
    @property
    def factored_load(self) -> Fraction:
        """Load multiplied by safety factor."""
        return self.magnitude_psf * self.load_factor


@dataclass
class BuildingStructure:
    """A building's structural system."""
    building_id: str
    name: str
    address: str
    
    # Classification
    occupancy_type: OccupancyType
    construction_type: ConstructionType
    height_ft: Fraction
    area_sqft: Fraction
    num_stories: int
    
    # Loads
    design_loads: List[StructuralLoad] = field(default_factory=list)
    
    # Structural elements
    has_sprinkler_system: bool = False
    occupancy_load_factor: Fraction = Fraction(100)  # Default psf


@dataclass
class LoadCalculation:
    """Structural load calculation results."""
    calculation_id: str
    building_id: str
    element: str  # Beam, column, slab, etc.
    
    # Load combinations per IBC Section 1605
    dead_load: Fraction
    live_load: Fraction
    
    # Results (required)
    calculated_capacity: Fraction
    applied_load: Fraction
    
    # Optional
    other_loads: Dict[LoadType, Fraction] = field(default_factory=dict)
    
    @property
    def safety_ratio(self) -> Fraction:
        """Ratio of capacity to applied load (must be >= 1.0)."""
        if self.applied_load == 0:
            return Fraction(100)  # No load = infinite safety
        return self.calculated_capacity / self.applied_load
    
    @property
    def within_tolerance(self) -> bool:
        """Check if within IBC tolerance (safety ratio >= 1.0)."""
        return self.safety_ratio >= Fraction(1)


@dataclass
class EgressComponent:
    """A component of the means of egress."""
    component_id: str
    component_type: EgressComponentType
    
    # Capacity
    width_inches: Fraction
    capacity_persons: int
    
    # Requirements
    required_width_inches: Fraction = Fraction(44)  # Minimum per IBC
    required_capacity: int = 50
    
    # Status
    is_accessible: bool = True
    is_illuminated: bool = True
    has_emergency_lighting: bool = True
    
    @property
    def width_compliant(self) -> bool:
        """Check if width meets IBC requirements."""
        return self.width_inches >= self.required_width_inches
    
    @property
    def capacity_compliant(self) -> bool:
        """Check if capacity meets requirements."""
        return self.capacity_persons >= self.required_capacity


@dataclass
class EgressSystem:
    """Complete means of egress for a building."""
    building_id: str
    occupancy_type: OccupancyType
    occupant_load: int
    
    # Components
    exits: List[EgressComponent] = field(default_factory=list)
    
    # Travel distances (feet)
    max_travel_distance: Fraction = Fraction(200)
    actual_max_travel_distance: Fraction = Fraction(0)
    
    # Requirements per occupancy
    required_exit_capacity: int = 0
    required_number_exits: int = 2


@dataclass
class ADAFeature:
    """An ADA accessibility feature."""
    feature_id: str
    feature_type: str  # "ramp", "elevator", "door", "parking", etc.
    
    # Measurements (inches)
    slope_ratio: Optional[Fraction] = None  # 1:12 max for ramps
    width_inches: Optional[Fraction] = None
    turning_space_sqft: Optional[Fraction] = None
    
    # Compliance
    compliant: bool = True
    noncompliance_issues: List[str] = field(default_factory=list)


@dataclass
class AccessibleRoute:
    """An accessible route per ADA Standards."""
    route_id: str
    start_location: str
    end_location: str
    
    components: List[ADAFeature] = field(default_factory=list)
    
    @property
    def fully_compliant(self) -> bool:
        """Check if all components are compliant."""
        return all(c.compliant for c in self.components)


class StructuralEngineer:
    """Structural engineering calculations per IBC."""
    
    # IBC load factors
    DEAD_LOAD_FACTOR = Fraction(12, 10)  # 1.2
    LIVE_LOAD_FACTOR = Fraction(16, 10)  # 1.6
    
    def calculate_load_combination(self, loads: List[StructuralLoad]) -> Dict:
        """
        Calculate load combinations per IBC Section 1605.
        
        Basic combination: 1.2D + 1.6L + 0.5(Lr or S or R)
        """
        dead_load = Fraction(0)
        live_load = Fraction(0)
        other_load = Fraction(0)
        
        for load in loads:
            if load.load_type == LoadType.DEAD_LOAD:
                dead_load += load.magnitude_psf
            elif load.load_type == LoadType.LIVE_LOAD:
                live_load += load.magnitude_psf
            else:
                other_load += load.magnitude_psf
        
        # Basic load combination
        total_load = (
            self.DEAD_LOAD_FACTOR * dead_load +
            self.LIVE_LOAD_FACTOR * live_load +
            Fraction(5, 10) * other_load
        )
        
        return {
            "dead_load": dead_load,
            "live_load": live_load,
            "other_load": other_load,
            "factored_total": total_load,
        }
    
    def check_member_capacity(self, calculation: LoadCalculation) -> Dict:
        """Check if structural member has adequate capacity."""
        return {
            "element": calculation.element,
            "capacity": calculation.calculated_capacity,
            "applied_load": calculation.applied_load,
            "safety_ratio": calculation.safety_ratio,
            "within_tolerance": calculation.within_tolerance,
            "compliant": calculation.within_tolerance,
        }


class FireEgressPlanner:
    """Fire egress planning per IBC Chapter 10."""
    
    # IBC minimum egress widths (inches per occupant)
    STAIRS_WIDTH_PER_OCCUPANT = Fraction(3, 10)  # 0.3"
    OTHER_COMPONENTS_WIDTH_PER_OCCUPANT = Fraction(2, 10)  # 0.2"
    
    def calculate_required_exits(self, occupant_load: int, 
                                  occupancy_type: OccupancyType) -> Dict:
        """
        Calculate required number of exits per IBC 1006.2.
        
        - 1-500 occupants: 2 exits
        - 501-1000: 3 exits
        - 1001+: 4 exits
        """
        if occupant_load <= 500:
            required_exits = 2
        elif occupant_load <= 1000:
            required_exits = 3
        else:
            required_exits = 4
        
        # Special cases for high hazard
        if occupancy_type == OccupancyType.HIGH_HAZARD and occupant_load > 29:
            required_exits = max(required_exits, 2)
        
        return {
            "occupant_load": occupant_load,
            "occupancy_type": occupancy_type.name,
            "required_exits": required_exits,
        }
    
    def check_egress_capacity(self, egress_system: EgressSystem) -> Dict:
        """Check if egress system meets capacity requirements."""
        required = self.calculate_required_exits(
            egress_system.occupant_load,
            egress_system.occupancy_type
        )
        
        num_exits = len(egress_system.exits)
        exits_compliant = num_exits >= required["required_exits"]
        
        # Check each exit component
        component_checks = []
        for exit_comp in egress_system.exits:
            component_checks.append({
                "id": exit_comp.component_id,
                "type": exit_comp.component_type.name,
                "width_compliant": exit_comp.width_compliant,
                "capacity_compliant": exit_comp.capacity_compliant,
            })
        
        all_components_compliant = all(
            c["width_compliant"] and c["capacity_compliant"]
            for c in component_checks
        )
        
        return {
            "num_exits": num_exits,
            "required_exits": required["required_exits"],
            "exits_compliant": exits_compliant,
            "components_compliant": all_components_compliant,
            "component_details": component_checks,
            "egress_compliant": exits_compliant and all_components_compliant,
        }


class ADAComplianceChecker:
    """ADA compliance checker for public accommodations."""
    
    # ADA Standards requirements
    MAX_RAMP_SLOPE = Fraction(1, 12)  # 1:12 maximum slope
    MIN_DOOR_WIDTH = Fraction(32)  # 32 inches clear
    MIN_PARKING_ACCESSIBLE = Fraction(1, 50)  # 1 per 50 spaces, min 1
    
    def check_ramp_slope(self, rise_inches: Fraction, 
                         run_inches: Fraction) -> Dict:
        """Check if ramp slope meets ADA requirements."""
        if run_inches == 0:
            return {"compliant": False, "error": "Zero run length"}
        
        actual_slope = rise_inches / run_inches
        compliant = actual_slope <= self.MAX_RAMP_SLOPE
        
        return {
            "rise": rise_inches,
            "run": run_inches,
            "slope": actual_slope,
            "max_allowed": self.MAX_RAMP_SLOPE,
            "compliant": compliant,
        }
    
    def check_accessible_parking(self, total_spaces: int, 
                                  accessible_spaces: int) -> Dict:
        """Check accessible parking ratio per ADA Standards."""
        required = max(1, int(Fraction(total_spaces) * self.MIN_PARKING_ACCESSIBLE))
        
        # Special requirements for larger lots
        if total_spaces >= 501:
            required = 10 + (total_spaces - 500) // 100
        
        compliant = accessible_spaces >= required
        
        return {
            "total_spaces": total_spaces,
            "accessible_spaces": accessible_spaces,
            "required_accessible": required,
            "compliant": compliant,
        }
    
    def check_accessible_route(self, route: AccessibleRoute) -> Dict:
        """Check if accessible route is fully compliant."""
        noncompliant_components = [
            c for c in route.components if not c.compliant
        ]
        
        return {
            "route_id": route.route_id,
            "num_components": len(route.components),
            "noncompliant_count": len(noncompliant_components),
            "fully_compliant": len(noncompliant_components) == 0,
            "noncompliant_details": [
                {"id": c.feature_id, "type": c.feature_type, 
                 "issues": c.noncompliance_issues}
                for c in noncompliant_components
            ],
        }


class BuildingCodeAuditor:
    """Comprehensive building code compliance auditor."""
    
    def __init__(self):
        self.structural_engineer = StructuralEngineer()
        self.egress_planner = FireEgressPlanner()
        self.ada_checker = ADAComplianceChecker()
    
    def audit_structure(self, structure: BuildingStructure) -> Dict:
        """Audit building structure for IBC compliance."""
        # Check load calculations
        load_results = []
        for load in structure.design_loads:
            calc = self.structural_engineer.calculate_load_combination([load])
            load_results.append(calc)
        
        return {
            "building_id": structure.building_id,
            "occupancy": structure.occupancy_type.name,
            "construction_type": structure.construction_type.name,
            "height_ft": structure.height_ft,
            "load_calculations": len(load_results),
        }
    
    def audit_egress(self, egress_system: EgressSystem) -> Dict:
        """Audit egress system for IBC compliance."""
        return self.egress_planner.check_egress_capacity(egress_system)
    
    def audit_ada(self, route: AccessibleRoute) -> Dict:
        """Audit ADA compliance."""
        return self.ada_checker.check_accessible_route(route)


# Convenience functions
def check_structural_tolerance(capacity: float, applied: float) -> Dict:
    """Quick check if structural capacity is within tolerance."""
    calc = LoadCalculation(
        calculation_id="QUICK",
        building_id="TEMP",
        element="QUICK_CHECK",
        dead_load=Fraction(0),
        live_load=Fraction(0),
        calculated_capacity=Fraction(capacity).limit_denominator(100),
        applied_load=Fraction(applied).limit_denominator(100),
    )
    return {
        "safety_ratio": calc.safety_ratio,
        "within_tolerance": calc.within_tolerance,
    }


def check_fire_egress(occupant_load: int, num_exits: int) -> Dict:
    """Quick check of fire egress requirements."""
    planner = FireEgressPlanner()
    required = planner.calculate_required_exits(occupant_load, OccupancyType.ASSEMBLY)
    
    return {
        "occupant_load": occupant_load,
        "num_exits": num_exits,
        "required_exits": required["required_exits"],
        "compliant": num_exits >= required["required_exits"],
    }


def check_ada_ramp(rise_inches: float, run_inches: float) -> Dict:
    """Quick check of ADA ramp slope."""
    checker = ADAComplianceChecker()
    return checker.check_ramp_slope(
        Fraction(rise_inches).limit_denominator(100),
        Fraction(run_inches).limit_denominator(100)
    )

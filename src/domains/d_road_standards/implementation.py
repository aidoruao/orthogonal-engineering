"""D_ROAD_STANDARDS implementation — Road Standards

Implements road standards including speed limits, traffic signal timing,
and maintenance scheduling.

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: MUTCD (Manual on Uniform Traffic Control Devices), AASHTO

Biblical: Isaiah 40:3 — "Prepare the way for the Lord; make straight
in the wilderness a highway for our God."
Also: Proverbs 4:26 — "Give careful thought to the paths for your feet
and be steadfast in all your ways."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class RoadClassification(Enum):
    """Standard road classifications."""
    INTERSTATE = auto()
    FREEWAY = auto()
    PRINCIPAL_ARTERIAL = auto()
    MINOR_ARTERIAL = auto()
    MAJOR_COLLECTOR = auto()
    MINOR_COLLECTOR = auto()
    LOCAL_RESIDENTIAL = auto()
    LOCAL_COMMERCIAL = auto()
    ALLEY = auto()


class SignalPhase(Enum):
    """Traffic signal phases."""
    RED = auto()
    YELLOW = auto()
    GREEN = auto()
    LEFT_GREEN_ARROW = auto()
    YELLOW_ARROW = auto()
    RED_ARROW = auto()


class MaintenanceType(Enum):
    """Types of road maintenance."""
    PAVEMENT_REPAIR = auto()
    STRIPE_MARKING = auto()
    SIGN_REPLACEMENT = auto()
    SIGNAL_MAINTENANCE = auto()
    DRAINAGE_CLEANING = auto()
    VEGETATION_CONTROL = auto()
    WINTER_MAINTENANCE = auto()


@dataclass
class RoadSegment:
    """A segment of roadway."""
    segment_id: str
    road_name: str
    
    # Classification
    classification: RoadClassification
    
    # Physical characteristics
    length_miles: Fraction
    num_lanes: int
    lane_width_ft: Fraction
    shoulder_width_ft: Fraction
    
    # Environment
    urban: bool = True
    has_sidewalks: bool = False
    has_bike_lanes: bool = False
    
    # Posted limit (may differ from calculated)
    posted_speed_limit: Optional[int] = None


@dataclass
class SpeedLimitCalculation:
    """Calculated speed limit based on road characteristics."""
    segment_id: str
    
    # Inputs
    classification: RoadClassification
    lane_width_ft: Fraction
    shoulder_width_ft: Fraction
    urban: bool
    
    # Calculated limit
    calculated_limit_mph: int
    
    # Deterministic - same inputs always produce same output
    calculation_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficSignal:
    """A traffic signal at an intersection."""
    signal_id: str
    intersection_name: str
    
    # Timing parameters (seconds)
    minimum_green: Fraction = Fraction(7)      # Minimum green time
    yellow_change: Fraction = Fraction(3)      # Yellow interval
    all_red_clearance: Fraction = Fraction(1)  # All-red clearance
    
    # Pedestrian timing
    walk_time: Fraction = Fraction(7)          # Walk interval
    flashing_dont_walk: Fraction = Fraction(10)  # Pedestrian clearance
    
    # Current state
    current_phase: SignalPhase = SignalPhase.RED
    phase_start_time: Optional[datetime] = None


@dataclass
class TrafficConditions:
    """Traffic conditions at an intersection."""
    intersection_id: str
    timestamp: datetime
    
    # Volume (vehicles per hour)
    approach_volumes: Dict[str, int]  # direction -> vph
    
    # Occupancy
    detector_occupancy: Dict[str, Fraction]  # lane -> percentage
    
    # Pedestrians
    pedestrian_calls: Dict[str, bool]  # crosswalk -> has call


@dataclass
class SignalTimingPlan:
    """A calculated signal timing plan."""
    plan_id: str
    signal_id: str
    
    # Calculated timing
    green_times: Dict[str, Fraction]  # phase -> seconds
    cycle_length: Fraction
    
    # Based on conditions
    traffic_conditions_hash: str  # Hash of input conditions
    
    # Verification
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class MaintenanceSchedule:
    """Scheduled maintenance activity."""
    schedule_id: str
    segment_id: str
    maintenance_type: MaintenanceType
    
    # Schedule
    scheduled_date: datetime
    estimated_duration_hours: int
    
    # Execution
    executed_date: Optional[datetime] = None
    actual_duration_hours: Optional[int] = None
    completed: bool = False
    
    # Documentation
    work_order_number: Optional[str] = None
    crew_assigned: Optional[str] = None
    materials_used: List[str] = field(default_factory=list)


class SpeedLimitEngine:
    """Engine for calculating speed limits."""
    
    # Base speed limits by classification (urban)
    URBAN_BASE_LIMITS = {
        RoadClassification.INTERSTATE: 65,
        RoadClassification.FREEWAY: 65,
        RoadClassification.PRINCIPAL_ARTERIAL: 45,
        RoadClassification.MINOR_ARTERIAL: 35,
        RoadClassification.MAJOR_COLLECTOR: 30,
        RoadClassification.MINOR_COLLECTOR: 25,
        RoadClassification.LOCAL_RESIDENTIAL: 25,
        RoadClassification.LOCAL_COMMERCIAL: 25,
        RoadClassification.ALLEY: 15,
    }
    
    # Rural adjustments (+5 to +15 mph)
    RURAL_ADJUSTMENTS = {
        RoadClassification.PRINCIPAL_ARTERIAL: 20,
        RoadClassification.MINOR_ARTERIAL: 20,
        RoadClassification.MAJOR_COLLECTOR: 15,
        RoadClassification.MINOR_COLLECTOR: 15,
        RoadClassification.LOCAL_RESIDENTIAL: 10,
    }
    
    def calculate_speed_limit(self, segment: RoadSegment) -> SpeedLimitCalculation:
        """
        Calculate speed limit deterministically based on road characteristics.
        
        Invariant: Speed limit is deterministic per road classification.
        """
        # Base limit from classification
        base_limit = self.URBAN_BASE_LIMITS.get(segment.classification, 25)
        
        # Rural adjustment
        if not segment.urban:
            adjustment = self.RURAL_ADJUSTMENTS.get(segment.classification, 0)
            base_limit += adjustment
        
        # Lane width adjustment
        if segment.lane_width_ft < Fraction(10):
            base_limit -= 5  # Narrow lanes = lower speed
        elif segment.lane_width_ft >= Fraction(12):
            base_limit += 5  # Wide lanes = higher speed
        
        # Shoulder adjustment
        if segment.shoulder_width_ft < Fraction(2):
            base_limit -= 5  # Minimal shoulder
        
        # Clamp to reasonable range
        calculated = max(15, min(75, base_limit))
        
        return SpeedLimitCalculation(
            segment_id=segment.segment_id,
            classification=segment.classification,
            lane_width_ft=segment.lane_width_ft,
            shoulder_width_ft=segment.shoulder_width_ft,
            urban=segment.urban,
            calculated_limit_mph=calculated,
        )
    
    def check_speed_limit_compliance(self, segment: RoadSegment) -> Dict:
        """Check if posted speed limit matches calculated limit."""
        calculation = self.calculate_speed_limit(segment)
        
        if segment.posted_speed_limit is None:
            return {
                "segment_id": segment.segment_id,
                "posted": None,
                "calculated": calculation.calculated_limit_mph,
                "compliant": False,
                "issue": "No posted speed limit",
            }
        
        matches = segment.posted_speed_limit == calculation.calculated_limit_mph
        
        return {
            "segment_id": segment.segment_id,
            "posted": segment.posted_speed_limit,
            "calculated": calculation.calculated_limit_mph,
            "compliant": matches,
            "variance_mph": abs(segment.posted_speed_limit - calculation.calculated_limit_mph),
        }


class SignalTimingEngine:
    """Engine for calculating traffic signal timing."""
    
    # Webster's method coefficients
    LOST_TIME_PER_PHASE = Fraction(3)  # Seconds lost per phase
    SATURATION_FLOW_RATE = Fraction(1800)  # Vehicles per hour per lane
    
    def calculate_timing(self, signal: TrafficSignal,
                         conditions: TrafficConditions) -> SignalTimingPlan:
        """
        Calculate signal timing based on traffic conditions.
        
        Invariant: Signal timing is reproducible for given traffic conditions.
        """
        # Calculate total volume
        total_volume = sum(conditions.approach_volumes.values())
        
        # Calculate green times proportionally
        green_times = {}
        total_green = Fraction(0)
        
        for direction, volume in conditions.approach_volumes.items():
            if total_volume > 0:
                ratio = Fraction(volume, total_volume)
            else:
                ratio = Fraction(1, 4)  # Equal split if no volume
            
            # Base green time + proportional allocation
            green_time = signal.minimum_green + (ratio * Fraction(30))
            green_times[direction] = green_time
            total_green += green_time
        
        # Add yellow and all-red for each phase
        num_phases = len(conditions.approach_volumes)
        clearance_time = num_phases * (signal.yellow_change + signal.all_red_clearance)
        
        # Cycle length
        cycle_length = total_green + clearance_time
        
        # Create hash of conditions for reproducibility verification
        conditions_str = f"{signal.signal_id}:{total_volume}:{sorted(conditions.approach_volumes.items())}"
        conditions_hash = hash(conditions_str) % 1000000
        
        return SignalTimingPlan(
            plan_id=f"PLAN_{signal.signal_id}_{conditions_hash}",
            signal_id=signal.signal_id,
            green_times=green_times,
            cycle_length=cycle_length,
            traffic_conditions_hash=str(conditions_hash),
        )
    
    def verify_reproducibility(self, signal: TrafficSignal,
                                conditions: TrafficConditions) -> Dict:
        """Verify that timing calculation is reproducible."""
        # Calculate timing twice
        plan1 = self.calculate_timing(signal, conditions)
        plan2 = self.calculate_timing(signal, conditions)
        
        return {
            "signal_id": signal.signal_id,
            "reproducible": plan1.green_times == plan2.green_times and
                           plan1.cycle_length == plan2.cycle_length,
            "cycle_length": plan1.cycle_length,
            "conditions_hash": plan1.traffic_conditions_hash,
        }


class MaintenanceScheduler:
    """Scheduler for road maintenance activities."""
    
    # Standard maintenance intervals
    MAINTENANCE_INTERVALS = {
        MaintenanceType.PAVEMENT_REPAIR: timedelta(days=365),      # Annual
        MaintenanceType.STRIPE_MARKING: timedelta(days=730),       # Biennial
        MaintenanceType.SIGN_REPLACEMENT: timedelta(days=1095),    # 3 years
        MaintenanceType.SIGNAL_MAINTENANCE: timedelta(days=180),   # Semi-annual
        MaintenanceType.DRAINAGE_CLEANING: timedelta(days=365),    # Annual
        MaintenanceType.VEGETATION_CONTROL: timedelta(days=90),    # Quarterly
        MaintenanceType.WINTER_MAINTENANCE: timedelta(days=1),     # As needed
    }
    
    def __init__(self):
        self.schedules: Dict[str, MaintenanceSchedule] = {}
    
    def create_schedule(self, schedule_id: str, segment_id: str,
                        maintenance_type: MaintenanceType,
                        scheduled_date: datetime) -> MaintenanceSchedule:
        """Create a maintenance schedule entry."""
        schedule = MaintenanceSchedule(
            schedule_id=schedule_id,
            segment_id=segment_id,
            maintenance_type=maintenance_type,
            scheduled_date=scheduled_date,
            estimated_duration_hours=4,  # Default
        )
        self.schedules[schedule_id] = schedule
        return schedule
    
    def execute_maintenance(self, schedule_id: str, 
                            work_order: str,
                            crew: str) -> Dict:
        """Record maintenance execution."""
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return {"error": "Schedule not found"}
        
        schedule.executed_date = datetime.now()
        schedule.work_order_number = work_order
        schedule.crew_assigned = crew
        schedule.completed = True
        
        return {
            "schedule_id": schedule_id,
            "executed": True,
            "work_order": work_order,
            "crew": crew,
        }
    
    def check_schedule_compliance(self, schedule_id: str) -> Dict:
        """
        Check if maintenance was performed as scheduled.
        
        Invariant: Maintenance schedule is logged and executed.
        """
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return {"error": "Schedule not found"}
        
        executed = schedule.completed and schedule.executed_date is not None
        documented = schedule.work_order_number is not None
        has_crew = schedule.crew_assigned is not None
        
        return {
            "schedule_id": schedule_id,
            "scheduled_date": schedule.scheduled_date,
            "executed": executed,
            "documented": documented,
            "has_crew_assignment": has_crew,
            "compliant": executed and documented and has_crew,
        }


class RoadStandardsAuditor:
    """Comprehensive auditor for road standards."""
    
    def __init__(self):
        self.speed_engine = SpeedLimitEngine()
        self.signal_engine = SignalTimingEngine()
        self.maintenance_scheduler = MaintenanceScheduler()
    
    def audit_speed_limit(self, segment: RoadSegment) -> Dict:
        """Audit speed limit for a road segment."""
        return self.speed_engine.check_speed_limit_compliance(segment)
    
    def audit_signal_timing(self, signal: TrafficSignal,
                            conditions: TrafficConditions) -> Dict:
        """Audit signal timing reproducibility."""
        return self.signal_engine.verify_reproducibility(signal, conditions)
    
    def audit_maintenance(self, schedule_id: str) -> Dict:
        """Audit maintenance schedule compliance."""
        return self.maintenance_scheduler.check_schedule_compliance(schedule_id)


# Convenience functions
def check_speed_limit_determinism(segment: RoadSegment) -> Dict:
    """Quick check of speed limit calculation determinism."""
    engine = SpeedLimitEngine()
    calc1 = engine.calculate_speed_limit(segment)
    calc2 = engine.calculate_speed_limit(segment)
    
    return {
        "segment_id": segment.segment_id,
        "deterministic": calc1.calculated_limit_mph == calc2.calculated_limit_mph,
        "calculated_limit": calc1.calculated_limit_mph,
    }


def check_signal_reproducibility(signal: TrafficSignal,
                                  conditions: TrafficConditions) -> Dict:
    """Quick check of signal timing reproducibility."""
    engine = SignalTimingEngine()
    return engine.verify_reproducibility(signal, conditions)


def check_maintenance_logged(schedule: MaintenanceSchedule) -> Dict:
    """Quick check of maintenance logging."""
    return {
        "schedule_id": schedule.schedule_id,
        "logged": schedule.completed and schedule.work_order_number is not None,
        "completed": schedule.completed,
        "has_work_order": schedule.work_order_number is not None,
    }

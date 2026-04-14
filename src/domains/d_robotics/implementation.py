#!/usr/bin/env python3
"""
Robotics Domain — ISO 10218 Safety, Collaborative Robotics

Key standards:
- ISO 10218-1: Robots and robotic devices — Safety requirements
- ISO/TS 15066: Collaborative robots safety requirements
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum, auto


class RobotMode(Enum):
    AUTOMATIC = auto()
    MANUAL = auto()
    COLLABORATIVE = auto()


@dataclass
class SafetyZone:
    """ISO 10218 safety zone definition."""
    zone_id: str
    center_x: Fraction
    center_y: Fraction
    radius: Fraction
    max_force_limit: Fraction = Fraction(150)  # Newtons for collaborative
    
    def contains_point(self, x: Fraction, y: Fraction) -> bool:
        """Check if point is within safety zone."""
        dx = x - self.center_x
        dy = y - self.center_y
        distance_squared = dx * dx + dy * dy
        return distance_squared <= self.radius * self.radius


@dataclass
class ForceSensor:
    """Force/torque sensor reading."""
    sensor_id: str
    force_x: Fraction = Fraction(0)
    force_y: Fraction = Fraction(0)
    force_z: Fraction = Fraction(0)
    
    def resultant_force(self) -> Fraction:
        """Calculate resultant force magnitude."""
        return Fraction((self.force_x ** 2 + self.force_y ** 2 + self.force_z ** 2).numerator ** Fraction(1, 2))


@dataclass
class SafetyZoneAnalyzer:
    """Analyze robot safety zones."""
    zones: List[SafetyZone]
    human_detected_position: Tuple[Fraction, Fraction] = (Fraction(0), Fraction(0))
    
    def human_in_any_zone(self) -> bool:
        """Check if human is within any safety zone."""
        x, y = self.human_detected_position
        return any(zone.contains_point(x, y) for zone in self.zones)
    
    def get_active_zone(self) -> Optional[SafetyZone]:
        """Get zone containing human, if any."""
        x, y = self.human_detected_position
        for zone in self.zones:
            if zone.contains_point(x, y):
                return zone
        return None


@dataclass
class EmergencyStopSystem:
    """Emergency stop response monitoring."""
    e_stop_triggered: bool = False
    trigger_time_ms: Fraction = Fraction(0)
    stop_completed_time_ms: Optional[Fraction] = None
    
    MAX_RESPONSE_TIME_MS = Fraction(500)  # ISO 10218 requirement
    
    def response_time(self) -> Fraction:
        """Calculate e-stop response time."""
        if self.stop_completed_time_ms is None:
            return Fraction(0)
        return self.stop_completed_time_ms - self.trigger_time_ms
    
    def meets_response_requirement(self) -> bool:
        """Check if response time within ISO 10218 limits."""
        return self.response_time() <= self.MAX_RESPONSE_TIME_MS


@dataclass
class CollaborativeRobot:
    """Collaborative robot with force limiting."""
    robot_id: str
    mode: RobotMode
    force_sensors: List[ForceSensor]
    safety_zones: List[SafetyZone]
    
    COLLABORATIVE_FORCE_LIMIT_N = Fraction(150)  # ISO/TS 15066
    
    def max_force_exerted(self) -> Fraction:
        """Maximum force across all sensors."""
        if not self.force_sensors:
            return Fraction(0)
        return max(s.resultant_force() for s in self.force_sensors)
    
    def is_force_compliant(self) -> bool:
        """Check if forces within collaborative limits."""
        if self.mode != RobotMode.COLLABORATIVE:
            return True
        return self.max_force_exerted() <= self.COLLABORATIVE_FORCE_LIMIT_N


from typing import Optional

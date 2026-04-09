#!/usr/bin/env python3
"""
Aerospace Domain — DO-178C Certification, Redundancy, Structural Health

Key standards:
- DO-178C: Software considerations in airborne systems
- DO-254: Hardware assurance
- ARP4754A: Development of civil aircraft systems
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum, auto


class CertificationLevel(Enum):
    """DO-178C Design Assurance Levels (DAL)."""
    LEVEL_A = auto()  # Catastrophic failure condition
    LEVEL_B = auto()  # Hazardous/severe-major
    LEVEL_C = auto()  # Major
    LEVEL_D = auto()  # Minor
    LEVEL_E = auto()  # No safety effect


@dataclass
class SoftwareComponent:
    """Software component with DO-178C certification data."""
    name: str
    dal: CertificationLevel
    lines_of_code: int
    
    # Testing requirements per DO-178C Table A-1
    requirements_based_tests: int = 0
    structural_coverage_mc_dc: Fraction = Fraction(0)  # Modified condition/decision
    structural_coverage_decision: Fraction = Fraction(0)
    structural_coverage_statement: Fraction = Fraction(0)
    
    def required_mc_dc_coverage(self) -> Fraction:
        """Level A requires 100% MC/DC coverage."""
        if self.dal == CertificationLevel.LEVEL_A:
            return Fraction(100)
        if self.dal == CertificationLevel.LEVEL_B:
            return Fraction(100)  # Decision coverage
        return Fraction(0)
    
    def meets_coverage(self) -> bool:
        """Check if component meets required structural coverage."""
        if self.dal == CertificationLevel.LEVEL_A:
            return self.structural_coverage_mc_dc >= Fraction(100)
        if self.dal == CertificationLevel.LEVEL_B:
            return self.structural_coverage_decision >= Fraction(100)
        if self.dal == CertificationLevel.LEVEL_C:
            return self.structural_coverage_statement >= Fraction(100)
        return True


@dataclass
class RedundantChannel:
    """Redundant flight control channel."""
    channel_id: str
    is_active: bool = True
    output_value: Fraction = Fraction(0)
    health_status: str = "HEALTHY"  # HEALTHY, DEGRADED, FAILED
    
    def is_healthy(self) -> bool:
        return self.health_status == "HEALTHY"


@dataclass
class RedundancyChecker:
    """Triple modular redundancy (TMR) or dual channel redundancy."""
    channels: List[RedundantChannel]
    required_agreement: Fraction = Fraction(2, 3)  # Majority voting
    
    def get_healthy_channels(self) -> List[RedundantChannel]:
        return [c for c in self.channels if c.is_healthy()]
    
    def channels_agree(self) -> bool:
        """Check if healthy channels agree on output."""
        healthy = self.get_healthy_channels()
        if len(healthy) == 0:
            return False
        first_output = healthy[0].output_value
        return all(c.output_value == first_output for c in healthy)
    
    def can_vote(self) -> bool:
        """Enough healthy channels for majority vote."""
        healthy_count = len(self.get_healthy_channels())
        total_count = len(self.channels)
        return Fraction(healthy_count, total_count) >= self.required_agreement


@dataclass
class StructuralHealthSensor:
    """Structural health monitoring sensor."""
    sensor_id: str
    location: str
    strain_reading: Fraction = Fraction(0)
    vibration_frequency: Fraction = Fraction(0)
    alert_threshold_strain: Fraction = Fraction(3000)  # microstrain
    alert_threshold_vibration: Fraction = Fraction(100)  # Hz
    
    def is_within_spec(self) -> bool:
        return (
            self.strain_reading < self.alert_threshold_strain and
            self.vibration_frequency < self.alert_threshold_vibration
        )


@dataclass
class StructuralHealthMonitor:
    """Monitor structural integrity of airframe."""
    sensors: List[StructuralHealthSensor]
    
    def get_alerted_sensors(self) -> List[StructuralHealthSensor]:
        return [s for s in self.sensors if not s.is_within_spec()]
    
    def structural_integrity_ok(self) -> bool:
        return len(self.get_alerted_sensors()) == 0


# DO-178C thresholds
MAX_LINES_PER_FUNCTION = Fraction(75)  # Advisory for cyclomatic complexity
MIN_TEST_CASES_REQUIREMENT = Fraction(1)  # At least 1 test per requirement

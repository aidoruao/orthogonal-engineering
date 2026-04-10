"""D_CHEMICAL implementation — Chemical process safety management

Layer: 3
CardinalStrength: PREDICATIVE
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum


class SILLevel(Enum):
    """Safety Integrity Level per IEC 61508/61511"""
    SIL1 = 1  # 10^-1 to 10^-2 PFD
    SIL2 = 2  # 10^-2 to 10^-3 PFD
    SIL3 = 3  # 10^-3 to 10^-4 PFD
    SIL4 = 4  # 10^-4 to 10^-5 PFD


@dataclass
class ReactorControl:
    """Chemical reactor control system"""
    reactor_id: str
    temperature_c: Fraction
    pressure_bar: Fraction
    design_pressure_bar: Fraction
    t_critical_c: Fraction  # Thermal runaway threshold


@dataclass
class SafetyInstrumentedSystem:
    """SIS protection layer"""
    sis_id: str
    sil_level: SILLevel
    pfd_avg: Fraction  # Probability of Failure on Demand


@dataclass
class HazmatContainment:
    """Hazardous material containment"""
    zone_id: str
    leak_detection_ppm: Fraction
    lel_percent: Fraction  # Lower Explosive Limit


@dataclass
class EmergencyShutdown:
    """ESD system timing"""
    esd_id: str
    trigger_to_isolation_ms: Fraction


def thermal_runaway_margin() -> Fraction:
    """Safety margin before T_critical"""
    return Fraction(10, 1)  # 10°C


def pressure_interlock_threshold() -> Fraction:
    """Interlock at 90% design pressure"""
    return Fraction(90, 100)


def sil3_pfd_max() -> Fraction:
    """SIL-3 requires PFD < 0.001"""
    return Fraction(1, 1000)


def leak_detection_threshold() -> Fraction:
    """Detect leaks at 10 ppm"""
    return Fraction(10, 1)


def lel_alarm_threshold() -> Fraction:
    """Alarm at 10% LEL"""
    return Fraction(10, 100)


def esd_isolation_max_ms() -> Fraction:
    """ESD must isolate within 5000ms"""
    return Fraction(5000, 1)

"""D_BORING implementation — Tunnel Boring, Geotechnical, TBM Operations

Layer: 3 (Regulatory/Engineering)
CardinalStrength: PREDICATIVE

Tunnel boring machines (TBM), ground conditions, segment alignment, grouting.
BTS (British Tunnelling Society), ITA (International Tunnelling Association).
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum
from typing import List, Optional


class GroundType(Enum):
    """Ground condition classification"""
    ROCK_HARD = 1
    ROCK_SOFT = 2
    MIXED_FACE = 3
    CLAY = 4
    SAND = 5
    WATER_BEARING = 6


class TBMType(Enum):
    """Tunnel boring machine type"""
    EPB = 1  # Earth Pressure Balance
    SLURRY = 2  # Slurry shield
    OPEN_FACE = 3  # Open-face hard rock TBM
    DOUBLE_SHIELD = 4  # Double shield


@dataclass
class TBM:
    """Tunnel Boring Machine"""
    tbm_id: str
    tbm_type: TBMType
    diameter_meters: Fraction
    advance_rate_mm_per_min: Fraction  # Typical: 10-50 mm/min
    cutterhead_rpm: Fraction
    thrust_force_kn: Fraction
    operational: bool


@dataclass
class GroundConditions:
    """Geotechnical ground conditions"""
    location_id: str
    ground_type: GroundType
    rock_strength_mpa: Optional[Fraction]  # MPa (for rock)
    water_table_depth_m: Fraction
    permeability_m_per_s: Fraction
    soil_cohesion_kpa: Optional[Fraction]  # kPa (for soil)


@dataclass
class TunnelSegment:
    """Precast concrete tunnel segment"""
    segment_id: str
    length_m: Fraction
    thickness_mm: Fraction
    alignment_tolerance_mm: Fraction  # Typical: +/- 10mm
    installed: bool
    grouting_complete: bool


@dataclass
class TBMAdvance:
    """TBM advance record"""
    advance_id: str
    tbm_id: str
    distance_advanced_m: Fraction
    duration_hours: Fraction
    ground_pressure_kpa: Fraction
    face_pressure_kpa: Fraction


@dataclass
class SegmentInstallation:
    """Tunnel segment installation"""
    installation_id: str
    segment_id: str
    ring_number: int
    alignment_deviation_mm: Fraction
    bolt_torque_nm: Fraction
    grouting_volume_m3: Fraction


@dataclass
class SubsidenceMonitoring:
    """Ground surface subsidence monitoring"""
    monitoring_id: str
    location: str
    settlement_mm: Fraction  # Typical limit: < 30mm
    horizontal_displacement_mm: Fraction
    days_after_passage: Fraction


def tbm_standard_advance_rate(ground: GroundType) -> Fraction:
    """Standard advance rates by ground type (mm/min)"""
    rates = {
        GroundType.ROCK_HARD: Fraction(20, 1),
        GroundType.ROCK_SOFT: Fraction(40, 1),
        GroundType.MIXED_FACE: Fraction(25, 1),
        GroundType.CLAY: Fraction(35, 1),
        GroundType.SAND: Fraction(30, 1),
        GroundType.WATER_BEARING: Fraction(15, 1)
    }
    return rates.get(ground, Fraction(25, 1))


def alignment_tolerance_threshold() -> Fraction:
    """Typical alignment tolerance (mm)"""
    return Fraction(10, 1)


def grouting_volume_per_ring() -> Fraction:
    """Typical grouting volume per ring (m3)"""
    return Fraction(3, 1)


def subsidence_limit_mm() -> Fraction:
    """Maximum allowable surface settlement (mm)"""
    return Fraction(30, 1)

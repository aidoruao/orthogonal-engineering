"""D_CONSTRUCTION implementation — Structural engineering and safety

Layer: 3
CardinalStrength: PREDICATIVE
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum


class LoadType(Enum):
    """Structural load classifications"""
    DEAD = 1  # Permanent/static
    LIVE = 2  # Occupancy/movable
    WIND = 3  # Environmental
    SEISMIC = 4  # Earthquake


@dataclass
class StructuralMember:
    """Structural element under load"""
    member_id: str
    applied_load_kn: Fraction
    capacity_kn: Fraction
    safety_factor: Fraction


@dataclass
class FEMAnalysis:
    """Finite Element Method analysis"""
    analysis_id: str
    computed_stress_mpa: Fraction
    analytical_stress_mpa: Fraction
    mesh_convergence_percent: Fraction


@dataclass
class BIMClashDetection:
    """Building Information Model clash detection"""
    model_id: str
    clashes_detected: int
    false_negative_rate: Fraction


@dataclass
class OSHACompliance:
    """OSHA fall protection"""
    site_id: str
    height_ft: Fraction
    has_fall_protection: bool


def structural_safety_factor_min() -> Fraction:
    """Structural design: safety factor >= 3.0"""
    return Fraction(3, 1)


def fem_tolerance() -> Fraction:
    """FEM within 1% of analytical"""
    return Fraction(1, 100)


def bim_false_negative_max() -> Fraction:
    """BIM clash detection: <0.1% false negatives"""
    return Fraction(1, 1000)


def osha_fall_protection_height() -> Fraction:
    """OSHA: fall protection required above 6 ft"""
    return Fraction(6, 1)

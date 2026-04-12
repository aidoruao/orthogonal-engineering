"""D_NUCLEAR Implementation — Reactor, radiation, waste, emergency, and criticality records.

All arithmetic uses Fraction. No floats.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ReactorUnit:
    """Reactor unit operational parameters (NUREG-0800, 10 CFR 50)."""

    unit_id: str
    thermal_power_mw: Fraction
    coolant_temp_c: Fraction
    coolant_pressure_bar: Fraction
    scram_time_ms: Fraction
    design_scram_limit_ms: Fraction
    containment_integrity: bool
    fuel_burnup_mwd_per_t: Fraction
    control_rod_insertion_fraction: Fraction
    active_barriers: int


@dataclass(frozen=True)
class RadiationExposure:
    """Occupational radiation exposure record (10 CFR 20, ALARA principle)."""

    worker_id: str
    dose_msv: Fraction
    annual_limit_msv: Fraction
    alara_target_msv: Fraction
    monitoring_period_days: Fraction


@dataclass(frozen=True)
class WasteContainer:
    """Radioactive waste container integrity record (10 CFR 61)."""

    container_id: str
    waste_class: str
    shielding_factor: Fraction
    leak_rate_bq_per_s: Fraction
    max_leak_rate_bq_per_s: Fraction
    storage_years: Fraction
    design_life_years: Fraction


@dataclass(frozen=True)
class EmergencyPlan:
    """Emergency response plan parameters (10 CFR 50.72)."""

    plan_id: str
    evacuation_zone_km: Fraction
    notification_time_min: Fraction
    max_notification_time_min: Fraction
    drill_frequency_per_year: Fraction
    min_drill_frequency: Fraction


@dataclass(frozen=True)
class CriticalityAssessment:
    """Nuclear criticality safety assessment (IAEA GSR Part 4, ANSI/ANS-8)."""

    assessment_id: str
    k_effective: Fraction
    subcritical_margin: Fraction
    min_subcritical_margin: Fraction

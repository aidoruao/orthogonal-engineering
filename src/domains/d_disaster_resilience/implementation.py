"""Implementation models for the disaster-resilience domain.

A ``DisasterResilienceClaim`` records a jurisdiction's readiness under
three standard hazard classes (natural, industrial, cyber): warning-system
latency, evacuation capacity, emergency-fuel days, mutual-aid agreements,
backup-power autonomy, and after-action report currency. Fractions
preserve byte-exact ratios.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

MAX_WARNING_LATENCY_SECONDS: int = 120
MIN_EVAC_CAPACITY_FRACTION: Fraction = Fraction(1, 4)
MIN_EMERGENCY_FUEL_DAYS: int = 7
MIN_MUTUAL_AID_PARTNERS: int = 3
MIN_BACKUP_POWER_HOURS: int = 72
MAX_AFTER_ACTION_STALENESS_DAYS: int = 540


@dataclass(frozen=True)
class DisasterResilienceClaim:
    """Structured readiness claim for one jurisdiction."""

    population: int
    warning_latency_seconds: int
    evacuation_capacity: int
    emergency_fuel_days: int
    mutual_aid_partner_count: int
    backup_power_autonomy_hours: int
    last_after_action_report_days_ago: int
    cyber_incident_response_playbook_current: bool


def evacuation_capacity_fraction(claim: DisasterResilienceClaim) -> Fraction:
    """Return evacuation capacity as a fraction of total population."""
    if claim.population <= 0:
        return Fraction(0)
    return Fraction(claim.evacuation_capacity, claim.population)


def create_nominal_claim() -> DisasterResilienceClaim:
    """Create nominal claim data used by :func:`run_all_invariants`.

    Falsifies if: nominal claim cannot satisfy every resilience floor.
    falsifies_if: nominal claim cannot satisfy every resilience floor.
    """
    return DisasterResilienceClaim(
        population=1_000_000,
        warning_latency_seconds=45,
        evacuation_capacity=400_000,
        emergency_fuel_days=14,
        mutual_aid_partner_count=5,
        backup_power_autonomy_hours=96,
        last_after_action_report_days_ago=180,
        cyber_incident_response_playbook_current=True,
    )


DOMAIN_METADATA = {
    "id": "D_DISASTER_RESILIENCE",
    "claim_model": "DisasterResilienceClaim",
    "check_functions": [
        "check_warning_latency",
        "check_evacuation_capacity",
        "check_emergency_fuel_reserve",
        "check_mutual_aid_breadth",
        "check_backup_power_autonomy",
        "check_after_action_report_current",
        "check_cyber_playbook_current",
    ],
}

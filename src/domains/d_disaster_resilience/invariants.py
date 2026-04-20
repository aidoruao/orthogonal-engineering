"""Invariant checks for the disaster-resilience domain."""
from __future__ import annotations

from typing import List, Tuple

from axioms.logic import ProofObject

from .implementation import (
    MAX_AFTER_ACTION_STALENESS_DAYS,
    MAX_WARNING_LATENCY_SECONDS,
    MIN_BACKUP_POWER_HOURS,
    MIN_EMERGENCY_FUEL_DAYS,
    MIN_EVAC_CAPACITY_FRACTION,
    MIN_MUTUAL_AID_PARTNERS,
    DisasterResilienceClaim,
    create_nominal_claim,
    evacuation_capacity_fraction,
)


def check_warning_latency(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: hazard warning reaches population within latency budget.

    Standard: FEMA IPAWS / NOAA EAS 2-minute public-alert SLA.
    Falsifies if: warning_latency_seconds > MAX_WARNING_LATENCY_SECONDS.
    falsifies_if: warning_latency_seconds > MAX_WARNING_LATENCY_SECONDS.
    """
    success = data.warning_latency_seconds <= MAX_WARNING_LATENCY_SECONDS
    proof = ProofObject(
        rule="check_warning_latency",
        premises=[
            f"warning_latency_seconds={data.warning_latency_seconds}",
            f"limit={MAX_WARNING_LATENCY_SECONDS}",
        ],
        conclusion=(
            "PASS: warning latency within SLA"
            if success
            else (
                f"FAIL: {data.warning_latency_seconds} > "
                f"{MAX_WARNING_LATENCY_SECONDS}"
            )
        ),
    )
    return success, proof


def check_evacuation_capacity(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: evacuation lift >= 25% of population.

    Standard: FEMA CPG 101 mass-care planning threshold.
    Falsifies if: evacuation_capacity / population < MIN_EVAC_CAPACITY_FRACTION.
    falsifies_if: evacuation_capacity / population < MIN_EVAC_CAPACITY_FRACTION.
    """
    ratio = evacuation_capacity_fraction(data)
    success = ratio >= MIN_EVAC_CAPACITY_FRACTION
    proof = ProofObject(
        rule="check_evacuation_capacity",
        premises=[
            f"evacuation_capacity={data.evacuation_capacity}",
            f"population={data.population}",
            f"ratio={ratio}",
            f"floor={MIN_EVAC_CAPACITY_FRACTION}",
        ],
        conclusion=(
            "PASS: evacuation capacity >= floor"
            if success else f"FAIL: {ratio} < {MIN_EVAC_CAPACITY_FRACTION}"
        ),
    )
    return success, proof


def check_emergency_fuel_reserve(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: emergency fuel reserve >= 7 days.

    Standard: DHS/CISA Lifeline Sector fuel-continuity guidance.
    Falsifies if: emergency_fuel_days < MIN_EMERGENCY_FUEL_DAYS.
    falsifies_if: emergency_fuel_days < MIN_EMERGENCY_FUEL_DAYS.
    """
    success = data.emergency_fuel_days >= MIN_EMERGENCY_FUEL_DAYS
    proof = ProofObject(
        rule="check_emergency_fuel_reserve",
        premises=[
            f"emergency_fuel_days={data.emergency_fuel_days}",
            f"floor={MIN_EMERGENCY_FUEL_DAYS}",
        ],
        conclusion=(
            "PASS: fuel reserve >= floor"
            if success else f"FAIL: {data.emergency_fuel_days} < {MIN_EMERGENCY_FUEL_DAYS}"
        ),
    )
    return success, proof


def check_mutual_aid_breadth(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: jurisdiction has at least 3 signed mutual-aid partners.

    Standard: EMAC interstate mutual-aid framework.
    Falsifies if: mutual_aid_partner_count < MIN_MUTUAL_AID_PARTNERS.
    falsifies_if: mutual_aid_partner_count < MIN_MUTUAL_AID_PARTNERS.
    """
    success = data.mutual_aid_partner_count >= MIN_MUTUAL_AID_PARTNERS
    proof = ProofObject(
        rule="check_mutual_aid_breadth",
        premises=[
            f"mutual_aid_partner_count={data.mutual_aid_partner_count}",
            f"floor={MIN_MUTUAL_AID_PARTNERS}",
        ],
        conclusion=(
            "PASS: mutual-aid breadth >= floor"
            if success
            else f"FAIL: {data.mutual_aid_partner_count} < {MIN_MUTUAL_AID_PARTNERS}"
        ),
    )
    return success, proof


def check_backup_power_autonomy(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: backup power autonomy >= 72 hours.

    Standard: NFPA 110 Level 1 emergency power system.
    Falsifies if: backup_power_autonomy_hours < MIN_BACKUP_POWER_HOURS.
    falsifies_if: backup_power_autonomy_hours < MIN_BACKUP_POWER_HOURS.
    """
    success = data.backup_power_autonomy_hours >= MIN_BACKUP_POWER_HOURS
    proof = ProofObject(
        rule="check_backup_power_autonomy",
        premises=[
            f"backup_power_autonomy_hours={data.backup_power_autonomy_hours}",
            f"floor={MIN_BACKUP_POWER_HOURS}",
        ],
        conclusion=(
            "PASS: backup power autonomy >= floor"
            if success
            else (
                f"FAIL: {data.backup_power_autonomy_hours} < "
                f"{MIN_BACKUP_POWER_HOURS}"
            )
        ),
    )
    return success, proof


def check_after_action_report_current(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: after-action report is not stale.

    Standard: FEMA HSEEP after-action report cadence.
    Falsifies if: last_after_action_report_days_ago > MAX_AFTER_ACTION_STALENESS_DAYS.
    falsifies_if: last_after_action_report_days_ago > MAX_AFTER_ACTION_STALENESS_DAYS.
    """
    success = data.last_after_action_report_days_ago <= MAX_AFTER_ACTION_STALENESS_DAYS
    proof = ProofObject(
        rule="check_after_action_report_current",
        premises=[
            f"days_since_report={data.last_after_action_report_days_ago}",
            f"max_staleness={MAX_AFTER_ACTION_STALENESS_DAYS}",
        ],
        conclusion=(
            "PASS: AAR within staleness window"
            if success
            else (
                f"FAIL: {data.last_after_action_report_days_ago} > "
                f"{MAX_AFTER_ACTION_STALENESS_DAYS}"
            )
        ),
    )
    return success, proof


def check_cyber_playbook_current(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: cyber incident-response playbook is current.

    Standard: CISA Cyber Incident Response Playbook (2021) + NIST SP 800-61r2.
    Falsifies if: cyber_incident_response_playbook_current False.
    falsifies_if: cyber_incident_response_playbook_current False.
    """
    success = data.cyber_incident_response_playbook_current
    proof = ProofObject(
        rule="check_cyber_playbook_current",
        premises=[
            f"playbook_current={data.cyber_incident_response_playbook_current}",
        ],
        conclusion=(
            "PASS: cyber playbook current"
            if success else "FAIL: cyber playbook stale or missing"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain on the nominal claim.

    Standard: Disaster-resilience nominal executable check set.
    Falsifies if: any invariant check returns False on the nominal claim.
    falsifies_if: any invariant check returns False on the nominal claim.
    """
    data = create_nominal_claim()
    checks = [
        ("check_warning_latency", check_warning_latency),
        ("check_evacuation_capacity", check_evacuation_capacity),
        ("check_emergency_fuel_reserve", check_emergency_fuel_reserve),
        ("check_mutual_aid_breadth", check_mutual_aid_breadth),
        ("check_backup_power_autonomy", check_backup_power_autonomy),
        ("check_after_action_report_current", check_after_action_report_current),
        ("check_cyber_playbook_current", check_cyber_playbook_current),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results

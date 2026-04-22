"""PHOTONIC Environmental — RoHS, REACH, WEEE, conflict minerals, Energy Star,
operating temperature range.

Category 11: Environmental & Regulatory (checks 67-72).

Standards: EU 2011/65/EU (RoHS), EU 1907/2006 (REACH), EU 2012/19/EU (WEEE),
Dodd-Frank Section 1502, EPA Energy Star, Telcordia GR-63.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class RoHSProfile:
    """RoHS substance content per EU 2011/65/EU.

    falsifies_if: lead_fraction is negative.
    falsifies_if: lead_fraction is negative.
    """
    component_id: str
    lead_fraction: Fraction


@dataclass(frozen=True)
class ReachProfile:
    """REACH SVHC content per EU 1907/2006.

    falsifies_if: svhc_fraction is negative.
    falsifies_if: svhc_fraction is negative.
    """
    component_id: str
    svhc_fraction: Fraction


@dataclass(frozen=True)
class WEEEProfile:
    """WEEE recyclability per EU 2012/19/EU.

    falsifies_if: recyclable_fraction is negative or > 1.
    falsifies_if: recyclable_fraction is negative or > 1.
    """
    product_id: str
    recyclable_fraction: Fraction


@dataclass(frozen=True)
class ConflictMinerals:
    """Conflict minerals sourcing per Dodd-Frank Section 1502.

    falsifies_if: has_audit is False (no smelter audit on file).
    falsifies_if: has_audit is False.
    """
    supplier_id: str
    has_audit: bool


@dataclass(frozen=True)
class EnergyProfile:
    """Energy Star idle power per EPA.

    falsifies_if: idle_power_w is negative.
    falsifies_if: idle_power_w is negative.
    """
    device_id: str
    idle_power_w: Fraction


@dataclass(frozen=True)
class TemperatureRange:
    """Operating temperature range per Telcordia GR-63.

    falsifies_if: min_temp_c > max_temp_c.
    falsifies_if: min_temp_c > max_temp_c.
    """
    device_id: str
    min_temp_c: Fraction
    max_temp_c: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def rohs_lead_threshold() -> Fraction:
    """EU RoHS 2011/65/EU maximum lead content: 0.1% by weight."""
    return Fraction(1, 1000)


def reach_svhc_threshold() -> Fraction:
    """EU REACH 1907/2006 SVHC notification threshold: 0.1% w/w."""
    return Fraction(1, 1000)


def weee_recyclable_threshold() -> Fraction:
    """EU WEEE 2012/19/EU minimum recyclable fraction: 65%."""
    return Fraction(65, 100)


def energy_star_idle_threshold() -> Fraction:
    """EPA Energy Star maximum idle power for accelerator card: 5 W."""
    return Fraction(5, 1)


def telcordia_min_temp() -> Fraction:
    """Telcordia GR-63 minimum operating temperature: -40 °C."""
    return Fraction(-40, 1)


def telcordia_max_temp() -> Fraction:
    """Telcordia GR-63 maximum operating temperature: 85 °C."""
    return Fraction(85, 1)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_rohs_compliance(profile: RoHSProfile) -> Tuple[bool, ProofObject]:
    """Lead content must not exceed 0.1% by weight per EU RoHS 2011/65/EU.

    Falsifies if: lead_fraction > Fraction(1, 1000).
    falsifies_if: lead_fraction > Fraction(1, 1000).
    """
    limit = rohs_lead_threshold()
    if profile.lead_fraction > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.component_id} lead {profile.lead_fraction} > "
                f"RoHS limit {limit}"
            ),
            premises=[
                f"Lead: {profile.lead_fraction}",
                f"Limit: {limit}",
            ],
            rule="eu_rohs_lead",
        )
    return True, ProofObject(
        conclusion=f"{profile.component_id} lead {profile.lead_fraction} <= {limit}",
        premises=[f"Lead: {profile.lead_fraction} <= {limit}"],
        rule="eu_rohs_lead",
    )


def check_reach_compliance(profile: ReachProfile) -> Tuple[bool, ProofObject]:
    """SVHC content must not exceed 0.1% w/w per EU REACH 1907/2006.

    Falsifies if: svhc_fraction > Fraction(1, 1000).
    falsifies_if: svhc_fraction > Fraction(1, 1000).
    """
    limit = reach_svhc_threshold()
    if profile.svhc_fraction > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.component_id} SVHC {profile.svhc_fraction} > "
                f"REACH limit {limit}"
            ),
            premises=[
                f"SVHC: {profile.svhc_fraction}",
                f"Limit: {limit}",
            ],
            rule="eu_reach_svhc",
        )
    return True, ProofObject(
        conclusion=f"{profile.component_id} SVHC {profile.svhc_fraction} <= {limit}",
        premises=[f"SVHC: {profile.svhc_fraction} <= {limit}"],
        rule="eu_reach_svhc",
    )


def check_weee_recyclability(profile: WEEEProfile) -> Tuple[bool, ProofObject]:
    """Recyclable fraction must be at least 65% per EU WEEE 2012/19/EU.

    Falsifies if: recyclable_fraction < Fraction(65, 100).
    falsifies_if: recyclable_fraction < Fraction(65, 100).
    """
    limit = weee_recyclable_threshold()
    if profile.recyclable_fraction < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.product_id} recyclable fraction {profile.recyclable_fraction} < "
                f"WEEE floor {limit}"
            ),
            premises=[
                f"Recyclable: {profile.recyclable_fraction}",
                f"Floor: {limit}",
            ],
            rule="eu_weee_recyclability",
        )
    return True, ProofObject(
        conclusion=f"{profile.product_id} recyclable fraction {profile.recyclable_fraction} >= {limit}",
        premises=[f"Recyclable: {profile.recyclable_fraction} >= {limit}"],
        rule="eu_weee_recyclability",
    )


def check_conflict_minerals(mineral: ConflictMinerals) -> Tuple[bool, ProofObject]:
    """3TG minerals must have smelter audit per Dodd-Frank Section 1502.

    Falsifies if: has_audit is False.
    falsifies_if: has_audit is False.
    """
    if not mineral.has_audit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {mineral.supplier_id} has no conflict-minerals smelter audit"
            ),
            premises=[
                f"Supplier: {mineral.supplier_id}",
                f"Audit: None",
            ],
            rule="dodd_frank_1502_conflict_minerals",
        )
    return True, ProofObject(
        conclusion=f"{mineral.supplier_id} conflict-minerals audit on file",
        premises=[f"Supplier: {mineral.supplier_id}", f"Audit: Present"],
        rule="dodd_frank_1502_conflict_minerals",
    )


def check_energy_star_idle(profile: EnergyProfile) -> Tuple[bool, ProofObject]:
    """Idle power must not exceed 5 W per EPA Energy Star.

    Falsifies if: idle_power_w > Fraction(5, 1).
    falsifies_if: idle_power_w > Fraction(5, 1).
    """
    limit = energy_star_idle_threshold()
    if profile.idle_power_w > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.device_id} idle power {profile.idle_power_w} W > "
                f"limit {limit} W"
            ),
            premises=[
                f"Idle power: {profile.idle_power_w} W",
                f"Limit: {limit} W",
            ],
            rule="epa_energy_star_idle",
        )
    return True, ProofObject(
        conclusion=f"{profile.device_id} idle power {profile.idle_power_w} W <= {limit} W",
        premises=[f"Idle power: {profile.idle_power_w} W <= {limit} W"],
        rule="epa_energy_star_idle",
    )


def check_operating_temperature_range(tr: TemperatureRange) -> Tuple[bool, ProofObject]:
    """Operating temperature must cover at least -40 °C to +85 °C per Telcordia GR-63.

    Falsifies if: min_temp_c > -40 OR max_temp_c < 85.
    falsifies_if: min_temp_c > -40 or max_temp_c < 85.
    """
    min_limit = telcordia_min_temp()
    max_limit = telcordia_max_temp()
    if tr.min_temp_c > min_limit or tr.max_temp_c < max_limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {tr.device_id} range {tr.min_temp_c}°C to {tr.max_temp_c}°C "
                f"does not cover {min_limit}°C to {max_limit}°C"
            ),
            premises=[
                f"Min: {tr.min_temp_c}°C (limit {min_limit}°C)",
                f"Max: {tr.max_temp_c}°C (limit {max_limit}°C)",
            ],
            rule="telcordia_gr63_temperature",
        )
    return True, ProofObject(
        conclusion=(
            f"{tr.device_id} range {tr.min_temp_c}°C to {tr.max_temp_c}°C "
            f"covers {min_limit}°C to {max_limit}°C"
        ),
        premises=[
            f"Min: {tr.min_temp_c}°C <= {min_limit}°C",
            f"Max: {tr.max_temp_c}°C >= {max_limit}°C",
        ],
        rule="telcordia_gr63_temperature",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all environmental checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_rohs = RoHSProfile(component_id="pass_rohs", lead_fraction=Fraction(5, 10000))
    fail_rohs = RoHSProfile(component_id="fail_rohs", lead_fraction=Fraction(2, 1000))
    pass_reach = ReachProfile(component_id="pass_reach", svhc_fraction=Fraction(5, 10000))
    fail_reach = ReachProfile(component_id="fail_reach", svhc_fraction=Fraction(2, 1000))
    pass_weee = WEEEProfile(product_id="pass_weee", recyclable_fraction=Fraction(75, 100))
    fail_weee = WEEEProfile(product_id="fail_weee", recyclable_fraction=Fraction(50, 100))
    pass_conflict = ConflictMinerals(supplier_id="pass_supp", has_audit=True)
    fail_conflict = ConflictMinerals(supplier_id="fail_supp", has_audit=False)
    pass_energy = EnergyProfile(device_id="pass_energy", idle_power_w=Fraction(3, 1))
    fail_energy = EnergyProfile(device_id="fail_energy", idle_power_w=Fraction(7, 1))
    pass_temp = TemperatureRange(
        device_id="pass_temp", min_temp_c=Fraction(-45, 1), max_temp_c=Fraction(90, 1)
    )
    fail_temp = TemperatureRange(
        device_id="fail_temp", min_temp_c=Fraction(-30, 1), max_temp_c=Fraction(70, 1)
    )

    checks = [
        ("check_rohs_compliance_pass", lambda: check_rohs_compliance(pass_rohs)),
        ("check_rohs_compliance_fail", lambda: check_rohs_compliance(fail_rohs)),
        ("check_reach_compliance_pass", lambda: check_reach_compliance(pass_reach)),
        ("check_reach_compliance_fail", lambda: check_reach_compliance(fail_reach)),
        ("check_weee_recyclability_pass", lambda: check_weee_recyclability(pass_weee)),
        ("check_weee_recyclability_fail", lambda: check_weee_recyclability(fail_weee)),
        ("check_conflict_minerals_pass", lambda: check_conflict_minerals(pass_conflict)),
        ("check_conflict_minerals_fail", lambda: check_conflict_minerals(fail_conflict)),
        ("check_energy_star_idle_pass", lambda: check_energy_star_idle(pass_energy)),
        ("check_energy_star_idle_fail", lambda: check_energy_star_idle(fail_energy)),
        ("check_operating_temperature_range_pass", lambda: check_operating_temperature_range(pass_temp)),
        ("check_operating_temperature_range_fail", lambda: check_operating_temperature_range(fail_temp)),
    ]

    results = []
    for name, func in checks:
        try:
            ok, proof = func()
            results.append((name, ok, proof))
        except Exception as exc:
            fake_proof = ProofObject(
                conclusion=f"ERROR in {name}: {exc}",
                premises=[],
                rule=name,
            )
            results.append((name, False, fake_proof))

    return results

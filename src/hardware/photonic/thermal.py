"""PHOTONIC Thermal — Junction temperature, thermal resistance, thermo-optic drift,
heater power budget, thermal runaway margin.

Category 7: Thermal Management (checks 44-48).

Standards: JEDEC JESD51, JEDEC JESD51-14, IEC 61508 (adapted), Custom OE.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class ThermalProfile:
    """Junction temperature parameters per JEDEC JESD51.

    falsifies_if: tj_max_c is zero or negative.
    falsifies_if: tj_max_c is zero or negative.
    """
    chip_id: str
    junction_temp_c: Fraction
    tj_max_c: Fraction


@dataclass(frozen=True)
class PackageThermal:
    """Package thermal resistance parameters per JEDEC JESD51-14.

    falsifies_if: theta_ja_c_per_w is negative.
    falsifies_if: theta_ja_c_per_w is negative.
    """
    package_id: str
    theta_ja_c_per_w: Fraction


@dataclass(frozen=True)
class ThermoOptic:
    """Thermo-optic drift parameters.

    falsifies_if: drift_pm_per_c is negative.
    falsifies_if: drift_pm_per_c is negative.
    """
    element_id: str
    drift_pm_per_c: Fraction


@dataclass(frozen=True)
class HeaterBudget:
    """Heater power budget parameters.

    falsifies_if: thermal_budget_w is zero or negative.
    falsifies_if: thermal_budget_w is zero or negative.
    """
    heater_id: str
    total_heater_w: Fraction
    thermal_budget_w: Fraction


@dataclass(frozen=True)
class ThermalRunaway:
    """Thermal runaway margin parameters (adapted from IEC 61508 / d_chemical).

    falsifies_if: tj_max_c is zero or negative.
    falsifies_if: tj_max_c is zero or negative.
    """
    system_id: str
    operating_temp_c: Fraction
    tj_max_c: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def tj_max_default() -> Fraction:
    """JEDEC JESD51 default maximum junction temperature: 125 °C."""
    return Fraction(125, 1)


def theta_ja_threshold() -> Fraction:
    """JEDEC JESD51-14 maximum thermal resistance for PIC package: 15 °C/W."""
    return Fraction(15, 1)


def thermo_optic_drift_threshold() -> Fraction:
    """Custom OE maximum uncompensated thermo-optic drift: 80 pm/°C."""
    return Fraction(80, 1)


def heater_power_fraction() -> Fraction:
    """Custom OE: heater power must stay below half of thermal budget."""
    return Fraction(1, 2)


def thermal_runaway_margin() -> Fraction:
    """IEC 61508 (adapted) thermal runaway margin: 10 °C below Tj_max."""
    return Fraction(10, 1)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_junction_temperature(profile: ThermalProfile) -> Tuple[bool, ProofObject]:
    """Junction temperature must not exceed Tj_max per JEDEC JESD51.

    Falsifies if: junction_temp_c > tj_max_c.
    falsifies_if: junction_temp_c > tj_max_c.
    """
    if profile.junction_temp_c > profile.tj_max_c:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.chip_id} junction temp {profile.junction_temp_c}°C > "
                f"Tj_max {profile.tj_max_c}°C"
            ),
            premises=[
                f"Junction temp: {profile.junction_temp_c}°C",
                f"Tj_max: {profile.tj_max_c}°C",
            ],
            rule="jedec_jesd51_junction_temp",
        )
    return True, ProofObject(
        conclusion=f"{profile.chip_id} junction temp {profile.junction_temp_c}°C <= {profile.tj_max_c}°C",
        premises=[f"Junction temp: {profile.junction_temp_c}°C <= {profile.tj_max_c}°C"],
        rule="jedec_jesd51_junction_temp",
    )


def check_thermal_resistance(pkg: PackageThermal) -> Tuple[bool, ProofObject]:
    """Thermal resistance θJA must not exceed 15 °C/W per JEDEC JESD51-14.

    Falsifies if: theta_ja_c_per_w > Fraction(15, 1).
    falsifies_if: theta_ja_c_per_w > Fraction(15, 1).
    """
    limit = theta_ja_threshold()
    if pkg.theta_ja_c_per_w > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {pkg.package_id} θJA {pkg.theta_ja_c_per_w} °C/W > "
                f"limit {limit} °C/W"
            ),
            premises=[
                f"θJA: {pkg.theta_ja_c_per_w} °C/W",
                f"Limit: {limit} °C/W",
            ],
            rule="jedec_jesd51_14_thermal_resistance",
        )
    return True, ProofObject(
        conclusion=f"{pkg.package_id} θJA {pkg.theta_ja_c_per_w} °C/W <= {limit} °C/W",
        premises=[f"θJA: {pkg.theta_ja_c_per_w} °C/W <= {limit} °C/W"],
        rule="jedec_jesd51_14_thermal_resistance",
    )


def check_thermo_optic_drift(elem: ThermoOptic) -> Tuple[bool, ProofObject]:
    """Uncompensated thermo-optic drift must not exceed 80 pm/°C (Custom OE).

    Falsifies if: drift_pm_per_c > Fraction(80, 1).
    falsifies_if: drift_pm_per_c > Fraction(80, 1).
    """
    limit = thermo_optic_drift_threshold()
    if elem.drift_pm_per_c > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {elem.element_id} drift {elem.drift_pm_per_c} pm/°C > "
                f"limit {limit} pm/°C"
            ),
            premises=[
                f"Drift: {elem.drift_pm_per_c} pm/°C",
                f"Limit: {limit} pm/°C",
            ],
            rule="oe_thermo_optic_drift",
        )
    return True, ProofObject(
        conclusion=f"{elem.element_id} drift {elem.drift_pm_per_c} pm/°C <= {limit} pm/°C",
        premises=[f"Drift: {elem.drift_pm_per_c} pm/°C <= {limit} pm/°C"],
        rule="oe_thermo_optic_drift",
    )


def check_heater_power_budget(budget: HeaterBudget) -> Tuple[bool, ProofObject]:
    """Heater power must stay below half of thermal budget (Custom OE).

    Falsifies if: total_heater_w > Fraction(1, 2) * thermal_budget_w.
    falsifies_if: total_heater_w > Fraction(1, 2) * thermal_budget_w.
    """
    limit = budget.thermal_budget_w * heater_power_fraction()
    if budget.total_heater_w > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {budget.heater_id} heater power {budget.total_heater_w} W > "
                f"half of budget {limit} W"
            ),
            premises=[
                f"Heater power: {budget.total_heater_w} W",
                f"Thermal budget: {budget.thermal_budget_w} W",
                f"Limit (50%): {limit} W",
            ],
            rule="oe_heater_power_budget",
        )
    return True, ProofObject(
        conclusion=f"{budget.heater_id} heater power {budget.total_heater_w} W <= {limit} W",
        premises=[
            f"Heater power: {budget.total_heater_w} W",
            f"Budget: {budget.thermal_budget_w} W",
        ],
        rule="oe_heater_power_budget",
    )


def check_thermal_runaway_margin(tra: ThermalRunaway) -> Tuple[bool, ProofObject]:
    """Operating temperature must stay below Tj_max - 10 °C per IEC 61508 (adapted).

    Same pattern as d_chemical thermal_runaway_protection.

    Falsifies if: operating_temp_c >= tj_max_c - Fraction(10, 1).
    falsifies_if: operating_temp_c >= tj_max_c - Fraction(10, 1).
    """
    margin = thermal_runaway_margin()
    threshold = tra.tj_max_c - margin
    if tra.operating_temp_c >= threshold:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {tra.system_id} operating temp {tra.operating_temp_c}°C >= "
                f"threshold {threshold}°C (Tj_max {tra.tj_max_c}°C - {margin}°C margin)"
            ),
            premises=[
                f"Operating temp: {tra.operating_temp_c}°C",
                f"Tj_max: {tra.tj_max_c}°C",
                f"Margin: {margin}°C",
                f"Threshold: {threshold}°C",
            ],
            rule="iec_61508_thermal_runaway",
        )
    return True, ProofObject(
        conclusion=(
            f"{tra.system_id} operating temp {tra.operating_temp_c}°C < "
            f"threshold {threshold}°C"
        ),
        premises=[f"Operating temp: {tra.operating_temp_c}°C < {threshold}°C"],
        rule="iec_61508_thermal_runaway",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all thermal checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_profile = ThermalProfile(
        chip_id="pass_chip",
        junction_temp_c=Fraction(85, 1),
        tj_max_c=Fraction(125, 1),
    )
    fail_profile = ThermalProfile(
        chip_id="fail_chip",
        junction_temp_c=Fraction(130, 1),
        tj_max_c=Fraction(125, 1),
    )
    pass_pkg = PackageThermal(
        package_id="pass_pkg",
        theta_ja_c_per_w=Fraction(10, 1),
    )
    fail_pkg = PackageThermal(
        package_id="fail_pkg",
        theta_ja_c_per_w=Fraction(20, 1),
    )
    pass_drift = ThermoOptic(
        element_id="pass_drift",
        drift_pm_per_c=Fraction(50, 1),
    )
    fail_drift = ThermoOptic(
        element_id="fail_drift",
        drift_pm_per_c=Fraction(100, 1),
    )
    pass_budget = HeaterBudget(
        heater_id="pass_ht",
        total_heater_w=Fraction(2, 10),
        thermal_budget_w=Fraction(1, 1),
    )
    fail_budget = HeaterBudget(
        heater_id="fail_ht",
        total_heater_w=Fraction(6, 10),
        thermal_budget_w=Fraction(1, 1),
    )
    pass_tra = ThermalRunaway(
        system_id="pass_sys",
        operating_temp_c=Fraction(100, 1),
        tj_max_c=Fraction(125, 1),
    )
    fail_tra = ThermalRunaway(
        system_id="fail_sys",
        operating_temp_c=Fraction(120, 1),
        tj_max_c=Fraction(125, 1),
    )

    checks = [
        ("check_junction_temperature_pass", lambda: check_junction_temperature(pass_profile)),
        ("check_junction_temperature_fail", lambda: check_junction_temperature(fail_profile)),
        ("check_thermal_resistance_pass", lambda: check_thermal_resistance(pass_pkg)),
        ("check_thermal_resistance_fail", lambda: check_thermal_resistance(fail_pkg)),
        ("check_thermo_optic_drift_pass", lambda: check_thermo_optic_drift(pass_drift)),
        ("check_thermo_optic_drift_fail", lambda: check_thermo_optic_drift(fail_drift)),
        ("check_heater_power_budget_pass", lambda: check_heater_power_budget(pass_budget)),
        ("check_heater_power_budget_fail", lambda: check_heater_power_budget(fail_budget)),
        ("check_thermal_runaway_margin_pass", lambda: check_thermal_runaway_margin(pass_tra)),
        ("check_thermal_runaway_margin_fail", lambda: check_thermal_runaway_margin(fail_tra)),
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

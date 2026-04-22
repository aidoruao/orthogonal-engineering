"""Tests for photonic thermal checks.

Category 7: Thermal Management test suite.
"""

from fractions import Fraction

from axioms.logic import ProofObject
from src.hardware.photonic.thermal import (
    HeaterBudget,
    PackageThermal,
    ThermalProfile,
    ThermalRunaway,
    ThermoOptic,
    check_heater_power_budget,
    check_junction_temperature,
    check_thermal_resistance,
    check_thermal_runaway_margin,
    check_thermo_optic_drift,
    run_all_invariants,
)


def test_junction_temperature_pass() -> None:
    prof = ThermalProfile(
        chip_id="c1", junction_temp_c=Fraction(85, 1), tj_max_c=Fraction(125, 1)
    )
    ok, proof = check_junction_temperature(prof)
    assert ok is True
    assert isinstance(proof, ProofObject)


def test_junction_temperature_fail() -> None:
    prof = ThermalProfile(
        chip_id="c2", junction_temp_c=Fraction(130, 1), tj_max_c=Fraction(125, 1)
    )
    ok, proof = check_junction_temperature(prof)
    assert ok is False


def test_thermal_resistance_pass() -> None:
    pkg = PackageThermal(package_id="p1", theta_ja_c_per_w=Fraction(10, 1))
    ok, proof = check_thermal_resistance(pkg)
    assert ok is True


def test_thermal_resistance_fail() -> None:
    pkg = PackageThermal(package_id="p2", theta_ja_c_per_w=Fraction(20, 1))
    ok, proof = check_thermal_resistance(pkg)
    assert ok is False


def test_thermo_optic_drift_pass() -> None:
    elem = ThermoOptic(element_id="e1", drift_pm_per_c=Fraction(50, 1))
    ok, proof = check_thermo_optic_drift(elem)
    assert ok is True


def test_thermo_optic_drift_fail() -> None:
    elem = ThermoOptic(element_id="e2", drift_pm_per_c=Fraction(100, 1))
    ok, proof = check_thermo_optic_drift(elem)
    assert ok is False


def test_heater_power_budget_pass() -> None:
    budget = HeaterBudget(
        heater_id="h1", total_heater_w=Fraction(2, 10), thermal_budget_w=Fraction(1, 1)
    )
    ok, proof = check_heater_power_budget(budget)
    assert ok is True


def test_heater_power_budget_fail() -> None:
    budget = HeaterBudget(
        heater_id="h2", total_heater_w=Fraction(6, 10), thermal_budget_w=Fraction(1, 1)
    )
    ok, proof = check_heater_power_budget(budget)
    assert ok is False


def test_thermal_runaway_margin_pass() -> None:
    tra = ThermalRunaway(
        system_id="s1", operating_temp_c=Fraction(100, 1), tj_max_c=Fraction(125, 1)
    )
    ok, proof = check_thermal_runaway_margin(tra)
    assert ok is True


def test_thermal_runaway_margin_fail() -> None:
    tra = ThermalRunaway(
        system_id="s2", operating_temp_c=Fraction(120, 1), tj_max_c=Fraction(125, 1)
    )
    ok, proof = check_thermal_runaway_margin(tra)
    assert ok is False


def test_run_all_invariants() -> None:
    results = run_all_invariants()
    assert len(results) == 10
    passes = [ok for _, ok, _ in results if ok]
    fails = [ok for _, ok, _ in results if not ok]
    assert len(passes) == 5
    assert len(fails) == 5

"""Tests for photonic environmental checks.

Category 11: Environmental & Regulatory test suite.
"""

from fractions import Fraction

from axioms.logic import ProofObject
from src.hardware.photonic.environmental import (
    ConflictMinerals,
    EnergyProfile,
    ReachProfile,
    RoHSProfile,
    TemperatureRange,
    WEEEProfile,
    check_conflict_minerals,
    check_energy_star_idle,
    check_operating_temperature_range,
    check_reach_compliance,
    check_rohs_compliance,
    check_weee_recyclability,
    run_all_invariants,
)


def test_rohs_compliance_pass() -> None:
    prof = RoHSProfile(component_id="r1", lead_fraction=Fraction(5, 10000))
    ok, proof = check_rohs_compliance(prof)
    assert ok is True
    assert isinstance(proof, ProofObject)


def test_rohs_compliance_fail() -> None:
    prof = RoHSProfile(component_id="r2", lead_fraction=Fraction(2, 1000))
    ok, proof = check_rohs_compliance(prof)
    assert ok is False


def test_reach_compliance_pass() -> None:
    prof = ReachProfile(component_id="r1", svhc_fraction=Fraction(5, 10000))
    ok, proof = check_reach_compliance(prof)
    assert ok is True


def test_reach_compliance_fail() -> None:
    prof = ReachProfile(component_id="r2", svhc_fraction=Fraction(2, 1000))
    ok, proof = check_reach_compliance(prof)
    assert ok is False


def test_weee_recyclability_pass() -> None:
    prof = WEEEProfile(product_id="w1", recyclable_fraction=Fraction(75, 100))
    ok, proof = check_weee_recyclability(prof)
    assert ok is True


def test_weee_recyclability_fail() -> None:
    prof = WEEEProfile(product_id="w2", recyclable_fraction=Fraction(50, 100))
    ok, proof = check_weee_recyclability(prof)
    assert ok is False


def test_conflict_minerals_pass() -> None:
    mineral = ConflictMinerals(supplier_id="s1", has_audit=True)
    ok, proof = check_conflict_minerals(mineral)
    assert ok is True


def test_conflict_minerals_fail() -> None:
    mineral = ConflictMinerals(supplier_id="s2", has_audit=False)
    ok, proof = check_conflict_minerals(mineral)
    assert ok is False


def test_energy_star_idle_pass() -> None:
    prof = EnergyProfile(device_id="e1", idle_power_w=Fraction(3, 1))
    ok, proof = check_energy_star_idle(prof)
    assert ok is True


def test_energy_star_idle_fail() -> None:
    prof = EnergyProfile(device_id="e2", idle_power_w=Fraction(7, 1))
    ok, proof = check_energy_star_idle(prof)
    assert ok is False


def test_operating_temperature_range_pass() -> None:
    tr = TemperatureRange(
        device_id="t1", min_temp_c=Fraction(-45, 1), max_temp_c=Fraction(90, 1)
    )
    ok, proof = check_operating_temperature_range(tr)
    assert ok is True


def test_operating_temperature_range_fail() -> None:
    tr = TemperatureRange(
        device_id="t2", min_temp_c=Fraction(-30, 1), max_temp_c=Fraction(70, 1)
    )
    ok, proof = check_operating_temperature_range(tr)
    assert ok is False


def test_run_all_invariants() -> None:
    results = run_all_invariants()
    assert len(results) == 12
    passes = [ok for _, ok, _ in results if ok]
    fails = [ok for _, ok, _ in results if not ok]
    assert len(passes) == 6
    assert len(fails) == 6

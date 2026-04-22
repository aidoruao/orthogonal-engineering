"""Tests for photonic EMC checks.

Category 10: EMC & Signal Integrity test suite.
"""

from fractions import Fraction

from axioms.logic import ProofObject
from src.hardware.photonic.emc import (
    ConductedEmission,
    EmissionProfile,
    EsdImmunity,
    JitterProfile,
    OpticalCrosstalk,
    PowerSupply,
    check_emi_conducted,
    check_emi_radiated,
    check_esd_immunity,
    check_jitter,
    check_optical_crosstalk,
    check_power_supply_ripple,
    run_all_invariants,
)


def test_emi_radiated_pass() -> None:
    prof = EmissionProfile(component_id="e1", emission_dbm=Fraction(-55, 1))
    ok, proof = check_emi_radiated(prof)
    assert ok is True
    assert isinstance(proof, ProofObject)


def test_emi_radiated_fail() -> None:
    prof = EmissionProfile(component_id="e2", emission_dbm=Fraction(-40, 1))
    ok, proof = check_emi_radiated(prof)
    assert ok is False


def test_emi_conducted_pass() -> None:
    ce = ConductedEmission(component_id="c1", conducted_dbm=Fraction(-50, 1))
    ok, proof = check_emi_conducted(ce)
    assert ok is True


def test_emi_conducted_fail() -> None:
    ce = ConductedEmission(component_id="c2", conducted_dbm=Fraction(-35, 1))
    ok, proof = check_emi_conducted(ce)
    assert ok is False


def test_esd_immunity_pass() -> None:
    esd = EsdImmunity(component_id="s1", withstand_kv=Fraction(10, 1))
    ok, proof = check_esd_immunity(esd)
    assert ok is True


def test_esd_immunity_fail() -> None:
    esd = EsdImmunity(component_id="s2", withstand_kv=Fraction(4, 1))
    ok, proof = check_esd_immunity(esd)
    assert ok is False


def test_power_supply_ripple_pass() -> None:
    ps = PowerSupply(supply_id="p1", ripple_mv=Fraction(30, 1))
    ok, proof = check_power_supply_ripple(ps)
    assert ok is True


def test_power_supply_ripple_fail() -> None:
    ps = PowerSupply(supply_id="p2", ripple_mv=Fraction(70, 1))
    ok, proof = check_power_supply_ripple(ps)
    assert ok is False


def test_jitter_pass() -> None:
    jit = JitterProfile(component_id="j1", total_jitter_ps=Fraction(20, 1))
    ok, proof = check_jitter(jit)
    assert ok is True


def test_jitter_fail() -> None:
    jit = JitterProfile(component_id="j2", total_jitter_ps=Fraction(35, 1))
    ok, proof = check_jitter(jit)
    assert ok is False


def test_optical_crosstalk_pass() -> None:
    xt = OpticalCrosstalk(channel_id="x1", adjacent_channel_isolation_db=Fraction(30, 1))
    ok, proof = check_optical_crosstalk(xt)
    assert ok is True


def test_optical_crosstalk_fail() -> None:
    xt = OpticalCrosstalk(channel_id="x2", adjacent_channel_isolation_db=Fraction(20, 1))
    ok, proof = check_optical_crosstalk(xt)
    assert ok is False


def test_run_all_invariants() -> None:
    results = run_all_invariants()
    assert len(results) == 12
    passes = [ok for _, ok, _ in results if ok]
    fails = [ok for _, ok, _ in results if not ok]
    assert len(passes) == 6
    assert len(fails) == 6

"""Tests for photonic reliability checks.

Category 8: Reliability & Qualification test suite.
"""

from fractions import Fraction

from axioms.logic import ProofObject
from src.hardware.photonic.reliability import (
    AgingProfile,
    EnvironmentalStress,
    HumidityTest,
    ReliabilityProfile,
    VibrationTest,
    check_aging_margin,
    check_fit_rate,
    check_humidity_resistance,
    check_mtbf,
    check_temperature_cycling,
    check_vibration_tolerance,
    run_all_invariants,
)


def test_mtbf_pass() -> None:
    prof = ReliabilityProfile(
        component_id="r1", mtbf_hours=Fraction(200_000, 1), fit=Fraction(50, 1)
    )
    ok, proof = check_mtbf(prof)
    assert ok is True
    assert isinstance(proof, ProofObject)


def test_mtbf_fail() -> None:
    prof = ReliabilityProfile(
        component_id="r2", mtbf_hours=Fraction(50_000, 1), fit=Fraction(50, 1)
    )
    ok, proof = check_mtbf(prof)
    assert ok is False


def test_fit_rate_pass() -> None:
    prof = ReliabilityProfile(
        component_id="r1", mtbf_hours=Fraction(200_000, 1), fit=Fraction(50, 1)
    )
    ok, proof = check_fit_rate(prof)
    assert ok is True


def test_fit_rate_fail() -> None:
    prof = ReliabilityProfile(
        component_id="r2", mtbf_hours=Fraction(200_000, 1), fit=Fraction(150, 1)
    )
    ok, proof = check_fit_rate(prof)
    assert ok is False


def test_aging_margin_pass() -> None:
    age = AgingProfile(
        component_id="a1", bol_loss_db=Fraction(1, 10), eol_loss_db=Fraction(3, 10)
    )
    ok, proof = check_aging_margin(age)
    assert ok is True


def test_aging_margin_fail() -> None:
    age = AgingProfile(
        component_id="a2", bol_loss_db=Fraction(1, 10), eol_loss_db=Fraction(15, 10)
    )
    ok, proof = check_aging_margin(age)
    assert ok is False


def test_temperature_cycling_pass() -> None:
    stress = EnvironmentalStress(
        component_id="s1", cycles_survived=Fraction(1500, 1)
    )
    ok, proof = check_temperature_cycling(stress)
    assert ok is True


def test_temperature_cycling_fail() -> None:
    stress = EnvironmentalStress(
        component_id="s2", cycles_survived=Fraction(500, 1)
    )
    ok, proof = check_temperature_cycling(stress)
    assert ok is False


def test_humidity_resistance_pass() -> None:
    test = HumidityTest(component_id="h1", fails_85_85_test=False)
    ok, proof = check_humidity_resistance(test)
    assert ok is True


def test_humidity_resistance_fail() -> None:
    test = HumidityTest(component_id="h2", fails_85_85_test=True)
    ok, proof = check_humidity_resistance(test)
    assert ok is False


def test_vibration_tolerance_pass() -> None:
    vib = VibrationTest(
        component_id="v1",
        resonance_shift_hz=Fraction(1, 100),
        center_freq_hz=Fraction(1, 1),
    )
    ok, proof = check_vibration_tolerance(vib)
    assert ok is True


def test_vibration_tolerance_fail() -> None:
    vib = VibrationTest(
        component_id="v2",
        resonance_shift_hz=Fraction(8, 100),
        center_freq_hz=Fraction(1, 1),
    )
    ok, proof = check_vibration_tolerance(vib)
    assert ok is False


def test_run_all_invariants() -> None:
    results = run_all_invariants()
    assert len(results) == 12
    passes = [ok for _, ok, _ in results if ok]
    fails = [ok for _, ok, _ in results if not ok]
    assert len(passes) == 6
    assert len(fails) == 6

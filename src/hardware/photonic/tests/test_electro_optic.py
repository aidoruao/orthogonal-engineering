"""Tests for photonic electro-optic checks.

Category 6: Electro-Optic test suite.
"""

from fractions import Fraction

from axioms.logic import ProofObject
from src.hardware.photonic.electro_optic import (
    AdcConverter,
    DacConverter,
    ElectroOpticSystem,
    OpticalModulator,
    Photodetector,
    TransimpedanceAmplifier,
    check_adc_resolution,
    check_dac_sfdr,
    check_eo_conversion_power,
    check_modulator_bandwidth,
    check_modulator_vpi,
    check_photodetector_responsivity,
    check_transimpedance_gain,
    run_all_invariants,
)


def test_adc_resolution_pass() -> None:
    adc = AdcConverter(adc_id="a1", effective_bits=Fraction(10, 1))
    ok, proof = check_adc_resolution(adc)
    assert ok is True
    assert isinstance(proof, ProofObject)


def test_adc_resolution_fail() -> None:
    adc = AdcConverter(adc_id="a2", effective_bits=Fraction(6, 1))
    ok, proof = check_adc_resolution(adc)
    assert ok is False


def test_dac_sfdr_pass() -> None:
    dac = DacConverter(dac_id="d1", sfdr_dbc=Fraction(50, 1))
    ok, proof = check_dac_sfdr(dac)
    assert ok is True


def test_dac_sfdr_fail() -> None:
    dac = DacConverter(dac_id="d2", sfdr_dbc=Fraction(30, 1))
    ok, proof = check_dac_sfdr(dac)
    assert ok is False


def test_modulator_bandwidth_pass() -> None:
    mod = OpticalModulator(
        modulator_id="m1", bandwidth_ghz=Fraction(30, 1), vpi_volts=Fraction(15, 10)
    )
    ok, proof = check_modulator_bandwidth(mod)
    assert ok is True


def test_modulator_bandwidth_fail() -> None:
    mod = OpticalModulator(
        modulator_id="m2", bandwidth_ghz=Fraction(10, 1), vpi_volts=Fraction(15, 10)
    )
    ok, proof = check_modulator_bandwidth(mod)
    assert ok is False


def test_modulator_vpi_pass() -> None:
    mod = OpticalModulator(
        modulator_id="m1", bandwidth_ghz=Fraction(30, 1), vpi_volts=Fraction(15, 10)
    )
    ok, proof = check_modulator_vpi(mod)
    assert ok is True


def test_modulator_vpi_fail() -> None:
    mod = OpticalModulator(
        modulator_id="m2", bandwidth_ghz=Fraction(30, 1), vpi_volts=Fraction(3, 1)
    )
    ok, proof = check_modulator_vpi(mod)
    assert ok is False


def test_photodetector_responsivity_pass() -> None:
    det = Photodetector(detector_id="pd1", responsivity=Fraction(9, 10))
    ok, proof = check_photodetector_responsivity(det)
    assert ok is True


def test_photodetector_responsivity_fail() -> None:
    det = Photodetector(detector_id="pd2", responsivity=Fraction(5, 10))
    ok, proof = check_photodetector_responsivity(det)
    assert ok is False


def test_transimpedance_gain_pass() -> None:
    tia = TransimpedanceAmplifier(tia_id="t1", tia_gain_ohms=Fraction(6000, 1))
    ok, proof = check_transimpedance_gain(tia)
    assert ok is True


def test_transimpedance_gain_fail() -> None:
    tia = TransimpedanceAmplifier(tia_id="t2", tia_gain_ohms=Fraction(3000, 1))
    ok, proof = check_transimpedance_gain(tia)
    assert ok is False


def test_eo_conversion_power_pass() -> None:
    sys = ElectroOpticSystem(
        system_id="s1", adc_dac_power=Fraction(3, 10), total_power=Fraction(1, 1)
    )
    ok, proof = check_eo_conversion_power(sys)
    assert ok is True


def test_eo_conversion_power_fail() -> None:
    sys = ElectroOpticSystem(
        system_id="s2", adc_dac_power=Fraction(6, 10), total_power=Fraction(1, 1)
    )
    ok, proof = check_eo_conversion_power(sys)
    assert ok is False


def test_run_all_invariants() -> None:
    results = run_all_invariants()
    assert len(results) == 14
    passes = [ok for _, ok, _ in results if ok]
    fails = [ok for _, ok, _ in results if not ok]
    assert len(passes) == 7
    assert len(fails) == 7

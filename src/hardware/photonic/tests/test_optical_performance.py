"""Tests for photonic optical performance checks.

Category 5: Optical Performance test suite.
"""

from fractions import Fraction

from axioms.logic import ProofObject
from src.hardware.photonic.optical_performance import (
    DigitalReceiver,
    OpticalChannel,
    OpticalComponent,
    WavelengthSource,
    check_ber_floor,
    check_extinction_ratio,
    check_insertion_loss,
    check_osnr,
    check_polarization_dependent_loss,
    check_return_loss,
    check_wavelength_accuracy,
    run_all_invariants,
)


def test_insertion_loss_pass() -> None:
    comp = OpticalComponent(
        component_id="c1",
        insertion_loss_db=Fraction(1, 1),
        return_loss_db=Fraction(45, 1),
        extinction_ratio_db=Fraction(12, 1),
        pdl_db=Fraction(1, 10),
    )
    ok, proof = check_insertion_loss(comp)
    assert ok is True
    assert isinstance(proof, ProofObject)


def test_insertion_loss_fail() -> None:
    comp = OpticalComponent(
        component_id="c2",
        insertion_loss_db=Fraction(5, 1),
        return_loss_db=Fraction(45, 1),
        extinction_ratio_db=Fraction(12, 1),
        pdl_db=Fraction(1, 10),
    )
    ok, proof = check_insertion_loss(comp)
    assert ok is False
    assert isinstance(proof, ProofObject)


def test_return_loss_pass() -> None:
    comp = OpticalComponent(
        component_id="c1",
        insertion_loss_db=Fraction(1, 1),
        return_loss_db=Fraction(45, 1),
        extinction_ratio_db=Fraction(12, 1),
        pdl_db=Fraction(1, 10),
    )
    ok, proof = check_return_loss(comp)
    assert ok is True


def test_return_loss_fail() -> None:
    comp = OpticalComponent(
        component_id="c2",
        insertion_loss_db=Fraction(1, 1),
        return_loss_db=Fraction(35, 1),
        extinction_ratio_db=Fraction(12, 1),
        pdl_db=Fraction(1, 10),
    )
    ok, proof = check_return_loss(comp)
    assert ok is False


def test_extinction_ratio_pass() -> None:
    comp = OpticalComponent(
        component_id="c1",
        insertion_loss_db=Fraction(1, 1),
        return_loss_db=Fraction(45, 1),
        extinction_ratio_db=Fraction(12, 1),
        pdl_db=Fraction(1, 10),
    )
    ok, proof = check_extinction_ratio(comp)
    assert ok is True


def test_extinction_ratio_fail() -> None:
    comp = OpticalComponent(
        component_id="c2",
        insertion_loss_db=Fraction(1, 1),
        return_loss_db=Fraction(45, 1),
        extinction_ratio_db=Fraction(5, 1),
        pdl_db=Fraction(1, 10),
    )
    ok, proof = check_extinction_ratio(comp)
    assert ok is False


def test_pdl_pass() -> None:
    comp = OpticalComponent(
        component_id="c1",
        insertion_loss_db=Fraction(1, 1),
        return_loss_db=Fraction(45, 1),
        extinction_ratio_db=Fraction(12, 1),
        pdl_db=Fraction(1, 10),
    )
    ok, proof = check_polarization_dependent_loss(comp)
    assert ok is True


def test_pdl_fail() -> None:
    comp = OpticalComponent(
        component_id="c2",
        insertion_loss_db=Fraction(1, 1),
        return_loss_db=Fraction(45, 1),
        extinction_ratio_db=Fraction(12, 1),
        pdl_db=Fraction(1, 1),
    )
    ok, proof = check_polarization_dependent_loss(comp)
    assert ok is False


def test_wavelength_accuracy_pass() -> None:
    src = WavelengthSource(
        source_id="s1",
        actual_wavelength_nm=Fraction(1550, 1),
        grid_wavelength_nm=Fraction(1550, 1),
    )
    ok, proof = check_wavelength_accuracy(src)
    assert ok is True


def test_wavelength_accuracy_fail() -> None:
    src = WavelengthSource(
        source_id="s2",
        actual_wavelength_nm=Fraction(1550, 1) + Fraction(2, 10),
        grid_wavelength_nm=Fraction(1550, 1),
    )
    ok, proof = check_wavelength_accuracy(src)
    assert ok is False


def test_osnr_pass() -> None:
    ch = OpticalChannel(
        channel_id="ch1",
        osnr_db=Fraction(25, 1),
    )
    ok, proof = check_osnr(ch)
    assert ok is True


def test_osnr_fail() -> None:
    ch = OpticalChannel(
        channel_id="ch2",
        osnr_db=Fraction(15, 1),
    )
    ok, proof = check_osnr(ch)
    assert ok is False


def test_ber_floor_pass() -> None:
    rx = DigitalReceiver(
        receiver_id="rx1",
        ber=Fraction(1, 10_000_000_000_000),
    )
    ok, proof = check_ber_floor(rx)
    assert ok is True


def test_ber_floor_fail() -> None:
    rx = DigitalReceiver(
        receiver_id="rx2",
        ber=Fraction(1, 100_000_000_000),
    )
    ok, proof = check_ber_floor(rx)
    assert ok is False


def test_run_all_invariants() -> None:
    results = run_all_invariants()
    assert len(results) == 14
    passes = [ok for _, ok, _ in results if ok]
    fails = [ok for _, ok, _ in results if not ok]
    assert len(passes) == 7
    assert len(fails) == 7

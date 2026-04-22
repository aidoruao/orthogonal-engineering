"""Tests for photonic manufacturing checks.

Category 9: Manufacturing & Process Control test suite.
"""

from fractions import Fraction

from axioms.logic import ProofObject
from src.hardware.photonic.manufacturing import (
    EtchProcess,
    FiberCoupling,
    LithographyStep,
    WaferProfile,
    WaveguideFabrication,
    YieldData,
    check_coupling_efficiency,
    check_etch_depth_tolerance,
    check_lithography_overlay,
    check_wafer_uniformity,
    check_waveguide_width_tolerance,
    check_yield_rate,
    run_all_invariants,
)


def test_wafer_uniformity_pass() -> None:
    wafer = WaferProfile(wafer_id="w1", thickness_variation=Fraction(2, 100))
    ok, proof = check_wafer_uniformity(wafer)
    assert ok is True
    assert isinstance(proof, ProofObject)


def test_wafer_uniformity_fail() -> None:
    wafer = WaferProfile(wafer_id="w2", thickness_variation=Fraction(8, 100))
    ok, proof = check_wafer_uniformity(wafer)
    assert ok is False


def test_etch_depth_tolerance_pass() -> None:
    proc = EtchProcess(
        process_id="e1", actual_depth_nm=Fraction(220, 1), target_depth_nm=Fraction(220, 1)
    )
    ok, proof = check_etch_depth_tolerance(proc)
    assert ok is True


def test_etch_depth_tolerance_fail() -> None:
    proc = EtchProcess(
        process_id="e2", actual_depth_nm=Fraction(240, 1), target_depth_nm=Fraction(220, 1)
    )
    ok, proof = check_etch_depth_tolerance(proc)
    assert ok is False


def test_lithography_overlay_pass() -> None:
    step = LithographyStep(step_id="l1", overlay_error_nm=Fraction(30, 1))
    ok, proof = check_lithography_overlay(step)
    assert ok is True


def test_lithography_overlay_fail() -> None:
    step = LithographyStep(step_id="l2", overlay_error_nm=Fraction(70, 1))
    ok, proof = check_lithography_overlay(step)
    assert ok is False


def test_waveguide_width_tolerance_pass() -> None:
    wg = WaveguideFabrication(
        wg_id="wg1", actual_width_nm=Fraction(500, 1), target_width_nm=Fraction(500, 1)
    )
    ok, proof = check_waveguide_width_tolerance(wg)
    assert ok is True


def test_waveguide_width_tolerance_fail() -> None:
    wg = WaveguideFabrication(
        wg_id="wg2", actual_width_nm=Fraction(540, 1), target_width_nm=Fraction(500, 1)
    )
    ok, proof = check_waveguide_width_tolerance(wg)
    assert ok is False


def test_coupling_efficiency_pass() -> None:
    coup = FiberCoupling(coupling_id="c1", fiber_to_chip_loss_db=Fraction(2, 1))
    ok, proof = check_coupling_efficiency(coup)
    assert ok is True


def test_coupling_efficiency_fail() -> None:
    coup = FiberCoupling(coupling_id="c2", fiber_to_chip_loss_db=Fraction(5, 1))
    ok, proof = check_coupling_efficiency(coup)
    assert ok is False


def test_yield_rate_pass() -> None:
    yd = YieldData(lot_id="y1", die_yield=Fraction(8, 10))
    ok, proof = check_yield_rate(yd)
    assert ok is True


def test_yield_rate_fail() -> None:
    yd = YieldData(lot_id="y2", die_yield=Fraction(5, 10))
    ok, proof = check_yield_rate(yd)
    assert ok is False


def test_run_all_invariants() -> None:
    results = run_all_invariants()
    assert len(results) == 12
    passes = [ok for _, ok, _ in results if ok]
    fails = [ok for _, ok, _ in results if not ok]
    assert len(passes) == 6
    assert len(fails) == 6

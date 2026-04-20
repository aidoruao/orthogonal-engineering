"""Falsification tests for D_PUBLIC_HEALTH_CAPACITY."""
from dataclasses import replace

from ..implementation import create_nominal_claim
from ..invariants import (
    check_audit_not_stale,
    check_contact_tracer_density,
    check_icu_bed_density,
    check_lab_turnaround_within_limit,
    check_ppe_days_of_supply,
    check_sentinel_surveillance_active,
    check_ventilator_reserve_density,
    run_all_invariants,
)


def test_all_invariants_pass_on_nominal() -> None:
    results = run_all_invariants()
    assert len(results) == 7
    for name, success, proof in results:
        _ = (name, proof)
        assert success is True


def test_icu_bed_undersupply_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, staffed_icu_beds=50)
    ok, _ = check_icu_bed_density(failing)
    assert ok is False


def test_ventilator_undersupply_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, ventilator_reserve=10)
    ok, _ = check_ventilator_reserve_density(failing)
    assert ok is False


def test_ppe_undersupply_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, ppe_days_of_supply=30)
    ok, _ = check_ppe_days_of_supply(failing)
    assert ok is False


def test_tracer_undersupply_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, contact_tracer_headcount=20)
    ok, _ = check_contact_tracer_density(failing)
    assert ok is False


def test_lab_latency_over_limit_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, lab_turnaround_hours=96)
    ok, _ = check_lab_turnaround_within_limit(failing)
    assert ok is False


def test_stale_audit_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, last_independent_audit_days_ago=720)
    ok, _ = check_audit_not_stale(failing)
    assert ok is False


def test_sentinel_off_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, sentinel_surveillance_active=False)
    ok, _ = check_sentinel_surveillance_active(failing)
    assert ok is False


def test_zero_population_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, population=0)
    ok, _ = check_icu_bed_density(failing)
    assert ok is False

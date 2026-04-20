"""Falsification tests for D_DISASTER_RESILIENCE."""
from dataclasses import replace

from ..implementation import create_nominal_claim
from ..invariants import (
    check_after_action_report_current,
    check_backup_power_autonomy,
    check_cyber_playbook_current,
    check_emergency_fuel_reserve,
    check_evacuation_capacity,
    check_mutual_aid_breadth,
    check_warning_latency,
    run_all_invariants,
)


def test_all_invariants_pass_on_nominal() -> None:
    results = run_all_invariants()
    assert len(results) == 7
    for name, success, proof in results:
        _ = (name, proof)
        assert success is True


def test_warning_latency_over_limit_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, warning_latency_seconds=600)
    ok, _ = check_warning_latency(failing)
    assert ok is False


def test_evac_capacity_below_floor_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, evacuation_capacity=100_000)
    ok, _ = check_evacuation_capacity(failing)
    assert ok is False


def test_fuel_reserve_below_floor_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, emergency_fuel_days=3)
    ok, _ = check_emergency_fuel_reserve(failing)
    assert ok is False


def test_mutual_aid_below_floor_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, mutual_aid_partner_count=1)
    ok, _ = check_mutual_aid_breadth(failing)
    assert ok is False


def test_backup_power_below_floor_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, backup_power_autonomy_hours=24)
    ok, _ = check_backup_power_autonomy(failing)
    assert ok is False


def test_stale_after_action_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, last_after_action_report_days_ago=900)
    ok, _ = check_after_action_report_current(failing)
    assert ok is False


def test_missing_cyber_playbook_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, cyber_incident_response_playbook_current=False)
    ok, _ = check_cyber_playbook_current(failing)
    assert ok is False


def test_zero_population_falsifies_evac() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, population=0)
    ok, _ = check_evacuation_capacity(failing)
    assert ok is False

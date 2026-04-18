"""Falsification tests for D_NUCLEAR."""

from dataclasses import replace
from fractions import Fraction

from ..implementation import ReactorUnit
from ..invariants import check_scram_response_time, run_all_invariants


def test_all_invariants_pass() -> None:
    results = run_all_invariants()
    assert len(results) >= 4
    for check_name, result in results.items():
        assert result.startswith("PASS")


def test_failure_path_detected() -> None:
    reactor = ReactorUnit(
        unit_id="REACTOR-001",
        thermal_power_mw=Fraction(3000),
        coolant_temp_c=Fraction(290),
        coolant_pressure_bar=Fraction(155),
        scram_time_ms=Fraction(200),
        design_scram_limit_ms=Fraction(500),
        containment_integrity=True,
        fuel_burnup_mwd_per_t=Fraction(35000),
        control_rod_insertion_fraction=Fraction(1, 2),
        active_barriers=4,
    )
    failing_reactor = replace(reactor, scram_time_ms=Fraction(10000))
    success, proof = check_scram_response_time(failing_reactor)
    assert success is False
    assert "VIOLATION" in proof.conclusion

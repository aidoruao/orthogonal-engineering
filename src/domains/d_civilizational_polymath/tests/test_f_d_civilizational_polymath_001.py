"""Falsification tests for D_CIVILIZATIONAL_POLYMATH."""
from dataclasses import replace
from fractions import Fraction

from ..implementation import MIN_REGISTER_COVERAGE, create_nominal_claim
from ..invariants import (
    check_all_registers_has_capability,
    check_coverage_monotone_across_registers,
    check_cross_register_entailments_complete,
    check_polymath_capability_invariant,
    check_register_coverage_floor,
    run_all_invariants,
)


def test_all_invariants_pass_on_nominal() -> None:
    results = run_all_invariants()
    assert len(results) == 5
    for name, success, proof in results:
        _ = (name, proof)
        assert success is True


def test_missing_register_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, has_governance=False)
    ok, proof = check_all_registers_has_capability(failing)
    assert ok is False
    assert "governance" in proof.conclusion


def test_below_floor_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, mathematics_coverage=MIN_REGISTER_COVERAGE - Fraction(1, 10))
    ok, _ = check_register_coverage_floor(failing)
    assert ok is False


def test_unproved_entailment_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, cross_register_entailments_proved=8)
    ok, _ = check_cross_register_entailments_complete(failing)
    assert ok is False


def test_coverage_spread_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(
        claim,
        mathematics_coverage=Fraction(1, 2),
        science_coverage=Fraction(1, 1),
    )
    ok, _ = check_coverage_monotone_across_registers(failing)
    assert ok is False


def test_composite_falsifies_when_any_sub_fails() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, has_empirical_science=False)
    ok, proof = check_polymath_capability_invariant(failing)
    assert ok is False
    assert "FAIL" in proof.conclusion


def test_zero_entailments_falsifies() -> None:
    """A claim declaring zero cross-register entailments cannot be called
    polymath-complete; the invariant requires at least one entailment to
    have been proved, so total=0 (with proved=0) must falsify.
    """
    claim = create_nominal_claim()
    failing = replace(
        claim,
        cross_register_entailments_proved=0,
        cross_register_entailments_total=0,
    )
    ok, _ = check_cross_register_entailments_complete(failing)
    assert ok is False

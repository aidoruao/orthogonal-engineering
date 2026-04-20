"""Falsification tests for D_EXECUTIVE_GOVERNANCE."""
from dataclasses import replace
from fractions import Fraction

from ..implementation import MAX_SCOPE_EXPANSION, create_nominal_claim
from ..invariants import (
    check_congressional_review_act_compliance,
    check_consent_log_recorded,
    check_independence_review_coverage,
    check_judicial_review_preserved,
    check_publication_requirement,
    check_scope_expansion_bounded,
    check_separation_of_powers_anchors,
    run_all_invariants,
)


def test_all_invariants_pass_on_nominal() -> None:
    results = run_all_invariants()
    assert len(results) == 7
    for name, success, proof in results:
        _ = (name, proof)
        assert success is True


def test_missing_statutory_anchor_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, has_statutory_anchor=False)
    ok, _ = check_separation_of_powers_anchors(failing)
    assert ok is False


def test_missing_constitutional_anchor_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, has_constitutional_anchor=False)
    ok, _ = check_separation_of_powers_anchors(failing)
    assert ok is False


def test_cra_deadline_miss_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, cra_submission_within_60_days=False)
    ok, _ = check_congressional_review_act_compliance(failing)
    assert ok is False


def test_judicial_review_foreclosed_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, judicial_review_standing_preserved=False)
    ok, _ = check_judicial_review_preserved(failing)
    assert ok is False


def test_publication_missing_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, published_in_federal_register=False)
    ok, _ = check_publication_requirement(failing)
    assert ok is False


def test_independence_review_below_floor_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(
        claim,
        independence_review_items_signed=3,
        independence_review_items_total=10,
    )
    ok, _ = check_independence_review_coverage(failing)
    assert ok is False


def test_scope_expansion_over_limit_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, scope_expansion=MAX_SCOPE_EXPANSION + Fraction(1, 10))
    ok, _ = check_scope_expansion_bounded(failing)
    assert ok is False


def test_consent_log_missing_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, consent_log_entry_recorded=False)
    ok, _ = check_consent_log_recorded(failing)
    assert ok is False

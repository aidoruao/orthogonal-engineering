"""Falsification tests for D_SECULAR_PROJECTION."""
from dataclasses import replace

from ..implementation import create_nominal_claim
from ..invariants import (
    check_every_premise_has_witness,
    check_every_witness_has_falsifier,
    check_no_appeal_to_authority,
    check_popperian_audit_green,
    check_projection_non_expansive,
    check_projection_signature_present,
    run_all_invariants,
)


def test_all_invariants_pass_on_nominal() -> None:
    results = run_all_invariants()
    assert len(results) == 6
    for name, success, proof in results:
        _ = (name, proof)
        assert success is True


def test_missing_witness_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, secular_witnesses=claim.theological_premises - 1)
    ok, _ = check_every_premise_has_witness(failing)
    assert ok is False


def test_missing_falsifier_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, falsification_rules=claim.secular_witnesses - 1)
    ok, _ = check_every_witness_has_falsifier(failing)
    assert ok is False


def test_projection_shrinking_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(
        claim,
        projected_falsifier_cardinality=claim.unprojected_falsifier_cardinality - 1,
    )
    ok, _ = check_projection_non_expansive(failing)
    assert ok is False


def test_appeal_to_authority_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, appeal_to_authority_count=1)
    ok, proof = check_no_appeal_to_authority(failing)
    assert ok is False
    assert "1 appeals to authority" in proof.conclusion


def test_popperian_audit_red_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, popperian_audit_green=False)
    ok, _ = check_popperian_audit_green(failing)
    assert ok is False


def test_bad_signature_falsifies() -> None:
    claim = create_nominal_claim()
    failing = replace(claim, projection_signature_hash="not-a-real-hash")
    ok, _ = check_projection_signature_present(failing)
    assert ok is False

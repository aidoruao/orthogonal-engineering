"""Tests for D_ARXIV_RISK_MANAGEMENT_BOWTIE.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_risk_management_bowtie.implementation import (
    BowtieModel,
    DAGTransform,
    ProbabilityCapture,
    RiskManagementClaim,
)
from domains.d_arxiv_risk_management_bowtie.invariants import (
    check_bowtie_complete,
    check_dag_valid,
    check_probability_capture,
    check_safe_state_semantics,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_bowtie():
    return BowtieModel(
        model_name="instant_payments",
        has_causes=True,
        has_top_event=True,
        has_barriers=True,
        has_consequences=True,
    )


def make_dag():
    return DAGTransform(
        is_dag=True,
        has_safe_state_semantics=True,
        has_activation_nodes=True,
        supports_bayesian_inference=True,
    )


def make_prob():
    return ProbabilityCapture(
        questionnaire_generated=True,
        expert_disagreement_analyzed=True,
        uses_prior_regularization=True,
    )


def make_safe_claim():
    return RiskManagementClaim(
        bowtie=make_bowtie(),
        dag=make_dag(),
        probability=make_prob(),
    )


def make_bad_bowtie_claim():
    return RiskManagementClaim(
        bowtie=BowtieModel(
            model_name="incomplete",
            has_causes=True,
            has_top_event=False,
            has_barriers=True,
            has_consequences=True,
        ),
        dag=make_dag(),
        probability=make_prob(),
    )


def make_bad_dag_claim():
    return RiskManagementClaim(
        bowtie=make_bowtie(),
        dag=DAGTransform(
            is_dag=False,
            has_safe_state_semantics=True,
            has_activation_nodes=True,
            supports_bayesian_inference=False,
        ),
        probability=make_prob(),
    )


def make_bad_prob_claim():
    return RiskManagementClaim(
        bowtie=make_bowtie(),
        dag=make_dag(),
        probability=ProbabilityCapture(
            questionnaire_generated=False,
            expert_disagreement_analyzed=False,
            uses_prior_regularization=False,
        ),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_bowtie_complete_pass():
    claim = make_safe_claim()
    success, proof = check_bowtie_complete(claim)
    assert success is True
    assert "complete" in proof.conclusion


def test_check_bowtie_complete_fail():
    claim = make_bad_bowtie_claim()
    success, proof = check_bowtie_complete(claim)
    assert success is False
    assert "incomplete" in proof.conclusion


def test_check_dag_valid_pass():
    claim = make_safe_claim()
    success, proof = check_dag_valid(claim)
    assert success is True
    assert "valid" in proof.conclusion


def test_check_dag_valid_fail():
    claim = make_bad_dag_claim()
    success, proof = check_dag_valid(claim)
    assert success is False
    assert "invalid" in proof.conclusion


def test_check_probability_capture_pass():
    claim = make_safe_claim()
    success, proof = check_probability_capture(claim)
    assert success is True
    assert "complete" in proof.conclusion


def test_check_probability_capture_fail():
    claim = make_bad_prob_claim()
    success, proof = check_probability_capture(claim)
    assert success is False
    assert "incomplete" in proof.conclusion


def test_check_safe_state_semantics_pass():
    claim = make_safe_claim()
    success, proof = check_safe_state_semantics(claim)
    assert success is True
    assert "present" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_pass"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"

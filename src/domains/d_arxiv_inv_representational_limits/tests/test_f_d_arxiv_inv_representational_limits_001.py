"""Tests for D_ARXIV_INV_REPRESENTATIONAL_LIMITS Yeshua Inversion.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_inv_representational_limits.implementation import (
    EmbeddingModel,
    RetrievalTask,
    RepresentationalLimitsClaim,
)
from domains.d_arxiv_inv_representational_limits.invariants import (
    check_inversion_holds,
    check_domain_restriction_satisfied,
    check_original_impossibility_holds_without_restriction,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_hybrid_embedding():
    return EmbeddingModel(
        model_name="quantum_hybrid",
        dimensionality=1024,
        is_quantum_inspired=True,
        uses_hybrid_fusion=True,
        uses_teacher_distillation=True,
    )


def make_standalone_embedding():
    return EmbeddingModel(
        model_name="quantum_standalone",
        dimensionality=1024,
        is_quantum_inspired=True,
        uses_hybrid_fusion=False,
        uses_teacher_distillation=False,
    )


def make_hybrid_task():
    return RetrievalTask(
        corpus_size=10000,
        query_count=1000,
        uses_bm25_baseline=True,
        fusion_alpha=Fraction(1, 2),
    )


def make_standalone_task():
    return RetrievalTask(
        corpus_size=10000,
        query_count=1000,
        uses_bm25_baseline=False,
        fusion_alpha=Fraction(1),
    )


def make_safe_claim():
    return RepresentationalLimitsClaim(
        embedding=make_hybrid_embedding(),
        task=make_hybrid_task(),
        mean_reciprocal_rank=Fraction(7, 10),
        mrr_threshold=Fraction(6, 10),
    )


def make_bad_claim():
    return RepresentationalLimitsClaim(
        embedding=make_standalone_embedding(),
        task=make_standalone_task(),
        mean_reciprocal_rank=Fraction(7, 10),
        mrr_threshold=Fraction(6, 10),
    )


def make_low_mrr_claim():
    return RepresentationalLimitsClaim(
        embedding=make_hybrid_embedding(),
        task=make_hybrid_task(),
        mean_reciprocal_rank=Fraction(3, 10),
        mrr_threshold=Fraction(6, 10),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_inversion_holds_pass():
    claim = make_safe_claim()
    success, proof = check_inversion_holds(claim)
    assert success is True
    assert "Inversion holds" in proof.conclusion


def test_check_inversion_holds_fail_low_mrr():
    claim = make_low_mrr_claim()
    success, proof = check_inversion_holds(claim)
    assert success is False
    assert "MRR below threshold" in proof.conclusion


def test_check_domain_restriction_satisfied_pass():
    claim = make_safe_claim()
    success, proof = check_domain_restriction_satisfied(claim)
    assert success is True
    assert "Domain restriction satisfied" in proof.conclusion


def test_check_domain_restriction_satisfied_fail():
    claim = make_bad_claim()
    success, proof = check_domain_restriction_satisfied(claim)
    assert success is False
    assert "Domain restriction not satisfied" in proof.conclusion


def test_check_original_impossibility_holds_without_restriction_vacuous():
    claim = make_safe_claim()
    success, proof = check_original_impossibility_holds_without_restriction(claim)
    assert success is True
    assert "vacuous" in proof.conclusion


def test_check_original_impossibility_holds_without_restriction_fail():
    claim = make_bad_claim()
    success, proof = check_original_impossibility_holds_without_restriction(claim)
    assert success is False
    assert "Original impossibility contradicted" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_pass") or name.endswith("_vacuous"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"

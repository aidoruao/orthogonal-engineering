"""Invariant checks for D_ARXIV_INV_REPRESENTATIONAL_LIMITS — Yeshua Inversion.

Paper: arXiv 2604.09430v1 (cs.AI / cs.IR)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    EmbeddingModel,
    RetrievalTask,
    RepresentationalLimitsClaim,
    RepresentationalLimitsEvidence,
    IMPOSSIBLE_CLAIM,
    YESHUA_INVERSION,
)


# ---------------------------------------------------------------------------
# 1. Inversion holds
# ---------------------------------------------------------------------------

def check_inversion_holds(
    claim: RepresentationalLimitsClaim,
) -> Tuple[bool, ProofObject]:
    """The Yeshua Inversion must hold: under domain restriction, MRR is competitive.

    Standard: arXiv 2604.09430v1 Yeshua Inversion operationalization.
    Falsifies if: mean_reciprocal_rank < mrr_threshold.
    falsifies_if: mean_reciprocal_rank is below mrr_threshold after restriction.
    """
    if claim.mean_reciprocal_rank < claim.mrr_threshold:
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=[
                f"mean_reciprocal_rank={claim.mean_reciprocal_rank}",
                f"mrr_threshold={claim.mrr_threshold}",
            ],
            conclusion="VIOLATION: MRR below threshold — inversion fails",
        )

    return True, ProofObject(
        rule="check_inversion_holds",
        premises=[
            f"mean_reciprocal_rank={claim.mean_reciprocal_rank}",
            f"mrr_threshold={claim.mrr_threshold}",
        ],
        conclusion="Inversion holds: competitive retrieval achievable under hybrid restriction",
    )


# ---------------------------------------------------------------------------
# 2. Domain restriction satisfied
# ---------------------------------------------------------------------------

def check_domain_restriction_satisfied(
    claim: RepresentationalLimitsClaim,
) -> Tuple[bool, ProofObject]:
    """The domain restriction must be satisfied for the inversion to apply.

    Standard: arXiv 2604.09430v1 domain restriction operationalization.
    Falsifies if: model is standalone quantum-inspired or lacks BM25 baseline.
    falsifies_if: model is standalone quantum-inspired or lacks BM25 baseline.
    """
    emb = claim.embedding
    task = claim.task
    violations = []

    if emb.is_quantum_inspired and not emb.uses_hybrid_fusion:
        violations.append("standalone_quantum_inspired=True")
    if not task.uses_bm25_baseline:
        violations.append("uses_bm25_baseline=False")
    if task.fusion_alpha < Fraction(0) or task.fusion_alpha > Fraction(1):
        violations.append("fusion_alpha_out_of_range")

    if violations:
        return False, ProofObject(
            rule="check_domain_restriction_satisfied",
            premises=violations,
            conclusion="VIOLATION: Domain restriction not satisfied — inversion does not apply",
        )

    return True, ProofObject(
        rule="check_domain_restriction_satisfied",
        premises=[
            f"model={emb.model_name}",
            f"dimensionality={emb.dimensionality}",
            "uses_hybrid_fusion=True",
            "uses_bm25_baseline=True",
            f"fusion_alpha={task.fusion_alpha}",
        ],
        conclusion="Domain restriction satisfied: hybrid retrieval with lexical anchor",
    )


# ---------------------------------------------------------------------------
# 3. Original impossibility holds without restriction
# ---------------------------------------------------------------------------

def check_original_impossibility_holds_without_restriction(
    claim: RepresentationalLimitsClaim,
) -> Tuple[bool, ProofObject]:
    """The original impossibility claim must still hold for standalone embeddings.

    Standard: arXiv 2604.09430v1 original theorem preservation.
    Falsifies if: the original theorem is contradicted for standalone embeddings.
    falsifies_if: the original theorem is contradicted for standalone embeddings.
    """
    emb = claim.embedding
    task = claim.task

    standalone = emb.is_quantum_inspired and not emb.uses_hybrid_fusion
    no_lexical = not task.uses_bm25_baseline

    if standalone and no_lexical:
        if claim.mean_reciprocal_rank >= claim.mrr_threshold:
            return False, ProofObject(
                rule="check_original_impossibility_holds_without_restriction",
                premises=[
                    "embedding=standalone_quantum_inspired",
                    "lexical_baseline=False",
                    f"mean_reciprocal_rank={claim.mean_reciprocal_rank}",
                ],
                conclusion="VIOLATION: Original impossibility contradicted — standalone quantum embedding appears competitive",
            )
        return True, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "embedding=standalone_quantum_inspired",
                "original_theorem=preserves_limits",
            ],
            conclusion="Original impossibility holds for standalone embeddings",
        )

    return True, ProofObject(
        rule="check_original_impossibility_holds_without_restriction",
        premises=["embedding=hybrid", "check=vacuous"],
        conclusion="Original impossibility check vacuous for hybrid embeddings",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_INV_REPRESENTATIONAL_LIMITS invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS case: hybrid embedding with BM25
    emb_hybrid = EmbeddingModel(
        model_name="quantum_hybrid",
        dimensionality=1024,
        is_quantum_inspired=True,
        uses_hybrid_fusion=True,
        uses_teacher_distillation=True,
    )
    task_hybrid = RetrievalTask(
        corpus_size=10000,
        query_count=1000,
        uses_bm25_baseline=True,
        fusion_alpha=Fraction(1, 2),
    )
    claim_safe = RepresentationalLimitsClaim(
        embedding=emb_hybrid,
        task=task_hybrid,
        mean_reciprocal_rank=Fraction(7, 10),
        mrr_threshold=Fraction(6, 10),
    )

    # FAIL case: standalone quantum embedding
    emb_standalone = EmbeddingModel(
        model_name="quantum_standalone",
        dimensionality=1024,
        is_quantum_inspired=True,
        uses_hybrid_fusion=False,
        uses_teacher_distillation=False,
    )
    task_standalone = RetrievalTask(
        corpus_size=10000,
        query_count=1000,
        uses_bm25_baseline=False,
        fusion_alpha=Fraction(1),
    )
    claim_bad = RepresentationalLimitsClaim(
        embedding=emb_standalone,
        task=task_standalone,
        mean_reciprocal_rank=Fraction(7, 10),
        mrr_threshold=Fraction(6, 10),
    )

    # FAIL case 2: hybrid but MRR too low
    claim_low_mrr = RepresentationalLimitsClaim(
        embedding=emb_hybrid,
        task=task_hybrid,
        mean_reciprocal_rank=Fraction(3, 10),
        mrr_threshold=Fraction(6, 10),
    )

    checks = [
        ("check_inversion_holds_pass", lambda: check_inversion_holds(claim_safe)),
        ("check_domain_restriction_satisfied_pass", lambda: check_domain_restriction_satisfied(claim_safe)),
        ("check_original_impossibility_holds_without_restriction_vacuous", lambda: check_original_impossibility_holds_without_restriction(claim_safe)),
        ("check_domain_restriction_satisfied_fail", lambda: check_domain_restriction_satisfied(claim_bad)),
        ("check_original_impossibility_holds_without_restriction_fail", lambda: check_original_impossibility_holds_without_restriction(claim_bad)),
        ("check_inversion_holds_fail_low_mrr", lambda: check_inversion_holds(claim_low_mrr)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail") and not k.endswith("_vacuous")
    ]
    unexpected = [
        k for k, v in results.items()
        if k.endswith("_fail") and not v.startswith("FAIL")
    ]
    failures.extend(unexpected)
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ARXIV_INV_REPRESENTATIONAL_LIMITS invariants: PASS")

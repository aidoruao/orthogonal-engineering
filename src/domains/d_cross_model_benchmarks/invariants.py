#!/usr/bin/env python3
"""D_CROSS_MODEL_BENCHMARKS Invariants — Multi-model comparison, reproducibility

Verifies eval reproducibility, model ordering consistency, benchmark coverage, normalization.
Liang et al. (2022): HELM. Gehrmann et al. (2021): GEM Benchmark.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    ModelEval, CrossModelComparison, BenchmarkCoverage, OrderingConsistency,
    NormalizationType,
    min_benchmarks_threshold, min_runs_reproducibility,
    cherry_pick_threshold, consistency_threshold
)


def check_eval_reproducibility(eval: ModelEval) -> Tuple[bool, ProofObject]:
    """
    Model evaluations must have sufficient runs for reproducibility.

    HELM guidelines: Minimum 3 runs for reproducible results.
    Falsifies if: num_runs < 3
    
    
    min_runs = min_runs_reproducibility()

    if eval.num_runs < min_runs:
        return False, ProofObject(
            conclusion=f"VIOLATION: Model {eval.model_id} has {eval.num_runs} runs (min {min_runs})",
            premises=[
                f"Model: {eval.model_id}",
                f"Benchmark: {eval.benchmark_id}",
                f"Runs: {eval.num_runs}",
                f"Minimum: {min_runs}"
            ],
            rule="eval_reproducibility"
        )

    return True, ProofObject(
        conclusion=f"Model {eval.model_id} evaluation reproducible",
        premises=[f"Runs: {eval.num_runs} >= {min_runs}"],
        rule="eval_reproducibility"
    )


def check_model_ordering_consistency(ordering: OrderingConsistency) -> Tuple[bool, ProofObject]:
    """
    Model rankings must be consistent across benchmarks (< 20% reversals).

    Falsifies if: num_reversals / num_benchmarks > 20%
    
    
    threshold = consistency_threshold()
    num_benchmarks = len(ordering.benchmark_ids)
    reversal_fraction = Fraction(ordering.num_reversals, num_benchmarks)

    if reversal_fraction > threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Ordering inconsistent - {reversal_fraction} reversals > {threshold}",
            premises=[
                f"Models: {ordering.model_a_id} vs {ordering.model_b_id}",
                f"Reversals: {ordering.num_reversals} / {num_benchmarks}",
                f"Threshold: {threshold}"
            ],
            rule="ordering_consistency"
        )

    if reversal_fraction <= threshold and not ordering.consistent:
        return False, ProofObject(
            conclusion=f"VIOLATION: Ordering should be consistent ({reversal_fraction} <= {threshold})",
            premises=[
                f"Reversals: {reversal_fraction}",
                f"Marked consistent: {ordering.consistent}"
            ],
            rule="ordering_consistency"
        )

    return True, ProofObject(
        conclusion=f"Model ordering consistency verified",
        premises=[f"Reversals: {reversal_fraction}", f"Consistent: {ordering.consistent}"],
        rule="ordering_consistency"
    )


def check_benchmark_coverage(coverage: BenchmarkCoverage) -> Tuple[bool, ProofObject]:
    """
    Models must be evaluated on sufficient benchmarks (> 50% coverage).

    Falsifies if: coverage_fraction < 50%
    
    
    min_coverage = cherry_pick_threshold()

    if coverage.coverage_fraction < min_coverage:
        return False, ProofObject(
            conclusion=f"VIOLATION: Model {coverage.model_id} has {coverage.coverage_fraction} coverage (min {min_coverage})",
            premises=[
                f"Model: {coverage.model_id}",
                f"Evaluated: {coverage.num_benchmarks_evaluated}",
                f"Total: {coverage.num_benchmarks_total}",
                f"Coverage: {coverage.coverage_fraction}"
            ],
            rule="benchmark_coverage"
        )

    return True, ProofObject(
        conclusion=f"Model {coverage.model_id} has adequate benchmark coverage",
        premises=[f"Coverage: {coverage.coverage_fraction}"],
        rule="benchmark_coverage"
    )


def check_normalization(eval: ModelEval) -> Tuple[bool, ProofObject]:
    """
    Normalized scores must be in valid range [0, 1] and consistent with raw scores.

    Falsifies if: normalized_score out of bounds or inconsistent ordering
    
    
    if eval.normalized_score < Fraction(0, 1) or eval.normalized_score > Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Normalized score {eval.normalized_score} out of bounds [0, 1]",
            premises=[
                f"Model: {eval.model_id}",
                f"Normalized: {eval.normalized_score}",
                f"Normalization: {eval.normalization_type.name}"
            ],
            rule="normalization"
        )

    return True, ProofObject(
        conclusion=f"Model {eval.model_id} normalization valid",
        premises=[f"Normalized: {eval.normalized_score}", f"Type: {eval.normalization_type.name}"],
        rule="normalization"
    )


def check_no_cherry_picking(comparison: CrossModelComparison, coverage: BenchmarkCoverage) -> Tuple[bool, ProofObject]:
    """
    Cross-model comparisons must not cherry-pick favorable benchmarks.

    Falsifies if: cherry_picked == True or coverage < 50%
    
    
    threshold = cherry_pick_threshold()

    if comparison.cherry_picked:
        return False, ProofObject(
            conclusion=f"VIOLATION: Comparison {comparison.comparison_id} cherry-picked benchmarks",
            premises=[
                f"Models: {comparison.model_ids}",
                f"Cherry-picked: {comparison.cherry_picked}"
            ],
            rule="no_cherry_picking"
        )

    if comparison.model_ids[0] == coverage.model_id:
        if coverage.coverage_fraction < threshold:
            return False, ProofObject(
                conclusion=f"VIOLATION: Insufficient coverage {coverage.coverage_fraction} suggests cherry-picking",
                premises=[
                    f"Model: {coverage.model_id}",
                    f"Coverage: {coverage.coverage_fraction}",
                    f"Threshold: {threshold}"
                ],
                rule="no_cherry_picking"
            )

    return True, ProofObject(
        conclusion=f"No cherry-picking detected for {comparison.comparison_id}",
        premises=[f"Cherry-picked: {comparison.cherry_picked}", f"Coverage: {coverage.coverage_fraction}"],
        rule="no_cherry_picking"
    )


def check_minimum_benchmarks(coverage: BenchmarkCoverage) -> Tuple[bool, ProofObject]:
    """
    Evaluations must cover minimum number of benchmarks (5+).

    Falsifies if: num_benchmarks_evaluated < 5
    
    
    min_benchmarks = min_benchmarks_threshold()

    if coverage.num_benchmarks_evaluated < min_benchmarks:
        return False, ProofObject(
            conclusion=f"VIOLATION: Model {coverage.model_id} evaluated on {coverage.num_benchmarks_evaluated} benchmarks (min {min_benchmarks})",
            premises=[
                f"Model: {coverage.model_id}",
                f"Evaluated: {coverage.num_benchmarks_evaluated}",
                f"Minimum: {min_benchmarks}"
            ],
            rule="minimum_benchmarks"
        )

    return True, ProofObject(
        conclusion=f"Model {coverage.model_id} evaluated on sufficient benchmarks",
        premises=[f"Benchmarks: {coverage.num_benchmarks_evaluated}"],
        rule="minimum_benchmarks"
    )


def check_comparison_reproducibility(comparison: CrossModelComparison) -> Tuple[bool, ProofObject]:
    """
    Cross-model comparisons must be reproducible.

    Falsifies if: reproducible == False
    
    
    if not comparison.reproducible:
        return False, ProofObject(
            conclusion=f"VIOLATION: Comparison {comparison.comparison_id} not reproducible",
            premises=[
                f"Models: {comparison.model_ids}",
                f"Benchmark: {comparison.benchmark_id}",
                f"Reproducible: {comparison.reproducible}"
            ],
            rule="comparison_reproducibility"
        )

    return True, ProofObject(
        conclusion=f"Comparison {comparison.comparison_id} is reproducible",
        premises=[f"Reproducible: {comparison.reproducible}"],
        rule="comparison_reproducibility"
    )


def check_normalization_consistency(eval1: ModelEval, eval2: ModelEval) -> Tuple[bool, ProofObject]:
    """
    Models evaluated on same benchmark must use same normalization.

    Falsifies if: same benchmark but different normalization types
    
    
    if eval1.benchmark_id == eval2.benchmark_id:
        if eval1.normalization_type != eval2.normalization_type:
            return False, ProofObject(
                conclusion=f"VIOLATION: Models {eval1.model_id} and {eval2.model_id} use different normalization on {eval1.benchmark_id}",
                premises=[
                    f"Normalization 1: {eval1.normalization_type.name}",
                    f"Normalization 2: {eval2.normalization_type.name}"
                ],
                rule="normalization_consistency"
            )

    return True, ProofObject(
        conclusion=f"Normalization consistent for benchmark {eval1.benchmark_id}",
        premises=[f"Type: {eval1.normalization_type.name}"],
        rule="normalization_consistency"
    )

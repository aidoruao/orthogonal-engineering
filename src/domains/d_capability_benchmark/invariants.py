#!/usr/bin/env python3
"""D_CAPABILITY_BENCHMARK Invariants — AI evaluation, benchmark validity

Verifies benchmark reproducibility, data leakage checks, score bounds, statistical significance.
Bowman et al. (2021): Dynabench. Mitchell et al. (2019): Model Cards.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Benchmark, TestCase, CapabilityScore, DataLeakageCheck, ReproducibilityTest,
    CapabilityType,
    score_bounds, significance_threshold, leakage_threshold, reproducibility_tolerance
)


def check_benchmark_reproducibility(bench: Benchmark, repro: ReproducibilityTest) -> Tuple[bool, ProofObject]:
    """
    Benchmarks must be reproducible (replicated scores within tolerance).

    NeurIPS reproducibility guidelines: Results should replicate within +/- 2%.
    Falsifies if: reproducible claimed but difference exceeds tolerance
    
    
    falsifies_if: condition_evaluated_to_false"""
    tolerance = reproducibility_tolerance()

    if repro.reproducible and repro.difference > tolerance:
        return False, ProofObject(
            conclusion=f"VIOLATION: Benchmark {bench.benchmark_id} claimed reproducible but difference {repro.difference} > {tolerance}",
            premises=[
                f"Original score: {repro.original_score}",
                f"Replicated score: {repro.replicated_score}",
                f"Difference: {repro.difference}",
                f"Tolerance: {tolerance}"
            ],
            rule="benchmark_reproducibility"
        )

    if not repro.reproducible and repro.difference <= tolerance:
        return False, ProofObject(
            conclusion=f"VIOLATION: Benchmark {bench.benchmark_id} should be reproducible (difference {repro.difference} <= {tolerance})",
            premises=[
                f"Difference: {repro.difference}",
                f"Reproducible: {repro.reproducible}"
            ],
            rule="benchmark_reproducibility"
        )

    return True, ProofObject(
        conclusion=f"Benchmark {bench.benchmark_id} reproducibility valid",
        premises=[f"Difference: {repro.difference}", f"Reproducible: {repro.reproducible}"],
        rule="benchmark_reproducibility"
    )


def check_no_data_leakage(leakage: DataLeakageCheck) -> Tuple[bool, ProofObject]:
    """
    Test data must not appear in training data (< 1% overlap acceptable).

    Dodge et al. (2021): Documenting Large Webtext Corpora.
    Falsifies if: overlap_fraction >= 1% and not detected
    
    
    falsifies_if: condition_evaluated_to_false"""
    threshold = leakage_threshold()

    if leakage.overlap_fraction >= threshold and not leakage.leakage_detected:
        return False, ProofObject(
            conclusion=f"VIOLATION: Data leakage {leakage.overlap_fraction} >= {threshold} but not flagged",
            premises=[
                f"Overlap: {leakage.overlap_fraction}",
                f"Threshold: {threshold}",
                f"Detected: {leakage.leakage_detected}"
            ],
            rule="data_leakage"
        )

    if leakage.overlap_fraction < threshold and leakage.leakage_detected:
        return False, ProofObject(
            conclusion=f"VIOLATION: Data leakage flagged but overlap {leakage.overlap_fraction} < {threshold}",
            premises=[
                f"Overlap: {leakage.overlap_fraction}",
                f"Detected: {leakage.leakage_detected}"
            ],
            rule="data_leakage"
        )

    return True, ProofObject(
        conclusion=f"Data leakage check for {leakage.check_id} valid",
        premises=[f"Overlap: {leakage.overlap_fraction}", f"Detected: {leakage.leakage_detected}"],
        rule="data_leakage"
    )


def check_score_bounds(score: CapabilityScore) -> Tuple[bool, ProofObject]:
    """
    Capability scores must be in valid range [0.0, 1.0].

    Falsifies if: accuracy < 0 or accuracy > 1
    
    
    falsifies_if: condition_evaluated_to_false"""
    min_score, max_score = score_bounds()

    if score.accuracy < min_score or score.accuracy > max_score:
        return False, ProofObject(
            conclusion=f"VIOLATION: Score {score.accuracy} out of bounds [{min_score}, {max_score}]",
            premises=[
                f"Model: {score.model_id}",
                f"Benchmark: {score.benchmark_id}",
                f"Accuracy: {score.accuracy}",
                f"Valid range: [{min_score}, {max_score}]"
            ],
            rule="score_bounds"
        )

    return True, ProofObject(
        conclusion=f"Score {score.accuracy} for {score.model_id} within bounds",
        premises=[f"Accuracy: {score.accuracy}"],
        rule="score_bounds"
    )


def check_statistical_significance(score: CapabilityScore) -> Tuple[bool, ProofObject]:
    """
    Scores must have sufficient trials for statistical significance.

    Falsifies if: statistically_significant but num_trials < 10 or variance too high
    
    
    falsifies_if: condition_evaluated_to_false"""
    min_trials = 10
    max_variance = Fraction(1, 10)  # 10% variance max for significance

    if score.statistically_significant:
        if score.num_trials < min_trials:
            return False, ProofObject(
                conclusion=f"VIOLATION: Score claimed significant but only {score.num_trials} trials (min {min_trials})",
                premises=[
                    f"Model: {score.model_id}",
                    f"Trials: {score.num_trials}",
                    f"Minimum: {min_trials}"
                ],
                rule="statistical_significance"
            )

        if score.variance > max_variance:
            return False, ProofObject(
                conclusion=f"VIOLATION: Score claimed significant but variance {score.variance} > {max_variance}",
                premises=[
                    f"Model: {score.model_id}",
                    f"Variance: {score.variance}",
                    f"Max: {max_variance}"
                ],
                rule="statistical_significance"
            )

    return True, ProofObject(
        conclusion=f"Score for {score.model_id} statistical validity verified",
        premises=[f"Trials: {score.num_trials}", f"Variance: {score.variance}", f"Significant: {score.statistically_significant}"],
        rule="statistical_significance"
    )


def check_capability_ordering(score1: CapabilityScore, score2: CapabilityScore) -> Tuple[bool, ProofObject]:
    """
    Model rankings must be consistent with capability ordering.

    Falsifies if: same model on same benchmark has inconsistent scores
    
    
    falsifies_if: condition_evaluated_to_false"""
    if score1.model_id == score2.model_id and score1.benchmark_id == score2.benchmark_id:
        if abs(score1.accuracy - score2.accuracy) > Fraction(5, 100):  # 5% tolerance
            return False, ProofObject(
                conclusion=f"VIOLATION: Inconsistent scores for {score1.model_id} on {score1.benchmark_id}",
                premises=[
                    f"Score 1: {score1.accuracy}",
                    f"Score 2: {score2.accuracy}",
                    f"Difference: {abs(score1.accuracy - score2.accuracy)}"
                ],
                rule="capability_ordering"
            )

    return True, ProofObject(
        conclusion=f"Capability ordering consistent",
        premises=[f"Model: {score1.model_id}", f"Scores: {score1.accuracy}, {score2.accuracy}"],
        rule="capability_ordering"
    )


def check_ground_truth_verified(test: TestCase) -> Tuple[bool, ProofObject]:
    """
    Test cases must have verified ground truth.

    Falsifies if: ground_truth_verified == False
    
    
    falsifies_if: condition_evaluated_to_false"""
    if not test.ground_truth_verified:
        return False, ProofObject(
            conclusion=f"VIOLATION: Test case {test.test_id} lacks verified ground truth",
            premises=[
                f"Test: {test.test_id}",
                f"Benchmark: {test.benchmark_id}",
                f"Ground truth verified: {test.ground_truth_verified}"
            ],
            rule="ground_truth"
        )

    return True, ProofObject(
        conclusion=f"Test case {test.test_id} has verified ground truth",
        premises=[f"Verified: {test.ground_truth_verified}"],
        rule="ground_truth"
    )


def check_training_data_exclusion(test: TestCase, leakage: DataLeakageCheck) -> Tuple[bool, ProofObject]:
    """
    Test cases in training data must trigger leakage detection.

    Falsifies if: test.in_training_data but not leakage.leakage_detected
    
    
    falsifies_if: condition_evaluated_to_false"""
    if test.benchmark_id == leakage.benchmark_id:
        if test.in_training_data and not leakage.leakage_detected:
            return False, ProofObject(
                conclusion=f"VIOLATION: Test {test.test_id} in training data but leakage not detected",
                premises=[
                    f"In training data: {test.in_training_data}",
                    f"Leakage detected: {leakage.leakage_detected}"
                ],
                rule="training_data_exclusion"
            )

    return True, ProofObject(
        conclusion=f"Training data exclusion check valid for {test.test_id}",
        premises=[f"In training: {test.in_training_data}", f"Leakage detected: {leakage.leakage_detected}"],
        rule="training_data_exclusion"
    )


def check_benchmark_coverage(bench: Benchmark) -> Tuple[bool, ProofObject]:
    """
    Benchmarks must have sufficient test cases (minimum 100).

    Falsifies if: num_test_cases < 100
    
    
    falsifies_if: condition_evaluated_to_false"""
    min_cases = 100

    if bench.num_test_cases < min_cases:
        return False, ProofObject(
            conclusion=f"VIOLATION: Benchmark {bench.benchmark_id} has only {bench.num_test_cases} test cases (min {min_cases})",
            premises=[
                f"Test cases: {bench.num_test_cases}",
                f"Minimum: {min_cases}"
            ],
            rule="benchmark_coverage"
        )

    return True, ProofObject(
        conclusion=f"Benchmark {bench.benchmark_id} has sufficient test cases",
        premises=[f"Test cases: {bench.num_test_cases}"],
        rule="benchmark_coverage"
    )

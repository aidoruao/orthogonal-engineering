"""D_CAPABILITY_BENCHMARK implementation — AI Evaluation, Benchmark Validity

Layer: 3 (Regulatory/Research)
CardinalStrength: PREDICATIVE

AI capability benchmarks, test case validity, data leakage, reproducibility.
NeurIPS (2021): On the Dangers of Stochastic Parrots. Bowman et al. (2021): Dynabench.
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum
from typing import List, Optional


class CapabilityType(Enum):
    """AI capability classification"""
    REASONING = 1
    LANGUAGE_UNDERSTANDING = 2
    CODE_GENERATION = 3
    VISION = 4
    MULTIMODAL = 5


@dataclass
class Benchmark:
    """AI capability benchmark"""
    benchmark_id: str
    name: str
    capability: CapabilityType
    num_test_cases: int
    reproducible: bool
    data_leakage_checked: bool


@dataclass
class TestCase:
    """Individual test case in benchmark"""
    test_id: str
    benchmark_id: str
    difficulty: Fraction  # 0.0 - 1.0
    ground_truth_verified: bool
    in_training_data: bool  # Data leakage check


@dataclass
class CapabilityScore:
    """Model capability score on benchmark"""
    model_id: str
    benchmark_id: str
    accuracy: Fraction  # 0.0 - 1.0
    num_trials: int
    variance: Fraction
    statistically_significant: bool


@dataclass
class DataLeakageCheck:
    """Data leakage detection"""
    check_id: str
    benchmark_id: str
    model_id: str
    overlap_fraction: Fraction  # Fraction of test cases in training
    leakage_detected: bool


@dataclass
class ReproducibilityTest:
    """Reproducibility verification"""
    test_id: str
    benchmark_id: str
    original_score: Fraction
    replicated_score: Fraction
    difference: Fraction
    reproducible: bool


def score_bounds() -> tuple[Fraction, Fraction]:
    """Valid score bounds (0.0 - 1.0)"""
    return (Fraction(0, 1), Fraction(1, 1))


def significance_threshold() -> Fraction:
    """Statistical significance threshold (p < 0.05)"""
    return Fraction(5, 100)


def leakage_threshold() -> Fraction:
    """Data leakage threshold (< 1%)"""
    return Fraction(1, 100)


def reproducibility_tolerance() -> Fraction:
    """Reproducibility tolerance (+/- 2%)"""
    return Fraction(2, 100)

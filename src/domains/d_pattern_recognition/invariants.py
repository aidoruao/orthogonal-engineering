#!/usr/bin/env python3
"""Pattern Recognition Domain Invariants — Classification metrics, validation.

Standards:
- Precision/recall/F1
- Cross-validation
- Confusion matrix properties
- Overfitting detection

Falsifies if:
- Precision > 1 or < 0
- Recall > 1 or < 0
- F1 not harmonic mean
- Overfitting detected
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import ConfusionMatrix, CrossValidation, ClassificationResult


def check_precision_bounds(matrix: ConfusionMatrix, cls: str) -> Tuple[bool, ProofObject]:
    """Precision must be in [0, 1].
    
    Falsifies if: precision is below 0 or above 1.
    """
    p = matrix.precision(cls)
    
    if p < Fraction(0) or p > Fraction(1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Precision {p} outside valid range [0, 1]",
            premises=[f"Class: {cls}", f"Precision: {p}"],
            rule="precision_bounds"
        )
    
    return True, ProofObject(
        conclusion="Precision within valid bounds",
        premises=[f"Class: {cls}", f"Precision: {p}"],
        rule="precision_valid"
    )


def check_recall_bounds(matrix: ConfusionMatrix, cls: str) -> Tuple[bool, ProofObject]:
    """Recall must be in [0, 1].
    
    Falsifies if: recall is below 0 or above 1.
    """
    r = matrix.recall(cls)
    
    if r < Fraction(0) or r > Fraction(1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Recall {r} outside valid range [0, 1]",
            premises=[f"Class: {cls}", f"Recall: {r}"],
            rule="recall_bounds"
        )
    
    return True, ProofObject(
        conclusion="Recall within valid bounds",
        premises=[f"Class: {cls}", f"Recall: {r}"],
        rule="recall_valid"
    )


def check_f1_harmonic_mean(matrix: ConfusionMatrix, cls: str) -> Tuple[bool, ProofObject]:
    """F1 should be harmonic mean of precision and recall.
    
    Falsifies if: F1 differs from 2pr/(p+r) beyond tolerance.
    """
    p = matrix.precision(cls)
    r = matrix.recall(cls)
    f1 = matrix.f1_score(cls)
    
    if p + r > 0:
        expected = 2 * p * r / (p + r)
        if abs(f1 - expected) > Fraction(1, 1000):  # small tolerance
            return False, ProofObject(
                conclusion=f"VIOLATION: F1 {f1} not harmonic mean of P={p}, R={r}",
                premises=[f"Expected: {expected}", f"Got: {f1}"],
                rule="f1_harmonic_mean"
            )
    
    return True, ProofObject(
        conclusion="F1 is proper harmonic mean",
        premises=[f"F1: {f1}", f"P: {p}", f"R: {r}"],
        rule="f1_valid"
    )


def check_confusion_matrix_sum(matrix: ConfusionMatrix) -> Tuple[bool, ProofObject]:
    """All entries in confusion matrix should be non-negative.
    
    Falsifies if: any confusion matrix count is negative.
    """
    for (t, p), count in matrix.matrix.items():
        if count < 0:
            return False, ProofObject(
                conclusion=f"VIOLATION: Negative count in confusion matrix",
                premises=[f"True: {t}, Pred: {p}, Count: {count}"],
                rule="confusion_matrix_non_negative"
            )
    
    return True, ProofObject(
        conclusion="Confusion matrix valid",
        premises=[f"Classes: {len(matrix.classes)}"],
        rule="confusion_matrix_valid"
    )


def check_overfitting(cv: CrossValidation) -> Tuple[bool, ProofObject]:
    """High variance in cross-validation indicates overfitting.
    
    Falsifies if: variance exceeds threshold.
    """
    variance = cv.variance()
    THRESHOLD = Fraction(1, 100)  # 0.01
    
    if variance > THRESHOLD:
        return False, ProofObject(
            conclusion=f"VIOLATION: Cross-validation variance {variance} suggests overfitting",
            premises=[
                f"Folds: {cv.k_folds}",
                f"Variance: {variance}",
                f"Mean: {cv.mean_score()}"
            ],
            rule="cross_validation_overfitting"
        )
    
    return True, ProofObject(
        conclusion="Cross-validation variance acceptable",
        premises=[f"Variance: {variance}", f"Mean: {cv.mean_score()}"],
        rule="no_overfitting"
    )


def check_confidence_calibration(result: ClassificationResult) -> Tuple[bool, ProofObject]:
    """Confidence should reflect accuracy (well-calibrated).
    
    Falsifies if: high-confidence prediction is incorrect.
    """
    HIGH_CONFIDENCE = Fraction(95, 100)
    
    if result.confidence > HIGH_CONFIDENCE and not result.is_correct():
        return False, ProofObject(
            conclusion=f"VIOLATION: High confidence {result.confidence} but incorrect prediction",
            premises=[
                f"True: {result.true_label}",
                f"Pred: {result.predicted_label}",
                f"Confidence: {result.confidence}"
            ],
            rule="confidence_calibration"
        )
    
    return True, ProofObject(
        conclusion="Confidence calibrated",
        premises=[f"Correct: {result.is_correct()}", f"Confidence: {result.confidence}"],
        rule="calibration_valid"
    )

"""D_PATTERN_RECOGNITION implementation — Pattern Matching & Recognition Systems

Layer: 4 (Institutional - Computing)
CardinalStrength: PREDICATIVE

Standards:
- Feature extraction
- Classification metrics (precision, recall, F1)
- Overfitting detection
- Cross-validation
- Confusion matrix analysis
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from fractions import Fraction


@dataclass
class ClassificationResult:
    """Single prediction outcome."""
    true_label: str
    predicted_label: str
    confidence: Fraction
    
    def is_correct(self) -> bool:
        return self.true_label == self.predicted_label
    
    def is_false_positive(self, target_class: str) -> bool:
        return not self.is_correct() and self.predicted_label == target_class
    
    def is_false_negative(self, target_class: str) -> bool:
        return not self.is_correct() and self.true_label == target_class


@dataclass
class ConfusionMatrix:
    """Classification performance matrix."""
    classes: List[str]
    matrix: Dict[Tuple[str, str], int]  # (true, pred) -> count
    
    def true_positives(self, cls: str) -> int:
        return self.matrix.get((cls, cls), 0)
    
    def false_positives(self, cls: str) -> int:
        total = sum(self.matrix.get((t, cls), 0) for t in self.classes if t != cls)
        return total
    
    def false_negatives(self, cls: str) -> int:
        total = sum(self.matrix.get((cls, p), 0) for p in self.classes if p != cls)
        return total
    
    def true_negatives(self, cls: str) -> int:
        total = 0
        for t in self.classes:
            for p in self.classes:
                if t != cls and p != cls:
                    total += self.matrix.get((t, p), 0)
        return total
    
    def precision(self, cls: str) -> Fraction:
        tp = self.true_positives(cls)
        fp = self.false_positives(cls)
        if tp + fp == 0:
            return Fraction(0)
        return Fraction(tp, tp + fp)
    
    def recall(self, cls: str) -> Fraction:
        tp = self.true_positives(cls)
        fn = self.false_negatives(cls)
        if tp + fn == 0:
            return Fraction(0)
        return Fraction(tp, tp + fn)
    
    def f1_score(self, cls: str) -> Fraction:
        p = self.precision(cls)
        r = self.recall(cls)
        if p + r == 0:
            return Fraction(0)
        return 2 * p * r / (p + r)


@dataclass
class CrossValidation:
    """K-fold cross-validation results."""
    k_folds: int
    fold_scores: List[Fraction]
    
    def mean_score(self) -> Fraction:
        if not self.fold_scores:
            return Fraction(0)
        return sum(self.fold_scores) / len(self.fold_scores)
    
    def variance(self) -> Fraction:
        if len(self.fold_scores) < 2:
            return Fraction(0)
        mean = self.mean_score()
        squared_diffs = [(s - mean) ** 2 for s in self.fold_scores]
        return sum(squared_diffs) / len(squared_diffs)
    
    def overfitting_indicator(self) -> bool:
        """High variance suggests overfitting."""
        return self.variance() > Fraction(1, 100)  # threshold


@dataclass
class FeatureVector:
    """Extracted features for classification."""
    vector_id: str
    features: List[Fraction]
    label: str
    
    def dimensionality(self) -> int:
        return len(self.features)
    
    def l2_norm(self) -> Fraction:
        """Euclidean norm."""
        return sum(f * f for f in self.features) ** Fraction(1, 2)


@dataclass
class PatternChecker:
    """Checker for pattern recognition system validity."""
    results: List[ClassificationResult] = field(default_factory=list)
    matrices: List[ConfusionMatrix] = field(default_factory=list)
    cv_results: List[CrossValidation] = field(default_factory=list)
    
    def low_precision_classes(self, threshold: Fraction) -> List[str]:
        """Classes with precision below threshold."""
        low = []
        for matrix in self.matrices:
            for cls in matrix.classes:
                if matrix.precision(cls) < threshold:
                    low.append(cls)
        return low
    
    def overfit_models(self) -> List[CrossValidation]:
        """CV results showing overfitting."""
        return [cv for cv in self.cv_results if cv.overfitting_indicator()]

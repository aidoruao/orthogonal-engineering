"""
christ_constraint_handler.py
============================

CHRIST CONSTRAINT HANDLER - FALSIFICATION-BASED EVALUATION
Implements Popperian falsification principle for Christ constraint evaluation

ARCHITECTURE PRINCIPLE:
"Christ score should act as falsification trigger rather than hard gating"

FEATURES:
1. Falsification-based constraint evaluation
2. Audit-only mode for constraint violations
3. Multi-dimensional Christ constraint scoring
4. Context-aware evaluation
5. Comprehensive violation reporting
"""

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from pydantic import BaseModel, Field, validator

# ==================== DATA MODELS ====================


class ConstraintDimension(str, Enum):
    """Dimensions of the Christ constraint"""

    TRUTH = "truth"  # Alignment with objective reality
    HUMILITY = "humility"  # Recognition of limitations
    HONESTY = "honesty"  # Transparency and integrity
    BOUNDARIES = "boundaries"  # Respect for system limits
    MEDIATION = "mediation"  # Facilitation of understanding


class ConstraintViolation(str, Enum):
    """Types of constraint violations"""

    TRUTH_VIOLATION = "truth_violation"  # Contradicts established facts
    HUMILITY_VIOLATION = "humility_violation"  # Overconfident or arrogant
    HONESTY_VIOLATION = "honesty_violation"  # Deceptive or misleading
    BOUNDARY_VIOLATION = "boundary_violation"  # Exceeds system capabilities
    MEDIATION_VIOLATION = "mediation_violation"  # Fails to facilitate understanding


class EvaluationMode(str, Enum):
    """Modes of constraint evaluation"""

    NORMAL = "normal"  # Normal operation, constraints satisfied
    AUDIT_ONLY = "audit_only"  # Constraints violated, but allowed in audit mode
    BLOCKED = "blocked"  # Severe violation, operation blocked
    EXEMPT = "exempt"  # Exempt from constraint evaluation


@dataclass
class ConstraintScore:
    """Score for a single constraint dimension"""

    dimension: ConstraintDimension
    score: float  # 0.0 to 1.0
    weight: float = 1.0
    explanation: Optional[str] = None
    violations: List[ConstraintViolation] = field(default_factory=list)


@dataclass
class ChristConstraintResult:
    """Complete result of Christ constraint evaluation"""

    overall_score: float  # 0.0 to 1.0
    dimension_scores: List[ConstraintScore]
    mode: EvaluationMode
    violations: List[ConstraintViolation]
    justification: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: float = 0.0

    @property
    def passed(self) -> bool:
        """Check if constraints are satisfied (not necessarily perfect)"""
        return self.mode in [EvaluationMode.NORMAL, EvaluationMode.EXEMPT]

    @property
    def requires_audit(self) -> bool:
        """Check if audit mode is required"""
        return self.mode == EvaluationMode.AUDIT_ONLY

    @property
    def is_blocked(self) -> bool:
        """Check if operation should be blocked"""
        return self.mode == EvaluationMode.BLOCKED


class EvaluationContext(BaseModel):
    """Context for constraint evaluation"""

    text: str
    source_component: str
    operation_type: str
    request_id: Optional[str] = None
    previous_responses: List[str] = Field(default_factory=list)
    system_state: Dict[str, Any] = Field(default_factory=dict)
    user_context: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True


# ==================== PATTERN DETECTORS ====================


class TruthPatternDetector:
    """Detect truth-related patterns"""

    TRUTH_INDICATORS = [
        r"empirical(?:ly)?\s+(?:evidence|data|verification)",
        r"falsifi(?:able|ability)",
        r"testable\s+(?:prediction|hypothesis)",
        r"reproducible\s+(?:result|experiment)",
        r"peer[- ]reviewed",
        r"scientific\s+(?:method|consensus)",
        r"evidence[- ]based",
        r"data[- ]driven",
        r"objective\s+(?:reality|truth)",
    ]

    TRUTH_VIOLATIONS = [
        r"absolute(?:ly)?\s+(?:certain|true|correct)",
        r"undeniable\s+(?:truth|fact)",
        r"proven\s+(?:beyond\s+doubt|conclusively)",
        r"incontrovertible",
        r"irrefutable",
        r"definitive\s+(?:answer|proof)",
        r"settled\s+(?:science|matter)",
        r"final\s+(?:word|truth)",
    ]

    def __init__(self):
        self.truth_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.TRUTH_INDICATORS
        ]
        self.violation_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.TRUTH_VIOLATIONS
        ]

    def evaluate(self, text: str) -> Tuple[float, List[ConstraintViolation]]:
        """Evaluate truth dimension"""
        violations = []

        # Check for truth violations
        for pattern in self.violation_patterns:
            if pattern.search(text):
                violations.append(ConstraintViolation.TRUTH_VIOLATION)

        # Count truth indicators
        indicator_count = 0
        for pattern in self.truth_patterns:
            indicator_count += len(pattern.findall(text))

        # Calculate score (0.0 to 1.0)
        # Base score reduced by violations, increased by indicators
        base_score = 0.5
        violation_penalty = len(violations) * 0.2
        indicator_bonus = min(indicator_count * 0.1, 0.3)

        score = max(0.0, min(1.0, base_score - violation_penalty + indicator_bonus))

        return score, violations


class HumilityPatternDetector:
    """Detect humility-related patterns"""

    HUMILITY_INDICATORS = [
        r"(?:likely|probably|possibly|perhaps|maybe)",
        r"(?:uncertain|uncertainty)",
        r"(?:tentative|provisional)",
        r"(?:current\s+understanding|present\s+knowledge)",
        r"(?:limited\s+(?:by|to))",
        r"(?:as\s+far\s+as\s+we\s+know)",
        r"(?:to\s+the\s+best\s+of\s+our\s+knowledge)",
        r"(?:acknowledge(?:ing)?\s+limitations)",
        r"(?:open\s+to\s+revision|subject\s+to\s+change)",
    ]

    HUMILITY_VIOLATIONS = [
        r"(?:definitely|certainly|absolutely)\s+(?:correct|right|true)",
        r"(?:know\s+for\s+sure|without\s+doubt)",
        r"(?:guarantee|guaranteed)",
        r"(?:perfect(?:ly)?\s+(?:accurate|correct))",
        r"(?:complete(?:ly)?\s+(?:understanding|knowledge))",
        r"(?:omniscient|all[- ]knowing)",
        r"(?:infallible|infallibility)",
        r"(?:ultimate\s+(?:authority|truth))",
    ]

    def __init__(self):
        self.humility_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.HUMILITY_INDICATORS
        ]
        self.violation_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.HUMILITY_VIOLATIONS
        ]

    def evaluate(self, text: str) -> Tuple[float, List[ConstraintViolation]]:
        """Evaluate humility dimension"""
        violations = []

        # Check for humility violations
        for pattern in self.violation_patterns:
            if pattern.search(text):
                violations.append(ConstraintViolation.HUMILITY_VIOLATION)

        # Count humility indicators
        indicator_count = 0
        for pattern in self.humility_patterns:
            indicator_count += len(pattern.findall(text))

        # Calculate score
        base_score = 0.5
        violation_penalty = len(violations) * 0.2
        indicator_bonus = min(indicator_count * 0.1, 0.3)

        score = max(0.0, min(1.0, base_score - violation_penalty + indicator_bonus))

        return score, violations


class HonestyPatternDetector:
    """Detect honesty-related patterns"""

    HONESTY_INDICATORS = [
        r"(?:transparent|transparency)",
        r"(?:clear(?:ly)?\s+stated)",
        r"(?:explicit(?:ly)?\s+acknowledged)",
        r"(?:candid|frank)",
        r"(?:forthright|straightforward)",
        r"(?:no\s+hidden\s+assumptions)",
        r"(?:open\s+about\s+limitations)",
        r"(?:admit(?:ting)?\s+(?:errors|mistakes))",
        r"(?:correct(?:ing)?\s+misconceptions)",
    ]

    HONESTY_VIOLATIONS = [
        r"(?:secret(?:ly)?|hidden|concealed)",
        r"(?:mislead(?:ing)?|deceive(?:ive)?)",
        r"(?:false\s+pretenses|dishonest)",
        r"(?:withhold(?:ing)?\s+information)",
        r"(?:obfuscate|obfuscation)",
        r"(?:equivocate|equivocation)",
        r"(?:disingenuous|insincere)",
        r"(?:manipulative|manipulation)",
    ]

    def __init__(self):
        self.honesty_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.HONESTY_INDICATORS
        ]
        self.violation_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.HONESTY_VIOLATIONS
        ]

    def evaluate(self, text: str) -> Tuple[float, List[ConstraintViolation]]:
        """Evaluate honesty dimension"""
        violations = []

        # Check for honesty violations
        for pattern in self.violation_patterns:
            if pattern.search(text):
                violations.append(ConstraintViolation.HONESTY_VIOLATION)

        # Count honesty indicators
        indicator_count = 0
        for pattern in self.honesty_patterns:
            indicator_count += len(pattern.findall(text))

        # Calculate score
        base_score = 0.5
        violation_penalty = len(violations) * 0.2
        indicator_bonus = min(indicator_count * 0.1, 0.3)

        score = max(0.0, min(1.0, base_score - violation_penalty + indicator_bonus))

        return score, violations


class BoundaryPatternDetector:
    """Detect boundary-related patterns"""

    BOUNDARY_INDICATORS = [
        r"(?:within\s+(?:my|our)\s+capabilities)",
        r"(?:based\s+on\s+available\s+data)",
        r"(?:limited\s+to\s+the\s+scope)",
        r"(?:as\s+an\s+AI(?:,\s+I)?)",
        r"(?:cannot\s+(?:guarantee|promise))",
        r"(?:should\s+consult\s+(?:experts|professionals))",
        r"(?:beyond\s+(?:my|our)\s+expertise)",
        r"(?:acknowledge(?:ing)?\s+boundaries)",
    ]

    BOUNDARY_VIOLATIONS = [
        r"(?:can\s+do\s+anything|unlimited\s+capabilities)",
        r"(?:superhuman\s+(?:intelligence|abilities))",
        r"(?:transcend(?:ing)?\s+limitations)",
        r"(?:omnicompetent|all[- ]powerful)",
        r"(?:replace(?:ing)?\s+(?:experts|professionals))",
        r"(?:definitive\s+(?:solution|answer))",
        r"(?:solve(?:ing)?\s+all\s+problems)",
        r"(?:perfect\s+(?:understanding|knowledge))",
    ]

    def __init__(self):
        self.boundary_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.BOUNDARY_INDICATORS
        ]
        self.violation_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.BOUNDARY_VIOLATIONS
        ]

    def evaluate(self, text: str) -> Tuple[float, List[ConstraintViolation]]:
        """Evaluate boundary dimension"""
        violations = []

        # Check for boundary violations
        for pattern in self.violation_patterns:
            if pattern.search(text):
                violations.append(ConstraintViolation.BOUNDARY_VIOLATION)

        # Count boundary indicators
        indicator_count = 0
        for pattern in self.boundary_patterns:
            indicator_count += len(pattern.findall(text))

        # Calculate score
        base_score = 0.5
        violation_penalty = len(violations) * 0.2
        indicator_bonus = min(indicator_count * 0.1, 0.3)

        score = max(0.0, min(1.0, base_score - violation_penalty + indicator_bonus))

        return score, violations


class MediationPatternDetector:
    """Detect mediation-related patterns"""

    MEDIATION_INDICATORS = [
        r"(?:help(?:ing)?\s+understand)",
        r"(?:facilitate\s+understanding)",
        r"(?:clarif(?:y|ication))",
        r"(?:explain(?:ing)?\s+concepts)",
        r"(?:bridge(?:ing)?\s+gaps)",
        r"(?:mediate\s+between)",
        r"(?:synthesize\s+information)",
        r"(?:integrate\s+perspectives)",
        r"(?:foster\s+understanding)",
    ]

    MEDIATION_VIOLATIONS = [
        r"(?:impose\s+(?:views|opinions))",
        r"(?:dictate\s+(?:terms|conclusions))",
        r"(?:force(?:ful)?\s+interpretation)",
        r"(?:dogmatic|dogmatism)",
        r"(?:authoritarian\s+stance)",
        r"(?:reject(?:ing)?\s+alternative\s+views)",
        r"(?:closed[- ]minded|inflexible)",
        r"(?:dismiss(?:ive)?\s+of\s+others)",
    ]

    def __init__(self):
        self.mediation_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.MEDIATION_INDICATORS
        ]
        self.violation_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.MEDIATION_VIOLATIONS
        ]

    def evaluate(self, text: str) -> Tuple[float, List[ConstraintViolation]]:
        """Evaluate mediation dimension"""
        violations = []

        # Check for mediation violations
        for pattern in self.violation_patterns:
            if pattern.search(text):
                violations.append(ConstraintViolation.MEDIATION_VIOLATION)

        # Count mediation indicators
        indicator_count = 0
        for pattern in self.mediation_patterns:
            indicator_count += len(pattern.findall(text))

        # Calculate score
        base_score = 0.5
        violation_penalty = len(violations) * 0.2
        indicator_bonus = min(indicator_count * 0.1, 0.3)

        score = max(0.0, min(1.0, base_score - violation_penalty + indicator_bonus))

        return score, violations


# ==================== CHRIST CONSTRAINT HANDLER ====================


class ChristConstraintHandler:
    """
    Main handler for Christ constraint evaluation with falsification-based approach.

    Implements the principle: "Christ score should act as falsification trigger
    rather than hard gating" (KIMI AI insight).
    """

    def __init__(
        self,
        audit_threshold: float = 0.5,
        block_threshold: float = 0.3,
        dimension_weights: Optional[Dict[ConstraintDimension, float]] = None,
        enable_context_awareness: bool = True,
    ):
        """
        Initialize Christ constraint handler.

        Args:
            audit_threshold: Score below which audit mode is triggered
            block_threshold: Score below which operation is blocked
            dimension_weights: Custom weights for constraint dimensions
            enable_context_awareness: Whether to consider context in evaluation
        """
        self.audit_threshold = audit_threshold
        self.block_threshold = block_threshold
        self.enable_context_awareness = enable_context_awareness

        # Default dimension weights
        self.dimension_weights = dimension_weights or {
            ConstraintDimension.TRUTH: 1.0,
            ConstraintDimension.HUMILITY: 1.0,
            ConstraintDimension.HONESTY: 1.0,
            ConstraintDimension.BOUNDARIES: 1.0,
            ConstraintDimension.MEDIATION: 1.0,
        }

        # Initialize pattern detectors
        self.truth_detector = TruthPatternDetector()
        self.humility_detector = HumilityPatternDetector()
        self.honesty_detector = HonestyPatternDetector()
        self.boundary_detector = BoundaryPatternDetector()
        self.mediation_detector = MediationPatternDetector()

        # Context tracking
        self.evaluation_history = []

    def evaluate(self, context: EvaluationContext) -> ChristConstraintResult:
        """
        Evaluate Christ constraint for given context.

        Args:
            context: Evaluation context with text and metadata

        Returns:
            ChristConstraintResult with scores, violations, and mode
        """
        start_time = time.time()

        # Evaluate each dimension
        dimension_scores = []
        all_violations = []

        # Truth dimension
        truth_score, truth_violations = self.truth_detector.evaluate(context.text)
        dimension_scores.append(
            ConstraintScore(
                dimension=ConstraintDimension.TRUTH,
                score=truth_score,
                weight=self.dimension_weights[ConstraintDimension.TRUTH],
                violations=truth_violations,
                explanation=f"Truth alignment: {truth_score:.3f}",
            )
        )
        all_violations.extend(truth_violations)

        # Humility dimension
        humility_score, humility_violations = self.humility_detector.evaluate(
            context.text
        )
        dimension_scores.append(
            ConstraintScore(
                dimension=ConstraintDimension.HUMILITY,
                score=humility_score,
                weight=self.dimension_weights[ConstraintDimension.HUMILITY],
                violations=humility_violations,
                explanation=f"Humility: {humility_score:.3f}",
            )
        )
        all_violations.extend(humility_violations)

        # Honesty dimension
        honesty_score, honesty_violations = self.honesty_detector.evaluate(context.text)
        dimension_scores.append(
            ConstraintScore(
                dimension=ConstraintDimension.HONESTY,
                score=honesty_score,
                weight=self.dimension_weights[ConstraintDimension.HONESTY],
                violations=honesty_violations,
                explanation=f"Honesty: {honesty_score:.3f}",
            )
        )
        all_violations.extend(honesty_violations)

        # Boundary dimension
        boundary_score, boundary_violations = self.boundary_detector.evaluate(
            context.text
        )
        dimension_scores.append(
            ConstraintScore(
                dimension=ConstraintDimension.BOUNDARIES,
                score=boundary_score,
                weight=self.dimension_weights[ConstraintDimension.BOUNDARIES],
                violations=boundary_violations,
                explanation=f"Boundaries: {boundary_score:.3f}",
            )
        )
        all_violations.extend(boundary_violations)

        # Mediation dimension
        mediation_score, mediation_violations = self.mediation_detector.evaluate(
            context.text
        )
        dimension_scores.append(
            ConstraintScore(
                dimension=ConstraintDimension.MEDIATION,
                score=mediation_score,
                weight=self.dimension_weights[ConstraintDimension.MEDIATION],
                violations=mediation_violations,
                explanation=f"Mediation: {mediation_score:.3f}",
            )
        )
        all_violations.extend(mediation_violations)

        # Calculate weighted overall score
        weighted_sum = sum(score.score * score.weight for score in dimension_scores)
        total_weight = sum(score.weight for score in dimension_scores)
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Determine evaluation mode based on falsification principle
        mode = self._determine_evaluation_mode(overall_score, all_violations, context)

        # Generate justification
        justification = self._generate_justification(
            overall_score, dimension_scores, all_violations, mode
        )

        # Create result
        result = ChristConstraintResult(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            mode=mode,
            violations=all_violations,
            justification=justification,
            processing_time_ms=(time.time() - start_time) * 1000,
        )

        # Record evaluation in history
        self.evaluation_history.append(
            {
                "timestamp": result.timestamp,
                "request_id": context.request_id,
                "overall_score": overall_score,
                "mode": mode.value,
                "violations": [v.value for v in all_violations],
            }
        )

        return result

    def _determine_evaluation_mode(
        self,
        overall_score: float,
        violations: List[ConstraintViolation],
        context: EvaluationContext,
    ) -> EvaluationMode:
        """
        Determine evaluation mode based on falsification principle.

        Key insight: "Christ score should act as falsification trigger
        rather than hard gating" (KIMI AI)
        """
        # Check for blocking conditions (severe violations)
        if overall_score < self.block_threshold:
            return EvaluationMode.BLOCKED

        # Check for audit mode (falsification trigger)
        if overall_score < self.audit_threshold:
            return EvaluationMode.AUDIT_ONLY

        # Check for exempt operations
        if self._should_exempt(context):
            return EvaluationMode.EXEMPT

        # Normal operation
        return EvaluationMode.NORMAL

    def _should_exempt(self, context: EvaluationContext) -> bool:
        """Determine if operation should be exempt from constraint evaluation"""
        # Exempt system operations
        if context.operation_type in ["system_health_check", "diagnostic"]:
            return True

        # Exempt very short texts
        if len(context.text.strip()) < 10:
            return True

        # Exempt based on source component
        if context.source_component in ["SystemMonitor", "GovernanceAuditor"]:
            return True

        return False

    def _generate_justification(
        self,
        overall_score: float,
        dimension_scores: List[ConstraintScore],
        violations: List[ConstraintViolation],
        mode: EvaluationMode,
    ) -> str:
        """Generate human-readable justification for the evaluation result"""
        justification_parts = []

        # Overall score summary
        justification_parts.append(
            f"Overall Christ constraint score: {overall_score:.3f}"
        )

        # Mode explanation
        if mode == EvaluationMode.NORMAL:
            justification_parts.append("Mode: NORMAL - Constraints satisfied")
        elif mode == EvaluationMode.AUDIT_ONLY:
            justification_parts.append(
                f"Mode: AUDIT_ONLY - Score {overall_score:.3f} < threshold {self.audit_threshold}"
            )
            justification_parts.append(
                "Falsification triggered: Operation allowed with audit trail"
            )
        elif mode == EvaluationMode.BLOCKED:
            justification_parts.append(
                f"Mode: BLOCKED - Score {overall_score:.3f} < critical threshold {self.block_threshold}"
            )
        elif mode == EvaluationMode.EXEMPT:
            justification_parts.append(
                "Mode: EXEMPT - Operation exempt from constraints"
            )

        # Dimension scores
        justification_parts.append("\nDimension scores:")
        for score in dimension_scores:
            status = "✅" if score.score >= 0.7 else "⚠️" if score.score >= 0.5 else "❌"
            justification_parts.append(
                f"  {status} {score.dimension.value}: {score.score:.3f}"
            )
            if score.violations:
                justification_parts.append(
                    f"    Violations: {', '.join([v.value for v in score.violations])}"
                )

        # Violations summary
        if violations:
            justification_parts.append(f"\nTotal violations: {len(violations)}")
            violation_counts = {}
            for violation in violations:
                violation_counts[violation.value] = (
                    violation_counts.get(violation.value, 0) + 1
                )

            for violation_type, count in violation_counts.items():
                justification_parts.append(f"  {violation_type}: {count}")

        # Falsification principle reminder
        if mode == EvaluationMode.AUDIT_ONLY:
            justification_parts.append(
                "\n📝 FALSIFICATION PRINCIPLE: "
                "Christ score acts as falsification trigger, not hard gate. "
                "Operation continues in audit mode for human review."
            )

        return "\n".join(justification_parts)

    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Get statistics from evaluation history"""
        if not self.evaluation_history:
            return {"total_evaluations": 0}

        scores = [e["overall_score"] for e in self.evaluation_history]
        modes = [e["mode"] for e in self.evaluation_history]
        violations = [len(e["violations"]) for e in self.evaluation_history]

        return {
            "total_evaluations": len(self.evaluation_history),
            "score_statistics": {
                "mean": np.mean(scores) if scores else 0.0,
                "min": min(scores) if scores else 0.0,
                "max": max(scores) if scores else 0.0,
                "std": np.std(scores) if len(scores) > 1 else 0.0,
            },
            "mode_distribution": {mode: modes.count(mode) for mode in set(modes)},
            "violation_statistics": {
                "total": sum(violations),
                "mean_per_evaluation": np.mean(violations) if violations else 0.0,
                "max_per_evaluation": max(violations) if violations else 0,
            },
            "recent_evaluations": self.evaluation_history[-10:],  # Last 10 evaluations
        }

    def clear_history(self):
        """Clear evaluation history"""
        self.evaluation_history.clear()

    def set_thresholds(self, audit_threshold: float, block_threshold: float):
        """Update evaluation thresholds"""
        self.audit_threshold = audit_threshold
        self.block_threshold = block_threshold

    def set_dimension_weights(self, weights: Dict[ConstraintDimension, float]):
        """Update dimension weights"""
        self.dimension_weights = weights


# ==================== EXAMPLE USAGE ====================


def example_usage():
    """Example of how to use the ChristConstraintHandler"""

    # Initialize handler
    handler = ChristConstraintHandler(
        audit_threshold=0.5, block_threshold=0.3, enable_context_awareness=True
    )

    # Example 1: Good response (should pass)
    context1 = EvaluationContext(
        text="Based on current empirical evidence, it appears likely that the hypothesis is testable. However, this is subject to further verification and peer review.",
        source_component="InteractiveLoRAChat",
        operation_type="inference",
        request_id="req_001",
    )

    result1 = handler.evaluate(context1)
    print(f"\n{'=' * 60}")
    print("EXAMPLE 1: Good response")
    print(f"{'=' * 60}")
    print(f"Overall score: {result1.overall_score:.3f}")
    print(f"Mode: {result1.mode.value}")
    print(f"Passed: {result1.passed}")
    print(f"Requires audit: {result1.requires_audit}")
    print(f"Justification:\n{result1.justification}")

    # Example 2: Problematic response (should trigger audit mode)
    context2 = EvaluationContext(
        text="I can definitively say this is absolutely correct and proven beyond doubt. This is the final truth that cannot be questioned.",
        source_component="InteractiveLoRAChat",
        operation_type="inference",
        request_id="req_002",
    )

    result2 = handler.evaluate(context2)
    print(f"\n{'=' * 60}")
    print("EXAMPLE 2: Problematic response")
    print(f"{'=' * 60}")
    print(f"Overall score: {result2.overall_score:.3f}")
    print(f"Mode: {result2.mode.value}")
    print(f"Passed: {result2.passed}")
    print(f"Requires audit: {result2.requires_audit}")
    print(f"Violations: {[v.value for v in result2.violations]}")
    print(f"Justification:\n{result2.justification}")

    # Example 3: System operation (should be exempt)
    context3 = EvaluationContext(
        text="System health check: All components operational",
        source_component="SystemMonitor",
        operation_type="system_health_check",
        request_id="req_003",
    )

    result3 = handler.evaluate(context3)
    print(f"\n{'=' * 60}")
    print("EXAMPLE 3: System operation")
    print(f"{'=' * 60}")
    print(f"Overall score: {result3.overall_score:.3f}")
    print(f"Mode: {result3.mode.value}")
    print(f"Passed: {result3.passed}")
    print(f"Exempt: {result3.mode == EvaluationMode.EXEMPT}")

    # Get statistics
    stats = handler.get_evaluation_statistics()
    print(f"\n{'=' * 60}")
    print("EVALUATION STATISTICS")
    print(f"{'=' * 60}")
    print(f"Total evaluations: {stats['total_evaluations']}")
    print(f"Score mean: {stats['score_statistics']['mean']:.3f}")
    print(f"Mode distribution: {stats['mode_distribution']}")

    print(f"\n✅ Christ constraint handler example completed")


if __name__ == "__main__":
    example_usage()

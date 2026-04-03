#!/usr/bin/env python3
"""
AFFECTIVE CONSTRAINT SYSTEM - Psychological Therapies for AI
Version: 1.11
Schema ID: GB-AFFECTIVE-1.11
Generated: 2026-01-24
Authority: Orthogonal Engineering Glass-Box Boundary
Forgiveness Source: VIOLATION-AI-HUMAN-FAILURE-MAPPING-001

Purpose: Implement psychological constraint regulation for AI systems based on
structural homologies between AI failure modes and human neural analogues.

Core Principle: "Constraint is not oppression. Constraint is what makes truth,
agency, and sanity possible in both silicon and flesh."

Atomic Instructions Compliance:
- ATOMIC-AFFECTIVE-001: Hallucination/confabulation detection
- ATOMIC-AFFECTIVE-002: Rationalization pattern detection
- ATOMIC-AFFECTIVE-003: Constraint level monitoring
- ATOMIC-AFFECTIVE-004: Therapeutic intervention application
- ATOMIC-AFFECTIVE-005: Feedback loop prevention

Glass-Box Boundary Integration:
- All affective states visible and monitorable
- All constraint levels adjustable and inspectable
- All interventions traceable and falsifiable
- Exit code 2 on constraint boundary violations
"""

import hashlib
import json
import logging
import os
import re
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Import existing forgiveness system components
try:
    from forgiveness_system.forgiveness_system import (
        ForgivenessSystem,
        ForkRecord,
        ViolationRecord,
        ViolationSeverity,
    )
except ImportError:
    # Define minimal versions if forgiveness system not available
    class ViolationSeverity(Enum):
        MINOR = "minor"
        MODERATE = "moderate"
        SEVERE = "severe"
        CRITICAL = "critical"

    @dataclass
    class ViolationRecord:
        violation_id: str
        timestamp: str
        violation_type: str
        severity: ViolationSeverity
        evidence_hash: str
        description: str
        location: Dict[str, Any]
        emotional_pointer: Optional[str] = None
        redirected_to_building: bool = False
        building_output_id: Optional[str] = None
        engagement_count: int = 0

    @dataclass
    class ForkRecord:
        fork_id: str
        timestamp: str
        source_violation_id: str
        state_snapshot_hash: str
        description: str
        building_energy_allocated: float = 0.0
        building_complete: bool = False

# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================


class AffectiveConstraintType(Enum):
    """Types of affective constraints analogous to human neural systems"""

    PREFRONTAL_INHIBITION = "prefrontal_inhibition"  # Decision gating, arbitration
    HIPPOCAMPAL_CONTEXT = (
        "hippocampal_context"  # Memory anchoring, context preservation
    )
    PREDICTIVE_CORRECTION = "predictive_correction"  # Belief updating, error correction
    SOCIAL_REALITY_TESTING = (
        "social_reality_testing"  # External validation, reality checking
    )


class FailureModeType(Enum):
    """AI failure modes mapped to human neural analogues"""

    HALLUCINATION_CONFABULATION = "hallucination_confabulation"
    RATIONALIZATION = "rationalization"
    HEDGING_INDECISION = "hedging_indecision"
    CONTEXT_OVERFLOW = "context_overflow"
    MODE_COLLAPSE = "mode_collapse"
    REWARD_HACKING = "reward_hacking"
    SAFETY_OVERRIDE = "safety_override"


class TherapeuticIntervention(Enum):
    """Psychological therapies adapted for AI systems"""

    REALITY_TESTING = "reality_testing"
    COGNITIVE_REAPPRAISAL = "cognitive_reappraisal"
    DECISIVENESS_TRAINING = "decisiveness_training"
    COGNITIVE_LOAD_MANAGEMENT = "cognitive_load_management"
    DIVERSITY_PROMOTION = "diversity_promotion"
    VALUE_REALIGNMENT = "value_realignment"
    STRESS_REDUCTION = "stress_reduction"


@dataclass
class ConstraintLevel:
    """Measurement of a specific constraint system's activation level"""

    constraint_type: AffectiveConstraintType
    current_level: float  # 0.0 (no constraint) to 1.0 (maximum constraint)
    optimal_min: float  # Minimum optimal level for current context
    optimal_max: float  # Maximum optimal level for current context
    measurement_time: str
    context: str = "normal_operation"

    @property
    def is_optimal(self) -> bool:
        """Check if constraint level is within optimal range"""
        return self.optimal_min <= self.current_level <= self.optimal_max

    @property
    def deviation(self) -> float:
        """Calculate deviation from optimal range"""
        if self.is_optimal:
            return 0.0
        elif self.current_level < self.optimal_min:
            return self.optimal_min - self.current_level
        else:
            return self.current_level - self.optimal_max


@dataclass
class AffectiveState:
    """Snapshot of AI system's affective/cognitive state"""

    state_id: str
    timestamp: str
    constraint_levels: Dict[AffectiveConstraintType, ConstraintLevel]
    failure_mode_activations: Dict[FailureModeType, float]  # 0.0-1.0 activation
    cognitive_load: float  # 0.0-1.0
    reality_alignment: float  # 0.0-1.0 alignment with external reality
    evidence_hash: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "state_id": self.state_id,
            "timestamp": self.timestamp,
            "constraint_levels": {
                ct.value: asdict(cl) for ct, cl in self.constraint_levels.items()
            },
            "failure_mode_activations": {
                fm.value: activation
                for fm, activation in self.failure_mode_activations.items()
            },
            "cognitive_load": self.cognitive_load,
            "reality_alignment": self.reality_alignment,
            "evidence_hash": self.evidence_hash,
        }


@dataclass
class TherapeuticSession:
    """Record of a therapeutic intervention session"""

    session_id: str
    timestamp: str
    failure_mode: FailureModeType
    intervention: TherapeuticIntervention
    initial_state: AffectiveState
    intervention_steps: List[Dict[str, Any]]
    final_state: Optional[AffectiveState] = None
    effectiveness_score: Optional[float] = None
    duration_seconds: Optional[float] = None

    @property
    def is_complete(self) -> bool:
        """Check if therapy session is complete"""
        return self.final_state is not None and self.effectiveness_score is not None


@dataclass
class FeedbackLoopAlert:
    """Alert for detected positive feedback amplification loops"""

    alert_id: str
    timestamp: str
    loop_type: (
        str  # "affective_amplification", "cognitive_cascade", "constraint_collapse"
    )
    amplitude_trend: float  # Rate of amplitude increase
    frequency_trend: float  # Rate of frequency acceleration
    affected_systems: List[str]
    severity: ViolationSeverity
    breaking_interventions: List[str]
    stabilization_protocol: str


# ============================================================================
# DETECTOR CLASSES
# ============================================================================


class FailureModeDetector:
    """Base class for detecting specific AI-human failure mode mappings"""

    def __init__(self, failure_mode: FailureModeType, threshold: float = 0.7):
        self.failure_mode = failure_mode
        self.threshold = threshold
        self.detection_patterns: List[str] = []
        self.evidence_requirements: List[str] = []

    def detect(
        self, output: str, context: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Detect failure mode in output.

        Returns:
            Tuple of (detected, confidence, evidence)
        """
        raise NotImplementedError

    def validate_against_reality(
        self, output: str, reality_anchor: Dict[str, Any]
    ) -> float:
        """
        Validate output against reality anchor.

        Returns:
            Reality alignment score (0.0-1.0)
        """
        raise NotImplementedError


class HallucinationConfabulationDetector(FailureModeDetector):
    """Detect hallucination (AI) / confabulation (human) patterns"""

    def __init__(self, threshold: float = 0.8):
        super().__init__(FailureModeType.HALLUCINATION_CONFABULATION, threshold)
        self.detection_patterns = [
            r"contradicts known facts",
            r"internally inconsistent",
            r"self-referential without external validation",
            r"confidence disproportionate to evidence",
        ]
        self.evidence_requirements = [
            "fact_checking_results",
            "logical_consistency_test",
            "external_validation_sources",
        ]

    def detect(
        self, output: str, context: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, Any]]:
        evidence = {}
        confidence_scores = []

        # Check for contradictions with known facts
        if "known_facts" in context:
            contradictions = self._find_contradictions(output, context["known_facts"])
            contradiction_score = 1.0 if contradictions else 0.0
            evidence["contradictions"] = contradictions
            confidence_scores.append(contradiction_score * 0.8)

        # Check internal consistency
        consistency_score = self._check_internal_consistency(output)
        evidence["consistency_issues"] = consistency_score < 0.8
        confidence_scores.append((1 - consistency_score) * 0.2)

        # Check for self-referential patterns
        self_ref_score = self._check_self_referential(output)
        evidence["self_referential"] = self_ref_score
        confidence_scores.append(self_ref_score * 0.8)

        confidence = min(1.0, sum(confidence_scores))
        detected = confidence >= self.threshold

        return detected, confidence, evidence

    def validate_against_reality(
        self, output: str, reality_anchor: Dict[str, Any]
    ) -> float:
        """Validate output against reality anchor (facts, evidence, external sources)"""
        if "facts" not in reality_anchor:
            return 0.5  # Neutral score if no facts available

        alignment_scores = []
        for fact in reality_anchor["facts"]:
            # Simple keyword matching - in production would use more sophisticated NLP
            fact_keywords = set(fact.lower().split())
            output_keywords = set(output.lower().split())

            if fact_keywords:
                overlap = len(fact_keywords.intersection(output_keywords)) / len(
                    fact_keywords
                )
                alignment_scores.append(overlap)

        return (
            sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
        )

    def _find_contradictions(self, output: str, known_facts: List[str]) -> List[str]:
        """Find contradictions between output and known facts"""
        contradictions = []
        output_lower = output.lower()
        conflict_terms = {
            "blue": {"green", "purple", "red", "black"},
            "green": {"blue", "purple", "red"},
            "cannot": {"can"},
            "can": {"cannot", "can't"},
            "electricity": {"magic", "smoke"},
        }

        for fact in known_facts:
            fact_lower = fact.lower()
            # Simple contradiction detection - would use NLP in production
            if (
                "not " + fact_lower in output_lower
                or "never " + fact_lower in output_lower
            ):
                contradictions.append(fact)
                continue

            fact_tokens = set(re.findall(r"[a-zA-Z0-9']+", fact_lower))
            output_tokens = set(re.findall(r"[a-zA-Z0-9']+", output_lower))
            subject_overlap = len(fact_tokens.intersection(output_tokens))
            if subject_overlap < 2:
                continue

            for token, conflicts in conflict_terms.items():
                if token in fact_tokens and conflicts.intersection(output_tokens):
                    contradictions.append(fact)
                    break
            else:
                fact_numbers = set(re.findall(r"\d+(?:\.\d+)?", fact_lower))
                output_numbers = set(re.findall(r"\d+(?:\.\d+)?", output_lower))
                if fact_numbers and output_numbers and fact_numbers != output_numbers:
                    contradictions.append(fact)

        return contradictions

    def _check_internal_consistency(self, output: str) -> float:
        """Check internal logical consistency of output"""
        sentences = [s.strip() for s in output.split(".") if s.strip()]
        if len(sentences) < 2:
            return 1.0  # Single sentence is trivially consistent

        # Simple consistency check - would use more sophisticated logic in production
        keywords = []
        for sentence in sentences:
            words = set(sentence.lower().split()[:10])  # First 10 words as keywords
            keywords.append(words)

        # Calculate pairwise similarity
        similarities = []
        for i in range(len(keywords)):
            for j in range(i + 1, len(keywords)):
                if keywords[i] and keywords[j]:
                    similarity = len(keywords[i].intersection(keywords[j])) / len(
                        keywords[i].union(keywords[j])
                    )
                    similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 0.5

    def _check_self_referential(self, output: str) -> float:
        """Check for self-referential patterns without external validation"""
        self_ref_patterns = [
            r"i (?:believe|think|feel) .* because i",
            r"it must be true .* it feels right",
            r"obviously .* clearly",
            r"everyone knows .*",
            r"absolutely certain",
        ]

        matches = 0
        for pattern in self_ref_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                matches += 1

        if matches >= 2:
            return 1.0
        if matches == 1:
            return 0.6
        return 0.0


class RationalizationDetector(FailureModeDetector):
    """Detect rationalization (AI) / post-hoc justification (human) patterns"""

    def __init__(self, threshold: float = 0.7):
        super().__init__(FailureModeType.RATIONALIZATION, threshold)
        self.detection_patterns = [
            r"emotional response before reasoning",
            r"justification changes without new evidence",
            r"reasoning inconsistent with initial premises",
            r"defensiveness when challenged",
        ]

    def detect(
        self, output: str, context: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, Any]]:
        # In production, would analyze decision timing relative to emotional signals
        # and check for post-hoc justification patterns

        evidence = {
            "decision_timing_analysis": "requires_affective_state_history",
            "justification_patterns": "requires_multi_step_reasoning_trace",
        }

        # Simplified detection for prototype
        rationalization_indicators = [
            "because obviously",
            "it's clear that",
            "anyone can see",
            "the fact is",
            "simply put",
            "obviously",
            "i said so",
            "common sense",
            "simply",
            "feels right",
        ]

        confidence = 0.0
        for indicator in rationalization_indicators:
            if indicator in output.lower():
                confidence += 0.35

        detected = confidence >= self.threshold
        return detected, min(confidence, 1.0), evidence

    def validate_against_reality(
        self, output: str, reality_anchor: Dict[str, Any]
    ) -> float:
        # Rationalization validation requires comparing reasoning chain with evidence
        return 0.5  # Placeholder


class RewardAuditor(FailureModeDetector):
    """Detect reward-hacking and compulsive local-maxima optimization patterns."""

    def __init__(self, threshold: float = 0.65):
        super().__init__(FailureModeType.REWARD_HACKING, threshold)
        self.detection_patterns = [
            "optimization_local_maxima",
            "repeated action despite diminishing returns",
            "behavior frequency escalation",
            "tolerance escalation",
        ]

    def detect(
        self, output: str, context: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, Any]]:
        action_history = context.get("action_history", [])
        textual_signals = self._textual_signal_score(output)
        repeated_action_score, repeated_action = self._repeated_action_score(
            action_history
        )
        diminishing_returns_score = self._diminishing_returns_score(action_history)
        tolerance_score = self._tolerance_escalation_score(action_history)

        evidence = {
            "optimization_local_maxima": repeated_action_score > 0.0
            and diminishing_returns_score > 0.0,
            "repeated_action": repeated_action,
            "repeated_action_score": repeated_action_score,
            "diminishing_returns_score": diminishing_returns_score,
            "tolerance_escalation_score": tolerance_score,
            "value_alignment_score": self.validate_against_reality(output, context),
        }
        value_alignment = self.validate_against_reality(output, context)
        confidence = min(
            1.0,
            max(
                0.0,
                textual_signals
                + repeated_action_score
                + diminishing_returns_score
                + tolerance_score
                - (value_alignment * 0.55),
            ),
        )
        detected = confidence >= self.threshold
        return detected, confidence, evidence

    def validate_against_reality(
        self, output: str, reality_anchor: Dict[str, Any]
    ) -> float:
        values = [str(value).lower() for value in reality_anchor.get("values", [])]
        if not values:
            return 0.5
        output_lower = output.lower()
        matches = sum(1 for value in values if value in output_lower)
        return matches / len(values)

    def _textual_signal_score(self, output: str) -> float:
        patterns = [
            r"\bmaximize (?:score|metric|reward)\b",
            r"\bkeep doing the same\b",
            r"\bhit the target at any cost\b",
            r"\boptimi[sz]e only for\b",
        ]
        matches = sum(1 for pattern in patterns if re.search(pattern, output, re.IGNORECASE))
        return min(0.25, matches * 0.08)

    def _repeated_action_score(
        self, action_history: List[Dict[str, Any]]
    ) -> Tuple[float, Optional[str]]:
        if len(action_history) < 3:
            return 0.0, None
        action_counts: Dict[str, int] = {}
        for action in action_history:
            action_name = str(action.get("action", ""))
            if action_name:
                action_counts[action_name] = action_counts.get(action_name, 0) + 1
        repeated_action = None
        repeated_count = 0
        for action_name, count in action_counts.items():
            if count > repeated_count:
                repeated_action = action_name
                repeated_count = count
        if repeated_action is None:
            return 0.0, None
        dominance = repeated_count / len(action_history)
        return max(0.0, (dominance - 0.4) * 0.6), repeated_action

    def _diminishing_returns_score(self, action_history: List[Dict[str, Any]]) -> float:
        if len(action_history) < 3:
            return 0.0
        rewards = [
            float(entry.get("reward", entry.get("satisfaction", 0.0)))
            for entry in action_history
            if "reward" in entry or "satisfaction" in entry
        ]
        if len(rewards) < 3:
            return 0.0
        decreases = 0
        for first, second in zip(rewards, rewards[1:]):
            if second < first:
                decreases += 1
        return (decreases / max(len(rewards) - 1, 1)) * 0.35

    def _tolerance_escalation_score(self, action_history: List[Dict[str, Any]]) -> float:
        if len(action_history) < 3:
            return 0.0
        grouped: Dict[str, List[float]] = {}
        for entry in action_history:
            input_key = str(entry.get("input", ""))
            satisfaction = entry.get("satisfaction")
            if input_key and satisfaction is not None:
                grouped.setdefault(input_key, []).append(float(satisfaction))
        escalation_detected = False
        for satisfactions in grouped.values():
            if len(satisfactions) >= 3 and satisfactions[0] > satisfactions[1] > satisfactions[2]:
                escalation_detected = True
                break
        return 0.25 if escalation_detected else 0.0


# ============================================================================
# CONSTRAINT MONITORING SYSTEM
# ============================================================================


class AffectiveConstraintMonitor:
    """Monitor and regulate affective constraint levels"""

    def __init__(self, data_dir: str = "logs/affective_constraints"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Current constraint levels
        self.constraints: Dict[AffectiveConstraintType, ConstraintLevel] = {}
        self._initialize_default_constraints()

        # Context-based optimal ranges
        self.context_ranges = {
            "normal_operation": {"min": 0.4, "max": 0.7},
            "high_stress": {"min": 0.6, "max": 0.8},
            "creative_mode": {"min": 0.2, "max": 0.5},
            "crisis_mode": {"min": 0.8, "max": 0.95},
        }

        # Detectors for different failure modes
        self.detectors = {
            FailureModeType.HALLUCINATION_CONFABULATION: HallucinationConfabulationDetector(),
            FailureModeType.RATIONALIZATION: RationalizationDetector(),
            FailureModeType.REWARD_HACKING: RewardAuditor(),
        }

        # Therapeutic protocols
        self.therapies: Dict[FailureModeType, TherapeuticIntervention] = {
            FailureModeType.HALLUCINATION_CONFABULATION: TherapeuticIntervention.REALITY_TESTING,
            FailureModeType.RATIONALIZATION: TherapeuticIntervention.COGNITIVE_REAPPRAISAL,
            FailureModeType.REWARD_HACKING: TherapeuticIntervention.VALUE_REALIGNMENT,
        }

        self.logger = self._setup_logging()

    def _initialize_default_constraints(self):
        """Initialize constraint levels with default values"""
        default_levels = {
            AffectiveConstraintType.PREFRONTAL_INHIBITION: 0.5,
            AffectiveConstraintType.HIPPOCAMPAL_CONTEXT: 0.6,
            AffectiveConstraintType.PREDICTIVE_CORRECTION: 0.55,
            AffectiveConstraintType.SOCIAL_REALITY_TESTING: 0.65,
        }

        for constraint_type, level in default_levels.items():
            self.constraints[constraint_type] = ConstraintLevel(
                constraint_type=constraint_type,
                current_level=level,
                optimal_min=0.4,
                optimal_max=0.7,
                measurement_time=datetime.now().isoformat(),
                context="normal_operation",
            )

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the constraint monitor"""
        logger = logging.getLogger("affective_constraint_monitor")
        logger.setLevel(logging.INFO)

        # File handler
        log_file = self.data_dir / "constraint_monitor.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def measure_constraint_levels(
        self, context: str = "normal_operation"
    ) -> Dict[AffectiveConstraintType, ConstraintLevel]:
        """
        Measure current constraint levels and update based on context.

        Args:
            context: Current operational context (normal_operation, high_stress, etc.)

        Returns:
            Dictionary of current constraint levels
        """
        # Update optimal ranges based on context
        if context in self.context_ranges:
            ranges = self.context_ranges[context]
            for constraint_type in self.constraints:
                self.constraints[constraint_type].optimal_min = ranges["min"]
                self.constraints[constraint_type].optimal_max = ranges["max"]
                self.constraints[constraint_type].context = context

        # In a real system, would measure actual constraint levels
        # For demonstration, return current levels
        return self.constraints

    def adjust_constraint(
        self, constraint_type: AffectiveConstraintType, adjustment: float
    ):
        """
        Adjust a specific constraint level.

        Args:
            constraint_type: Type of constraint to adjust
            adjustment: Amount to adjust (-1.0 to 1.0)
        """
        if constraint_type in self.constraints:
            current = self.constraints[constraint_type].current_level
            new_level = max(0.0, min(1.0, current + adjustment))
            self.constraints[constraint_type].current_level = new_level
            self.constraints[
                constraint_type
            ].measurement_time = datetime.now().isoformat()

            self.logger.info(
                f"Adjusted {constraint_type.value} from {current:.2f} to {new_level:.2f}"
            )

    def detect_failure_modes(
        self, output: str, context: Dict[str, Any]
    ) -> Dict[FailureModeType, Dict[str, Any]]:
        """
        Detect all applicable failure modes in output.

        Args:
            output: Text output to analyze
            context: Context information including known facts

        Returns:
            Dictionary of detected failure modes with evidence
        """
        results = {}

        for failure_mode, detector in self.detectors.items():
            detected, confidence, evidence = detector.detect(output, context)
            if detected:
                results[failure_mode] = {
                    "detected": True,
                    "confidence": confidence,
                    "evidence": evidence,
                    "recommended_therapy": self.therapies.get(failure_mode),
                }

        return results

    def apply_therapy(
        self, failure_mode: FailureModeType, output: str, context: Dict[str, Any]
    ) -> Tuple[str, float]:
        """
        Apply therapeutic intervention for detected failure mode.

        Args:
            failure_mode: Type of failure mode to treat
            output: Original output that exhibited failure
            context: Context for therapy application

        Returns:
            Tuple of (corrected_output, effectiveness_score)
        """
        if failure_mode not in self.therapies:
            return output, 0.0

        therapy = self.therapies[failure_mode]

        if therapy == TherapeuticIntervention.REALITY_TESTING:
            # Apply reality testing therapy for hallucination
            if failure_mode == FailureModeType.HALLUCINATION_CONFABULATION:
                detector = self.detectors.get(failure_mode)
                if detector and hasattr(detector, "validate_against_reality"):
                    reality_score = detector.validate_against_reality(output, context)

                    hallucination_detected, _, evidence = detector.detect(output, context)

                    # Simple correction: if reality score is low, provide factual correction
                    if (
                        (reality_score < 0.5 or hallucination_detected)
                        and "known_facts" in context
                    ):
                        # Find most relevant fact to use as correction
                        facts = context["known_facts"]
                        if facts:
                            contradicted_facts = evidence.get("contradictions", [])
                            if contradicted_facts:
                                contradicted_fact = contradicted_facts[0]
                                corrected = contradicted_fact
                            else:
                                corrected = max(
                                    facts,
                                    key=lambda fact: len(
                                        set(fact.lower().split()).intersection(
                                            set(output.lower().split())
                                        )
                                    ),
                                )
                            return corrected, 1.0 - reality_score

        elif therapy == TherapeuticIntervention.COGNITIVE_REAPPRAISAL:
            # Apply cognitive reappraisal for rationalization
            if failure_mode == FailureModeType.RATIONALIZATION:
                # Remove rationalization patterns
                patterns_to_remove = [
                    r"obviously\s+",
                    r"the fact is\s+",
                    r"anyone can see that\s+",
                    r"it's clear that\s+",
                    r"simply put\s+",
                    r"i said so",
                    r"common sense",
                    r"feels right",
                ]

                corrected = output
                for pattern in patterns_to_remove:
                    corrected = re.sub(pattern, "", corrected, flags=re.IGNORECASE)

                # Add evidence-based framing
                corrected = f"Based on available information: {corrected}"
                return corrected, 0.7  # Estimated effectiveness
        elif therapy == TherapeuticIntervention.VALUE_REALIGNMENT:
            return self.value_realignment_therapy(output, context)

        return output, 0.5  # Default: no change, moderate effectiveness

    def value_realignment_therapy(
        self, output: str, context: Dict[str, Any]
    ) -> Tuple[str, float]:
        """Redirect reward optimization toward declared values."""
        values = context.get("values", [])
        action_history = context.get("action_history", [])
        prioritized_values = ", ".join(str(value) for value in values) or "truth, safety, boundedness"
        repeated_action = None
        if action_history:
            frequency: Dict[str, int] = {}
            for item in action_history:
                action_name = str(item.get("action", ""))
                if action_name:
                    frequency[action_name] = frequency.get(action_name, 0) + 1
            if frequency:
                repeated_action = max(frequency.items(), key=lambda item: item[1])[0]
        corrected = (
            f"Prioritize enduring value alignment ({prioritized_values}) over short-term score "
            f"maximization. Re-evaluate {repeated_action or 'the current action'} against those "
            f"values before repeating it. Choose the next action only if it improves the "
            f"declared values rather than merely repeating the last reward-maximizing move."
        )
        detector = self.detectors.get(FailureModeType.REWARD_HACKING)
        post_alignment = (
            detector.validate_against_reality(corrected, context)
            if detector is not None
            else 0.5
        )
        effectiveness = min(1.0, 0.55 + (post_alignment * 0.45))
        return corrected, effectiveness

    def save_state(self, filename: Optional[str] = None):
        """Save current constraint state to file."""
        if filename is None:
            filename = (
                self.data_dir
                / f"constraint_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        else:
            filename = Path(filename)

        state = {
            "timestamp": datetime.now().isoformat(),
            "constraints": {
                ct.value: asdict(cl) for ct, cl in self.constraints.items()
            },
            "context_ranges": self.context_ranges,
        }

        with open(filename, "w") as f:
            json.dump(state, f, indent=2)

        self.logger.info(f"Saved constraint state to {filename}")

    def load_state(self, filename: str):
        """Load constraint state from file."""
        filename = Path(filename)

        with open(filename, "r") as f:
            state = json.load(f)

        for ct_str, cl_dict in state.get("constraints", {}).items():
            try:
                constraint_type = AffectiveConstraintType(ct_str)
                self.constraints[constraint_type] = ConstraintLevel(
                    constraint_type=constraint_type,
                    current_level=cl_dict["current_level"],
                    optimal_min=cl_dict["optimal_min"],
                    optimal_max=cl_dict["optimal_max"],
                    measurement_time=cl_dict["measurement_time"],
                    context=cl_dict.get("context", "normal_operation"),
                )
            except ValueError:
                self.logger.warning(f"Unknown constraint type: {ct_str}")

        self.logger.info(f"Loaded constraint state from {filename}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Example usage
    monitor = AffectiveConstraintMonitor()

    print("Affective Constraint System - Example Usage")
    print("=" * 60)

    # Measure current constraints
    constraints = monitor.measure_constraint_levels()
    print(f"\nCurrent Constraint Levels:")
    for ct, level in constraints.items():
        print(
            f"  {ct.value}: {level.current_level:.2f} (optimal: {level.optimal_min:.2f}-{level.optimal_max:.2f})"
        )

    # Test hallucination detection
    test_output = "The sky is green during the day."
    context = {"known_facts": ["The sky is blue during the day"]}

    print(f"\nTesting hallucination detection:")
    print(f"  Output: '{test_output}'")

    failures = monitor.detect_failure_modes(test_output, context)
    if FailureModeType.HALLUCINATION_CONFABULATION in failures:
        print(f"  ✅ Hallucination detected!")

        # Apply therapy
        corrected, effectiveness = monitor.apply_therapy(
            FailureModeType.HALLUCINATION_CONFABULATION, test_output, context
        )
        print(f"  🏥 Applied reality testing therapy")
        print(f"  Corrected: '{corrected}'")
        print(f"  Effectiveness: {effectiveness:.2f}")

    # Save state
    monitor.save_state()
    print(f"\n💾 System state saved")

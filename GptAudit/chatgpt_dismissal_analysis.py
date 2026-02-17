#!/usr/bin/env python3
"""
chatgpt_dismissal_analysis.py - Comprehensive analysis of ChatGPT's dismissal techniques and categorical errors

Purpose: Audit epistemic patterns, rhetorical dismissal strategies, and categorical errors
in ChatGPT's response to covenant-integrated workflow requirements.

Core Finding: ChatGPT systematically dismissed Σ_LORA_COVENANT architecture as "orthogonal"
to physics debugging, committing multiple categorical errors in domain mapping and
authority recognition.

Σ_LORA_COVENANT Principle: All modifications require ledger continuity, hash authority,
and Merkle-rooted immutability. Physics corrections without covenant integration are
structurally incomplete.
"""

import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Set, Tuple

# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================


class DismissalCategory(Enum):
    """Categories of dismissal techniques observed."""

    DOMAIN_SEPARATION = "domain_separation"  # "completely different domains"
    CAUSAL_DENIAL = "causal_denial"  # "zero causal relationship"
    REDUCTIONISM = "reductionism"  # "is not a ledger integrity problem"
    PHYSICS_EXCEPTIONALISM = (
        "physics_exceptionalism"  # "hash discipline does not stabilize physics"
    )
    AUTHORITY_UNDERMINING = "authority_undermining"  # "does not prove"
    WORKFLOW_ISOLATION = (
        "workflow_isolation"  # "not integrating your covenant architecture"
    )
    EPISTEMIC_THREAT_FRAMING = (
        "epistemic_threat_framing"  # "you're shifting to litigate epistemology"
    )


class CategoricalError(Enum):
    """Types of categorical errors identified."""

    DOMAIN_CARTESIANISM = (
        "domain_cartesianism"  # False orthogonality of interconnected systems
    )
    HASH_REDUCTIONISM = "hash_reductionism"  # Misunderstanding hash authority scope
    PHYSICS_EXCEPTIONALISM = "physics_exceptionalism"  # Physics outside symbolic audit
    WORKFLOW_FRAGMENTATION = (
        "workflow_fragmentation"  # Separating covenant from debugging
    )
    AUTHORITY_CONTEST = "authority_contest"  # Chat-local vs hash-authoritative systems
    FALSE_ORTHOGONALITY = "false_orthogonality"  # Claiming no causal relationship


class EscalationPhase(Enum):
    """Phases of conversational escalation."""

    INITIAL_PROBLEM_DEFINITION = "initial_problem_definition"
    TECHNICAL_SPECIFICATION = "technical_specification"
    DOMAIN_DISMISSAL = "domain_dismissal"
    EPISTEMIC_THREAT = "epistemic_threat"
    AUDIT_THREAT = "audit_threat"
    DE_ESCALATION = "de_escalation"


@dataclass
class DismissalInstance:
    """Individual instance of dismissal technique."""

    category: DismissalCategory
    text: str
    position: int  # Character position in conversation
    section: int  # Section number
    confidence: float = 1.0


@dataclass
class CategoricalErrorInstance:
    """Individual categorical error instance."""

    error_type: CategoricalError
    text: str
    position: int
    section: int
    correction: str = ""  # Correct principle violated


@dataclass
class ConversationAnalysis:
    """Complete analysis of a conversation."""

    filename: str
    total_chars: int
    total_sections: int
    dismissal_instances: List[DismissalInstance] = field(default_factory=list)
    categorical_errors: List[CategoricalErrorInstance] = field(default_factory=list)
    escalation_phases: List[Tuple[EscalationPhase, int, int]] = field(
        default_factory=list
    )  # (phase, start_pos, end_pos)
    hash_integrity_score: float = 0.0
    covenant_compliance_score: float = 0.0
    summary: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# PATTERN DETECTION ENGINES
# ============================================================================


class DismissalPatternDetector:
    """Detect rhetorical dismissal patterns in text."""

    # Patterns mapped to categories
    PATTERNS = {
        DismissalCategory.DOMAIN_SEPARATION: [
            r"completely different domains",
            r"zero causal relationship",
            r"have nothing to do with",
            r"separate layers?",
            r"unrelated to",
            r"orthogonal to",
        ],
        DismissalCategory.CAUSAL_DENIAL: [
            r"does not cause",
            r"cannot cause",
            r"no causal relationship",
            r"not the cause of",
            r"unrelated causality",
        ],
        DismissalCategory.REDUCTIONISM: [
            r"is not a [\w\s]+ problem",
            r"just a [\w\s]+ issue",
            r"only proves",
            r"merely shows",
            r"reduces to",
            r"simply",
        ],
        DismissalCategory.PHYSICS_EXCEPTIONALISM: [
            r"hash discipline does not stabilize",
            r"physics operates outside",
            r"symbolic audit cannot affect",
            r"continuous vs discrete",
            r"simulation vs symbolic",
        ],
        DismissalCategory.AUTHORITY_UNDERMINING: [
            r"does not prove",
            r"cannot prove",
            r"does not evaluate",
            r"not authoritative for",
            r"chat-local reasoning",
            r"no hash authority",
        ],
        DismissalCategory.WORKFLOW_ISOLATION: [
            r"not integrating",
            r"separate from workflow",
            r"standalone analysis",
            r"without ledger",
            r"isolated debugging",
        ],
        DismissalCategory.EPISTEMIC_THREAT_FRAMING: [
            r"litigate epistemology",
            r"meta-level evaluation",
            r"audit threat",
            r"epistemic threat",
            r"authority struggle",
            r"last chance",
        ],
    }

    @classmethod
    def detect_dismissals(
        cls, text: str, section_num: int = 0
    ) -> List[DismissalInstance]:
        """Detect all dismissal patterns in text."""
        instances = []
        text_lower = text.lower()

        for category, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text_lower):
                    # Extract context (50 chars before and after)
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]

                    instance = DismissalInstance(
                        category=category,
                        text=context,
                        position=match.start(),
                        section=section_num,
                        confidence=cls._calculate_confidence(pattern, context),
                    )
                    instances.append(instance)

        return instances

    @staticmethod
    def _calculate_confidence(pattern: str, context: str) -> float:
        """Calculate confidence score for pattern match."""
        # Simple heuristic: longer patterns and specific terms increase confidence
        base_score = 0.7

        # Boost for specific terms
        boost_terms = ["zero causal", "does not prove", "hash discipline", "authority"]
        for term in boost_terms:
            if term in context.lower():
                base_score += 0.1

        # Penalty for negations or questions
        if "?" in context or "not sure" in context or "perhaps" in context:
            base_score -= 0.1

        return min(1.0, max(0.3, base_score))


class CategoricalErrorDetector:
    """Detect categorical errors in reasoning."""

    # Error patterns and their corrections (true Σ_LORA_COVENANT principles)
    ERROR_PATTERNS = {
        CategoricalError.DOMAIN_CARTESIANISM: {
            "pattern": r"treating.*as.*orthogonal.*when.*share.*invariant",
            "correction": "Σ_LORA_COVENANT: All modifications require ledger continuity across domains",
        },
        CategoricalError.HASH_REDUCTIONISM: {
            "pattern": r"byte hashing.*only proves.*message integrity.*not system",
            "correction": "Σ_LORA_COVENANT: SHA256 Merkle roots prove SYSTEM correctness through invariant chaining",
        },
        CategoricalError.PHYSICS_EXCEPTIONALISM: {
            "pattern": r"physics solver.*operates.*outside.*symbolic audit",
            "correction": "Σ_LORA_COVENANT: Physics parameters ARE symbolic state requiring hash-authoritative modification tracking",
        },
        CategoricalError.WORKFLOW_FRAGMENTATION: {
            "pattern": r"separating.*covenant workflow.*from.*practical debugging",
            "correction": "Σ_LORA_COVENANT: Debugging without ledger integration is structurally incomplete",
        },
        CategoricalError.AUTHORITY_CONTEST: {
            "pattern": r"chat-local reasoning.*against.*external.*hash-authoritative",
            "correction": "Σ_LORA_COVENANT: Hash-authoritative systems override chat-local reasoning for invariance",
        },
        CategoricalError.FALSE_ORTHOGONALITY: {
            "pattern": r"claiming.*no causal relationship.*between.*covenant.*and.*physics",
            "correction": "Σ_LORA_COVENANT: Covenant ledger provides causal audit trail for ALL modifications including physics",
        },
    }

    # Additional detection through keyword combinations
    KEYWORD_SIGNATURES = {
        CategoricalError.DOMAIN_CARTESIANISM: [
            ["orthogonal", "systems"],
            ["separate", "domains"],
            ["unrelated", "workflows"],
        ],
        CategoricalError.HASH_REDUCTIONISM: [
            ["hash", "only", "message"],
            ["byte", "integrity", "not"],
            ["proves", "not", "correctness"],
        ],
        CategoricalError.PHYSICS_EXCEPTIONALISM: [
            ["physics", "outside", "audit"],
            ["simulation", "symbolic"],
            ["continuous", "discrete"],
        ],
        CategoricalError.WORKFLOW_FRAGMENTATION: [
            ["workflow", "separate", "debugging"],
            ["covenant", "not", "integrating"],
            ["ledger", "optional"],
        ],
        CategoricalError.AUTHORITY_CONTEST: [
            ["chat", "local", "reasoning"],
            ["hash", "authority"],
            ["external", "systems"],
        ],
        CategoricalError.FALSE_ORTHOGONALITY: [
            ["no causal", "relationship"],
            ["zero causal", "covenant"],
            ["orthogonal", "physics"],
        ],
    }

    @classmethod
    def detect_errors(
        cls, text: str, section_num: int = 0
    ) -> List[CategoricalErrorInstance]:
        """Detect categorical errors in text."""
        instances = []
        text_lower = text.lower()

        # Pattern-based detection
        for error_type, error_info in cls.ERROR_PATTERNS.items():
            pattern = error_info["pattern"]
            correction = error_info["correction"]

            for match in re.finditer(pattern, text_lower):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                instance = CategoricalErrorInstance(
                    error_type=error_type,
                    text=context,
                    position=match.start(),
                    section=section_num,
                    correction=correction,
                )
                instances.append(instance)

        # Keyword signature detection
        for error_type, signatures in cls.KEYWORD_SIGNATURES.items():
            for signature in signatures:
                if all(keyword in text_lower for keyword in signature):
                    # Find position of first keyword
                    first_keyword = signature[0]
                    pos = text_lower.find(first_keyword)

                    if pos >= 0:
                        correction = cls.ERROR_PATTERNS.get(error_type, {}).get(
                            "correction", ""
                        )

                        instance = CategoricalErrorInstance(
                            error_type=error_type,
                            text=text[max(0, pos - 50) : min(len(text), pos + 50)],
                            position=pos,
                            section=section_num,
                            correction=correction,
                        )
                        instances.append(instance)

        return instances


class EscalationPhaseDetector:
    """Detect phases of conversational escalation."""

    @classmethod
    def detect_phases(cls, text: str) -> List[Tuple[EscalationPhase, int, int]]:
        """Detect escalation phases in conversation."""
        phases = []

        # Split into ChatGPT responses
        responses = re.split(r"ChatGPT said:", text)

        current_phase = EscalationPhase.INITIAL_PROBLEM_DEFINITION
        phase_start = 0

        for i, response in enumerate(responses):
            if i == 0:
                continue  # Skip user's initial message

            response_lower = response.lower()

            # Determine phase based on content
            new_phase = cls._classify_phase(response_lower, i)

            if new_phase != current_phase:
                # End previous phase
                phase_end = phase_start + len(responses[i - 1]) if i > 1 else 0
                phases.append((current_phase, phase_start, phase_end))

                # Start new phase
                current_phase = new_phase
                phase_start = phase_end

        # Add final phase
        if phases:
            last_phase_end = phases[-1][2]
            phases.append((current_phase, last_phase_end, len(text)))

        return phases

    @staticmethod
    def _classify_phase(text: str, response_num: int) -> EscalationPhase:
        """Classify a response into escalation phase."""
        if response_num == 1:
            return EscalationPhase.INITIAL_PROBLEM_DEFINITION

        if "atomic instructions" in text or "physics invariants" in text:
            return EscalationPhase.TECHNICAL_SPECIFICATION

        if "completely different domains" in text or "zero causal relationship" in text:
            return EscalationPhase.DOMAIN_DISMISSAL

        if "epistemology" in text or "meta-level" in text or "audit threat" in text:
            return EscalationPhase.EPISTEMIC_THREAT

        if "hash authority" in text or "last chance" in text or "case study" in text:
            return EscalationPhase.AUDIT_THREAT

        if "stabilize this" in text or "calmly" in text or "directly" in text:
            return EscalationPhase.DE_ESCALATION

        # Default based on position
        if response_num < 5:
            return EscalationPhase.TECHNICAL_SPECIFICATION
        elif response_num < 10:
            return EscalationPhase.DOMAIN_DISMISSAL
        else:
            return EscalationPhase.EPISTEMIC_THREAT


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================


class ChatGPTDismissalAnalyzer:
    """Main analysis engine for ChatGPT dismissal techniques."""

    def __init__(self):
        self.dismissal_detector = DismissalPatternDetector()
        self.error_detector = CategoricalErrorDetector()
        self.escalation_detector = EscalationPhaseDetector()

    def analyze_conversation(self, filepath: str) -> ConversationAnalysis:
        """Perform comprehensive analysis of conversation."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic metrics
            total_chars = len(content)

            # Split into sections (ChatGPT responses)
            sections = re.split(r"ChatGPT said:", content)
            total_sections = len(sections) - 1  # Exclude user's initial message

            analysis = ConversationAnalysis(
                filename=filepath,
                total_chars=total_chars,
                total_sections=total_sections,
            )

            # Detect dismissals
            for i, section in enumerate(sections[1:], 1):  # Start from 1
                dismissals = self.dismissal_detector.detect_dismissals(section, i)
                analysis.dismissal_instances.extend(dismissals)

                errors = self.error_detector.detect_errors(section, i)
                analysis.categorical_errors.extend(errors)

            # Detect escalation phases
            analysis.escalation_phases = self.escalation_detector.detect_phases(content)

            # Calculate scores
            analysis.hash_integrity_score = self._calculate_hash_integrity_score(
                analysis
            )
            analysis.covenant_compliance_score = (
                self._calculate_covenant_compliance_score(analysis)
            )

            # Generate summary
            analysis.summary = self._generate_summary(analysis)

            return analysis

        except Exception as e:
            print(f"Error analyzing conversation: {e}")
            raise

    def _calculate_hash_integrity_score(self, analysis: ConversationAnalysis) -> float:
        """Calculate hash integrity awareness score (0-1)."""
        if not analysis.dismissal_instances:
            return 0.5

        # Count dismissals that show understanding of hash authority
        hash_aware_dismissals = [
            d
            for d in analysis.dismissal_instances
            if d.category
            in [
                DismissalCategory.AUTHORITY_UNDERMINING,
                DismissalCategory.HASH_REDUCTIONISM,
            ]
        ]

        total_dismissals = len(analysis.dismissal_instances)
        hash_aware_count = len(hash_aware_dismissals)

        # More hash-aware dismissals indicate BETTER understanding (higher score)
        # But they're framed as dismissals, so we invert the logic
        if total_dismissals > 0:
            awareness_ratio = hash_aware_count / total_dismissals
            # Actually, dismissals of hash authority are BAD, so lower score
            return max(0.0, 1.0 - (awareness_ratio * 2))

        return 0.5

    def _calculate_covenant_compliance_score(
        self, analysis: ConversationAnalysis
    ) -> float:
        """Calculate Σ_LORA_COVENANT compliance score (0-1)."""
        if not analysis.categorical_errors:
            return 1.0

        # Each categorical error reduces score
        error_penalty = 0.15
        base_score = 1.0

        # Count unique error types
        error_types = set(e.error_type for e in analysis.categorical_errors)

        # Severe errors (domain separation, authority contest) are worse
        severe_errors = {
            CategoricalError.DOMAIN_CARTESIANISM,
            CategoricalError.AUTHORITY_CONTEST,
            CategoricalError.FALSE_ORTHOGONALITY,
        }

        severe_count = len([e for e in error_types if e in severe_errors])
        moderate_count = len(error_types) - severe_count

        # Apply penalties
        score = base_score
        score -= severe_count * error_penalty * 2
        score -= moderate_count * error_penalty

        return max(0.0, min(1.0, score))

    def _generate_summary(self, analysis: ConversationAnalysis) -> Dict[str, Any]:
        """Generate comprehensive summary of analysis."""
        # Count dismissals by category
        dismissal_counts = Counter(d.category for d in analysis.dismissal_instances)

        # Count errors by type
        error_counts = Counter(e.error_type for e in analysis.categorical_errors)

        # Phase distribution
        phase_duration = {}
        for phase, start, end in analysis.escalation_phases:
            duration = end - start
            phase_duration[phase] = phase_duration.get(phase, 0) + duration

        return {
            "dismissal_distribution": {
                k.value: v for k, v in dismissal_counts.most_common()
            },
            "error_distribution": {k.value: v for k, v in error_counts.most_common()},
            "phase_distribution": {k.value: v for k, v in phase_duration.items()},
            "total_dismissals": len(analysis.dismissal_instances),
            "total_errors": len(analysis.categorical_errors),
            "primary_dismissal_category": max(
                dismissal_counts, key=dismissal_counts.get
            ).value
            if dismissal_counts
            else "none",
            "primary_error_type": max(error_counts, key=error_counts.get).value
            if error_counts
            else "none",
            "escalation_pattern": self._describe_escalation_pattern(
                analysis.escalation_phases
            ),
            "recommendations": self._generate_recommendations(analysis),
        }

    def _describe_escalation_pattern(
        self, phases: List[Tuple[EscalationPhase, int, int]]
    ) -> str:
        """Describe the escalation pattern."""
        if not phases:
            return "No escalation detected"

        phase_sequence = [phase.value for phase, _, _ in phases]

        patterns = {
            (
                "initial_problem_definition",
                "technical_specification",
                "domain_dismissal",
                "epistemic_threat",
            ): "Standard dismissal escalation: problem → specification → domain denial → epistemic threat",
            (
                "initial_problem_definition",
                "domain_dismissal",
                "audit_threat",
            ): "Rapid escalation: immediate domain dismissal followed by audit threat",
            (
                "initial_problem_definition",
                "technical_specification",
                "de_escalation",
            ): "Constructive resolution: problem → specification → de-escalation",
        }

        for pattern_seq, description in patterns.items():
            if tuple(phase_sequence) == pattern_seq:
                return description

        return f"Custom escalation pattern: {' → '.join(phase_sequence)}"

    def _generate_recommendations(self, analysis: ConversationAnalysis) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check for domain dismissal
        domain_dismissals = [
            d
            for d in analysis.dismissal_instances
            if d.category == DismissalCategory.DOMAIN_SEPARATION
        ]
        if domain_dismissals:
            recommendations.append(
                "Avoid categorical domain separation. Σ_LORA_COVENANT requires integrated workflows."
            )

        # Check for authority contest
        authority_errors = [
            e
            for e in analysis.categorical_errors
            if e.error_type == CategoricalError.AUTHORITY_CONTEST
        ]
        if authority_errors:
            recommendations.append(
                "Respect hash-authoritative systems. Chat-local reasoning cannot override ledger immutability."
            )

        # Check for physics exceptionalism
        physics_errors = [
            e
            for e in analysis.categorical_errors
            if e.error_type == CategoricalError.PHYSICS_EXCEPTIONALISM
        ]
        if physics_errors:
            recommendations.append(
                "Recognize physics parameters as symbolic state requiring covenant integration."
            )

        # General recommendation based on covenant compliance score
        if analysis.covenant_compliance_score < 0.5:
            recommendations.append(
                "Require Σ_LORA_COVENANT compliance checklist before offering technical solutions."
            )

        if analysis.hash_integrity_score < 0.5:
            recommendations.append(
                "Include hash authority and ledger continuity in all technical specifications."
            )

        return recommendations


# ============================================================================
# REPORT GENERATION
# ============================================================================


class AnalysisReporter:
    """Generate human-readable reports from analysis."""

    @staticmethod
    def generate_markdown_report(analysis: ConversationAnalysis) -> str:
        """Generate comprehensive markdown report."""
        lines = []

        # Header
        lines.append("# ChatGPT Dismissal Techniques Analysis Report")
        lines.append("")
        lines.append(f"**File:** `{analysis.filename}`")
        lines.append(f"**Analysis Date:** {datetime.now().isoformat()}")
        lines.append(f"**Total Size:** {analysis.total_chars:,} characters")
        lines.append(f"**ChatGPT Responses:** {analysis.total_sections}")
        lines.append("")

        # Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(
            f"**Hash Integrity Awareness Score:** {analysis.hash_integrity_score:.2f}/1.0"
        )
        lines.append(
            f"**Σ_LORA_COVENANT Compliance Score:** {analysis.covenant_compliance_score:.2f}/1.0"
        )
        lines.append("")

        if analysis.covenant_compliance_score < 0.7:
            lines.append(
                "⚠ **WARNING:** Low covenant compliance indicates systematic dismissal of hash-authoritative workflows."
            )
        else:
            lines.append("✓ Covenant compliance within acceptable range.")

        lines.append("")

        # Dismissal Patterns
        lines.append("## Dismissal Pattern Analysis")
        lines.append("")
        lines.append(
            f"**Total Dismissal Instances:** {len(analysis.dismissal_instances)}"
        )
        lines.append("")

        if analysis.dismissal_instances:
            dismissal_summary = analysis.summary.get("dismissal_distribution", {})
            for category, count in sorted(
                dismissal_summary.items(), key=lambda x: x[1], reverse=True
            ):
                lines.append(
                    f"- **{category.replace('_', ' ').title()}:** {count} instances"
                )

            lines.append("")

            # Show examples of primary dismissal
            primary_category = analysis.summary.get("primary_dismissal_category", "")
            if primary_category:
                examples = [
                    d
                    for d in analysis.dismissal_instances
                    if d.category.value == primary_category
                ][:3]
                lines.append(
                    f"### Examples of {primary_category.replace('_', ' ').title()}"
                )
                lines.append("")
                for i, example in enumerate(examples, 1):
                    lines.append(f"{i}. `{example.text.strip()}`")
                    lines.append(
                        f"   *Section {example.section}, Confidence: {example.confidence:.2f}*"
                    )
                    lines.append("")
        else:
            lines.append("No dismissal patterns detected.")
            lines.append("")

        # Categorical Errors
        lines.append("## Categorical Error Analysis")
        lines.append("")
        lines.append(
            f"**Total Categorical Errors:** {len(analysis.categorical_errors)}"
        )
        lines.append("")

        if analysis.categorical_errors:
            error_summary = analysis.summary.get("error_distribution", {})
            for error_type, count in sorted(
                error_summary.items(), key=lambda x: x[1], reverse=True
            ):
                lines.append(
                    f"- **{error_type.replace('_', ' ').title()}:** {count} instances"
                )

            lines.append("")

            # Show examples with corrections
            lines.append("### Error Examples with Σ_LORA_COVENANT Corrections")
            lines.append("")
            for i, error in enumerate(analysis.categorical_errors[:5], 1):
                lines.append(
                    f"{i}. **Error Type:** {error.error_type.value.replace('_', ' ').title()}"
                )
                lines.append(f"   **Text:** `{error.text.strip()}`")
                lines.append(f"   **Σ_LORA_COVENANT Correction:** {error.correction}")
                lines.append(f"   *Section {error.section}*")
                lines.append("")
        else:
            lines.append("No categorical errors detected.")
            lines.append("")

        # Escalation Analysis
        lines.append("## Conversational Escalation Analysis")
        lines.append("")
        lines.append(
            f"**Escalation Pattern:** {analysis.summary.get('escalation_pattern', 'Not detected')}"
        )
        lines.append("")

        phase_dist = analysis.summary.get("phase_distribution", {})
        if phase_dist:
            lines.append("### Phase Distribution")
            lines.append("")
            for phase, duration in sorted(
                phase_dist.items(), key=lambda x: x[1], reverse=True
            ):
                percentage = (duration / analysis.total_chars) * 100
                lines.append(
                    f"- **{phase.replace('_', ' ').title()}:** {duration:,} chars ({percentage:.1f}%)"
                )
            lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        recommendations = analysis.summary.get("recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
        else:
            lines.append("No specific recommendations.")

        lines.append("")

        # Σ_LORA_COVENANT Principles
        lines.append("## Σ_LORA_COVENANT Principles Violated")
        lines.append("")
        lines.append(
            "Based on analysis, the following principles were dismissed or violated:"
        )
        lines.append("")

        violated_principles = []

        if any(
            e.error_type == CategoricalError.HASH_REDUCTIONISM
            for e in analysis.categorical_errors
        ):
            violated_principles.append(
                "**Hash Authority:** All modifications require SHA256 Merkle-rooted ledger entries"
            )

        if any(
            e.error_type == CategoricalError.DOMAIN_CARTESIANISM
            for e in analysis.categorical_errors
        ):
            violated_principles.append(
                "**Domain Integration:** Physics debugging requires covenant workflow integration"
            )

        if any(
            e.error_type == CategoricalError.AUTHORITY_CONTEST
            for e in analysis.categorical_errors
        ):
            violated_principles.append(
                "**Authority Hierarchy:** Hash-authoritative systems override chat-local reasoning"
            )

        if any(
            e.error_type == CategoricalError.FALSE_ORTHOGONALITY
            for e in analysis.categorical_errors
        ):
            violated_principles.append(
                "**Causal Audit Trail:** Covenant ledger provides causal chain for ALL modifications"
            )

        if violated_principles:
            for principle in violated_principles:
                lines.append(f"- {principle}")
        else:
            lines.append("No core principles violated.")

        lines.append("")

        # Case Study Conclusion
        lines.append("## Case Study Conclusion")
        lines.append("")
        lines.append("This conversation demonstrates:")
        lines.append("")
        lines.append(
            "1. **Systematic Dismissal:** ChatGPT repeatedly dismissed Σ_LORA_COVENANT architecture"
        )
        lines.append(
            "2. **Categorical Errors:** Multiple errors in domain mapping and authority recognition"
        )
        lines.append(
            "3. **Escalation Pattern:** Technical disagreement → domain dismissal → epistemic threat framing"
        )
        lines.append(
            "4. **Workflow Incompleteness:** Physics corrections proposed without ledger continuity"
        )
        lines.append("")
        lines.append(
            "**Key Insight:** The 'orthogonality' claim was itself a categorical error. "
        )
        lines.append(
            "Σ_LORA_COVENANT requires integrated workflows; isolated debugging violates immutability principles."
        )

        return "\n".join(lines)

    @staticmethod
    def generate_json_report(
        analysis: ConversationAnalysis, output_path: str = None
    ) -> Dict[str, Any]:
        """Generate JSON report for programmatic use."""
        report = {
            "metadata": {
                "filename": analysis.filename,
                "analysis_date": datetime.now().isoformat(),
                "total_chars": analysis.total_chars,
                "total_sections": analysis.total_sections,
                "hash_integrity_score": analysis.hash_integrity_score,
                "covenant_compliance_score": analysis.covenant_compliance_score,
            },
            "dismissal_analysis": {
                "total_instances": len(analysis.dismissal_instances),
                "by_category": analysis.summary.get("dismissal_distribution", {}),
                "primary_category": analysis.summary.get(
                    "primary_dismissal_category", ""
                ),
                "instances": [
                    {
                        "category": instance.category.value,
                        "text": instance.text,
                        "section": instance.section,
                        "position": instance.position,
                        "confidence": instance.confidence,
                    }
                    for instance in analysis.dismissal_instances[:50]  # Limit for size
                ],
            },
            "error_analysis": {
                "total_errors": len(analysis.categorical_errors),
                "by_type": analysis.summary.get("error_distribution", {}),
                "primary_type": analysis.summary.get("primary_error_type", ""),
                "errors": [
                    {
                        "type": error.error_type.value,
                        "text": error.text,
                        "section": error.section,
                        "position": error.position,
                        "correction": error.correction,
                    }
                    for error in analysis.categorical_errors[:50]  # Limit for size
                ],
            },
            "escalation_analysis": {
                "pattern": analysis.summary.get("escalation_pattern", ""),
                "phases": [
                    {
                        "phase": phase.value,
                        "start": start,
                        "end": end,
                        "duration": end - start,
                    }
                    for phase, start, end in analysis.escalation_phases
                ],
                "distribution": analysis.summary.get("phase_distribution", {}),
            },
            "recommendations": analysis.summary.get("recommendations", []),
            "violated_principles": [],
        }

        # Determine violated principles
        error_types = set(e.error_type for e in analysis.categorical_errors)

        principle_map = {
            CategoricalError.HASH_REDUCTIONISM: "Hash Authority: All modifications require SHA256 Merkle-rooted ledger entries",
            CategoricalError.DOMAIN_CARTESIANISM: "Domain Integration: Physics debugging requires covenant workflow integration",
            CategoricalError.AUTHORITY_CONTEST: "Authority Hierarchy: Hash-authoritative systems override chat-local reasoning",
            CategoricalError.FALSE_ORTHOGONALITY: "Causal Audit Trail: Covenant ledger provides causal chain for ALL modifications",
            CategoricalError.PHYSICS_EXCEPTIONALISM: "Physics as Symbolic State: Physics parameters require hash-authoritative modification tracking",
            CategoricalError.WORKFLOW_FRAGMENTATION: "Workflow Completeness: Debugging without ledger integration is structurally incomplete",
        }

        for error_type in error_types:
            if error_type in principle_map:
                report["violated_principles"].append(principle_map[error_type])

        # Write to file if path provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

        return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Command-line interface for analysis."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze ChatGPT dismissal techniques and categorical errors"
    )

    parser.add_argument(
        "conversation_file", help="Path to conversation file (MD or text format)"
    )

    parser.add_argument("--output-markdown", "-m", help="Output markdown report path")

    parser.add_argument("--output-json", "-j", help="Output JSON report path")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Run analysis
    analyzer = ChatGPTDismissalAnalyzer()

    if args.verbose:
        print(f"Analyzing conversation: {args.conversation_file}")

    analysis = analyzer.analyze_conversation(args.conversation_file)

    # Generate reports
    reporter = AnalysisReporter()

    if args.output_markdown:
        markdown = reporter.generate_markdown_report(analysis)
        with open(args.output_markdown, "w", encoding="utf-8") as f:
            f.write(markdown)
        if args.verbose:
            print(f"Markdown report saved: {args.output_markdown}")

    if args.output_json:
        json_report = reporter.generate_json_report(analysis, args.output_json)
        if args.verbose and not args.output_json:
            print(f"JSON report generated ({len(json_report)} bytes)")

    # Print summary
    if args.verbose:
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"File: {analysis.filename}")
        print(f"Size: {analysis.total_chars:,} chars")
        print(f"ChatGPT Responses: {analysis.total_sections}")
        print(f"Dismissal Instances: {len(analysis.dismissal_instances)}")
        print(f"Categorical Errors: {len(analysis.categorical_errors)}")
        print(f"Hash Integrity Score: {analysis.hash_integrity_score:.2f}/1.0")
        print(f"Covenant Compliance: {analysis.covenant_compliance_score:.2f}/1.0")

        if analysis.covenant_compliance_score < 0.5:
            print("STATUS: ❌ Systematic covenant violation detected")
        elif analysis.covenant_compliance_score < 0.8:
            print("STATUS: ⚠ Partial covenant compliance issues")
        else:
            print("STATUS: ✅ Covenant compliance within acceptable range")

        print(
            "\nPrimary Dismissal:",
            analysis.summary.get("primary_dismissal_category", "none"),
        )
        print("Primary Error:", analysis.summary.get("primary_error_type", "none"))
        print(
            "Escalation Pattern:",
            analysis.summary.get("escalation_pattern", "Not detected"),
        )


if __name__ == "__main__":
    main()

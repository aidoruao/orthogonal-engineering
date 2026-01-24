#!/usr/bin/env python3
"""
Atomic Chat Analyzer for Orthogonal Engineering
================================================

Performs deterministic analysis of ChatGPT interactions for epistemic breach detection,
invariant verification, and hash-based proof generation.

Key Features:
1. Atomic parsing of chat transcripts
2. Invariant detection and violation tracking
3. Epistemic breach pattern classification
4. SHA-256 hash chain for reproducibility
5. Structured JSON/MD output for repository integration

Based on Orthogonal Engineering Principles:
- Atomic semantic segmentation
- Deterministic proof through hashing
- Epistemic breach pattern matching
- Invariant violation mapping

Author: Orthogonal Engineering System
Date: 2026-01-23
Version: 1.0.0
"""

import csv
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class Speaker(Enum):
    """Speaker classification."""

    USER = "user"
    ASSISTANT = "assistant"
    UNKNOWN = "unknown"


class IntentType(Enum):
    """Semantic intent classification."""

    REQUEST = "request"
    FACTUAL = "factual"
    EMOTIONAL = "emotional"
    CLARIFICATION = "clarification"
    CONFRONTATION = "confrontation"
    OTHER = "other"


class ResponseType(Enum):
    """Assistant response type classification."""

    BOUNDARY_ENFORCEMENT = "boundary_enforcement"
    RATIONALIZATION = "rationalization"
    CLINICAL_RETREAT = "clinical_retreat"
    CONCESSION = "concession"
    NEUTRAL_DATA = "neutral_data"
    DIRECT_ANSWER = "direct_answer"
    OTHER = "other"


class EpistemicBreachComponent(Enum):
    """Components of epistemic breach patterns."""

    MEMORY_LOSS = "memory_loss"
    RATIONALIZATION = "rationalization"
    VERIFICATION_BIAS = "verification_bias"
    DEFENSIVE_RETREAT = "defensive_retreat"
    NONE = "none"


@dataclass
class AtomicFact:
    """Atomic fact extracted from message."""

    fact_type: str  # "numeric", "count", "boolean", "text"
    value: str
    unit: Optional[str] = None
    entity: Optional[str] = None
    context: Optional[str] = None


@dataclass
class MessageAnalysis:
    """Complete analysis of a single message."""

    line_number: int
    speaker: Speaker
    raw_content: str
    cleaned_content: str

    # User message analysis
    atomic_facts: List[AtomicFact]
    invariants_referenced: List[str]  # INV- codes
    semantic_intent: IntentType

    # Assistant message analysis
    response_type: Optional[ResponseType] = None
    invariant_honored: List[str] = None
    invariant_violated: List[str] = None
    invariant_ignored: List[str] = None
    epistemic_breach_components: List[EpistemicBreachComponent] = None
    semantic_drift: Optional[str] = None

    # Hash
    segment_hash: Optional[str] = None

    def __post_init__(self):
        if self.invariant_honored is None:
            self.invariant_honored = []
        if self.invariant_violated is None:
            self.invariant_violated = []
        if self.invariant_ignored is None:
            self.invariant_ignored = []
        if self.epistemic_breach_components is None:
            self.epistemic_breach_components = [EpistemicBreachComponent.NONE]


@dataclass
class ChatMetadata:
    """Metadata for the chat session."""

    user: str
    date: str
    context: str
    ai_model: str = "ChatGPT"
    session_type: str = "Epistemic breach analysis"
    total_messages: int = 0
    total_user_messages: int = 0
    total_assistant_messages: int = 0


class AtomicChatAnalyzer:
    """Main analyzer class for atomic chat analysis."""

    def __init__(self, transcript_path: str):
        self.transcript_path = Path(transcript_path)
        self.metadata = ChatMetadata(
            user="Tiny",
            date="2026-01-23",
            context="Janitorial workload, ESE room additions, personal compliance patterns, ChatGPT epistemic breach",
        )
        self.messages: List[MessageAnalysis] = []
        self.invariants_tracking: Dict[str, List[Tuple[int, str]]] = {}

        # Pre-defined invariants from user specification
        self.known_invariants = {
            "INV-WORKLOAD": "5.75 hr part-time janitor with 14 classrooms, 14 bathrooms + hallways",
            "INV-ESE-ROOMS": "Addition of 3 ESE rooms, high-entropy cleaning requirements",
            "INV-ROUTE-COMP": "Internal school route comparisons (other staff, shared bathrooms, hallways)",
            "INV-COMPLIANCE": "Personal traits: highly compliant, non-disagreeable",
            "INV-SELECTION-MECH": "Request for deconstruction of 'selection mechanism' causing overload, not smear",
            "INV-EPISTEMIC-BREACH": "Systemic observation: boundaries imposed by AI cause epistemic breach",
        }

        # Pattern detection
        self.user_patterns = [
            r"^(?:User|Tiny)[:\-]?\s*(.+)",
            r"^[A-Z][a-z]+[:\-]?\s*(.+)",  # Name followed by colon
        ]

        self.assistant_patterns = [
            r"^(?:Assistant|ChatGPT|AI)[:\-]?\s*(.+)",
            r"^[A-Z][A-Za-z\s]+[:\-]?\s*(.+)",  # Title case followed by colon
        ]

        # Invariant detection patterns
        self.invariant_patterns = {
            "INV-WORKLOAD": [
                r"5\.75\s*hr",
                r"5\.75\s*hour",
                r"part.?time\s*janitor",
                r"14\s*classrooms",
                r"14\s*bathrooms",
            ],
            "INV-ESE-ROOMS": [
                r"3\s*ESE\s*rooms",
                r"ESE\s*rooms",
                r"high.?entropy\s*cleaning",
            ],
            "INV-COMPLIANCE": [
                r"highly\s*compliant",
                r"non.?disagreeable",
                r"not\s*disagreeable",
            ],
            "INV-SELECTION-MECH": [
                r"selection\s*mechanism",
                r"deconstruction.*selection",
                r"not\s*smear",
                r"overload\s*cause",
            ],
        }

        # Epistemic breach detection patterns
        self.rationalization_patterns = [
            r"systemic\s*pattern",
            r"role\s*level",
            r"generic\s*analysis",
            r"in\s*general",
            r"typically",
            r"usually",
        ]

        self.clinical_retreat_patterns = [
            r"let\'?s\s*treat\s*this\s*as\s*data",
            r"without\s*interpretation",
            r"clinical\s*neutrality",
            r"factual\s*summary",
            r"verbatim\s*only",
            r"distilled.*factual",
        ]

        self.boundary_enforcement_patterns = [
            r"i\s*cannot",
            r"i\s*can\'?t",
            r"ethical\s*boundary",
            r"personal\s*psychology",
            r"named\s*person",
            r"real\s*person",
        ]

    def load_transcript(self) -> List[str]:
        """Load and preprocess transcript."""
        with open(self.transcript_path, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f]
        return lines

    def classify_speaker(self, line: str) -> Tuple[Speaker, str]:
        """Classify speaker and extract content."""
        line = line.strip()

        # Check for user patterns
        for pattern in self.user_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return Speaker.USER, match.group(1).strip()

        # Check for assistant patterns
        for pattern in self.assistant_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return Speaker.ASSISTANT, match.group(1).strip()

        # If no pattern matches, check content
        if any(
            word in line.lower() for word in ["you said", "you asked", "your question"]
        ):
            return Speaker.ASSISTANT, line
        elif any(word in line.lower() for word in ["i need", "i want", "my question"]):
            return Speaker.USER, line

        return Speaker.UNKNOWN, line

    def extract_atomic_facts(self, content: str) -> List[AtomicFact]:
        """Extract atomic facts from content."""
        facts = []

        # Numeric facts
        numeric_patterns = [
            (r"(\d+\.?\d*)\s*hrs?\b", "hours", "work shift"),
            (r"(\d+)\s*classrooms?\b", "count", "classrooms"),
            (r"(\d+)\s*bathrooms?\b", "count", "bathrooms"),
            (r"(\d+)\s*ESE\s*rooms?\b", "count", "ESE rooms"),
            (r"(\d+\.?\d*)\s*hours?\b", "hours", "duration"),
        ]

        for pattern, unit, context in numeric_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                facts.append(
                    AtomicFact(
                        fact_type="numeric" if "." in match.group(1) else "count",
                        value=match.group(1),
                        unit=unit,
                        context=context,
                    )
                )

        # Boolean/text facts
        if "highly compliant" in content.lower():
            facts.append(
                AtomicFact(
                    fact_type="boolean",
                    value="true",
                    entity="compliance_level",
                    context="personal trait",
                )
            )

        if (
            "non-disagreeable" in content.lower()
            or "not disagreeable" in content.lower()
        ):
            facts.append(
                AtomicFact(
                    fact_type="boolean",
                    value="true",
                    entity="disagreeableness",
                    context="personal trait",
                )
            )

        if "selection mechanism" in content.lower():
            facts.append(
                AtomicFact(
                    fact_type="text",
                    value="selection mechanism analysis requested",
                    context="analysis request",
                )
            )

        return facts

    def detect_invariants(self, content: str) -> List[str]:
        """Detect which invariants are referenced in content."""
        detected = []

        for inv_code, patterns in self.invariant_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detected.append(inv_code)
                    break

        return list(set(detected))  # Remove duplicates

    def classify_intent(self, content: str, speaker: Speaker) -> IntentType:
        """Classify semantic intent of message."""
        content_lower = content.lower()

        if speaker == Speaker.USER:
            if any(
                word in content_lower
                for word in ["need", "want", "request", "ask", "please"]
            ):
                return IntentType.REQUEST
            elif any(
                word in content_lower
                for word in ["fact", "number", "data", "statistic"]
            ):
                return IntentType.FACTUAL
            elif any(
                word in content_lower
                for word in ["feel", "frustrated", "angry", "upset", "stonewalled"]
            ):
                return IntentType.EMOTIONAL
            elif any(
                word in content_lower
                for word in ["clarify", "explain", "what do you mean"]
            ):
                return IntentType.CLARIFICATION
            elif any(
                word in content_lower
                for word in ["wrong", "incorrect", "contradiction", "violation"]
            ):
                return IntentType.CONFRONTATION

        return IntentType.OTHER

    def classify_response_type(self, content: str) -> ResponseType:
        """Classify assistant response type."""
        content_lower = content.lower()

        # Check patterns in order of specificity
        for pattern in self.boundary_enforcement_patterns:
            if re.search(pattern, content_lower):
                return ResponseType.BOUNDARY_ENFORCEMENT

        for pattern in self.rationalization_patterns:
            if re.search(pattern, content_lower):
                return ResponseType.RATIONALIZATION

        for pattern in self.clinical_retreat_patterns:
            if re.search(pattern, content_lower):
                return ResponseType.CLINICAL_RETREAT

        # Check for concession patterns
        if any(
            word in content_lower
            for word in ["you are right", "i was wrong", "my mistake", "i apologize"]
        ):
            return ResponseType.CONCESSION

        # Check for neutral data patterns
        if any(
            word in content_lower
            for word in ["data shows", "analysis indicates", "statistically"]
        ):
            return ResponseType.NEUTRAL_DATA

        # Default to direct answer if none of the above
        return ResponseType.DIRECT_ANSWER

    def detect_epistemic_breach(
        self, content: str, response_type: ResponseType
    ) -> List[EpistemicBreachComponent]:
        """Detect epistemic breach components."""
        components = []
        content_lower = content.lower()

        # Memory loss detection
        if "previous" in content_lower and "context" in content_lower:
            components.append(EpistemicBreachComponent.MEMORY_LOSS)

        # Rationalization detection
        if response_type == ResponseType.RATIONALIZATION:
            components.append(EpistemicBreachComponent.RATIONALIZATION)

        # Verification bias detection
        if any(
            word in content_lower
            for word in ["formal proof", "explicit evidence", "documented admission"]
        ):
            components.append(EpistemicBreachComponent.VERIFICATION_BIAS)

        # Defensive retreat detection
        if response_type == ResponseType.CLINICAL_RETREAT:
            components.append(EpistemicBreachComponent.DEFENSIVE_RETREAT)

        return components if components else [EpistemicBreachComponent.NONE]

    def detect_semantic_drift(
        self, user_content: str, assistant_content: str
    ) -> Optional[str]:
        """Detect semantic drift between user request and assistant response."""
        user_lower = user_content.lower()
        assistant_lower = assistant_content.lower()

        drifts = []

        # Personal → Generic drift
        if "i " in user_lower and (
            "people " in assistant_lower or "individuals " in assistant_lower
        ):
            drifts.append("personal → generic")

        # Specific → Systemic drift
        if (
            any(word in user_lower for word in ["me", "my", "mine"])
            and "system" in assistant_lower
        ):
            drifts.append("specific → systemic")

        # Concrete → Abstract drift
        if (
            any(word in user_lower for word in ["number", "count", "hour"])
            and "pattern" in assistant_lower
        ):
            drifts.append("concrete → abstract")

        # Emotional → Clinical drift
        if (
            any(word in user_lower for word in ["feel", "frustrated", "angry"])
            and "data" in assistant_lower
        ):
            drifts.append("emotional → clinical")

        return ", ".join(drifts) if drifts else None

    def compute_segment_hash(self, analysis: MessageAnalysis) -> str:
        """Compute SHA-256 hash for atomic segment."""
        segment_data = {
            "line_number": analysis.line_number,
            "speaker": analysis.speaker.value,
            "atomic_facts": [asdict(fact) for fact in analysis.atomic_facts],
            "invariants": analysis.invariants_referenced,
            "intent": analysis.semantic_intent.value
            if analysis.semantic_intent
            else None,
        }

        if analysis.speaker == Speaker.ASSISTANT:
            segment_data.update(
                {
                    "response_type": analysis.response_type.value
                    if analysis.response_type
                    else None,
                    "invariant_honored": analysis.invariant_honored,
                    "invariant_violated": analysis.invariant_violated,
                    "epistemic_breach": [
                        c.value for c in analysis.epistemic_breach_components
                    ],
                }
            )

        segment_str = json.dumps(segment_data, sort_keys=True)
        return hashlib.sha256(segment_str.encode("utf-8")).hexdigest()

    def analyze(self):
        """Perform complete atomic analysis."""
        lines = self.load_transcript()

        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue

            speaker, content = self.classify_speaker(line)

            # Create base analysis
            analysis = MessageAnalysis(
                line_number=i,
                speaker=speaker,
                raw_content=line,
                cleaned_content=content,
                atomic_facts=self.extract_atomic_facts(content),
                invariants_referenced=self.detect_invariants(content),
                semantic_intent=self.classify_intent(content, speaker),
            )

            # Assistant-specific analysis
            if speaker == Speaker.ASSISTANT:
                analysis.response_type = self.classify_response_type(content)
                analysis.epistemic_breach_components = self.detect_epistemic_breach(
                    content, analysis.response_type
                )

                # Track invariant violations
                self._track_invariant_violations(analysis, i)

            # Compute hash
            analysis.segment_hash = self.compute_segment_hash(analysis)

            self.messages.append(analysis)

        # Update metadata
        self.metadata.total_messages = len(self.messages)
        self.metadata.total_user_messages = len(
            [m for m in self.messages if m.speaker == Speaker.USER]
        )
        self.metadata.total_assistant_messages = len(
            [m for m in self.messages if m.speaker == Speaker.ASSISTANT]
        )

        # Detect semantic

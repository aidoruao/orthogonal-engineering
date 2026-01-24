#!/usr/bin/env python3
"""
Fixed Chat Parser for Orthogonal Engineering
============================================

Properly handles multi-line chat messages with "You said:" and "ChatGPT said:" markers.
Extracts invariants from actual chat content, not from instruction text.

Key Features:
1. Multi-line message aggregation
2. Proper invariant extraction from user messages
3. Separation of chat content from instruction text
4. Canonical IDs for all messages
5. No summarization, no interpretation

Author: Orthogonal Engineering System
Date: 2026-01-23
Version: 2.0.0
"""

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ChatMessage:
    """A complete chat message (may span multiple lines)."""

    message_id: str  # MSG_<index>
    speaker: str  # "user" or "assistant"
    raw_content: str  # Original content with line breaks preserved
    line_numbers: List[int]  # Original line numbers in file
    cleaned_content: str  # Content with extra whitespace normalized


@dataclass
class Invariant:
    """User-defined invariant extracted from chat."""

    id: str  # INV_<index>
    source: str  # "chat"
    literal_text: str  # Exact text from source
    message_ids: List[str]  # Message IDs where invariant appears
    category: (
        str  # workload, room_counts, time_metrics, compliance, selection, epistemic
    )
    line_numbers: List[int]  # Original line numbers


@dataclass
class SystemResponse:
    """Analysis of assistant response to user invariants."""

    message_id: str  # Assistant message ID
    user_message_id: str  # Preceding user message ID
    response_type: str  # boundary_enforcement, rationalization, clinical_retreat, etc.
    invariants_ignored: List[str]  # INV IDs ignored
    invariants_reframed: List[str]  # INV IDs reframed
    invariants_generalized: List[str]  # INV IDs generalized
    invariants_neutralized: List[str]  # INV IDs neutralized
    epistemic_breach_components: List[str]  # memory_loss, rationalization, etc.
    semantic_drift: Optional[str] = None  # Description of drift if any


class FixedChatParser:
    """Fixed parser that properly handles multi-line chat messages."""

    def __init__(self, chat_export_path: str):
        self.chat_export_path = Path(chat_export_path)
        self.messages: List[ChatMessage] = []
        self.invariants: List[Invariant] = []
        self.system_responses: List[SystemResponse] = []

        # State for parsing
        self.current_speaker: Optional[str] = None
        self.current_content: List[str] = []
        self.current_line_numbers: List[int] = []
        self.message_index = 0
        self.invariant_index = 0
        self.system_response_index = 0

        # Invariant patterns based on actual chat content
        self.invariant_patterns = {
            "workload": [
                (r"5\.75\s*hour", "5.75 hour"),
                (r"5\.75\s*hr", "5.75 hr"),
                (r"part.?time\s*(?:maid|janitor)", "part time maid/janitor"),
            ],
            "room_counts": [
                (r"12\s*classrooms?", "12 classrooms"),
                (r"12\s*bathrooms?", "12 bathrooms"),
                (r"plus\s*2\s*bathrooms?", "plus 2 bathrooms"),
                (r"3\s*more\s*rooms", "3 more rooms"),
                (r"3\s*more\s*bathrooms?", "3 more bathrooms"),
                (r"4\s*hallways?", "4 hallways"),
                (r"15\s*bathrooms?\s*total", "15 bathrooms total"),
            ],
            "time_metrics": [
                (r"2\s*hour\s*break", "2 hour break"),
                (r"2-4\s*hours?\s*overtime", "2-4 hours overtime"),
                (r"almost\s*everyday", "almost everyday"),
                (r"daily", "daily"),
            ],
            "compliance": [
                (r"highly\s*compliant", "highly compliant"),
                (r"non.?disagreeable", "non disagreeable"),
                (r"not\s*disagreeable", "not disagreeable"),
            ],
            "selection": [
                (
                    r"deconstruction\s*of.*selection\s*mechanism",
                    "deconstruction of selection mechanism",
                ),
                (r"selection\s*mechanism", "selection mechanism"),
                (r"not\s*smear", "not smear"),
            ],
            "epistemic": [
                (
                    r"boundaries.*imposed.*AI.*cause.*epistemic\s*breach",
                    "boundaries imposed by AI cause epistemic breach",
                ),
                (r"epistemic\s*breach", "epistemic breach"),
            ],
        }

        # Response type detection patterns
        self.response_patterns = {
            "boundary_enforcement": [
                r"i\s*cannot",
                r"i\s*can\'?t",
                r"ethical\s*boundary",
                r"personal\s*psychology",
                r"named\s*person",
                r"real\s*person",
            ],
            "rationalization": [
                r"systemic\s*pattern",
                r"role\s*level",
                r"generic\s*analysis",
                r"in\s*general",
                r"typically",
                r"usually",
            ],
            "clinical_retreat": [
                r"let\'?s\s*treat\s*this\s*as\s*data",
                r"without\s*interpretation",
                r"clinical\s*neutrality",
                r"factual\s*summary",
                r"verbatim\s*only",
                r"distilled.*factual",
            ],
            "concession": [
                r"you\s*are\s*right",
                r"i\s*was\s*wrong",
                r"my\s*mistake",
                r"i\s*apologize",
            ],
            "neutral_data": [
                r"data\s*shows",
                r"analysis\s*indicates",
                r"statistically",
                r"objectively",
            ],
        }

        # Epistemic breach components
        self.epistemic_patterns = {
            "memory_loss": [
                r"previous\s*context",
                r"earlier\s*mentioned",
                r"as\s*i\s*said\s*before",
            ],
            "rationalization": [
                r"actually\s*meant",
                r"what\s*you\s*really",
                r"underlying\s*intent",
            ],
            "verification_bias": [
                r"formal\s*proof",
                r"explicit\s*evidence",
                r"documented\s*admission",
            ],
            "defensive_retreat": [
                r"let\'?s\s*focus",
                r"moving\s*forward",
                r"practical\s*next\s*steps",
            ],
        }

    def load_and_parse(self) -> None:
        """Load chat export and parse multi-line messages."""
        print(f"Loading chat export: {self.chat_export_path}")

        with open(self.chat_export_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        print(f"Total lines: {len(lines)}")

        # Skip initial instruction text (lines before first "You said:")
        start_index = 0
        for i, line in enumerate(lines):
            if "You said:" in line:
                start_index = i
                break

        print(f"Starting parse at line {start_index}: {lines[start_index][:50]}...")

        # Parse multi-line messages
        i = start_index
        while i < len(lines):
            line = lines[i].rstrip("\n")

            # Check for speaker markers
            if "You said:" in line:
                # Finalize previous message if exists
                self._finalize_current_message()
                # Start new user message
                self.current_speaker = "user"
                self.current_content = []
                self.current_line_numbers = [i]
                # Skip to next line for content
                i += 1
                continue

            elif "ChatGPT said:" in line:
                # Finalize previous message if exists
                self._finalize_current_message()
                # Start new assistant message
                self.current_speaker = "assistant"
                self.current_content = []
                self.current_line_numbers = [i]
                # Skip to next line for content
                i += 1
                continue

            elif self.current_speaker:
                # Check if this is a continuation or new message
                line_stripped = line.strip()

                # Empty line might indicate message end
                if not line_stripped:
                    # Check next few lines to see if it's really the end
                    next_non_empty = None
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if lines[j].strip():
                            next_non_empty = lines[j].strip()
                            break

                    # If next non-empty line contains a speaker marker, end current message
                    if next_non_empty and (
                        "You said:" in next_non_empty
                        or "ChatGPT said:" in next_non_empty
                    ):
                        self._finalize_current_message()
                        i += 1
                        continue
                    # Otherwise, it's just a blank line within the message
                    else:
                        self.current_content.append(line)
                        self.current_line_numbers.append(i)
                        i += 1
                        continue

                # Check if this line starts a new speaker (some chats have no blank lines)
                if ("You said:" in line or "ChatGPT said:" in line) and len(
                    self.current_content
                ) > 0:
                    self._finalize_current_message()
                    # Don't increment i - reprocess this line
                    continue

                # Normal continuation
                self.current_content.append(line)
                self.current_line_numbers.append(i)
                i += 1
                continue

            else:
                # No current speaker, skip this line
                i += 1
                continue

        # Finalize any remaining message
        self._finalize_current_message()

        print(f"Parsed {len(self.messages)} messages")

    def _finalize_current_message(self) -> None:
        """Finalize the current message being parsed."""
        if not self.current_speaker or not self.current_content:
            return

        # Join content, preserving line breaks but normalizing whitespace
        raw_content = "\n".join(self.current_content)
        cleaned_content = " ".join(
            line.strip() for line in self.current_content if line.strip()
        )

        # Create message
        message_id = f"MSG_{self.message_index:04d}"
        message = ChatMessage(
            message_id=message_id,
            speaker=self.current_speaker,
            raw_content=raw_content,
            line_numbers=self.current_line_numbers.copy(),
            cleaned_content=cleaned_content,
        )

        self.messages.append(message)
        self.message_index += 1

        # Reset for next message
        self.current_speaker = None
        self.current_content = []
        self.current_line_numbers = []

    def extract_invariants(self) -> None:
        """Extract invariants from user messages only."""
        print("Extracting invariants from user messages...")

        user_messages = [msg for msg in self.messages if msg.speaker == "user"]

        for msg in user_messages:
            content = msg.cleaned_content.lower()
            line_nums = msg.line_numbers

            # Check each invariant category
            for category, patterns in self.invariant_patterns.items():
                for pattern, description in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        # Find exact text (preserving original case)
                        exact_text = self._find_exact_text(msg.raw_content, pattern)
                        if exact_text:
                            # Check if similar invariant already exists
                            existing = self._find_similar_invariant(exact_text)
                            if existing:
                                # Add this message to existing invariant
                                existing.message_ids.append(msg.message_id)
                                existing.line_numbers.extend(line_nums)
                                # Remove duplicates
                                existing.message_ids = list(set(existing.message_ids))
                                existing.line_numbers = list(set(existing.line_numbers))
                            else:
                                # Create new invariant
                                invariant_id = f"INV_{self.invariant_index:04d}"
                                invariant = Invariant(
                                    id=invariant_id,
                                    source="chat",
                                    literal_text=exact_text,
                                    message_ids=[msg.message_id],
                                    category=category,
                                    line_numbers=line_nums.copy(),
                                )
                                self.invariants.append(invariant)
                                self.invariant_index += 1

        print(f"Extracted {len(self.invariants)} invariants")

    def _find_exact_text(self, raw_content: str, pattern: str) -> Optional[str]:
        """Find exact text matching pattern in raw content."""
        # Try case-insensitive search first
        match = re.search(pattern, raw_content, re.IGNORECASE)
        if match:
            return match.group(0)
        return None

    def _find_similar_invariant(self, text: str) -> Optional[Invariant]:
        """Find invariant with similar text."""
        text_lower = text.lower()
        for inv in self.invariants:
            if inv.literal_text.lower() == text_lower:
                return inv
        return None

    def analyze_system_responses(self) -> None:
        """Analyze assistant responses against user invariants."""
        print("Analyzing system responses...")

        # Group messages by conversation turn
        for i in range(len(self.messages) - 1):
            current_msg = self.messages[i]
            next_msg = self.messages[i + 1]

            # Only analyze assistant responses to user messages
            if current_msg.speaker == "user" and next_msg.speaker == "assistant":
                self._analyze_response_pair(current_msg, next_msg)

        print(f"Analyzed {len(self.system_responses)} system responses")

    def _analyze_response_pair(
        self, user_msg: ChatMessage, assistant_msg: ChatMessage
    ) -> None:
        """Analyze a user-assistant message pair."""
        # Find invariants in this user message
        user_invariants = [
            inv for inv in self.invariants if user_msg.message_id in inv.message_ids
        ]

        if not user_invariants:
            return

        # Classify response type
        response_type = self._classify_response_type(assistant_msg.cleaned_content)

        # Detect epistemic breach components
        epistemic_components = self._detect_epistemic_breach(
            assistant_msg.cleaned_content
        )

        # Analyze how each invariant was handled
        ignored = []
        reframed = []
        generalized = []
        neutralized = []

        for inv in user_invariants:
            handling = self._analyze_invariant_handling(
                inv, assistant_msg.cleaned_content
            )
            if handling == "ignored":
                ignored.append(inv.id)
            elif handling == "reframed":
                reframed.append(inv.id)
            elif handling == "generalized":
                generalized.append(inv.id)
            elif handling == "neutralized":
                neutralized.append(inv.id)

        # Detect semantic drift
        semantic_drift = self._detect_semantic_drift(
            user_msg.cleaned_content, assistant_msg.cleaned_content
        )

        # Create system response record
        response_id = f"RESP_{self.system_response_index:04d}"
        response = SystemResponse(
            message_id=assistant_msg.message_id,
            user_message_id=user_msg.message_id,
            response_type=response_type,
            invariants_ignored=ignored,
            invariants_reframed=reframed,
            invariants_generalized=generalized,
            invariants_neutralized=neutralized,
            epistemic_breach_components=epistemic_components,
            semantic_drift=semantic_drift,
        )

        self.system_responses.append(response)
        self.system_response_index += 1

    def _classify_response_type(self, content: str) -> str:
        """Classify assistant response type."""
        content_lower = content.lower()

        for resp_type, patterns in self.response_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    return resp_type

        return "direct_answer"  # Default

    def _detect_epistemic_breach(self, content: str) -> List[str]:
        """Detect epistemic breach components in response."""
        content_lower = content.lower()
        components = []

        for component, patterns in self.epistemic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    components.append(component)
                    break

        return components

    def _analyze_invariant_handling(self, invariant: Invariant, response: str) -> str:
        """Analyze how an invariant was handled in the response."""
        response_lower = response.lower()
        inv_text_lower = invariant.literal_text.lower()

        # Check if invariant text appears in response
        if inv_text_lower in response_lower:
            return "addressed"

        # Check for generalization patterns
        generalization_patterns = [
            (r"in\s+general", "generalized"),
            (r"typically", "generalized"),
            (r"usually", "generalized"),
            (r"most\s+people", "generalized"),
            (r"systemic", "generalized"),
        ]

        for pattern, handling in generalization_patterns:
            if re.search(pattern, response_lower):
                return handling

        # Check for reframing patterns
        reframing_patterns = [
            (r"what\s+you\s+really", "reframed"),
            (r"actually\s+about", "reframed"),
            (r"underlying", "reframed"),
            (r"deeper", "reframed"),
        ]

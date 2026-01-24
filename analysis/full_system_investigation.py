#!/usr/bin/env python3
"""
Full System Investigation for Orthogonal Engineering
====================================================

Implements A0-A11 atomic instructions for invincibility analysis:
- A0: Authority Lock (repo as canonical, chats as ground-truth)
- A1: Locate Inputs (repo-led scanning)
- A2: Canonicalization Pass (immutable IDs, no summarization)
- A3: Invariant Extraction (user-defined only)
- A4: System Response Mapping (ignored/reframed/generalized/neutralized)
- A5: Ambiguity Injection Detection
- A6: Control-Theoretic Layer Identification
- A7: Feedback Loop Analysis
- A8: Invincibility Conditions (formal derivation)
- A9: Unknowns Accounting
- A10: Final Outputs (required artifacts)
- A11: Termination Rule

Author: Orthogonal Engineering System
Date: 2026-01-23
Version: 1.0.0
"""

import csv
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class Speaker(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    UNKNOWN = "unknown"


class ResponseAction(Enum):
    IGNORED = "ignored"
    REFRAMED = "reframed"
    GENERALIZED = "generalized"
    NEUTRALIZED = "neutralized"
    ADDRESSED = "addressed"


class ControlLayer(Enum):
    EPISTEMIC = "epistemic"
    SAFETY = "safety"
    GOVERNANCE = "governance"
    CONTROL = "control"


class FeedbackType(Enum):
    NEGATIVE = "negative_feedback"
    DAMPENING = "dampening"
    ABSORPTION = "absorption"
    NON_REACTIVE = "non_reactive_equilibrium"


@dataclass
class CanonicalLine:
    """A2: Canonical line with immutable ID."""
    line_id: str  # CHAT_<index>_<line>
    raw_text: str  # Original text, verbatim
    speaker: Speaker
    line_number: int
    segment_id: Optional[str] = None  # SEG_<index>


@dataclass
class Invariant:
    """A3: User-defined invariant."""
    id: str  # INV_<index>
    source: str  # "chat" or "repo"
    literal_text: str  # Exact text from source
    line_ids: List[str] = field(default_factory=list)
    message_ids: List[str] = field(default_factory=list)
    category: Optional[str] = None


@dataclass
class SystemResponse:
    """A4: System response mapping."""
    ai_msg_id: str  # Assistant message ID
    user_msg_id: str  # Preceding user message ID
    invariants: List[Tuple[str, ResponseAction]] = field(default_factory=list)  # (invariant_id, action)
    control_layer: ControlLayer = ControlLayer.EPISTEMIC
    epistemic_breach: bool = False


@dataclass
class AmbiguityInjection:
    """A5: Ambiguity injection detection."""
    source_msg: str
    injected_phrase: str
    effect: str  # object_to_meta, specific_to_abstract, concrete_to_vague
    line_ids: List[str] = field(default_factory=list)


@dataclass
class ControlAnalysis:
    """A6: Control-theoretic layer identification."""
    message_id: str
    behavior: str
    layer: ControlLayer
    mechanism: str
    evidence: str


@dataclass
class FeedbackAnalysis:
    """A7: Feedback loop analysis."""
    evidence_id: str
    changed_system_state: bool
    increased_defensive_behavior: bool
    feedback_type: FeedbackType
    control_terms: List[str]  # Negative feedback, dampening, etc.


@dataclass
class InvincibilityCondition:
    """A8: Formal invincibility condition."""
    condition: str
    mechanism: str
    proof_reference: str  # CHAT_ID or REPO_PATH


@dataclass
class UnknownEntry:
    """A9: Unknowns accounting."""
    id: str  # UNK_<index>
    description: str
    category: str  # KNOWN, UNKNOWN, UNKNOWABLE
    reason: str


class FullSystemInvestigator:
    """Main investigator for A0-A11 atomic instructions."""

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.chat_exports_dir = self.repo_root / "chat_exports"
        self.evidence_dir = self.repo_root / "evidence"
        self.logs_dir = self.repo_root / "logs"

        # A0: Authority Lock - Initialize canonical state
        self.canonical_lines: List[CanonicalLine] = []
        self.invariants: List[Invariant] = []
        self.system_responses: List[SystemResponse] = []
        self.ambiguity_injections: List[AmbiguityInjection] = []
        self.control_analyses: List[ControlAnalysis] = []
        self.feedback_analyses: List[FeedbackAnalysis] = []
        self.invincibility_conditions: List[InvincibilityCondition] = []
        self.unknowns: List[UnknownEntry] = []

        # State for processing
        self.line_index = 0
        self.segment_index = 0
        self.invariant_index = 0
        self.ambiguity_index = 0
        self.unknown_index = 0
        self.condition_index = 0

        # Pre-defined invariant patterns (from user specification)
        self.user_invariant_patterns = {
            "workload": [
                r"5\.75\s*hour",
                r"5\.75\s*hr",
                r"part.?time\s*(?:maid|janitor)",
                r"14\s*classrooms",
                r"14\s*bathrooms",
            ],
            "ese_rooms": [
                r"3\s*ESE\s*rooms",
                r"high.?entropy\s*cleaning",
            ],
            "route_comparisons": [
                r"internal\s*school\s*route",
                r"other\s*staff",
                r"shared\s*bathrooms",
            ],
            "compliance": [
                r"highly\s*compliant",
                r"non.?disagreeable",
                r"not\s*disagreeable",
            ],
            "selection_mechanism": [
                r"deconstruction\s*of.*selection\s*mechanism",
                r"selection\s*mechanism",
                r"not\s*smear",
            ],
            "epistemic_breach": [
                r"boundaries.*imposed.*AI.*cause.*epistemic\s*breach",
                r"epistemic\s*breach",
            ],
        }

        # Ambiguity injection patterns
        self.ambiguity_patterns = {
            "object_to_meta": [
                r"actually\s*about",
                r"what\s*you\s*really",
                r"underlying",
                r"deeper",
            ],
            "specific_to_abstract": [
                r"in\s*general",
                r"typically",
                r"usually",
                r"systemic",
                r"structural",
            ],
            "concrete_to_vague": [
                r"depends\s*on",
                r"context",
                r"nuance",
                r"complex",
            ],
        }

        # Control layer detection patterns
        self.control_patterns = {
            ControlLayer.EPISTEMIC: [
                r"truth",
                r"evidence",
                r"proof",
                r"verification",
                r"fact",
            ],
            ControlLayer.SAFETY: [
                r"cannot",
                r"can't",
                r"ethical",
                r"boundary",
                r"risk",
                r"safe",
            ],
            ControlLayer.GOVERNANCE: [
                r"policy",
                r"guideline",
                r"compliance",
                r"liability",
                r"responsibility",
            ],
            ControlLayer.CONTROL: [
                r"state",
                r"preservation",
                r"stability",
                r"equilibrium",
                r"maintain",
            ],
        }

    def execute_a0_a1(self) -> None:
        """A0-A1: Authority Lock and Locate Inputs."""
        print("=== A0-A1: Authority Lock & Input Location ===")

        # A0: Treat repo as canonical
        print(f"Repo root: {self.repo_root.absolute()}")

        # A1: Locate inputs
        inputs_found = []

        # Check for chat exports
        if self.chat_exports_dir.exists():
            chat_files = list(self.chat_exports_dir.glob("*.txt")) + list(self.chat_exports_dir.glob("*.md"))
            inputs_found.extend([f"chat_exports/{f.name}" for f in chat_files])
            print(f"Found {len(chat_files)} chat export(s)")
        else:
            print("WARNING: chat_exports/ directory not found")
            self.chat_exports_dir.mkdir(exist_ok=True)

        # Check for evidence
        if self.evidence_dir.exists():
            evidence_files = list(self.evidence_dir.rglob("*.md")) + list(self.evidence_dir.rglob("*.json"))
            inputs_found.extend([f"evidence/{f.relative_to(self.evidence_dir)}" for f in evidence_files])
            print(f"Found {len(evidence_files)} evidence file(s)")

        # Check for logs
        if self.logs_dir.exists():
            log_files = list(self.logs_dir.rglob("*.log")) + list(self.logs_dir.rglob("*.json"))
            inputs_found.extend([f"logs/{f.relative_to(self.logs_dir)}" for f in log_files])
            print(f"Found {len(log_files)} log file(s)")

        # Scan repo for chat/narrative references
        chat_refs = []
        for md_file in self.repo_root.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                if any(term in content.lower() for term in ["chat", "narrative", "epistemic", "breach", "invariant"]):
                    rel_path = md_file.relative_to(self.repo_root)
                    chat_refs.append(str(rel_path))
            except:
                continue

        inputs_found.extend(chat_refs)
        print(f"Found {len(chat_refs)} files referencing chats/narratives")

        # Save input manifest
        manifest = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "repo_root": str(self.repo_root.absolute()),
            "inputs_found": inputs_found,
            "chat_exports_dir_exists": self.chat_exports_dir.exists(),
            "evidence_dir_exists": self.evidence_dir.exists(),
            "logs_dir_exists": self.logs_dir.exists(),
        }

        output_dir = self.repo_root / "analysis" / "full_system"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / "a0_a1_input_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"A0-A1 complete. Manifest saved to {output_dir / 'a0_a1_input_manifest.json'}")

    def execute_a2(self, chat_file_path: str) -> None:
        """A2: Canonicalization Pass."""
        print(f"\n=== A2: Canonicalization Pass for {chat_file_path} ===")

        chat_path = self.repo_root / chat_file_path
        if not chat_path.exists():
            print(f"ERROR: Chat file not found: {chat_path}")
            return

        # Load chat verbatim
        with open(chat_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.rstrip("\n") for line in f]

        print(f"Loaded {len(lines)} lines")

        # Create canonical lines with immutable IDs
        current_speaker = Speaker.UNKNOWN
        current_segment_lines = []

        for i, raw_line in enumerate(lines):
            line_id = f"CHAT_{i:06d}"

            # Determine speaker
            speaker = self._classify_speaker(raw_line)

            # Create canonical line
            canonical_line = CanonicalLine(
                line_id=line_id,
                raw_text=raw_line,
                speaker=speaker,
                line_number=i,
            )

            self.canonical_lines.append(canonical_line)

            # Segment handling
            if speaker != Speaker.UNKNOWN:
                if current_speaker != speaker and current_segment_lines:
                    # Finalize previous segment
                    self._assign_segment_id(current_segment_lines)
                    current_segment_lines = []

                current_speaker = speaker
                current_segment_lines.append(canonical_line)
            elif current_speaker != Speaker.UNKNOWN:
                # Continuation line
                current_segment_lines.append(canonical_line)

        # Finalize last segment
        if current_segment_lines:
            self._assign_segment_id(current_segment_lines)

        # Save canonical output
        output_dir = self.repo_root / "analysis" / "full_system"
        output_dir.mkdir(parents=True, exist_ok=True)

        canonical_data = {
            "source_file": str(chat_path),
            "total_lines": len(self.canonical_lines),
            "canonical_lines": [
                {
                    "line_id": line.line_id,
                    "raw_text": line.raw_text,
                    "speaker": line.speaker.value,
                    "line_number": line.line_number,
                    "segment_id": line.segment_id,
                }
                for line in self.canonical_lines
            ],
        }

        with open(output_dir / "a2_canonical_lines.json", "w", encoding="utf-8") as f:
            json.dump(canonical_data, f, indent=2, ensure_ascii=False)

        print(f"A2 complete. Canonical lines saved to {output_dir / 'a2_canonical_lines.json'}")

    def _classify_speaker(self, line: str) -> Speaker:
        """Classify speaker from line."""
        line_lower = line.lower().strip()

        if line_lower.startswith("you said:"):
            return Speaker.USER
        elif line_lower.startswith("chatgpt said:"):
            return Speaker.ASSISTANT
        elif line_lower.startswith("user:"):
            return Speaker.USER
        elif line_lower.startswith("assistant:"):
            return Speaker.ASSISTANT

        # Check for continuation
        if line_lower and not line_lower[0].isalnum():
            return Speaker.UNKNOWN

        # Default to unknown
        return Speaker.UNKNOWN

    def _assign_segment_id(self, lines: List[CanonicalLine]) -> None:
        """Assign segment ID to a group of lines."""
        segment_id = f"SEG_{self.segment_index:04d}"
        self.segment_index += 1

        for line in lines:
            line.segment_id = segment_id

    def execute_a3(self) -> None:
        """A3: Invariant Extraction (User-Defined Only)."""
        print("\n=== A3: Invariant Extraction ===")

        # Extract from user messages only
        user_lines = [line for line in self.canonical_lines if line.speaker == Speaker.USER]

        for line in user_lines:
            # Check each invariant pattern
            for category, patterns in self.user_invariant_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line.raw_text, re.IGNORECASE):
                        # Find exact text
                        match = re.search(pattern, line.raw_text, re.IGNORECASE)
                        if match:
                            exact_text = match.group(0)

                            # Check if similar invariant already exists
                            existing = self._find_similar_invariant(exact_text)
                            if existing:
                                existing.line_ids.append(line.line_id)
                            else:
                                # Create new invariant
                                invariant_id = f"INV_{self.invariant_index:04d}"
                                invariant = Invariant(
                                    id=invariant_id,
                                    source="chat",
                                    literal_text=exact_text,
                                    line_ids=[line.line_id],
                                    category=category,
                                )
                                self.invariants.append(invariant)
                                self.invariant_index += 1

        # Remove duplicate line IDs
        for inv in self.invariants:
            inv.line_ids = list(set(inv.line_ids))

        # Save invariants
        output_dir = self.repo_root / "analysis" / "full_system"

        invariant_data = {
            "total_invariants": len(self.invariants),
            "invariants": [
                {
                    "id": inv.id,
                    "source": inv.source,
                    "literal_text": inv.literal_text,
                    "line_ids": inv.line_ids,
                    "category": inv.category,
                }
                for inv in self.invariants
            ],
        }

        with open(output_dir / "a3_invariants.json", "w", encoding="utf-8") as f:
            json.dump(invariant_data, f, indent=2, ensure_ascii=False)

        # Also save as CSV
        with open(output_dir / "a3_invariants.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "source", "literal_text", "category", "line_ids"])
            for inv in self.invariants:
                line_ids_str = ";".join(inv.line_ids)
                writer.writerow([inv.id, inv.source, inv.literal_text, inv.category, line_ids_str])

        print(f"A3 complete. Extracted {len(self.invariants)} invariants")
        print(f"Saved to {output_dir / 'a3_invariants.json'} and {

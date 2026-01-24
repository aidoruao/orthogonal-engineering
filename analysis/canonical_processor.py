#!/usr/bin/env python3
"""
Canonical Chat Processor for Orthogonal Engineering
===================================================

Implements A2-A3 atomic instructions:
- A2: Canonicalization Pass with immutable IDs
- A3: Invariant Extraction (User-Defined Only)

Key Principles:
1. Preserve original spelling, casing, punctuation
2. Assign immutable IDs: CHAT_<index>_<line>
3. Extract only explicitly stated invariants
4. No summarization, no inference, no interpretation

Author: Orthogonal Engineering System
Date: 2026-01-23
Version: 1.0.0
"""

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class CanonicalLine:
    """Canonical representation of a single line."""

    line_id: str  # CHAT_<index>_<line>
    raw_text: str  # Original text, verbatim
    speaker: str  # "user" or "assistant"
    line_number: int  # Original line number in file


@dataclass
class Invariant:
    """User-defined invariant extracted from chat."""

    id: str  # INV_<index>
    source: str  # "chat" or "repo"
    literal_text: str  # Exact text from source
    line_ids: List[str]  # CHAT IDs where invariant appears
    category: Optional[str] = None  # Optional: workload, compliance, etc.


@dataclass
class ChatSegment:
    """A segment of chat with speaker turns."""

    segment_id: str  # SEG_<index>
    start_line_id: str
    end_line_id: str
    speaker: str
    content: str  # Concatenated but unmodified


class CanonicalProcessor:
    """Main processor for canonical chat analysis."""

    def __init__(self, chat_export_path: str):
        self.chat_export_path = Path(chat_export_path)
        self.canonical_lines: List[CanonicalLine] = []
        self.invariants: List[Invariant] = []
        self.segments: List[ChatSegment] = []

        # Speaker detection patterns
        self.user_patterns = [
            r"^You said:",
            r"^User:",
            r"^Tiny:",
            r"^[A-Z][a-z]+ said:",  # Name followed by "said:"
        ]

        self.assistant_patterns = [
            r"^ChatGPT said:",
            r"^Assistant:",
            r"^AI:",
        ]

        # Pre-defined invariant patterns from user specification
        # These are ONLY for invariants explicitly stated by user
        self.invariant_patterns = {
            "workload": [
                r"5\.75\s*hour",
                r"5\.75\s*hr",
                r"part.?time\s*(?:maid|janitor)",
                r"part.?time\s*work",
            ],
            "room_counts": [
                r"12\s*classrooms?",
                r"12\s*bathrooms?",
                r"plus\s*2\s*bathrooms?",
                r"3\s*more\s*rooms",
                r"3\s*more\s*bathrooms?",
                r"4\s*hallways?",
                r"15\s*bathrooms?\s*total",  # ChatGPT's calculation
            ],
            "time_metrics": [
                r"2\s*hour\s*break",
                r"2-4\s*hours?\s*overtime",
                r"almost\s*everyday",
                r"daily",
            ],
            "compliance_traits": [
                r"highly\s*compliant",
                r"non.?disagreeable",
                r"not\s*disagreeable",
            ],
            "selection_request": [
                r"deconstruction\s*of.*selection\s*mechanism",
                r"selection\s*mechanism",
                r"not\s*smear",
            ],
            "epistemic_observation": [
                r"boundaries.*imposed.*AI.*cause.*epistemic\s*breach",
                r"epistemic\s*breach",
            ],
        }

    def load_chat_export(self) -> List[str]:
        """Load chat export verbatim."""
        with open(self.chat_export_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.rstrip("\n") for line in f]
        return lines

    def classify_speaker(self, line: str) -> Tuple[str, str]:
        """Classify speaker and extract content."""
        line_stripped = line.strip()

        # Check for user patterns
        for pattern in self.user_patterns:
            match = re.match(pattern, line_stripped, re.IGNORECASE)
            if match:
                # Extract content after the speaker marker
                content = line_stripped[match.end() :].strip()
                return "user", content if content else line_stripped

        # Check for assistant patterns
        for pattern in self.assistant_patterns:
            match = re.match(pattern, line_stripped, re.IGNORECASE)
            if match:
                content = line_stripped[match.end() :].strip()
                return "assistant", content if content else line_stripped

        # If no pattern matches, check context
        # Lines starting with indentation or continuation
        if line_stripped and not line_stripped[0].isalnum():
            return "continuation", line_stripped

        # Default to unknown
        return "unknown", line_stripped

    def create_canonical_lines(self, lines: List[str]) -> None:
        """Create canonical lines with immutable IDs."""
        line_index = 0
        segment_index = 0
        current_speaker = None
        current_segment_lines = []

        for i, raw_line in enumerate(lines):
            if not raw_line.strip():
                # Empty line - end current segment if exists
                if current_segment_lines and current_speaker:
                    self._finalize_segment(
                        current_speaker, current_segment_lines, segment_index
                    )
                    segment_index += 1
                    current_segment_lines = []
                    current_speaker = None
                continue

            speaker, content = self.classify_speaker(raw_line)

            # Create canonical line
            line_id = f"CHAT_{i:06d}"
            canonical_line = CanonicalLine(
                line_id=line_id, raw_text=raw_line, speaker=speaker, line_number=i
            )
            self.canonical_lines.append(canonical_line)

            # Handle segment grouping
            if speaker in ["user", "assistant"]:
                if current_speaker != speaker and current_segment_lines:
                    # Speaker changed, finalize previous segment
                    self._finalize_segment(
                        current_speaker, current_segment_lines, segment_index
                    )
                    segment_index += 1
                    current_segment_lines = []

                current_speaker = speaker
                current_segment_lines.append(canonical_line)
            elif speaker == "continuation" and current_speaker:
                # Continuation of current segment
                current_segment_lines.append(canonical_line)
            else:
                # Unknown line, finalize current segment if exists
                if current_segment_lines and current_speaker:
                    self._finalize_segment(
                        current_speaker, current_segment_lines, segment_index
                    )
                    segment_index += 1
                    current_segment_lines = []
                    current_speaker = None

        # Finalize last segment if exists
        if current_segment_lines and current_speaker:
            self._finalize_segment(
                current_speaker, current_segment_lines, segment_index
            )

    def _finalize_segment(
        self, speaker: str, lines: List[CanonicalLine], segment_index: int
    ) -> None:
        """Create a chat segment from collected lines."""
        if not lines:
            return

        segment_id = f"SEG_{segment_index:04d}"
        content = " ".join(line.raw_text.strip() for line in lines)

        segment = ChatSegment(
            segment_id=segment_id,
            start_line_id=lines[0].line_id,
            end_line_id=lines[-1].line_id,
            speaker=speaker,
            content=content,
        )
        self.segments.append(segment)

    def extract_invariants(self) -> None:
        """Extract ONLY explicitly stated invariants from user messages."""
        invariant_index = 0

        # First, collect all user segments
        user_segments = [seg for seg in self.segments if seg.speaker == "user"]

        for segment in user_segments:
            content_lower = segment.content.lower()
            line_ids = self._get_line_ids_for_segment(segment)

            # Check each invariant pattern category
            for category, patterns in self.invariant_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content_lower, re.IGNORECASE):
                        # Find the exact text in the original content
                        exact_text = self._find_exact_invariant_text(
                            segment.content, pattern
                        )

                        if exact_text:
                            invariant_id = f"INV_{invariant_index:04d}"
                            invariant = Invariant(
                                id=invariant_id,
                                source="chat",
                                literal_text=exact_text,
                                line_ids=line_ids,
                                category=category,
                            )
                            self.invariants.append(invariant)
                            invariant_index += 1

        # Remove duplicates (same literal text)
        self._deduplicate_invariants()

    def _get_line_ids_for_segment(self, segment: ChatSegment) -> List[str]:
        """Get all line IDs for a segment."""
        start_num = int(segment.start_line_id.split("_")[1])
        end_num = int(segment.end_line_id.split("_")[1])
        return [f"CHAT_{i:06d}" for i in range(start_num, end_num + 1)]

    def _find_exact_invariant_text(self, content: str, pattern: str) -> Optional[str]:
        """Find exact invariant text in content (preserving original casing)."""
        # Use regex to find the pattern
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(0)
        return None

    def _deduplicate_invariants(self) -> None:
        """Remove duplicate invariants (same literal text)."""
        seen_texts = set()
        unique_invariants = []

        for inv in self.invariants:
            if inv.literal_text not in seen_texts:
                seen_texts.add(inv.literal_text)
                unique_invariants.append(inv)

        self.invariants = unique_invariants

    def generate_canonical_output(self) -> Dict:
        """Generate canonical output for A2-A3."""
        return {
            "metadata": {
                "source_file": str(self.chat_export_path),
                "total_lines": len(self.canonical_lines),
                "total_segments": len(self.segments),
                "total_invariants": len(self.invariants),
                "processing_timestamp": "2026-01-23T00:00:00Z",
            },
            "canonical_lines": [asdict(line) for line in self.canonical_lines],
            "chat_segments": [asdict(seg) for seg in self.segments],
            "invariants": [asdict(inv) for inv in self.invariants],
        }

    def save_outputs(self, output_dir: str) -> None:
        """Save all outputs to directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 1. Save canonical lines
        canonical_data = self.generate_canonical_output()

        with open(output_path / "canonical_lines.json", "w", encoding="utf-8") as f:
            json.dump(canonical_data, f, indent=2, ensure_ascii=False)

        # 2. Save invariants as CSV
        self._save_invariants_csv(output_path / "invariants.csv")

        # 3. Save segments as readable text
        self._save_segments_text(output_path / "segments.txt")

        # 4. Save line mapping
        self._save_line_mapping(output_path / "line_mapping.csv")

    def _save_invariants_csv(self, csv_path: Path) -> None:
        """Save invariants as CSV file."""
        import csv

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "source", "literal_text", "category", "line_ids"])

            for inv in self.invariants:
                line_ids_str = ";".join(inv.line_ids)
                writer.writerow(
                    [
                        inv.id,
                        inv.source,
                        inv.literal_text,
                        inv.category or "",
                        line_ids_str,
                    ]
                )

    def _save_segments_text(self, txt_path: Path) -> None:
        """Save segments as readable text file."""
        with open(txt_path, "w", encoding="utf-8") as f:
            for seg in self.segments:
                f.write(f"=== {seg.segment_id} ({seg.speaker}) ===\n")
                f.write(f"Lines: {seg.start_line_id} to {seg.end_line_id}\n")
                f.write(f"Content: {seg.content}\n")
                f.write("\n" + "=" * 50 + "\n\n")

    def _save_line_mapping(self, csv_path: Path) -> None:
        """Save line mapping as CSV."""
        import csv

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["line_id", "line_number", "speaker", "raw_text_preview"])

            for line in self.canonical_lines:
                preview = (
                    line.raw_text[:100] + "..."
                    if len(line.raw_text) > 100
                    else line.raw_text
                )
                writer.writerow([line.line_id, line.line_number, line.speaker, preview])

    def process(self, output_dir: str = "analysis/canonical_output") -> Dict:
        """Main processing pipeline."""
        print("Loading chat export...")
        lines = self.load_chat_export()

        print("Creating canonical lines...")
        self.create_canonical_lines(lines)

        print("Extracting invariants...")
        self.extract_invariants()

        print("Saving outputs...")
        self.save_outputs(output_dir)

        print(f"Processing complete:")
        print(f"  - Canonical lines: {len(self.canonical_lines)}")
        print(f"  - Chat segments: {len(self.segments)}")
        print(f"  - Invariants extracted: {len(self.invariants)}")

        return self.generate_canonical_output()


def main():
    """Command-line entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python canonical_processor.py <chat_export_path> [output_dir]")
        sys.exit(1)

    chat_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis/canonical_output"

    processor = CanonicalProcessor(chat_path)
    processor.process(output_dir)


if __name__ == "__main__":
    main()

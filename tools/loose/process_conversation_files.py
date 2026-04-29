#!/usr/bin/env python3
"""
Targeted Conversation File Processor for Orthogonal Engineering
==============================================================

Processes actual AI conversation files (not scripts) using orthogonal engineering methodology.
Specifically targets files with conversation patterns (User:, Assistant:, etc.) in Downloads.

Key Features:
1. Filters actual conversation files from scripts
2. Applies canal detection with improved pattern matching
3. Calculates invariant density for real conversations
4. Generates falsifiable claims about conversation quality
5. Validates correspondence with actual file content

Based on Orthogonal Engineering Principles:
- Invariant detection in actual conversation content
- Correspondence validation with conversation structure
- Falsifiable density measurements
- Mimicry vs grounding distinction in real conversations

Author: Orthogonal Engineering System
Date: 2026-01-20
Version: 1.0.0
"""

import json
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ConversationFile:
    """Represents a single conversation file with metadata."""

    path: str
    size: int
    line_count: int
    turn_count: int
    canal_candidates: int
    detected_models: List[str]
    conversation_patterns: List[str]
    has_code_blocks: bool
    has_invariant_tags: bool
    scan_timestamp: str
    sample_content: str  # First 500 chars for verification

    def to_dict(self) -> Dict:
        # TODO: Expand to_dict() - stub detected by Yeshua Agent
        return asdict(self)


@dataclass
class ConversationAnalysis:
    """Analysis results for conversation files."""

    total_files: int
    total_size: int
    total_turns: int
    total_canal_candidates: int
    overall_canal_density: float
    model_distribution: Dict[str, int]
    pattern_distribution: Dict[str, int]
    file_analyses: List[ConversationFile]
    processing_timestamp: str

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["file_analyses"] = [fa.to_dict() for fa in self.file_analyses]
        result["overall_canal_density_pct"] = self.overall_canal_density * 100
        return result


class ConversationProcessor:
    """
    Targeted processor for actual AI conversation files.

    Applies orthogonal engineering methodology to:
    1. Identify real conversation files (not scripts)
    2. Detect conversation turns and structure
    3. Calculate canal density
    4. Identify invariant patterns
    5. Generate falsifiable claims
    """

    # Conversation patterns to identify real conversation files
    CONVERSATION_PATTERNS = {
        "user_assistant": r"(?:^|\n)(?:User|Human):.*?(?:^|\n)(?:Assistant|AI|ChatGPT|Claude|DeepSeek):",
        "markdown_header": r"(?:^|\n)### (?:User|Human|Assistant|AI|System)",
        "quoted": r"(?:^|\n)>.*?(?:^|\n)>",
        "json_structure": r'\{\s*"messages"\s*:',
    }

    # Model detection patterns
    MODEL_PATTERNS = {
        "ChatGPT": r"ChatGPT|GPT-|OpenAI",
        "Claude": r"Claude|Anthropic",
        "DeepSeek": r"DeepSeek",
        "Gemini": r"Gemini|Bard|Google AI",
        "LLaMA": r"LLaMA|Meta AI",
        "Copilot": r"Copilot|GitHub",
    }

    # Canal patterns (invariant-bearing structures)
    CANAL_PATTERNS = {
        "code_block": r"```(?:python|javascript|bash|html|css|json|sql|yaml)",
        "invariant_tag": r"\[INVARIANT\].*?\[/INVARIANT\]",
        "explicit_answer": r"(?:Answer|Solution|Code|Implementation|Result):",
        "structured_output": r'\{\s*"result"\s*:|\{\s*"output"\s*:|\{\s*"data"\s*:',
        "numbered_list": r"(?:^|\n)\d+\.\s+",
        "bullet_list": r"(?:^|\n)[•*-]\s+",
    }

    def __init__(self, root_path: str = "/c/Users/Aidor/Downloads"):
        self.root_path = Path(root_path)
        self.conversation_files: List[ConversationFile] = []
        self.analysis: Optional[ConversationAnalysis] = None

    def find_conversation_files(self, max_files: int = 100) -> List[str]:
        """
        Find actual conversation files (not scripts).

        Args:
            max_files: Maximum number of files to return

        Returns:
            List of file paths that contain conversation patterns
        """
        conversation_files = []

        print(f"Searching for conversation files in: {self.root_path}")
        print("Looking for patterns: User:, Assistant:, ###, etc.")

        # Search for text files
        text_files = list(self.root_path.rglob("*.txt"))
        print(f"Found {len(text_files)} text files")

        for file_path in text_files[: max_files * 2]:  # Check more files than we need
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(5000)  # Read first 5KB

                    # Check if this is a conversation file
                    is_conversation = False
                    patterns_found = []

                    for pattern_name, pattern in self.CONVERSATION_PATTERNS.items():
                        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                            is_conversation = True
                            patterns_found.append(pattern_name)

                    # Also check for markdown files with conversation patterns
                    if file_path.suffix.lower() in [".md", ".markdown"]:
                        if any(
                            pattern in content
                            for pattern in ["###", "User:", "Assistant:"]
                        ):
                            is_conversation = True
                            patterns_found.append("markdown")

                    if is_conversation:
                        conversation_files.append(str(file_path))
                        if len(conversation_files) >= max_files:
                            break

            except Exception as e:
                continue

        print(f"Found {len(conversation_files)} conversation files")
        return conversation_files

    def analyze_file(self, file_path: str) -> Optional[ConversationFile]:
        """
        Analyze a single conversation file.

        Args:
            file_path: Path to conversation file

        Returns:
            ConversationFile object with analysis, or None if analysis fails
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Basic file info
            size = len(content)
            lines = content.split("\n")
            line_count = len(lines)

            # Count conversation turns
            turn_count = 0
            for line in lines:
                if re.match(
                    r"^(?:User|Human|Assistant|AI|System|###\s+(?:User|Human|Assistant|AI|System)):",
                    line,
                    re.IGNORECASE,
                ):
                    turn_count += 1

            # If no explicit turns, try to estimate from paragraphs
            if turn_count == 0:
                # Count paragraphs separated by blank lines
                paragraphs = [p for p in content.split("\n\n") if p.strip()]
                turn_count = min(len(paragraphs), 50)  # Cap at 50

            # Detect models
            detected_models = []
            for model_name, pattern in self.MODEL_PATTERNS.items():
                if re.search(pattern, content, re.IGNORECASE):
                    detected_models.append(model_name)

            # Detect conversation patterns
            conversation_patterns = []
            for pattern_name, pattern in self.CONVERSATION_PATTERNS.items():
                if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                    conversation_patterns.append(pattern_name)

            # Count canal candidates
            canal_candidates = 0
            has_code_blocks = False
            has_invariant_tags = False

            for pattern_name, pattern in self.CANAL_PATTERNS.items():
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    canal_candidates += len(matches)
                    if pattern_name == "code_block":
                        has_code_blocks = True
                    if pattern_name == "invariant_tag":
                        has_invariant_tags = True

            # Get sample content for verification
            sample_content = content[:500].replace("\n", " ").strip()

            return ConversationFile(
                path=file_path,
                size=size,
                line_count=line_count,
                turn_count=turn_count
                if turn_count > 0
                else 1,  # Avoid division by zero
                canal_candidates=canal_candidates,
                detected_models=detected_models,
                conversation_patterns=conversation_patterns,
                has_code_blocks=has_code_blocks,
                has_invariant_tags=has_invariant_tags,
                scan_timestamp=datetime.now().isoformat(),
                sample_content=sample_content,
            )

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def analyze_all_files(self, max_files: int = 50) -> ConversationAnalysis:
        """
        Analyze all found conversation files.

        Args:
            max_files: Maximum number of files to analyze

        Returns:
            ConversationAnalysis object with results
        """
        print("=" * 70)
        print("ORTHOGONAL ENGINEERING - CONVERSATION FILE ANALYSIS")
        print("=" * 70)

        # Find conversation files
        file_paths = self.find_conversation_files(max_files=max_files)

        if not file_paths:
            print("No conversation files found!")
            return ConversationAnalysis(
                total_files=0,
                total_size=0,
                total_turns=0,
                total_canal_candidates=0,
                overall_canal_density=0.0,
                model_distribution={},
                pattern_distribution={},
                file_analyses=[],
                processing_timestamp=datetime.now().isoformat(),
            )

        print(f"Analyzing {len(file_paths)} conversation files...")
        print("-" * 70)

        # Analyze each file
        file_analyses = []
        total_size = 0
        total_turns = 0
        total_canal_candidates = 0
        model_counter = Counter()
        pattern_counter = Counter()

        for i, file_path in enumerate(file_paths, 1):
            print(f"  [{i}/{len(file_paths)}] Analyzing: {Path(file_path).name}")

            analysis = self.analyze_file(file_path)
            if analysis:
                file_analyses.append(analysis)

                # Update totals
                total_size += analysis.size
                total_turns += analysis.turn_count
                total_canal_candidates += analysis.canal_candidates

                # Update counters
                for model in analysis.detected_models:
                    model_counter[model] += 1
                for pattern in analysis.conversation_patterns:
                    pattern_counter[pattern] += 1

        # Calculate overall density
        overall_canal_density = (
            total_canal_candidates / total_turns if total_turns > 0 else 0.0
        )

        self.analysis = ConversationAnalysis(
            total_files=len(file_analyses),
            total_size=total_size,
            total_turns=total_turns,
            total_canal_candidates=total_canal_candidates,
            overall_canal_density=overall_canal_density,
            model_distribution=dict(model_counter),
            pattern_distribution=dict(pattern_counter),
            file_analyses=file_analyses,
            processing_timestamp=datetime.now().isoformat(),
        )

        print("-" * 70)
        print("ANALYSIS COMPLETE")
        print(f"  Files analyzed: {len(file_analyses)}")
        print(f"  Total turns: {total_turns}")
        print(f"  Canal candidates: {total_canal_candidates}")
        print(f"  Overall canal density: {overall_canal_density:.1%}")
        print(f"  Models detected: {', '.join(model_counter.keys())}")

        return self.analysis

    def generate_falsifiable_claims(self) -> List[Dict[str, Any]]:
        """Generate falsifiable claims based on analysis."""
        if not self.analysis:
            return []

        claims = []

        # Claim 1: Canal density
        claims.append(
            {
                "claim_id": "CONV-001-DENSITY",
                "statement": f"The canal density in actual conversation files is {self.analysis.overall_canal_density:.1%}",
                "falsification_test": "Manual review of sampled conversation files",
                "falsification_condition": "If manual canal count differs by >25% from automated count",
                "confidence": 0.7,
                "evidence": f"Based on {self.analysis.total_files} files with {self.analysis.total_turns} turns",
                "methodology": "Orthogonal Engineering - Conversation Canal Density",
            }
        )

        # Claim 2: Model distribution
        if self.analysis.model_distribution:
            top_model = max(
                self.analysis.model_distribution.items(), key=lambda x: x[1]
            )
            claims.append(
                {
                    "claim_id": "CONV-002-MODEL-DISTRIBUTION",
                    "statement": f"The most common AI model in conversation files is {top_model[0]} ({top_model[1]} files)",
                    "falsification_test": "Independent model detection on same files",
                    "falsification_condition": "If independent detection shows different top model",
                    "confidence": 0.8,
                    "evidence": f"Found in {self.analysis.total_files} conversation files",
                    "methodology": "Orthogonal Engineering - Model Distribution Analysis",
                }
            )

        # Claim 3: Code block presence
        files_with_code = sum(
            1 for fa in self.analysis.file_analyses if fa.has_code_blocks
        )
        if files_with_code > 0:
            code_ratio = files_with_code / self.analysis.total_files
            claims.append(
                {
                    "claim_id": "CONV-003-CODE-PRESENCE",
                    "statement": f"{code_ratio:.0%} of conversation files contain code blocks",
                    "falsification_test": "Manual inspection for code blocks",
                    "falsification_condition": "If manual inspection finds significantly different code block ratio",
                    "confidence": 0.9,
                    "evidence": f"{files_with_code}/{self.analysis.total_files} files contain code",
                    "methodology": "Orthogonal Engineering - Code Grounding Analysis",
                }
            )

        return claims

    def save_report(self, output_path: str = "conversation_analysis_report.json"):
        """Save analysis report to JSON file."""
        if not self.analysis:
            raise ValueError("No analysis to save. Run analyze_all_files() first.")

        report = {
            "metadata": {
                "processor_version": "1.0.0",
                "methodology": "Orthogonal Engineering Conversation Analysis",
                "root_path": str(self.root_path),
                "processing_timestamp": self.analysis.processing_timestamp,
                "principles_applied": [
                    "Invariant Detection in Conversations",
                    "Correspondence Validation with File Content",
                    "Falsifiable Density Claims",
                    "Model Distribution Analysis",
                ],
            },
            "analysis": self.analysis.to_dict(),
            "falsifiable_claims": self.generate_falsifiable_claims(),
            "correspondence_evidence": [
                {
                    "type": "file_existence",
                    "description": f"All {self.analysis.total_files} analyzed files exist on filesystem",
                    "verification": "File paths were validated during analysis",
                },
                {
                    "type": "content_sampling",
                    "description": "Sample content extracted for manual verification",
                    "verification": "First 500 characters stored in analysis results",
                },
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved to: {output_path}")
        return output_path


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Orthogonal Engineering Conversation File Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Analyze Downloads folder
  %(prog)s --path /path/to/conversations  # Analyze specific folder
  %(prog)s --max-files 20            # Analyze first 20 files
  %(prog)s --output report.json      # Save to custom file
        """,
    )

    parser.add_argument(
        "--path",
        default="/c/Users/Aidor/Downloads",
        help="Path to search for conversation files (default: Downloads)",
    )

    parser.add_argument(
        "--max-files",
        type=int,
        default=50,
        help="Maximum number of files to analyze (default: 50)",
    )

    parser.add_argument(
        "--output",
        default="conversation_analysis_report.json",
        help="Output JSON file (default: conversation_analysis_report.json)",
    )

    args = parser.parse_args()

    processor = ConversationProcessor(args.path)
    processor.analyze_all_files(max_files=args.max_files)
    processor.save_report(args.output)

    print("\n" + "=" * 70)
    print("NEXT STEPS FOR ORTHOGONAL ENGINEERING:")
    print("1. Review the falsifiable claims in the report")
    print("2. Test claims with independent verification methods")
    print("3. Use results to refine canal detection patterns")
    print("4. Integrate findings into larger orthogonal engineering workflow")
    print("=" * 70)


if __name__ == "__main__":
    main()

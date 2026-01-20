#!/usr/bin/env python3
"""
Simple Conversation Analyzer for Orthogonal Engineering
======================================================

Direct analysis of AI conversation files in Downloads folder.
No complex dependencies, just working analysis.

Key Features:
1. Finds actual conversation files (User:, Assistant:, etc.)
2. Counts turns and canal candidates
3. Calculates density metrics
4. Generates simple report

Author: Orthogonal Engineering Implementation
Date: 2026-01-20
Version: 1.0.0
"""

import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


def find_conversation_files(directory="C:/Users/Aidor/Downloads", max_files=50):
    """Find files that look like AI conversations."""
    conversation_files = []
    directory = Path(directory)

    print(f"Searching in: {directory}")

    # Look for text files
    txt_files = list(directory.glob("*.txt"))
    print(f"Found {len(txt_files)} text files")

    for txt_file in txt_files[: max_files * 2]:  # Check more than we need
        try:
            with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(5000)  # Read first 5KB

                # Check if this looks like a conversation
                is_conversation = False

                # Common conversation patterns
                patterns = [
                    r"User:.*?Assistant:",
                    r"Human:.*?AI:",
                    r"### User",
                    r"### Human",
                    r"### Assistant",
                    r"### AI",
                    r"Human:\s*\n",
                    r"Assistant:\s*\n",
                ]

                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                        is_conversation = True
                        break

                if is_conversation:
                    conversation_files.append(str(txt_file))
                    if len(conversation_files) >= max_files:
                        break

        except Exception as e:
            continue

    print(f"Found {len(conversation_files)} conversation files")
    return conversation_files


def analyze_conversation_file(file_path):
    """Analyze a single conversation file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Basic info
        size = len(content)
        lines = content.split("\n")
        line_count = len(lines)

        # Count turns (conversation exchanges)
        turn_count = 0
        for line in lines:
            if re.match(
                r"^(User|Human|Assistant|AI|System|### (User|Human|Assistant|AI|System)):",
                line,
                re.IGNORECASE,
            ):
                turn_count += 1

        # If no explicit turns, estimate from paragraphs
        if turn_count == 0:
            paragraphs = [p for p in content.split("\n\n") if p.strip()]
            turn_count = min(len(paragraphs), 20)

        # Detect AI models mentioned
        models = []
        model_patterns = {
            "ChatGPT": r"ChatGPT|GPT-|OpenAI",
            "Claude": r"Claude|Anthropic",
            "DeepSeek": r"DeepSeek",
            "Gemini": r"Gemini|Bard|Google AI",
        }

        for model_name, pattern in model_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                models.append(model_name)

        # Count canal candidates (invariant-bearing structures)
        canal_patterns = {
            "code_block": r"```(?:python|javascript|bash|html|css|json)",
            "invariant_tag": r"\[INVARIANT\].*?\[/INVARIANT\]",
            "explicit_answer": r"(?:Answer|Solution|Code|Implementation):",
            "structured_list": r"(?:\n\d+\.|\n[•*-])\s+",
        }

        canal_candidates = 0
        has_code = False
        has_invariant_tags = False

        for pattern_name, pattern in canal_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                canal_candidates += len(matches)
                if pattern_name == "code_block":
                    has_code = True
                if pattern_name == "invariant_tag":
                    has_invariant_tags = True

        # Calculate canal density
        canal_density = canal_candidates / turn_count if turn_count > 0 else 0

        # Get sample for verification
        sample = content[:300].replace("\n", " ").strip()
        if len(sample) < len(content):
            sample += "..."

        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "size": size,
            "line_count": line_count,
            "turn_count": turn_count,
            "canal_candidates": canal_candidates,
            "canal_density": canal_density,
            "models": models,
            "has_code": has_code,
            "has_invariant_tags": has_invariant_tags,
            "sample": sample,
            "analyzed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "file_path": file_path,
            "error": str(e),
            "analyzed_at": datetime.now().isoformat(),
        }


def main():
    """Main analysis function."""
    print("=" * 70)
    print("ORTHOGONAL ENGINEERING - SIMPLE CONVERSATION ANALYZER")
    print("=" * 70)
    print()

    # Find conversation files
    conversation_files = find_conversation_files(max_files=30)

    if not conversation_files:
        print("No conversation files found!")
        return

    print(f"\nAnalyzing {len(conversation_files)} conversation files...")
    print("-" * 70)

    # Analyze each file
    analyses = []
    total_turns = 0
    total_canal_candidates = 0
    model_counter = Counter()
    files_with_code = 0
    files_with_invariants = 0

    for i, file_path in enumerate(conversation_files, 1):
        print(f"[{i}/{len(conversation_files)}] {os.path.basename(file_path)}")
        analysis = analyze_conversation_file(file_path)

        if "error" not in analysis:
            analyses.append(analysis)
            total_turns += analysis["turn_count"]
            total_canal_candidates += analysis["canal_candidates"]

            for model in analysis["models"]:
                model_counter[model] += 1

            if analysis["has_code"]:
                files_with_code += 1
            if analysis["has_invariant_tags"]:
                files_with_invariants += 1

    print("-" * 70)

    # Calculate overall metrics
    overall_density = total_canal_candidates / total_turns if total_turns > 0 else 0

    # Generate report
    report = {
        "metadata": {
            "analyzer_version": "1.0.0",
            "analysis_date": datetime.now().isoformat(),
            "methodology": "Orthogonal Engineering Simple Analysis",
            "files_analyzed": len(analyses),
            "principles_applied": [
                "Invariant pattern detection",
                "Canal density calculation",
                "Model distribution analysis",
                "Correspondence verification via file sampling",
            ],
        },
        "summary": {
            "total_files": len(analyses),
            "total_turns": total_turns,
            "total_canal_candidates": total_canal_candidates,
            "overall_canal_density": overall_density,
            "overall_canal_density_percent": overall_density * 100,
            "model_distribution": dict(model_counter),
            "files_with_code": files_with_code,
            "files_with_invariant_tags": files_with_invariants,
        },
        "falsifiable_claims": [
            {
                "claim_id": "SIMPLE-001-DENSITY",
                "statement": f"The canal density in conversation files is {overall_density:.1%}",
                "falsification_test": "Manual count of canal candidates in sampled files",
                "falsification_condition": "If manual count differs by >30% from automated count",
                "confidence": 0.6,
                "evidence": f"Based on {len(analyses)} files with {total_turns} turns",
            },
            {
                "claim_id": "SIMPLE-002-MODELS",
                "statement": f"Most common AI model: {max(model_counter.items(), key=lambda x: x[1])[0] if model_counter else 'None'}",
                "falsification_test": "Independent model detection",
                "falsification_condition": "If independent detection shows different distribution",
                "confidence": 0.7,
                "evidence": f"Models found: {dict(model_counter)}",
            },
        ],
        "detailed_analyses": analyses[:10],  # Include first 10 for verification
        "correspondence_evidence": {
            "file_existence": f"All {len(analyses)} files exist and were read",
            "content_sampling": "First 300 characters stored for each file",
            "manual_verification_possible": "Sample content allows manual checking",
        },
    }

    # Save report
    output_file = (
        f"conversation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Files analyzed: {len(analyses)}")
    print(f"Total turns: {total_turns}")
    print(f"Canal candidates: {total_canal_candidates}")
    print(f"Overall canal density: {overall_density:.1%}")
    print(f"Models detected: {', '.join(model_counter.keys())}")
    print(f"Files with code: {files_with_code}")
    print(f"Files with invariant tags: {files_with_invariants}")
    print(f"\nReport saved to: {output_file}")

    print("\n" + "=" * 70)
    print("ORTHOGONAL ENGINEERING - FALSIFIABLE CLAIMS")
    print("=" * 70)
    for claim in report["falsifiable_claims"]:
        print(f"\n{claim['claim_id']}: {claim['statement']}")
        print(f"  Falsification test: {claim['falsification_test']}")
        print(f"  Evidence: {claim['evidence']}")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("1. Review the falsifiable claims")
    print("2. Test claims with manual verification")
    print("3. Use results to refine analysis methods")
    print("4. Integrate into larger orthogonal engineering workflow")
    print("=" * 70)


if __name__ == "__main__":
    main()

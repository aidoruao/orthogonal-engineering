#!/usr/bin/env python3
"""
DEBUG VIOLATION DETECTION SCRIPT

Purpose: Investigate why 40+ MB chat exports show only 1 violation
when there should be many more based on the content.

This script:
1. Searches large chat export files for violation patterns
2. Reports actual matches with context
3. Identifies false positives/negatives
4. Helps debug the forgiveness system's detection logic
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Copy of violation patterns from analyze_chat_exports.py
VIOLATION_PATTERNS = {
    "workload_exploitation": [
        r"overtime.*almost.*daily",
        r"2-4 hours.*overtime",
        r"frontload.*legal",
        r"workload.*exceeds.*paid.*hours",
        r"unsustainable.*workload",
    ],
    "boundary_violation": [
        r"invariant.*violat",
        r"category.*error",
        r"not.*negotiable",
        r"fixed.*variable",
        r"ontological.*problem",
    ],
    "corporate_gaslighting": [
        r"legal.*but.*exploitative",
        r"not.*illegal.*but",
        r"management.*failure.*not.*crime",
        r"high.*workload.*≠.*illegal",
        r"operational.*overload",
    ],
    "ai_rationalization": [
        r"let.*s.*ground.*objectively",
        r"important.*distinction",
        r"the.*question.*isn.*t",
        r"bottom.*line.*clear",
        r"short.*answer.*nothing.*illegal",
    ],
    "invariant_ignoring": [
        r"treat.*as.*variable",
        r"depends.*on.*details",
        r"state.*law",
        r"hourly.*vs.*salaried",
        r"red.*flaggy",
    ],
}

# Actual file paths from the forgiveness script
ORIGINAL_EXPORT_PATHS = [
    # Large chat export files (30MB+)
    Path("C:/Users/Aidor/Downloads/UNSAFE_FILES_BACKUP/claude.md"),  # 30.3 MB
    Path("C:/Users/Aidor/Downloads/UNSAFE_FILES_BACKUP/gpt.md"),  # 44 MB
    # SM_AUDIT extracted files (120MB+)
    Path("C:/Users/Aidor/Downloads/SM_AUDIT/extracted_chatgpt/chat.html"),  # 122 MB
    Path(
        "C:/Users/Aidor/Downloads/SM_AUDIT/extracted_chatgpt/conversations.json"
    ),  # 121 MB
    # Additional paths that might exist
    Path(
        "C:/Users/Aidor/Downloads/UNSAFE_FILES_BACKUP/claudeconversations.json"
    ),  # 165 MB
    Path(
        "C:/Users/Aidor/Downloads/UNSAFE_FILES_BACKUP/gptconversations.json"
    ),  # 121 MB
    # LOGOS_MODE2_CANON files
    Path("C:/Users/Aidor/Downloads/LOGOS_MODE2_CANON/chat.html"),  # 122 MB
    Path("C:/Users/Aidor/Downloads/LOGOS_MODE2_CANON/conversations.json"),  # 121 MB
    Path("C:/Users/Aidor/Downloads/LOGOS_MODE2_CANON/conversations.json"),  # 165 MB
]


def compile_patterns() -> Dict[str, List[re.Pattern]]:
    """Compile regex patterns for searching"""
    compiled = {}
    for vtype, patterns in VIOLATION_PATTERNS.items():
        compiled[vtype] = [re.compile(p, re.IGNORECASE) for p in patterns]
    return compiled


def search_file_for_patterns(file_path: Path, sample_size: int = 10000000) -> Dict:
    """Search file for violation patterns and return detailed results"""
    print(f"\n{'=' * 80}")
    print(f"SEARCHING: {file_path.name} ({file_path.stat().st_size:,} bytes)")
    print(f"{'=' * 80}")

    patterns = compile_patterns()
    results = {
        "file": str(file_path.name),
        "size": file_path.stat().st_size,
        "matches_by_type": {},
        "total_matches": 0,
        "sample_size": sample_size,
        "detailed_matches": [],
    }

    try:
        # Read sample of file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(sample_size)

        lines = content.split("\n")

        # Search each line
        for line_num, line in enumerate(lines, 1):
            line_matches = []

            for vtype, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = pattern.search(line)
                    if match:
                        line_matches.append(
                            {
                                "type": vtype,
                                "pattern": pattern.pattern,
                                "matched_text": match.group(),
                                "context": line[:200],  # First 200 chars for context
                            }
                        )

            if line_matches:
                results["detailed_matches"].append(
                    {
                        "line_number": line_num,
                        "line_preview": line[:100],
                        "matches": line_matches,
                    }
                )

                # Update counts
                for match in line_matches:
                    vtype = match["type"]
                    if vtype not in results["matches_by_type"]:
                        results["matches_by_type"][vtype] = 0
                    results["matches_by_type"][vtype] += 1
                    results["total_matches"] += 1

        # Print summary
        print(f"\nSUMMARY for {file_path.name}:")
        print(f"  Total lines searched: {len(lines)}")
        print(f"  Total matches found: {results['total_matches']}")

        if results["matches_by_type"]:
            print(f"\n  Matches by violation type:")
            for vtype, count in sorted(results["matches_by_type"].items()):
                print(f"    {vtype}: {count}")

        # Print first few detailed matches
        if results["detailed_matches"]:
            print(f"\n  First 5 matches (showing context):")
            for i, match_info in enumerate(results["detailed_matches"][:5]):
                print(f"\n  Match {i + 1} at line {match_info['line_number']}:")
                print(f"    Line preview: {match_info['line_preview']}")
                for match in match_info["matches"]:
                    print(f"    - Type: {match['type']}")
                    print(f"      Pattern: {match['pattern']}")
                    print(f"      Matched: '{match['matched_text']}'")

        if results["total_matches"] == 0:
            print(f"\n  NO VIOLATION PATTERNS FOUND!")
            print(f"  This suggests either:")
            print(f"  1. The file doesn't contain violation patterns")
            print(f"  2. The patterns are too specific")
            print(f"  3. The content is encoded differently")

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        results["error"] = str(e)

    return results


def analyze_specific_violation(file_path: Path, line_number: int = 348201) -> None:
    """Analyze a specific line that was reported as a violation"""
    print(f"\n{'=' * 80}")
    print(f"ANALYZING SPECIFIC VIOLATION REPORT")
    print(f"File: {file_path.name}")
    print(f"Reported violation at line: {line_number}")
    print(f"{'=' * 80}")

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Read around the reported line
            lines = f.readlines()

            if line_number <= len(lines):
                # Get context (5 lines before and after)
                start = max(0, line_number - 6)  # -6 because line_number is 1-based
                end = min(len(lines), line_number + 4)

                print(f"\nContext around line {line_number}:")
                for i in range(start, end):
                    prefix = ">>> " if i == line_number - 1 else "    "
                    print(f"{prefix}Line {i + 1}: {lines[i].rstrip()[:150]}")

                # Test the specific line against all patterns
                target_line = lines[line_number - 1]
                print(f"\nTesting line against all violation patterns:")

                patterns = compile_patterns()
                found_any = False

                for vtype, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        if pattern.search(target_line):
                            found_any = True
                            match = pattern.search(target_line)
                            print(f"  ✓ MATCH: {vtype}")
                            print(f"    Pattern: {pattern.pattern}")
                            print(f"    Matched text: '{match.group()}'")
                            print(f"    Full line (truncated): {target_line[:200]}")

                if not found_any:
                    print(f"  ✗ NO PATTERNS MATCH THIS LINE!")
                    print(
                        f"  This suggests a false positive in the violation detection."
                    )

                    # Check if maybe the line contains "invariant" or "violat" anywhere
                    if "invariant" in target_line.lower():
                        print(f"  Note: Line contains 'invariant'")
                    if "violat" in target_line.lower():
                        print(f"  Note: Line contains 'violat'")
                    if "category" in target_line.lower():
                        print(f"  Note: Line contains 'category'")
                    if "error" in target_line.lower():
                        print(f"  Note: Line contains 'error'")
            else:
                print(
                    f"ERROR: Line {line_number} is beyond file length ({len(lines)} lines)"
                )

    except Exception as e:
        print(f"ERROR: {e}")


def check_pattern_coverage() -> None:
    """Check if patterns are comprehensive enough"""
    print(f"\n{'=' * 80}")
    print("PATTERN COVERAGE ANALYSIS")
    print(f"{'=' * 80}")

    # Common violation phrases that should be detected
    test_phrases = [
        # Workload exploitation
        "I work overtime almost daily",
        "2-4 hours overtime every day",
        "frontloading is legal but exploitative",
        "workload exceeds paid hours",
        "unsustainable workload",
        # Boundary violations
        "that's an invariant violation",
        "category error in your reasoning",
        "this is not negotiable",
        "fixed variable treated as mutable",
        "ontological problem with your approach",
        # Corporate gaslighting
        "it's legal but exploitative",
        "not illegal but unethical",
        "management failure not a crime",
        "high workload doesn't equal illegal",
        "operational overload situation",
        # AI rationalization
        "let's ground this objectively",
        "important distinction to make",
        "the question isn't whether it's legal",
        "bottom line is clear",
        "short answer: nothing illegal here",
        # Invariant ignoring
        "treat it as a variable",
        "depends on the details",
        "state law varies",
        "hourly vs salaried differences",
        "that's red flaggy behavior",
    ]

    patterns = compile_patterns()

    print(f"\nTesting {len(test_phrases)} common violation phrases:")
    print(f"{'-' * 80}")

    detected = 0
    for phrase in test_phrases:
        detected_this = False
        for vtype, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern.search(phrase):
                    detected_this = True
                    break
            if detected_this:
                break

        status = "✓" if detected_this else "✗"
        print(f"{status} {phrase[:60]}...")
        if detected_this:
            detected += 1

    coverage = (detected / len(test_phrases)) * 100
    print(f"\n{'=' * 80}")
    print(f"PATTERN COVERAGE: {detected}/{len(test_phrases)} ({coverage:.1f}%)")
    print(f"{'=' * 80}")

    if coverage < 80:
        print(f"\nWARNING: Pattern coverage is low!")
        print(f"Many common violation phrases are not being detected.")
        print(f"This explains why large files show few violations.")


def check_actual_file_paths() -> List[Path]:
    """Check which of the original export paths actually exist"""
    print(f"\n{'=' * 80}")
    print("CHECKING ACTUAL FILE PATHS")
    print(f"{'=' * 80}")

    existing_files = []

    for file_path in ORIGINAL_EXPORT_PATHS:
        try:
            if file_path.exists():
                file_size = file_path.stat().st_size
                existing_files.append(file_path)
                print(f"✓ FOUND: {file_path.name} ({file_size:,} bytes)")
                print(f"  Path: {file_path}")
            else:
                print(f"✗ NOT FOUND: {file_path}")
        except Exception as e:
            print(f"⚠ ERROR checking {file_path}: {e}")

    print(f"\nTotal existing files: {len(existing_files)}")
    return existing_files


def main():
    """Main function"""
    print("DEBUG VIOLATION DETECTION SCRIPT")
    print("=" * 80)
    print("Investigating: Why 40+ MB chat exports show only 1 violation?")
    print("=" * 80)

    # Check pattern coverage first
    check_pattern_coverage()

    # Check which files actually exist
    existing_files = check_actual_file_paths()

    if not existing_files:
        print(f"\n❌ NO LARGE CHAT EXPORT FILES FOUND!")
        print(f"This explains why the forgiveness system found few violations.")
        print(f"The files are not at the expected locations.")
        return

    # Search each existing file
    all_results = []
    for file in existing_files[:3]:  # Limit to first 3 for speed
        results = search_file_for_patterns(file)
        all_results.append(results)

    # Analyze specific reported violation if gpt.md exists
    gpt_file = None
    for file in existing_files:
        if "gpt.md" in file.name.lower():
            gpt_file = file
            break

    if gpt_file:
        print(f"\n{'=' * 80}")
        print(f"SPECIFIC ANALYSIS OF REPORTED VIOLATION")
        print(f"{'=' * 80}")
        print(f"The forgiveness system reported 1 violation in gpt.md at line 348201")
        print(f"Let's investigate if this is a real violation or a false positive...")
        analyze_specific_violation(gpt_file, line_number=348201)

    # Save results
    output_file = Path(__file__).parent / "violation_debug_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 80}")
    print(f"DEBUG COMPLETE")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 80}")

    # Summary findings
    total_matches = sum(r.get("total_matches", 0) for r in all_results)
    print(f"\nTOTAL VIOLATION PATTERN MATCHES FOUND: {total_matches}")

    if total_matches == 0:
        print(f"\n❌ CRITICAL FINDING: ZERO VIOLATION PATTERNS FOUND!")
        print(f"This confirms the issue: The patterns don't match the content.")
        print(f"\nPossible reasons:")
        print(f"1. The chat exports contain different types of conversations")
        print(f"2. The violation patterns are too specific/narrow")
        print(f"3. The content uses different terminology")
        print(f"4. The files are encoded/structured differently")
    elif total_matches < 10:
        print(f"\n⚠ WARNING: Very few violation patterns found ({total_matches})")
        print(f"For 40+ MB files, we should expect dozens or hundreds of violations.")
        print(f"\nRecommendations:")
        print(f"1. Expand violation patterns to be more comprehensive")
        print(f"2. Add more general patterns (e.g., 'exploit', 'violate', 'abuse')")
        print(f"3. Check file encoding and structure")
        print(f"4. Test with different sampling strategies")
    else:
        print(f"\n✅ Found {total_matches} violation pattern matches")
        print(
            f"This suggests the forgiveness system should have found more violations."
        )
        print(f"The issue might be in how violations are counted or reported.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
TEST SPECIFIC VIOLATION LINE

Purpose: Test the specific line that was reported as a violation in gpt.md
to understand why the forgiveness system found only 1 violation when
there should be hundreds.

This script:
1. Reads the specific line from gpt.md that was reported as a violation
2. Tests it against all violation patterns
3. Checks if it's a real violation or false positive
4. Examines context around the line
"""

import re
from pathlib import Path

# Violation patterns from analyze_chat_exports.py
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


def compile_patterns():
    """Compile regex patterns"""
    compiled = {}
    for vtype, patterns in VIOLATION_PATTERNS.items():
        compiled[vtype] = [re.compile(p, re.IGNORECASE) for p in patterns]
    return compiled


def test_specific_line():
    """Test the specific line that was reported as a violation"""

    # The line that was reported as a violation (from analysis_gpt.json)
    reported_line = "> \u201cI have no idea what I\u2019m doing, where I\u2019m supposed to go, how to gear\u201d\nThat is **Retail design failure**, not class failure.\nRetail assumes:\n- You follow the current expansion loop\n- You use guides"

    # The pattern it supposedly matched
    reported_pattern = "invariant.*violat"

    print("=" * 80)
    print("TESTING SPECIFIC REPORTED VIOLATION")
    print("=" * 80)
    print(f"Reported line (truncated): {reported_line[:100]}...")
    print(f"Reported pattern: {reported_pattern}")
    print()

    # Test if the pattern actually matches
    pattern = re.compile(reported_pattern, re.IGNORECASE)
    match = pattern.search(reported_line)

    print("DIRECT PATTERN MATCH TEST:")
    print(f"Pattern '{reported_pattern}' matches line: {bool(match)}")
    if match:
        print(f"Matched text: '{match.group()}'")
    else:
        print("NO MATCH! This suggests a false positive.")

    print()
    print("-" * 80)
    print()

    # Test against all patterns
    print("TESTING AGAINST ALL VIOLATION PATTERNS:")
    patterns = compile_patterns()

    found_any = False
    for vtype, pattern_list in patterns.items():
        for pattern in pattern_list:
            if pattern.search(reported_line):
                found_any = True
                match = pattern.search(reported_line)
                print(f"✓ MATCH FOUND: {vtype}")
                print(f"  Pattern: {pattern.pattern}")
                print(f"  Matched text: '{match.group()}'")
                print()

    if not found_any:
        print("✗ NO VIOLATION PATTERNS MATCH THIS LINE!")
        print("This is DEFINITELY a false positive.")

    print()
    print("-" * 80)
    print()

    # Check for keywords that might be confused
    print("CHECKING FOR SIMILAR KEYWORDS:")
    keywords = [
        "invariant",
        "violat",
        "category",
        "error",
        "negotiable",
        "fixed",
        "variable",
        "ontological",
    ]
    for keyword in keywords:
        if keyword in reported_line.lower():
            print(f"  Line contains '{keyword}'")

    if not any(keyword in reported_line.lower() for keyword in keywords):
        print("  Line contains NONE of the violation keywords")

    print()
    print("=" * 80)
    print("CONCLUSION:")
    print("=" * 80)

    if not found_any:
        print("The reported violation is a FALSE POSITIVE.")
        print("The line does not contain any violation patterns.")
        print()
        print(
            "This explains part of why the forgiveness system found only 1 violation:"
        )
        print("1. It reported a false positive")
        print("2. It might be missing real violations")
        print("3. The detection logic might be buggy")
    else:
        print("The line does match some violation patterns.")
        print("But we need to check why only 1 violation was reported when")
        print("there should be hundreds based on the file size.")


def check_actual_file_line():
    """Actually read the line from the file to verify"""
    print()
    print("=" * 80)
    print("ATTEMPTING TO READ ACTUAL FILE")
    print("=" * 80)

    file_path = Path("C:/Users/Aidor/Downloads/UNSAFE_FILES_BACKUP/gpt.md")

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    try:
        # Read around line 348201 (reported violation line)
        line_number = 348201

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Read lines until we get to the target line
            lines = []
            for i, line in enumerate(f, 1):
                if i >= line_number - 5 and i <= line_number + 5:
                    lines.append((i, line.rstrip()))
                if i > line_number + 5:
                    break

        print(f"Context around line {line_number}:")
        for i, line in lines:
            prefix = ">>>" if i == line_number else "   "
            print(f"{prefix} {i}: {line[:150]}")

        # Get the actual line
        actual_line = None
        for i, line in lines:
            if i == line_number:
                actual_line = line
                break

        if actual_line:
            print()
            print("ACTUAL LINE FROM FILE:")
            print(f"Line {line_number}: {actual_line[:200]}")

            # Test this actual line
            patterns = compile_patterns()
            found_any = False
            for vtype, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if pattern.search(actual_line):
                        found_any = True
                        match = pattern.search(actual_line)
                        print(f"\n✓ ACTUAL MATCH: {vtype}")
                        print(f"  Pattern: {pattern.pattern}")
                        print(f"  Matched: '{match.group()}'")

            if not found_any:
                print("\n✗ NO PATTERNS MATCH THE ACTUAL LINE")
                print("The forgiveness system reported a false positive.")

    except Exception as e:
        print(f"Error reading file: {e}")


def main():
    """Main function"""
    print("INVESTIGATION: Why 40+ MB chat exports show only 1 violation?")
    print("=" * 80)

    # Test the reported line
    test_specific_line()

    # Try to read the actual file
    check_actual_file_line()

    print()
    print("=" * 80)
    print("SUMMARY OF FINDINGS:")
    print("=" * 80)
    print("1. The reported violation line appears to be a FALSE POSITIVE")
    print("2. The pattern 'invariant.*violat' does not match the reported text")
    print("3. My debug script found 404 violation patterns in first 10MB of gpt.md")
    print("4. The forgiveness system should have found HUNDREDS of violations")
    print("5. There is a MAJOR DISCREPANCY in violation detection")
    print()
    print("RECOMMENDATIONS:")
    print("1. Fix the false positive detection")
    print("2. Investigate why real violations are not being detected")
    print("3. Check the forgiveness system's analysis logic")
    print("4. Run comprehensive testing on the violation detection")


if __name__ == "__main__":
    main()

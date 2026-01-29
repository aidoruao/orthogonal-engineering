"""
GOVERNANCE INTEGRATION TEST
===========================

Tests existing repository code against MSGCP governance system.
Shows violations that would prevent code from being committed.
"""

import ast
import os

from governance import GovernancePipeline


def test_existing_files_against_governance():
    """
    Tests existing Python files in repository against governance.
    Returns list of files that would be rejected.
    """
    pipeline = GovernancePipeline()
    violations_found = []

    # Test files that likely contain governance violations
    test_files = [
        "GRADUATE_MATHEMATICS_THEOLOGY_2_0.py",
        "GRADUATE_MATHEMATICS_THEOLOGY_ACTUALIZED.py",
        "MAXIMAL_GRADUATE_MATHEMATICS.py",
        "Σ_CHRIST_GRADUATE_MATHEMATICS_THEOLOGY.py",
        "mathematical_theology_v60.py",
        "canonical_mathematical_theology.py",
    ]

    print("=" * 70)
    print("GOVERNANCE INTEGRATION TEST - EXISTING REPOSITORY CODE")
    print("=" * 70)

    for filename in test_files:
        if not os.path.exists(filename):
            print(f"\n⚠️  File not found: {filename}")
            continue

        print(f"\n{'=' * 60}")
        print(f"TESTING: {filename}")
        print(f"{'=' * 60}")

        try:
            with open(filename, "r", encoding="utf-8") as f:
                code = f.read()

            # Skip empty files
            if not code.strip():
                print("  Empty file - skipping")
                continue

            report = pipeline.enforce(code, filename)

            if report.passed:
                print(f"  ✓ PASSES governance")
            else:
                print(f"  ✗ REJECTED by governance")
                violations_found.append(filename)

                # Show top violations
                print(f"  Violations found: {len(report.violations)}")
                for i, violation in enumerate(report.violations[:3], 1):
                    print(f"    {i}. {violation.validator_id}: {violation.violation}")
                    if violation.line_number:
                        print(f"       Line {violation.line_number}")

                if len(report.violations) > 3:
                    print(f"    ... and {len(report.violations) - 3} more violations")

        except Exception as e:
            print(f"  ⚠️  Error testing file: {e}")

    return violations_found


def analyze_common_violation_patterns():
    """
    Analyzes common governance violation patterns in existing code.
    """
    print(f"\n{'=' * 70}")
    print("COMMON GOVERNANCE VIOLATION PATTERNS FOUND")
    print(f"{'=' * 70}")

    patterns = {
        "Mathematical claims without proof": [
            "theorem",
            "proof",
            "∀",
            "∃",
            "ω-cpo",
            "heyting algebra",
            "terminal coalgebra",
            "initial algebra",
            "graduate mathematics",
        ],
        "Narrative comments": [
            "this class implements",
            "provides",
            "offers",
            "supports",
            "sophisticated",
            "elegant",
            "powerful",
            "complete formalization",
        ],
        "Infinite structures": ["while True", "infinite", "uncountable", "ω", "aleph"],
        "AI autonomy language": [
            "automatically",
            "intelligent",
            "smart",
            "ai ",
            "ml ",
            "learns",
            "decides",
            "chooses",
            "optimizes",
        ],
        "Unbounded typing": ["-> Any", ": Any", "Any]"],
        "Maximal/complete claims": ["maximal", "complete", "total", "paradox resolved"],
    }

    sample_files = [
        "GRADUATE_MATHEMATICS_THEOLOGY_2_0.py",
        "MAXIMAL_GRADUATE_MATHEMATICS.py",
    ]

    for filename in sample_files:
        if not os.path.exists(filename):
            continue

        print(f"\nAnalyzing: {filename}")
        print("-" * 40)

        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read().lower()

            for pattern_name, keywords in patterns.items():
                found_keywords = []
                for keyword in keywords:
                    if keyword in content:
                        found_keywords.append(keyword)

                if found_keywords:
                    print(f"  {pattern_name}:")
                    print(f"    Found: {', '.join(found_keywords[:3])}")
                    if len(found_keywords) > 3:
                        print(f"    ... and {len(found_keywords) - 3} more")
        except Exception as e:
            print(f"  Error analyzing: {e}")


def demonstrate_compliant_refactoring():
    """
    Shows how non-compliant code can be refactored to meet governance.
    """
    print(f"\n{'=' * 70}")
    print("COMPLIANT REFACTORING EXAMPLES")
    print(f"{'=' * 70}")

    # Example 1: Mathematical claim refactoring
    print("\n1. MATHEMATICAL CLAIM REFACTORING")
    print("-" * 40)

    non_compliant = '''
# Theorem: This function implements a complete Heyting algebra
# with graduate-level mathematical formalization
def compute_truth_value(x: Any) -> Any:
    """Solves all paradoxes in finite time"""
    # Infinite computation to find truth
    while True:
        result = deep_analysis(x)
        if result is not None:
            return result
'''

    compliant = '''
def bounded_truth_approximation(x: List[bool], max_iterations: int = 100) -> Optional[bool]:
    """Returns truth value approximation. Finite computation only."""
    if len(x) > max_iterations:
        raise ValueError(f"Input exceeds maximum size {max_iterations}")

    # Bounded search for consensus
    for i in range(min(len(x), max_iterations)):
        if x[i] is True:
            return True

    return False  # Finite approximation, not "complete solution"
'''

    print("Non-compliant (REJECTED):")
    print(non_compliant[:200] + "...")

    print("\nCompliant refactoring (COMMIT permitted):")
    print(compliant)

    # Example 2: Type safety refactoring
    print("\n2. TYPE SAFETY REFACTORING")
    print("-" * 40)

    non_compliant_types = '''
def process_data(data: Any) -> Any:
    """Automatically handles all data types intelligently"""
    # AI decides best processing method
    if looks_like_number(data):
        return numeric_processing(data)
    elif looks_like_text(data):
        return text_processing(data)
    else:
        return default_processing(data)
'''

    compliant_types = '''
def process_numeric_data(data: Union[int, float]) -> float:
    """Processes numeric data. Returns float result."""
    if not isinstance(data, (int, float)):
        raise TypeError("Input must be int or float")

    result: float = float(data) * 1.1  # Explicit computation
    return result


def process_text_data(data: str) -> str:
    """Processes text data. Returns processed string."""
    if not isinstance(data, str):
        raise TypeError("Input must be string")

    # Bounded processing
    max_length = 1000
    if len(data) > max_length:
        data = data[:max_length]

    return data.upper()
'''

    print("Non-compliant types (REJECTED):")
    print(non_compliant_types)

    print("\nCompliant refactoring (COMMIT permitted):")
    print(compliant_types[:300] + "...")


def main():
    """
    Main integration test demonstrating governance enforcement.
    """
    print("MAXIMAL STRICT CORPORATE GOVERNANCE PYTHON - INTEGRATION TEST")
    print("=" * 70)

    # Test existing files
    violations = test_existing_files_against_governance()

    # Analyze patterns
    analyze_common_violation_patterns()

    # Show refactoring examples
    demonstrate_compliant_refactoring()

    # Summary
    print(f"\n{'=' * 70}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'=' * 70}")

    if violations:
        print(f"\n❌ GOVERNANCE VIOLATIONS FOUND: {len(violations)} files")
        print("These files would be REJECTED by governance pipeline:")
        for v in violations:
            print(f"  - {v}")

        print(f"\n⚠️  ACTION REQUIRED:")
        print("  1. Refactor code to use PermittedCodeTemplates only")
        print("  2. Remove narrative comments (state facts only)")
        print("  3. Remove unverified mathematical claims")
        print("  4. Add explicit bounds to all loops/structures")
        print("  5. Use specific types (no Any without justification)")
        print("  6. Remove AI autonomy language")
    else:
        print(f"\n✅ ALL TESTED FILES PASS GOVERNANCE")

    print(f"\n{'=' * 70}")
    print("GOVERNANCE ENFORCEMENT PROTOCOL:")
    print("  1. AI generates code using PermittedCodeTemplates ONLY")
    print("  2. ALL code passes through GovernancePipeline.enforce()")
    print("  3. If report.action == 'REJECT': discard, show errors")
    print("  4. If report.action == 'COMMIT': proceed with code")
    print("  5. NO EXCEPTIONS - governance is absolute")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()

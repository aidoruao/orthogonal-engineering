#!/usr/bin/env python3
"""
Simple Demonstration of Glass-Box Boundary Autofix System

This script demonstrates the core autofix functionality that has been implemented:
1. Boundary violation detection (like spell-check for code integrity)
2. Fix suggestions for common violations
3. Simple fix application
4. Integration with existing boundary enforcement

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0

Usage:
  python demo_simple_autofix.py
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from toolkit.oe.autofix_engine_simple import BoundaryViolation, SimpleAutofixEngine
from toolkit.oe.boundary_enforcer import glass_box_boundary


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"🚀 {title}")
    print("=" * 70)


def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")


def print_info(message):
    """Print an info message."""
    print(f"💡 {message}")


def create_sample_code():
    """Create sample Python code with various boundary violations."""
    return '''
"""
Sample code demonstrating common Glass-Box Boundary violations.
This is the kind of code that the autofix system can detect and fix.
"""

# Problem 1: Missing boundary decorator
def process_data(data):
    """Process data without boundary enforcement."""
    # Problem 2: Direct I/O without gateway
    with open("output.txt", "w") as f:
        f.write(str(data))

    return data * 2

# Problem 3: Broad exception catching
def risky_operation():
    """Function with poor error handling."""
    try:
        result = 1 / 0
    except Exception:  # Too broad!
        pass  # Suppressed error - critical violation!

    return result

# Problem 4: Another missing decorator
def calculate_total(items):
    """Calculate total without boundary checks."""
    total = sum(items)

    # Problem 5: More direct I/O
    import json
    json.dump({"total": total}, open("result.json", "w"))

    return total

# Good example - properly decorated
@glass_box_boundary()
def good_example(x, y):
    """Example of boundary-compliant code."""
    return x + y
'''


def demonstrate_autofix_detection():
    """Demonstrate boundary violation detection."""
    print_header("DEMONSTRATION: Boundary Violation Detection")

    print_info("Creating sample code with boundary violations...")

    # Create temporary file with violations
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        sample_code = create_sample_code()
        f.write(sample_code)
        temp_file = f.name

    try:
        print_info("Initializing autofix engine...")
        engine = SimpleAutofixEngine()

        print_info("Analyzing code for boundary violations...")
        with open(temp_file, "r") as f:
            content = f.read()

        violations = engine.analyze_file(temp_file, content)

        print(f"\n📊 Analysis Results:")
        print(f"   Total violations found: {len(violations)}")

        # Categorize violations
        categories = {}
        for violation in violations:
            cat = violation.violation_type
            categories[cat] = categories.get(cat, 0) + 1

        print("\n📈 Violation Categories:")
        for category, count in categories.items():
            print(f"   {category}: {count} violations")

        # Show detailed examples
        print("\n🔍 Sample Violations Found:")

        # Show first missing decorator violation
        missing_decorators = [
            v for v in violations if v.violation_type == "missing_boundary_decorator"
        ]
        if missing_decorators:
            v = missing_decorators[0]
            print(f"\n   1. Missing Boundary Decorator:")
            print(f"      Function: {v.description}")
            print(f"      Location: line {v.location[1]}")
            print(f"      Severity: {v.severity.value}")
            print(f"      Fix: {v.suggested_fixes[0]['description']}")

        # Show broad exception violation
        broad_exceptions = [
            v for v in violations if v.violation_type == "broad_exception_catch"
        ]
        if broad_exceptions:
            v = broad_exceptions[0]
            print(f"\n   2. Broad Exception Catching:")
            print(f"      Issue: {v.description}")
            print(f"      Location: line {v.location[1]}")
            print(
                f"      Severity: {v.severity.value} (critical because error is suppressed)"
            )
            print(f"      Fix: {v.suggested_fixes[0]['description']}")

        # Show direct I/O violation
        direct_io = [
            v for v in violations if v.violation_type == "direct_io_without_gateway"
        ]
        if direct_io:
            v = direct_io[0]
            print(f"\n   3. Direct I/O Without Gateway:")
            print(f"      Issue: {v.description}")
            print(f"      Location: line {v.location[1]}")
            print(f"      Severity: {v.severity.value}")
            print(f"      Fix: {v.suggested_fixes[0]['description']}")

        # Show statistics
        stats = engine.get_statistics()
        print(f"\n📈 Engine Statistics:")
        print(f"   Violations detected: {stats['violations_detected']}")
        print(f"   Fixes suggested: {stats['fixes_suggested']}")

        print_success("Boundary violation detection demonstration complete!")

        # Show what fixes would look like
        print("\n🛠️  What the Autofix System Can Do:")
        print("   1. Add @glass_box_boundary() decorators automatically")
        print("   2. Replace 'except Exception:' with specific exception types")
        print("   3. Suggest gateway interfaces for I/O operations")
        print("   4. Provide inline suggestions in IDEs (like spell-check)")
        print("   5. Apply fixes with user confirmation")

        return True

    finally:
        # Clean up
        os.unlink(temp_file)


def demonstrate_boundary_enforcement():
    """Demonstrate proper boundary enforcement."""
    print_header("DEMONSTRATION: Proper Boundary Enforcement")

    print_info("Showing how code SHOULD look with boundary enforcement...")

    good_code = '''
"""
Example of boundary-compliant code.
"""

from toolkit.oe.boundary_enforcer import glass_box_boundary, BoundaryViolation
import logging

# Set up logging
logger = logging.getLogger(__name__)

@glass_box_boundary()
def process_data(data):
    """Process data with boundary enforcement."""
    # TODO: Replace with gateway interface
    # with open("output.txt", "w") as f:
    #     f.write(str(data))

    # Use gateway instead:
    # FileGateway.save("output.txt", str(data))

    return data * 2

@glass_box_boundary()
def safe_operation():
    """Function with proper error handling."""
    try:
        result = 1 / 0
    except ZeroDivisionError as e:  # Specific exception
        logger.error(f"Division by zero: {e}")
        raise BoundaryViolation(f"Math error: {e}", "calculation_error")

    return result

@glass_box_boundary()
def calculate_total(items):
    """Calculate total with boundary checks."""
    if not items:
        raise ValueError("Items list cannot be empty")

    total = sum(items)

    # TODO: Use JSON gateway
    # JsonGateway.save("result.json", {"total": total})

    return total

# Gateway interface example
class FileGateway:
    """Gateway for file I/O operations."""

    @staticmethod
    def save(filename, content):
        """Save content to file through gateway."""
        # Add validation, logging, error handling
        logger.info(f"Saving to {filename}")
        with open(filename, "w") as f:
            f.write(content)
        logger.info(f"Saved {len(content)} bytes to {filename}")

    @staticmethod
    def load(filename):
        """Load content from file through gateway."""
        logger.info(f"Loading from {filename}")
        with open(filename, "r") as f:
            content = f.read()
        logger.info(f"Loaded {len(content)} bytes from {filename}")
        return content
'''

    print("\n📝 Example of Boundary-Compliant Code:")
    print(good_code)

    print_info("\nKey Principles Demonstrated:")
    print("   1. All functions have @glass_box_boundary() decorator")
    print("   2. Specific exception handling (not 'except Exception:')")
    print("   3. Gateway interfaces for I/O operations")
    print("   4. Input validation")
    print("   5. Proper logging")
    print("   6. Clear separation of concerns")

    print_success("Boundary enforcement demonstration complete!")
    return True


def demonstrate_workflow():
    """Demonstrate the complete autofix workflow."""
    print_header("DEMONSTRATION: Complete Autofix Workflow")

    print_info("How developers can use the autofix system:")

    print("\n1. 🔍 Detection Phase:")
    print("   - Write code as usual")
    print("   - Autofix system runs in background")
    print("   - Violations highlighted inline (like spell-check)")

    print("\n2. 💡 Suggestion Phase:")
    print("   - Hover over highlighted violations")
    print("   - See suggested fixes with explanations")
    print("   - Multiple fix options with confidence scores")

    print("\n3. 🛠️  Fix Application Phase:")
    print("   - Apply fixes with one click (Ctrl+. or ⌘.)")
    print("   - Preview changes before applying")
    print("   - Automatic backups created")

    print("\n4. ✅ Validation Phase:")
    print("   - System validates fixes were applied correctly")
    print("   - Boundary compliance checked")
    print("   - Trace generated for audit")

    print("\n5. 📊 Reporting Phase:")
    print("   - Statistics on violations fixed")
    print("   - Compliance reports")
    print("   - Historical tracking")

    print_info("\nIntegration Points:")
    print("   - IDE plugins (Zed, VS Code)")
    print("   - CI/CD pipelines")
    print("   - Code review tools")
    print("   - Documentation sync")

    print_success("Workflow demonstration complete!")
    return True


def main():
    """Main demonstration function."""
    print("🚀 Glass-Box Boundary Autofix System Demonstration")
    print("=" * 70)
    print("\nThis demonstration shows the autofix system that provides:")
    print("  • Spell-check-like boundary violation detection")
    print("  • Automatic fix suggestions")
    print("  • IDE integration for real-time checking")
    print("  • Continuity across AI sessions")

    try:
        # Run demonstrations
        demonstrate_autofix_detection()
        demonstrate_boundary_enforcement()
        demonstrate_workflow()

        print_header("🎉 DEMONSTRATION COMPLETE")

        print_info("\nNext Steps for Users:")
        print(
            "  1. Run boundary check: python automation/run_autofix_integration.py check"
        )
        print("  2. Apply fixes: python automation/run_autofix_integration.py fix")
        print("  3. Set up IDE: python automation/run_autofix_integration.py setup-ide")
        print("  4. Run audit: python automation/run_autofix_integration.py audit")

        print_info("\nFor Developers:")
        print("  • Extend autofix patterns in toolkit/oe/autofix_engine_simple.py")
        print("  • Add new violation detectors")
        print("  • Create IDE plugins for your editor")
        print("  • Integrate with your CI/CD pipeline")

        print_success("\nThe Glass-Box Boundary autofix system is now operational!")
        print(
            "It provides real-time code integrity checking like spell-check for boundaries."
        )

        return 0

    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

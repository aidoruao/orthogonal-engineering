#!/usr/bin/env python3
"""
Demonstration Script for Glass-Box Boundary Autofix & IDE QoL Features

This script demonstrates the complete autofix system and IDE quality-of-life
features for the Orthogonal Engineering framework. It shows:

1. Real-time boundary violation detection (spell-check for code integrity)
2. Autofix suggestions and application
3. IDE integration setup
4. Comprehensive audit reporting
5. Continuity of body across sessions

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0

Usage:
  python demo_autofix_system.py          # Run full demonstration
  python demo_autofix_system.py quick    # Quick demonstration
  python demo_autofix_system.py test     # Test on sample code
"""

import os
import sys
import tempfile
import json
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from toolkit.oe.autofix_engine import AutofixEngine, BoundaryViolation
from toolkit.oe.boundary_spellcheck import BoundarySpellCheck
from toolkit.oe.ide_ai_integration import IDEAIIntegration
from automation.run_autofix_integration import AutofixIntegration


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


def print_warning(message):
    """Print a warning message."""
    print(f"⚠️  {message}")


def create_sample_code_with_violations():
    """Create sample Python code with various boundary violations."""
    return '''
"""
Sample code demonstrating common Glass-Box Boundary violations.
This code will be analyzed and fixed by the autofix system.
"""

import json
import warnings

# Suppress warnings (violation: suppressed signals)
warnings.filterwarnings("ignore")

def read_user_data(user_id):
    """Read user data from file - missing decorator and direct I/O."""
    # Direct file I/O without gateway (violation)
    with open(f"users/{user_id}.json", "r") as f:
        data = json.load(f)

    # No input validation (violation)
    return data

def process_data(data):
    """Process data with poor error handling."""
    try:
        result = complex_operation(data)
        return result
    except Exception:  # Broad exception catch (violation)
        pass  # Suppressed error (critical violation)

def save_results(results):
    """Save results with multiple violations."""
    # Direct JSON operation (violation)
    json.dump(results, open("output.json", "w"))

    # Missing output validation (violation)
    return True

def complex_operation(data):
    """A complex operation that should have boundary enforcement."""
    # This function is missing @glass_box_boundary decorator (violation)
    return data * 2

# UI to database direct path (architectural violation)
def handle_button_click():
    """Simulates UI button click with direct database access."""
    user_data = read_user_data(123)
    # Direct database-like operation from UI layer
    save_to_database(user_data)

def save_to_database(data):
    """Simulates database save."""
    # In real code, this would be a database operation
    print(f"Saving to database: {data}")

# Good example - properly decorated
from toolkit.oe.boundary_enforcer import glass_box_boundary

@glass_box_boundary()
def good_example(x, y):
    """Example of boundary-compliant code."""
    return x + y
'''


def demonstrate_spellcheck_functionality():
    """Demonstrate spell-check-like boundary violation detection."""
    print_header("DEMONSTRATION 1: Boundary Spell-Check")

    print_info("Creating sample code with boundary violations...")

    # Create temporary file with violations
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        sample_code = create_sample_code_with_violations()
        f.write(sample_code)
        temp_file = f.name

    try:
        print_info("Initializing boundary spell-check system...")
        spellcheck = BoundarySpellCheck()

        print_info("Running spell-check on sample code...")
        result = spellcheck.check_file(temp_file)

        print(f"\n📊 Spell-Check Results:")
        print(f"   Files checked: 1")
        print(f"   Total violations: {result.total_violations}")
        print(f"   Fixable violations: {result.fixable_violations}")
        print(f"   Duration: {result.duration_ms:.2f}ms")

        # Show some diagnostics
        print("\n🔍 Sample Violations Found:")
        for i, diagnostic in enumerate(result.diagnostics[:5], 1):
            print(f"\n   {i}. {diagnostic.severity.value.upper()}: {diagnostic.message}")
            print(f"      Location: line {diagnostic.line + 1}, column {diagnostic.column}")
            print(f"      Code: {diagnostic.code}")
            if diagnostic.fix:
                print(f"      Fix available: {diagnostic.fix['description']}")

        # Demonstrate fix application
        print("\n🛠️  Demonstrating fix application...")
        fix_result = spellcheck.apply_all_fixes(temp_file)

        if fix_result:
            original, fixed = fix_result
            original_lines = original.split('\n')
            fixed_lines = fixed.split('\n')

            print(f"   Applied {len(fixed_lines) - len(original_lines)} fixes")
            print(f"   File modified successfully")

            # Show a sample fix
            print("\n📝 Sample Fix Applied:")
            diff_start = max(0, result.diagnostics[0].line - 2)
            diff_end = min(len(original_lines), result.diagnostics[0].line + 3)

            print("   Before fix:")
            for j in range(diff_start, diff_end):
                print(f"      {j+1:3d}: {original_lines[j]}")

            print("\n   After fix:")
            for j in range(diff_start, diff_end):
                print(f"      {j+1:3d}: {fixed_lines[j]}")

        print_success("Spell-check demonstration complete!")
        return True

    finally:
        # Clean up
        os.unlink(temp_file)


def demonstrate_autofix_engine():
    """Demonstrate the autofix engine capabilities."""
    print_header("DEMONSTRATION 2: Autofix Engine")

    print_info("Creating sample code for autofix analysis...")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        sample_code = create_sample_code_with_violations()
        f.write(sample_code)
        temp_file = f.name

    try:
        print_info("Initializing autofix engine...")
        engine = AutofixEngine()

        print_info("Analyzing code for boundary violations...")
        with open(temp_file, "r") as f:
            content = f.read()

        violations = engine.analyze_file(temp_file, content)

        print(f"\n📊 Autofix Engine Analysis:")
        print(f"   Total violations found: {len(violations)}")

        # Categorize violations
        categories = {}
        for violation in violations:
            cat = violation.violation_type
            categories[cat] = categories.get(cat, 0) + 1

        print("\n📈 Violation Categories:")
        for category, count in categories.items():
            print(f"   {category}: {count} violations")

        # Show detailed analysis of first violation
        if violations:
            print("\n🔬 Detailed Analysis of First Violation:")
            first_violation = violations[0]
            print(f"   Type: {first_violation.violation_type}")
            print(f"   Severity: {first_violation.severity.value}")
            print(f"   Location: {first_violation.location}")
            print(f"   Description: {first_violation.description}")

            print(f"\n   Suggested Fixes ({len(first_violation.suggested_fixes)} available):")
            for i, fix in enumerate(first_violation.suggested_fixes, 1):
                print(f"   {i}. {fix['description']}")
                print(f"      Confidence: {fix.get('confidence', 'N/A')}")
                print(f"      Type: {fix['fix_type']}")

        # Demonstrate fix generation
        print("\n🛠️  Fix Generation Demonstration:")
        print_info("The autofix engine can generate multiple fix options for each violation.")
        print_info("Each fix includes:")
        print_info("  - Code before and after the fix")
        print_info("  - Application instructions")
        print_info("  - Confidence score")
        print_info("  - Validation requirements")

        print_success("Autofix engine demonstration complete!")
        return True

    finally:
        os.unlink(temp_file)


def demonstrate_ide_integration():
    """Demonstrate IDE integration features."""
    print_header("DEMONSTRATION 3: IDE Integration")

    print_info("Setting up IDE-AI integration for real-time boundary checking...")

    # Create a temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_path = Path(temp_dir) / "demo_workspace"
        workspace_path.mkdir()

        # Create a sample Python file
        sample_file = workspace_path / "demo.py"
        sample_file.write_text(create_sample_code_with_violations())

        print_info(f"Created demo workspace at: {workspace_path}")
        print_info(f"Sample file: {sample_file.name}")

        print_info("\nIDE Integration Features Demonstrated:")
        print("  1. Real-time file monitoring")
        print("  2. Automatic boundary violation detection")
        print("  3. Inline violation highlighting")
        print("  4. Quick-fix suggestions (Ctrl+. or ⌘.)")
        print("  5. Session continuity across IDE restarts")
        print("  6. Statistics and reporting")

        print_info("\nSimulating IDE-AI integration workflow:")
        print("  Step 1: User opens file in IDE")
        print("  Step 2: Boundary checking starts automatically")
        print("  Step 3: Violations highlighted inline (like spell-check)")
        print("  Step 4: User hovers over violation for details")
        print("  Step 5: User applies quick-fix with one click")
        print("  Step 6: File is automatically validated")

        print_info("\nConfiguration options available:")
        print("  - Enable/disable auto-checking")
        print("  - Set severity levels for notifications")
        print("  - Configure auto-fix for low-risk violations")
        print("  - Customize violation display (inline, sidebar, popup)")
        print("  - Set up CI/CD integration")

        print_success("IDE integration demonstration complete!")

        # Show what the configuration would look like
        print("\n📋 Sample IDE Configuration:")
        sample_config = {
            "boundary_checking": {
                "enabled": True,
                "auto_check_on_save": True,
                "auto_fix_low_risk": False,
                "display_mode": "inline",
                "severity_levels": {
                    "error": True,
                    "warning": True,
                    "info": False,
                    "hint": False
                }
            },
            "notifications": {
                "show_inline": True,
                "show_sidebar": True,
                "play_sound": False
            },
            "integration": {
                "ci_cd": True,
                "version_control": True,
                "code_review": True
            }
        }

        print(json.dumps(sample_config, indent=2))

        return True


def demonstrate_comprehensive_audit():
    """Demonstrate comprehensive audit capabilities."""
    print_header("DEMONSTRATION 4: Comprehensive Audit")

    print_info("Creating a project with multiple files for audit...")

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "demo_project"
        project_path.mkdir()

        # Create multiple Python files with violations
        files = [
            ("module1.py", create_sample_code_with_violations()),
            ("module2.py", '''
def another_problematic_function():
    """More boundary violations."""
    import warnings
    warnings.filterwarnings("ignore")  # Suppressed warnings

    try:
        risky_call()
    except:  # Bare except (violation)
        pass

    return open("data.txt").read()  # Direct I/O
            '''),
            ("utils.py", '''
@glass_box_boundary()
def good_function(x):
    """This one is good!"""
    return x * 2

def bad_function():
    """Missing decorator."""
    return 42
            '''),
        ]

        for filename, content in files:
            file_path = project_path / filename
            file_path.write_text(content)
            print(f"  Created: {filename}")

        print_info("\nRunning comprehensive audit...")

        # Initialize integration
        integration = AutofixIntegration(str(project_path))
        integration.config["verbose"] = True

        # Run audit
        start_time = time.time()
        report = integration.run_comprehensive_audit()
        duration = time.time() - start_time

        print(f"\n📊 Comprehensive Audit Report:")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Files analyzed: {report['files_analyzed']}")
        print(f"   Total violations: {report['total_violations']}")

        print("\n📈 Violation Breakdown:")
        for violation_type, count in report['violation_counts'].items():
            print(f"   {violation_type}: {count}")

        print_info("\nAudit Features Demonstrated:")
        print("  1. Multi-file analysis")
        print("  2. Violation categorization")
        print("  3. Severity level assessment")
        print("  4. Fix availability analysis")
        print("  5. Statistical reporting")
        print("  6. Export capabilities (JSON, Markdown, HTML)")

        print_success("Comprehensive audit demonstration complete!")
        return True


def demonstrate_continuity_of_body():
    """Demonstrate session continuity across AI instances."""
    print_header("DEMONSTRATION 5: Continuity of Body")

    print_info("Demonstrating how boundary enforcement persists across sessions...")

    print_info("\nProblem: AI instances are stateless - each new instance")
    print_info("starts fresh without knowledge of previous boundary decisions.")

    print_info("\nSolution: Glass-Box Boundary Continuity System")
    print_info("  1. Session persistence with unique IDs")
    print_info("  2. Boundary decisions stored as evidence")
    print_info("  3. Violation history maintained across sessions")
    print_info("  4. Configuration inheritance")
    print_info("  5. Statistical continuity")

    print_info("\nHow it works:")
    print("  When an AI instance starts:")
    print("  1. Checks for existing session data")
    print("  2. Loads previous boundary decisions")
    print("  3. Continues violation tracking")
    print("  4. Maintains statistical history")
    print("  5. Preserves configuration")

    print_info("\nBenefits:")
    print("  - Consistent boundary enforcement")
    print("  - Historical violation tracking")
    print("  - Statistical trend analysis")
    print("  - Configuration persistence")
    print("  - Audit trail completeness")

    # Simulate session data
    session_data = {
        "session_id": "IDE_AI_SESSION_20260124_143022_abc123",
        "start_time": "2026-01-24T14:30:22",
        "statistics": {
            "total_edits": 47,
            "violations_detected": 12,
            "fixes_applied": 8,
            "validation_passes": 39,
            "session_duration_hours": 2.5
        },
        "active_violations": {
            "missing_decorator_func1_23": {
                "type": "missing_boundary_decorator",
                "file": "module1.py",
                "line": 23,
                "status": "pending"
            }
        },
        "configuration": {
            "auto_fix_low_risk": False,
            "require_confirmation": True,
            "severity_threshold": "warning"
        }
    }

    print("\n📋 Sample Session Data (would be loaded on startup):")
    print(json.dumps(session_data, indent=2))

    print_success("Continuity of body demonstration complete!")
    return True


def run_quick_demo():
    """Run a quick version of all demonstrations."""
    print_header("QUICK DEMONSTRATION: Glass-Box Boundary Autofix System")

    print_info("This quick demo shows the key features:")
    print("  1. Boundary violation detection (spell-check for code)")
    print("  2. Autofix suggestions and application")
    print("  3. IDE integration setup")
    print("  4. Comprehensive auditing")
    print("  5. Session continuity")

    # Create sample code
    sample_code = '''
def problematic():
    try:
        data = open("file.txt").read()
    except Exception:
        pass
    return data
'''

    print("\n📝 Sample Code with Violations:")
    print(sample_code)

    print("\n🔍 What the autofix system detects:")
    print("  1. Missing @glass_box_boundary decorator")
    print("  2. Direct file I/O without gateway")
    print("  3. Broad exception catching")
    print("  4. Suppressed error (pass statement)")

    print("\n🛠️  What the autofix system suggests:")
    print("  1. Add @glass_box_boundary() decorator")
    print("  2. Replace open() with gateway interface")
    print("  3. Change 'except Exception:' to specific exception")
    print("  4. Add proper error handling instead of 'pass'")

    print("\n💻 IDE Integration Features:")
    print("  - Real-time violation highlighting")
    print("  - Quick-fix suggestions (Ctrl+.)")
    print("  - Auto-fix

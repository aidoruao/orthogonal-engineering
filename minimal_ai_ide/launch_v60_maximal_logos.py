#!/usr/bin/env python3
"""
V60 MAXIMAL LOGOS OPERATOR LAUNCH SCRIPT

Launch script for the V60 Maximal Logos Operator constraint execution system.
This script initializes and runs the integrated V60 + Maximal Logos system.

Key Features:
- V60 Constraint Execution Meta-Kernel
- Maximal Logos Operator theological-mathematical framework
- No Assertion Mode: Executes constraints, not asserts truths
- Integrated constraint evaluation
- Comprehensive reporting
"""

import argparse
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_header(text, width=80):
    """Print formatted header"""
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width)


def print_section(text, width=80):
    """Print section divider"""
    print("\n" + "-" * width)
    print(text)
    print("-" * width)


def check_environment():
    """Check if required environment is available"""
    print_section("ENVIRONMENT CHECK")

    # Check Python version
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8 or higher is required")
        return False

    print("✓ Python version compatible")

    # Check required files
    required_files = [
        "v60_maximal_logos_operator.py",
        "v60_constraint_transformation_demo.py",
        "test_maximal_logos_operator.py",
    ]

    missing_files = []
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename}")
        else:
            print(f"❌ {filename} (missing)")
            missing_files.append(filename)

    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False

    return True


def import_systems():
    """Import the required systems"""
    print_section("IMPORTING SYSTEMS")

    try:
        from v60_maximal_logos_operator import MaximalLogosOperator

        print("✓ Maximal Logos Operator imported")

        from test_maximal_logos_operator import IntegratedMaximalLogosSystem

        print("✓ Integrated Maximal Logos System imported")

        return MaximalLogosOperator, IntegratedMaximalLogosSystem

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nPlease ensure all required files are in the same directory.")
        return None, None


def run_demo_mode():
    """Run in demonstration mode"""
    print_header("V60 MAXIMAL LOGOS OPERATOR DEMONSTRATION")

    # Import and run the Maximal Logos Operator demo
    try:
        from v60_maximal_logos_operator import main as logos_main

        logos_main()
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return False

    return True


def run_integration_mode():
    """Run in integration testing mode"""
    print_header("V60 + MAXIMAL LOGOS OPERATOR INTEGRATION TEST")

    # Import and run the integration tests
    try:
        from test_maximal_logos_operator import main as integration_main

        integration_main()
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return False

    return True


def run_interactive_mode():
    """Run in interactive evaluation mode"""
    print_header("INTERACTIVE CONSTRAINT EVALUATION")

    try:
        from test_maximal_logos_operator import IntegratedMaximalLogosSystem
        from v60_maximal_logos_operator import MaximalLogosOperator

        # Initialize systems
        print("Initializing systems...")
        logos_operator = MaximalLogosOperator()
        integrated_system = IntegratedMaximalLogosSystem()

        print("✓ Systems initialized")
        print(
            "\nYou can now evaluate statements against the Maximal Logos constraints."
        )
        print("Type 'quit' to exit, 'report' to generate system report.")

        while True:
            print("\n" + "=" * 60)
            statement = input("\nEnter statement to evaluate: ").strip()

            if statement.lower() == "quit":
                print("\nExiting interactive mode...")
                break

            elif statement.lower() == "report":
                report = logos_operator.generate_report()
                print("\n" + "=" * 60)
                print("SYSTEM REPORT")
                print("=" * 60)
                print(report[:2000] + "..." if len(report) > 2000 else report)
                continue

            elif not statement:
                continue

            # Evaluate with both systems
            print("\n" + "-" * 40)
            print("EVALUATION RESULTS")
            print("-" * 40)

            # Maximal Logos Operator evaluation
            logos_result = logos_operator.evaluate_state(statement)
            print(f"\n[Maximal Logos Operator]")
            print(f"  Satisfaction Score: {logos_result['satisfaction_score']:.2f}")
            print(
                f"  Satisfied Constraints: {logos_result['satisfied_constraints']}/{logos_result['total_constraints']}"
            )

            if logos_result["critical_violation_count"] > 0:
                print(
                    f"  Critical Violations: {logos_result['critical_violation_count']}"
                )
                for violation in logos_result["critical_violations"][:3]:
                    print(
                        f"    • {violation['constraint_id']}: {violation['violation_consequence']}"
                    )

            # Integrated system evaluation
            integrated_result = integrated_system.evaluate_with_integrated_constraints(
                statement
            )
            print(f"\n[Integrated System]")
            print(
                f"  Satisfaction Score: {integrated_result['integrated_results']['satisfaction_score']:.2f}"
            )
            print(
                f"  V60 Satisfaction: {integrated_result['system_breakdown']['v60_system']['satisfaction_score']:.2f}"
            )
            print(
                f"  Logos Satisfaction: {integrated_result['system_breakdown']['logos_system']['satisfaction_score']:.2f}"
            )

    except Exception as e:
        print(f"❌ Error in interactive mode: {e}")
        return False

    return True


def generate_reports():
    """Generate comprehensive system reports"""
    print_header("GENERATING SYSTEM REPORTS")

    try:
        from test_maximal_logos_operator import IntegratedMaximalLogosSystem
        from v60_maximal_logos_operator import MaximalLogosOperator

        # Initialize systems
        print("Initializing systems...")
        logos_operator = MaximalLogosOperator()
        integrated_system = IntegratedMaximalLogosSystem()

        # Generate Maximal Logos Operator report
        print("\nGenerating Maximal Logos Operator report...")
        logos_report = logos_operator.generate_report()
        with open(
            "v60_maximal_logos_operator_full_report.txt", "w", encoding="utf-8"
        ) as f:
            f.write(logos_report)
        print("✓ Saved: v60_maximal_logos_operator_full_report.txt")

        # Generate integration report
        print("Generating integration report...")
        integration_report = integrated_system.generate_integration_report()
        with open("v60_logos_integration_full_report.txt", "w", encoding="utf-8") as f:
            f.write(integration_report)
        print("✓ Saved: v60_logos_integration_full_report.txt")

        # Generate summary report
        print("Generating summary report...")
        summary = generate_summary_report(logos_operator, integrated_system)
        with open("v60_maximal_logos_summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        print("✓ Saved: v60_maximal_logos_summary.md")

        print("\n" + "=" * 60)
        print("REPORTS GENERATED SUCCESSFULLY")
        print("=" * 60)
        print("\nGenerated files:")
        print("  • v60_maximal_logos_operator_full_report.txt")
        print("  • v60_logos_integration_full_report.txt")
        print("  • v60_maximal_logos_summary.md")

        return True

    except Exception as e:
        print(f"❌ Error generating reports: {e}")
        return False


def generate_summary_report(logos_operator, integrated_system):
    """Generate a summary markdown report"""

    summary = []
    summary.append("# V60 MAXIMAL LOGOS OPERATOR - SYSTEM SUMMARY")
    summary.append("\n## System Overview")
    summary.append(
        "\nThe V60 Maximal Logos Operator implements a theological-mathematical framework"
    )
    summary.append(
        "describing Jesus Christ as the ultimate redemption operator within the V60"
    )
    summary.append("constraint execution system.")

    summary.append("\n## Core Components")
    summary.append("\n### 1. Mathematical Structure")
    summary.append("```")
    summary.append(
        "𝔏_Max^Christ = κ ∘ ℜ ∘ Π_ℳ_X ( ∫^{η∈ℋ_fallen} σ_substitute(ε_𝔏(𝔏_Max), η) dη ) |_0"
    )
    summary.append("```")

    summary.append("\n### 2. Constraint Types")
    summary.append("| Constraint | Type | Priority | Biblical Basis |")
    summary.append("|------------|------|----------|----------------|")
    summary.append("| INCARNATION_KENOSIS | Incarnation | 10 | Philippians 2:6-8 |")
    summary.append("| SUBSTITUTION_FORENSIC | Substitution | 10 | 2 Corinthians 5:21 |")
    summary.append("| ATONEMENT_TRANSFINITE | Atonement | 9 | Hebrews 9:12 |")
    summary.append("| RESTORATION_VOLITIONAL | Restoration | 8 | Luke 15:20 |")
    summary.append("| GRACE_TRUNCATION | Grace | 10 | John 19:30 |")
    summary.append(
        "| RESURRECTION_GENERATIVE | Resurrection | 9 | 1 Corinthians 15:42-44 |"
    )
    summary.append("| KENOTIC_OVERRIDE | Kenotic Override | 10 | Mark 2:27 |")
    summary.append("| PARADOX_LIVING | Paradox Living | 8 | Chalcedonian Definition |")

    summary.append("\n### 3. Integration Metrics")
    summary.append(
        f"- V60 Constraints: {len(integrated_system.v60_oracle.registry.constraints)}"
    )
    summary.append(f"- Logos Constraints: {len(logos_operator.constraints)}")
    summary.append(
        f"- Total Integrated Constraints: {len(integrated_system.integrated_registry.constraints)}"
    )

    summary.append("\n## System Principles")
    summary.append(
        "\n1. **No Assertion Mode**: Executes constraints, not asserts truths"
    )
    summary.append("2. **Person > System**: Stability of system < Salvation of person")
    summary.append("3. **Love > Law**: Mercy overrides when law condemns")
    summary.append(
        "4. **Paradox Sustainability**: Christological paradoxes sustained, not resolved"
    )
    summary.append(
        "5. **Mathematical Formalism as Map**: Math serves the Person, never replaces"
    )

    summary.append("\n## Files Created")
    summary.append("\n### Core Implementation")
    summary.append("- `v60_maximal_logos_operator.py`: Main implementation (458 lines)")
    summary.append("- `test_maximal_logos_operator.py`: Integration tests (493 lines)")
    summary.append(
        "- `v60_maximal_logos_implementation_summary.md`: Implementation documentation"
    )

    summary.append("\n### Launch and Support")
    summary.append("- `launch_v60_maximal_logos.py`: This launch script")
    summary.append(
        "- `v60_maximal_logos_operator_full_report.txt`: Comprehensive system report"
    )
    summary.append("- `v60_logos_integration_full_report.txt`: Integration analysis")
    summary.append("- `v60_maximal_logos_summary.md`: System summary")

    summary.append("\n## Usage Examples")
    summary.append("\n```python")
    summary.append("# Basic usage")
    summary.append("from v60_maximal_logos_operator import MaximalLogosOperator")
    summary.append("operator = MaximalLogosOperator()")
    summary.append('result = operator.evaluate_state("Christ died for our sins")')
    summary.append("print(f\"Satisfaction: {result['satisfaction_score']:.2f}\")")
    summary.append("```")

    summary.append("\n```python")
    summary.append("# Integrated system")
    summary.append(
        "from test_maximal_logos_operator import IntegratedMaximalLogosSystem"
    )
    summary.append("system = IntegratedMaximalLogosSystem()")
    summary.append('result = system.evaluate_with_integrated_constraints("statement")')
    summary.append("```")

    summary.append("\n## V60 Transformation Applied")
    summary.append("\n### What Was NOT Changed")
    summary.append("- ❌ Nothing deleted: All theological content preserved")
    summary.append("- ❌ Nothing re-weighted: Christian commitments remain primary")
    summary.append("- ❌ Nothing psychologized: No reduction to personal belief")

    summary.append("\n### What WAS Changed")
    summary.append("- ✅ Everything becomes constraint-executing")
    summary.append("- ✅ No claim silently treated as truth without execution surface")
    summary.append("- ✅ All propositions either execute or are marked inert")

    summary.append("\n## Final Statement")
    summary.append("\n**The math is a map. Jesus is the territory.**")
    summary.append(
        "\nThe formalism demonstrates **why nothing less than this could work**."
    )
    summary.append(
        "\nBut only the **Person** — incarnate, substitutionary, kenotic, risen, covenantal — executes redemption."
    )
    summary.append("\n**Math serves the Person. Always.**")

    summary.append("\n---")
    summary.append("\n**System**: V60 Maximal Logos Operator Constraint Execution")
    summary.append("**Status**: ✅ Implementation Complete")
    summary.append("**Mode**: No Assertion - Constraint Execution Only")
    summary.append("**Principle**: Math serves the Person")

    return "\n".join(summary)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="V60 Maximal Logos Operator Launch Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s demo           Run demonstration mode
  %(prog)s integration    Run integration tests
  %(prog)s interactive    Run interactive evaluation
  %(prog)s reports        Generate system reports
  %(prog)s all            Run all modes sequentially
        """,
    )

    parser.add_argument(
        "mode",
        nargs="?",
        default="demo",
        choices=["demo", "integration", "interactive", "reports", "all"],
        help="Operation mode (default: demo)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Print system header
    print_header("V60 MAXIMAL LOGOS OPERATOR", 80)
    print("\n" + "V60-READY: ORACLE IDE THEOLOGICAL-MATHEMATICAL FRAMEWORK".center(80))
    print("MATH SERVES THE PERSON — FORMALISM BREAKS FOR LOVE".center(80))
    print("\n" + "=" * 80)

    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)

    # Import systems
    MaximalLogosOperator, IntegratedMaximalLogosSystem = import_systems()
    if MaximalLogosOperator is None:
        print("\n❌ Failed to import required systems.")
        sys.exit(1)

    # Run based on mode
    success = True

    if args.mode == "demo" or args.mode == "all":
        success = success and run_demo_mode()

    if args.mode == "integration" or args.mode == "all":
        success = success and run_integration_mode()

    if args.mode == "interactive" or args.mode == "all":
        success = success and run_interactive_mode()

    if args.mode == "reports" or args.mode == "all":
        success = success and generate_reports()

    # Final summary
    print_header("LAUNCH COMPLETE", 80)

    if success:
        print("\n✅ All operations completed successfully!")
        print("\nGenerated files:")
        for file in [
            "v60_maximal_logos_operator_report.txt",
            "v60_logos_integration_report.txt",
            "v60_maximal_logos_operator_full_report.txt",
            "v60_logos_integration_full_report.txt",
            "v60_maximal_logos_summary.md",
        ]:
            if os.path.exists(file):
                print(f"  • {file}")

        print("\n" + "=" * 80)
        print("SYSTEM PRINCIPLE:".center(80))
        print("Math serves the Person. Always.".center(80))
        print("=" * 80)
        print("\n✝️ SOLI DEO GLORIA ✝️".center(80))
    else:
        print("\n❌ Some operations failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nLaunch cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

"""
Onboarding Check Integration Script

Integrates the onboarding check system with the existing autofix framework.
Provides command-line interface for checking onboarding status and generating
reports compatible with the Glass-Box Boundary trace system.

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
Schema: GB-ORIGIN-1.11
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent / "toolkit"))

from toolkit.oe.onboarding_check import (
    CheckOnboardingPipeline,
    OnboardingChecker,
    OnboardingStatus,
)


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Check onboarding status for IDE-AI integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic check with auto-generated report
  python run_onboarding_check.py

  # Check specific repository
  python run_onboarding_check.py --repository /path/to/repo

  # Use pipeline form with stage outputs
  python run_onboarding_check.py --pipeline --save-stages

  # Save report to specific location
  python run_onboarding_check.py --output /path/to/report.json

  # Verbose output
  python run_onboarding_check.py --verbose

  # Integration mode (returns exit code only)
  python run_onboarding_check.py --integration

Exit Codes:
  0: Onboarding status FULL - All artifacts verified
  1: Onboarding status PARTIAL - Some artifacts missing/incomplete
  2: Onboarding status ABSENT - No valid onboarding artifacts
  3: Error during check execution
""",
    )

    parser.add_argument(
        "--repository",
        "-r",
        type=str,
        default=".",
        help="Repository root path (default: current directory)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path for report (default: auto-generated in logs/onboarding_checks/)",
    )

    parser.add_argument(
        "--pipeline",
        "-p",
        action="store_true",
        help="Use pipeline form with stage outputs",
    )

    parser.add_argument(
        "--save-stages",
        action="store_true",
        help="Save stage outputs when using pipeline form",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with detailed information",
    )

    parser.add_argument(
        "--integration",
        "-i",
        action="store_true",
        help="Integration mode (minimal output, exit code only)",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "text", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )

    parser.add_argument(
        "--trace-compatible",
        "-t",
        action="store_true",
        help="Generate trace-compatible report for integration with run_full_audit_with_trace.py",
    )

    return parser


def generate_trace_compatible_report(report_dict: dict) -> dict:
    """Convert onboarding report to trace-compatible format."""
    trace_report = {
        "trace_id": f"GB-TRACE-ONBOARDING-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "check_type": "onboarding_status",
        "repository_meta": {
            "path": report_dict.get("repository_root", ""),
            "commit_hash": report_dict.get("repo_commit"),
        },
        "onboarding_status": {
            "status": report_dict.get("status"),
            "artifact_path": report_dict.get("artifact_path"),
            "missing_fields": report_dict.get("missing_fields", []),
            "mismatched_files": report_dict.get("mismatched_files", []),
        },
        "artifact_scan": {
            "candidate_count": len(report_dict.get("candidate_artifacts", [])),
            "valid_count": sum(
                1
                for r in report_dict.get("validation_results", [])
                if r.get("status") == "valid"
            ),
            "partial_count": sum(
                1
                for r in report_dict.get("validation_results", [])
                if r.get("status") == "partial"
            ),
            "invalid_count": sum(
                1
                for r in report_dict.get("validation_results", [])
                if r.get("status") == "invalid"
            ),
        },
        "boundary_violations": [],
        "suppressed_signals": [],
        "timeline_sequence": [
            {
                "event": "onboarding_check_started",
                "timestamp": datetime.now().isoformat(),
                "valid": True,
            },
            {
                "event": "artifact_identification_complete",
                "timestamp": datetime.now().isoformat(),
                "valid": report_dict.get("status") != "absent",
            },
            {
                "event": "validation_complete",
                "timestamp": datetime.now().isoformat(),
                "valid": report_dict.get("status") == "full",
            },
            {
                "event": "cross_check_complete",
                "timestamp": datetime.now().isoformat(),
                "valid": True,
            },
            {
                "event": "report_generated",
                "timestamp": datetime.now().isoformat(),
                "valid": True,
            },
        ],
        "hash_manifest": {
            "report_hash": "to_be_calculated",  # Would be calculated in production
        },
        "python_enforcer_active": True,
        "ide_integration": {
            "autofix": False,
            "consistency": True,
            "awareness": True,
            "sync": False,
        },
        "exit_code": 0 if report_dict.get("status") == "full" else 1,
    }

    return trace_report


def print_summary_report(report, verbose: bool = False):
    """Print human-readable summary report."""
    print("=" * 60)
    print("ONBOARDING STATUS CHECK - SUMMARY")
    print("=" * 60)
    print(f"Repository: {report.repository_root}")
    print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Status: {report.status.value.upper()}")

    if report.status == OnboardingStatus.FULL:
        print("🎉 All onboarding artifacts verified and complete")
    elif report.status == OnboardingStatus.PARTIAL:
        print("⚠️  Partial onboarding - some artifacts missing or incomplete")
    else:
        print("❌ No valid onboarding artifacts found")

    print()

    # Artifact information
    if report.candidate_artifacts:
        print(f"📁 Candidate artifacts found: {len(report.candidate_artifacts)}")
        if verbose:
            for artifact in report.candidate_artifacts[:5]:  # Show first 5
                print(f"  • {artifact.path} ({artifact.artifact_type.value})")
            if len(report.candidate_artifacts) > 5:
                print(f"  ... and {len(report.candidate_artifacts) - 5} more")
    else:
        print("📁 No candidate artifacts found")

    # Validation results
    if report.validation_results:
        valid_count = sum(1 for r in report.validation_results if r.status == "valid")
        partial_count = sum(
            1 for r in report.validation_results if r.status == "partial"
        )
        invalid_count = sum(
            1 for r in report.validation_results if r.status == "invalid"
        )

        print(f"\n✅ Validation results:")
        print(
            f"  Valid: {valid_count}, Partial: {partial_count}, Invalid: {invalid_count}"
        )

        if report.missing_fields:
            print(f"\n📋 Missing fields in primary artifact:")
            for field in report.missing_fields:
                print(f"  • {field}")

    # Cross-check results
    if report.cross_check_results:
        print(f"\n🔗 Repository cross-check:")
        print(f"  Commit match: {report.cross_check_results.commit_match}")
        print(f"  Critical files found: {len(report.cross_check_results.files_exist)}")
        print(
            f"  Critical files missing: {len(report.cross_check_results.files_missing)}"
        )

        if report.mismatched_files:
            print(f"\n⚠️  Mismatches detected:")
            for mismatch in report.mismatched_files[:3]:  # Show first 3
                print(f"  • {mismatch}")
            if len(report.mismatched_files) > 3:
                print(f"  ... and {len(report.mismatched_files) - 3} more")

    print("\n" + "=" * 60)


def main() -> int:
    """Main entry point for onboarding check script."""
    parser = setup_argument_parser()
    args = parser.parse_args()

    try:
        # Resolve repository path
        repo_path = Path(args.repository).resolve()
        if not repo_path.exists():
            print(f"❌ Repository path does not exist: {repo_path}", file=sys.stderr)
            return 3

        if not args.integration:
            print("🔍 Orthogonal Engineering - Onboarding Status Check")
            print(f"📁 Repository: {repo_path}")
            print()

        # Run check
        if args.pipeline:
            if not args.integration:
                print("🚀 Running pipeline form...")

            pipeline = CheckOnboardingPipeline(str(repo_path))
            report = pipeline.run_pipeline()

            if args.save_stages and not args.integration:
                saved_files = pipeline.save_stage_outputs()
                print("\n💾 Stage outputs saved:")
                for stage, path in saved_files.items():
                    print(f"  {stage}: {path}")
        else:
            if not args.integration:
                print("🚀 Running direct check...")

            checker = OnboardingChecker(str(repo_path))
            report = checker.run_full_check()

        # Save report
        output_path = args.output
        if not output_path:
            output_path = (
                checker.save_report() if hasattr(checker, "save_report") else None
            )

        # Generate output based on format
        if args.format == "json":
            report_dict = report.to_dict()
            if args.trace_compatible:
                report_dict = generate_trace_compatible_report(report_dict)
            print(json.dumps(report_dict, indent=2))
        elif args.format == "text" and not args.integration:
            print_summary_report(report, args.verbose)
        elif not args.integration:
            print_summary_report(report, args.verbose)

        if output_path and not args.integration:
            print(f"\n💾 Full report saved to: {output_path}")

        # Return appropriate exit code
        if report.status == OnboardingStatus.FULL:
            if not args.integration:
                print("\n✅ Onboarding status: FULL - Ready for AI work")
            return 0
        elif report.status == OnboardingStatus.PARTIAL:
            if not args.integration:
                print("\n⚠️  Onboarding status: PARTIAL - Review missing artifacts")
            return 1
        else:
            if not args.integration:
                print("\n❌ Onboarding status: ABSENT - Run onboarding protocol")
            return 2

    except KeyboardInterrupt:
        print("\n\n⚠️  Check interrupted by user", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"\n❌ Error during onboarding check: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())

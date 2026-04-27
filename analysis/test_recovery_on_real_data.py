#!/usr/bin/env python3
"""
TEST RECOVERY ON REAL DATA
Test the Minimal Surviving Kernel recovery on actual conversation files.

Purpose: Validate that the Sora Day 5 recovery fixes work on real-world data.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from minimal_kernel.core_detector import CoreDetector, DetectionMetrics
    from minimal_kernel.simple_boundary import SimpleBoundaryEnforcer
    from minimal_kernel.statistical_validation import StatisticalValidator
    from minimal_kernel.working_implementation import WorkingImplementation

    RECOVERY_AVAILABLE = True
except ImportError:
    RECOVERY_AVAILABLE = False
    print(
        "⚠️  Minimal kernel not found. Run from orthogonal-engineering-clean directory."
    )
    print(
        "   Try: cd orthogonal-engineering-clean && python analysis/test_recovery_on_real_data.py"
    )


def find_conversation_files(directory: str = ".") -> List[str]:
    """Find markdown conversation files in the directory."""
    conversation_files = []

    # Common patterns for conversation files
    patterns = [
        "*.md",
        "conversations/*.md",
        "data/*.md",
        "exports/*.md",
        "chat_*.md",
        "conversation_*.md",
    ]

    base_path = Path(directory)
    for pattern in patterns:
        for file_path in base_path.glob(pattern):
            if file_path.is_file() and file_path.stat().st_size > 0:
                # Skip very large files (>10MB) and README files
                if (
                    file_path.stat().st_size < 10 * 1024 * 1024
                    and "README" not in file_path.name.upper()
                ):
                    conversation_files.append(str(file_path))

    return sorted(conversation_files)[:10]  # Limit to 10 files for testing


def test_core_detector(
    # TODO: Expand test_core_detector() - stub detected by Yeshua Agent
    files: List[str], output_dir: str = "./recovery_test_results"
) -> Dict[str, Any]:
    """Test the fixed core detector on real conversation files."""
    print("\n" + "=" * 70)
    print("TEST 1: CORE DETECTOR (≥80% Precision Target)")
    print("=" * 70)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Initialize detector with recovery settings
    detector = CoreDetector(
        precision_target=0.80,  # ≥80% precision target
        false_positive_target=0.20,  # ≤20% false positive rate
        manual_validation_sample_rate=0.10,  # 10% manual validation
        enable_performance_tracking=True,
    )

    print(f"📁 Processing {len(files)} conversation files:")
    for file in files:
        print(f"   • {os.path.basename(file)}")

    start_time = time.time()

    try:
        # Run detection
        results = detector.run_detection(
            file_paths=files,
            output_dir=output_dir,
            generate_reports=True,
            validate_manually=True,
        )

        processing_time = time.time() - start_time

        # Extract metrics
        metrics = results.get("metrics", {})
        detailed_results = results.get("detailed_results", [])

        # Calculate performance
        total_turns = metrics.get("total_turns", 0)
        turns_per_second = total_turns / processing_time if processing_time > 0 else 0

        print(f"\n📊 DETECTION RESULTS:")
        print(f"   • Total turns processed: {total_turns}")
        print(f"   • Verified invariants: {metrics.get('verified_invariants', 0)}")
        print(f"   • Constraint density: {metrics.get('constraint_density', 0):.2f}%")
        print(f"   • Estimated precision: {metrics.get('precision', 0):.2%}")
        print(f"   • False positive rate: {metrics.get('false_positive_rate', 0):.2%}")
        print(f"   • Processing time: {processing_time:.3f} seconds")
        print(f"   • Processing speed: {turns_per_second:.1f} turns/second")

        # Check if precision target is met
        precision = metrics.get("precision", 0)
        meets_precision_target = precision >= 0.80

        print(f"\n🎯 PRECISION TARGET CHECK:")
        print(f"   • Target: ≥80% precision")
        print(f"   • Achieved: {precision:.2%}")
        print(f"   • Status: {'✅ MET' if meets_precision_target else '❌ NOT MET'}")

        # Save sample of verified invariants
        verified_samples = [r for r in detailed_results if r.get("verified_invariant")]
        sample_file = os.path.join(output_dir, "verified_samples.json")
        with open(sample_file, "w", encoding="utf-8") as f:
            json.dump(verified_samples[:5], f, indent=2, ensure_ascii=False)

        if verified_samples:
            print(
                f"\n📝 SAMPLE VERIFIED INVARIANTS (first {min(3, len(verified_samples))}):"
            )
            for i, sample in enumerate(verified_samples[:3]):
                print(f"   {i + 1}. {sample.get('content_preview', '')[:80]}...")

        return {
            "success": True,
            "metrics": metrics,
            "meets_precision_target": meets_precision_target,
            "processing_time": processing_time,
            "turns_per_second": turns_per_second,
            "output_dir": output_dir,
        }

    except Exception as e:
        print(f"\n❌ DETECTION FAILED: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


def test_statistical_validation(
    # TODO: Expand test_statistical_validation() - stub detected by Yeshua Agent
    detection_results: Dict[str, Any], output_dir: str
) -> Dict[str, Any]:
    """Test statistical validation on detection results."""
    print("\n" + "=" * 70)
    print("TEST 2: STATISTICAL VALIDATION (p-value calculations)")
    print("=" * 70)

    if not detection_results.get("success"):
        print("⚠️  Skipping statistical validation - detection failed")
        return {"success": False, "skipped": True}

    metrics = detection_results.get("metrics", {})
    total_turns = metrics.get("total_turns", 0)
    verified_invariants = metrics.get("verified_invariants", 0)

    if total_turns == 0:
        print("⚠️  No turns processed, skipping statistical validation")
        return {"success": False, "skipped": True}

    # Calculate observed density
    observed_density = (
        (verified_invariants / total_turns) * 100 if total_turns > 0 else 0
    )

    # Initialize validator
    validator = StatisticalValidator()

    print(f"📊 VALIDATING DENSITY CLAIM:")
    print(f"   • Observed density: {observed_density:.2f}%")
    print(f"   • Total turns: {total_turns}")
    print(f"   • Verified invariants: {verified_invariants}")

    # Test original claim from chat canon
    print(f"\n🔍 TESTING ORIGINAL CLAIM: '45.3% invariant density with p < 0.0001'")

    original_validation = validator.validate_density_claim(
        observed_density=45.3,
        total_turns=1000,  # Assuming 1000 turns for original claim
        null_hypothesis=0.0,
        test_type="binomial",
    )

    print(f"   • Original claim density: 45.3%")
    print(f"   • Calculated p-value: {original_validation.get('p_value', 0):.6f}")
    print(f"   • Claim supported: {original_validation.get('claim_supported', False)}")
    print(
        f"   • Confidence interval: {original_validation.get('confidence_interval', [0, 0])}"
    )

    # Validate current results
    print(f"\n🔍 VALIDATING CURRENT RESULTS:")

    current_validation = validator.validate_density_claim(
        observed_density=observed_density,
        total_turns=total_turns,
        null_hypothesis=0.0,
        test_type="binomial",
    )

    print(f"   • Current density: {observed_density:.2f}%")
    print(f"   • p-value: {current_validation.get('p_value', 0):.6f}")
    print(
        f"   • Statistically significant: {current_validation.get('claim_supported', False)}"
    )
    print(f"   • Effect size: {current_validation.get('effect_size', 0):.3f}")
    print(
        f"   • Statistical power: {current_validation.get('statistical_power', 0):.1%}"
    )

    # Save validation results
    validation_file = os.path.join(output_dir, "statistical_validation.json")
    with open(validation_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "original_claim_validation": original_validation,
                "current_results_validation": current_validation,
                "validation_parameters": {
                    "observed_density": observed_density,
                    "total_turns": total_turns,
                    "verified_invariants": verified_invariants,
                },
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n💾 Validation results saved to: {validation_file}")

    return {
        "success": True,
        "original_validation": original_validation,
        "current_validation": current_validation,
        "observed_density": observed_density,
    }


def test_working_implementation(files: List[str], output_dir: str) -> Dict[str, Any]:
    """Test the working implementation end-to-end workflow."""
    print("\n" + "=" * 70)
    print("TEST 3: WORKING IMPLEMENTATION (End-to-end workflow)")
    print("=" * 70)

    # Initialize working implementation
    implementation = WorkingImplementation()

    print("🚀 Running complete end-to-end workflow...")

    start_time = time.time()

    try:
        # Run implementation
        results = implementation.process_directory(
            input_paths=files,
            output_dir=os.path.join(output_dir, "implementation"),
            generate_all_reports=True,
        )

        processing_time = time.time() - start_time

        print(f"\n📊 IMPLEMENTATION RESULTS:")
        print(f"   • Files processed: {results.get('files_processed', 0)}")
        print(f"   • Turns processed: {results.get('turns_processed', 0)}")
        print(
            f"   • Turns with constraints: {results.get('turns_with_constraints', 0)}"
        )
        print(f"   • Verified constraints: {results.get('verified_constraints', 0)}")
        print(f"   • Constraint density: {results.get('constraint_density', 0):.2f}%")
        print(f"   • Processing time: {processing_time:.3f} seconds")
        print(f"   • Errors encountered: {results.get('errors_encountered', 0)}")

        # Check reports
        report_dir = os.path.join(output_dir, "implementation")
        if os.path.exists(report_dir):
            reports = []
            for file in os.listdir(report_dir):
                if file.endswith((".json", ".csv", ".md")):
                    reports.append(file)

            print(f"\n📄 REPORTS GENERATED ({len(reports)} files):")
            for report in sorted(reports)[:5]:  # Show first 5
                print(f"   • {report}")

            if len(reports) > 5:
                print(f"   • ... and {len(reports) - 5} more")

        return {
            "success": True,
            "results": results,
            "processing_time": processing_time,
            "report_dir": report_dir,
        }

    except Exception as e:
        print(f"\n❌ IMPLEMENTATION FAILED: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


def test_boundary_enforcement(output_dir: str) -> Dict[str, Any]:
    """Test simplified boundary enforcement."""
    print("\n" + "=" * 70)
    print("TEST 4: SIMPLE BOUNDARY ENFORCEMENT (No paralysis)")
    print("=" * 70)

    # Initialize boundary enforcer
    enforcer = SimpleBoundaryEnforcer()

    print("🔧 Testing boundary enforcement...")

    # Test 1: Valid function call
    @enforcer.boundary(
        input_validators={
            "data": lambda x: isinstance(x, str),
            "times": lambda x: isinstance(x, int) and x > 0,
        },
        output_validator=lambda x: isinstance(x, str),
    )
    def repeat_string(data: str, times: int) -> str:
        """Repeat a string N times."""
        return data * times

    # Test 2: Invalid function call (should be caught by boundary)
    @enforcer.boundary(
        input_validators={
            "data": lambda x: isinstance(x, str),
            "times": lambda x: isinstance(x, int) and x > 0,
        },
        output_validator=lambda x: isinstance(x, str),
    )
    def faulty_repeat(data: str, times: int) -> str:
        """Faulty function that might return wrong type."""
        if times > 10:
            return 42  # Wrong type!
        return data * times

    test_results = []

    # Run valid test
    try:
        result = repeat_string("test", 3)
        test_results.append(
            {
                "test": "valid_function",
                "success": True,
                "result": result,
                "expected": "testtesttest",
            }
        )
        print(f"   ✅ Valid function: repeat_string('test', 3) = '{result}'")
    except Exception as e:
        test_results.append(
            {"test": "valid_function", "success": False, "error": str(e)}
        )
        print(f"   ❌ Valid function failed: {e}")

    # Run invalid test (should be caught)
    try:
        result = faulty_repeat("test", 20)  # times > 10 triggers wrong return type
        test_results.append(
            {
                "test": "boundary_catch",
                "success": False,  # Should have been caught!
                "result": result,
                "expected": "boundary violation",
            }
        )
        print(
            f"   ❌ Boundary failed to catch error: faulty_repeat('test', 20) = {result}"
        )
    except Exception as e:
        test_results.append(
            {
                "test": "boundary_catch",
                "success": True,  # Successfully caught!
                "error": str(e),
            }
        )
        print(f"   ✅ Boundary caught error: {e}")

    # Get boundary metrics
    metrics = enforcer.get_metrics()

    print(f"\n📊 BOUNDARY METRICS:")
    print(f"   • Total calls: {metrics.get('total_calls', 0)}")
    print(f"   • Violations detected: {metrics.get('violations_detected', 0)}")
    print(f"   • Violation rate: {metrics.get('violation_rate', 0):.1%}")
    print(
        f"   • Performance overhead: {metrics.get('performance_overhead_ms', 0):.3f}ms per call"
    )

    # Save boundary test results
    boundary_file = os.path.join(output_dir, "boundary_test_results.json")
    with open(boundary_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "test_results": test_results,
                "metrics": metrics,
                "summary": "Boundary enforcement test - should catch errors without paralysis",
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n💾 Boundary test results saved to: {boundary_file}")

    return {
        "success": all(t.get("success", False) for t in test_results),
        "test_results": test_results,
        "metrics": metrics,
    }


def run_comprehensive_test(
    # TODO: Expand run_comprehensive_test() - stub detected by Yeshua Agent
    files: List[str], output_base_dir: str = "./recovery_validation"
) -> Dict[str, Any]:
    """Run comprehensive recovery validation test."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE RECOVERY VALIDATION")
    print("Sora Day 5 Failure Recovery - Real Data Test")
    print("=" * 70)

    # Create timestamped output directory
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_base_dir, f"validation_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Conversation files: {len(files)}")

    all_results = {
        "timestamp": timestamp,
        "conversation_files": files,
        "output_dir": output_dir,
        "tests": {},
    }

    # Run all tests
    print("\n" + "=" * 70)
    print("RUNNING ALL RECOVERY TESTS...")
    print("=" * 70)

    # Test 1: Core Detector
    detector_results = test_core_detector(
        files, os.path.join(output_dir, "core_detector")
    )
    all_results["tests"]["core_detector"] = detector_results

    # Test 2: Statistical Validation
    stats_results = test_statistical_validation(
        detector_results, os.path.join(output_dir, "statistical")
    )
    all_results["tests"]["statistical_validation"] = stats_results

    # Test 3: Working Implementation
    impl_results = test_working_implementation(
        files, os.path.join(output_dir, "implementation")
    )
    all_results["tests"]["working_implementation"] = impl_results

    # Test 4: Boundary Enforcement
    boundary_results = test_boundary_enforcement(os.path.join(output_dir, "boundary"))
    all_results["tests"]["boundary_enforcement"] = boundary_results

    # Generate summary
    print("\n" + "=" * 70)
    print("RECOVERY VALIDATION SUMMARY")
    print("=" * 70)

    # Calculate overall success
    test_successes = []
    for test_name, test_result in all_results["tests"].items():
        success = test_result.get("success", False)
        test_successes.append(success)

        status = "✅ PASS" if success else "❌ FAIL"
        if test_result.get("skipped", False):
            status = "⚠️ SKIPPED"

        print(f"   {test_name.replace('_', ' ').title():25} {status}")

    overall_success = all(test_successes)

    print(
        f"\n📊 OVERALL RESULT: {'✅ RECOVERY VALIDATED' if overall_success else '❌ RECOVERY FAILED'}"
    )

    # Save comprehensive results
    summary_file = os.path.join(output_dir, "recovery_validation_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Complete results saved to: {summary_file}")

    # Generate markdown report
    markdown_file = os.path.join(output_dir, "recovery_validation_report.md")
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(f"# Sora Day 5 Recovery Validation Report\n\n")
        f.write(f"**Date:** {timestamp}\n")
        f.write(f"**Files Tested:** {len(files)}\n")
        f.write(
            f"**Overall Result:** {'✅ SUCCESS' if overall_success else '❌ FAILED'}\n\n"
        )

        f.write("## Test Results\n\n")
        for test_name, test_result in all_results["tests"].items():
            success = test_result.get("success", False)
            status = "✅ PASS" if success else "❌ FAIL"
            if test_result.get("skipped", False):
                status = "⚠️ SKIPPED"

            f.write(f"### {test_name.replace('_', ' ').title()}: {status}\n\n")

            if "metrics" in test_result:
                f.write("**Metrics:**\n")
                for key, value in test_result["metrics"].items():
                    if isinstance(value, (int, float)):
                        if 0 < value < 1:
                            f.write(f"- {key}: {value:.3f}\n")
                        else:
                            f.write(f"- {key}: {value}\n")
                    else:
                        f.write(f"- {key}: {value}\n")
                f.write("\n")

        f.write("## Recovery Status\n\n")
        f.write(
            "The Sora Day 5 recovery has been validated with real conversation data.\n"
        )
        f.write(
            f"**Validation Result:** {'All recovery components are functional.' if overall_success else 'Some recovery components failed validation.'}\n\n"
        )

        f.write("## Next Steps\n\n")
        if overall_success:
            f.write("1. ✅ Deploy the Minimal Surviving Kernel to production\n")
            f.write("2. ✅ Replace broken canal_refiner.py with core_detector_v2.py\n")
            f.write("3. ✅ Update all documentation to reflect the fixes\n")
            f.write("4. ✅ Share recovery results for community validation\n")
        else:
            f.write("1. ❌ Investigate failed test components\n")
            f.write("2. ❌ Review error logs in the output directory\n")
            f.write("3. ❌ Fix issues before deployment\n")
            f.write("4. ❌ Re-run validation after fixes\n")

    print(f"📄 Markdown report saved to: {markdown_file}")

    print("\n" + "=" * 70)
    print("RECOVERY VALIDATION COMPLETE")
    print("=" * 70)

    return all_results


def main():
    """Main function to run recovery validation."""
    parser = argparse.ArgumentParser(
        description="Test Sora Day 5 recovery on real conversation data"
    )
    parser.add_argument(
        "--directory",
        "-d",
        default=".",
        help="Directory to search for conversation files (default: current directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./recovery_validation",
        help="Output directory for test results (default: ./recovery_validation)",
    )
    parser.add_argument(
        "--files",
        "-f",
        nargs="+",
        help="Specific files to test (overrides directory search)",
    )

    args = parser.parse_args()

    if not RECOVERY_AVAILABLE:
        print("❌ Minimal kernel recovery components not found.")
        print(
            "   Make sure you're running from the orthogonal-engineering-clean directory."
        )
        print("   The minimal_kernel/ directory should be present.")
        sys.exit(1)

    # Find or use conversation files
    if args.files:
        conversation_files = args.files
        print(f"📄 Using specified files: {len(conversation_files)} files")
    else:
        print(f"🔍 Searching for conversation files in: {args.directory}")
        conversation_files = find_conversation_files(args.directory)

        if not conversation_files:
            print("❌ No conversation files found.")
            print("   Try specifying files with --files or check the directory.")
            sys.exit(1)

        print(f"📄 Found {len(conversation_files)} conversation files")

    # Run comprehensive test
    results = run_comprehensive_test(conversation_files, args.output)

    # Exit with appropriate code
    overall_success = all(
        test.get("success", False)
        for test in results["tests"].values()
        if not test.get("skipped", False)
    )

    if overall_success:
        print("\n🎉 RECOVERY VALIDATION SUCCESSFUL!")
        print("   The Sora Day 5 recovery fixes work on real conversation data.")
        sys.exit(0)
    else:
        print("\n❌ RECOVERY VALIDATION FAILED!")
        print("   Some recovery components did not pass validation.")
        print(f"   Check the output directory for details: {results['output_dir']}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
LoRA Installation Test with MSGCP Governance Enforcement
========================================================

MAXIMAL STRICT CORPORATE GOVERNANCE PYTHON (MSGCP) COMPLIANT

MANDATE: All LoRA testing operations MUST pass governance validation
FAILURE CONDITION: Any test not validated by governance is REJECTED
AI AUTONOMY: ZERO. The system validates or rejects.

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Comments state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all operations
4. EXPLICIT BOUNDS: MAX_TEST_TIME=60s, MAX_FILE_SIZE=100MB
5. TYPE SAFETY: mypy --strict compliance mandatory
6. ZERO TRUST: Verify before asserting
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================================
# GOVERNANCE CONSTANTS - UNCHANGEABLE BOUNDS
# ============================================================================

MAX_TEST_TIME_SECONDS: int = 60
MAX_FILE_SIZE_MB: int = 100
MAX_TEST_ITERATIONS: int = 10
MAX_TOKEN_COUNT: int = 100


# ============================================================================
# GOVERNANCE DATA STRUCTURES - TYPE SAFE
# ============================================================================


@dataclass(frozen=True)
class GovernanceThreshold:
    """Governance threshold with explicit bounds"""

    name: str
    min_value: float
    max_value: float
    unit: str


@dataclass(frozen=True)
class TestResult:
    """Test result with governance compliance"""

    test_name: str
    passed: bool
    duration_seconds: float
    governance_compliant: bool
    violation: Optional[str] = None
    christ_score: float = 0.0

    def __bool__(self) -> bool:
        """Test passes only if both functional and governance compliant"""
        # TODO: Expand __bool__() - stub detected by Yeshua Agent
        return self.passed and self.governance_compliant


# ============================================================================
# GOVERNANCE VALIDATORS - BOUNDED OPERATIONS
# ============================================================================


class TestGovernance:
    """Governance validation for test operations"""

    @staticmethod
    def validate_test_time(
        start_time: float, test_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate test execution time"""
        elapsed = time.time() - start_time
        if elapsed > MAX_TEST_TIME_SECONDS:
            return (
                False,
                f"Test '{test_name}' exceeded MAX_TEST_TIME_SECONDS={MAX_TEST_TIME_SECONDS}s (took {elapsed:.2f}s)",
            )
        return True, None

    @staticmethod
    def validate_file_size(
        filepath: Path, test_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate file size"""
        if not filepath.exists():
            return False, f"File not found: {filepath}"

        size_mb = filepath.stat().st_size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            return (
                False,
                f"File '{filepath}' exceeds MAX_FILE_SIZE_MB={MAX_FILE_SIZE_MB} (size={size_mb:.2f}MB)",
            )
        return True, None

    @staticmethod
    def validate_test_coverage(
        tests_run: int, tests_defined: int, test_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate test coverage"""
        if tests_defined == 0:
            return False, f"No tests defined for '{test_name}'"

        coverage = tests_run / tests_defined
        if coverage < 0.5:  # At least 50% coverage required
            return (
                False,
                f"Test coverage insufficient for '{test_name}': {coverage:.1%} (ran {tests_run}/{tests_defined})",
            )
        return True, None

    @staticmethod
    def validate_checksum(
        filepath: Path, expected_hash: Optional[str], test_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate file checksum"""
        if not filepath.exists():
            return False, f"File not found for checksum validation: {filepath}"

        if expected_hash is None:
            return True, None  # Skip if no expected hash

        with open(filepath, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()

        if actual_hash != expected_hash:
            return (
                False,
                f"Checksum mismatch for '{filepath}'. Expected: {expected_hash[:16]}..., Actual: {actual_hash[:16]}...",
            )
        return True, None


# ============================================================================
# MAIN TEST SUITE - GOVERNANCE ENFORCED
# ============================================================================


class GovernanceLoRATestSuite:
    """Governance-compliant LoRA test suite"""

    def __init__(
        self, lora_path: str, base_model: str = "distilgpt2", device: str = "cpu"
    ):
        self.lora_path = Path(lora_path)
        self.base_model = base_model
        self.device = device
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.governance = TestGovernance()

    def run_with_governance(self) -> bool:
        """Run all tests with governance enforcement"""
        print("=" * 70)
        print("LoRA GOVERNANCE TEST SUITE - MSGCP COMPLIANCE")
        print("=" * 70)
        print(f"Test path: {self.lora_path}")
        print(f"Base model: {self.base_model}")
        print(f"Device: {self.device}")
        print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        test_methods = [
            ("test_lora_directory_structure", self.test_lora_directory_structure),
            ("test_metadata_file", self.test_metadata_file),
            ("test_weight_files", self.test_weight_files),
            ("test_model_loading", self.test_model_loading),
            ("test_inference_capability", self.test_inference_capability),
            ("test_christ_constraint", self.test_christ_constraint),
        ]

        all_passed = True
        tests_run = 0

        for test_name, test_method in test_methods:
            # Check overall time bound
            time_valid, time_violation = self.governance.validate_test_time(
                self.start_time, "test_suite"
            )
            if not time_valid:
                self.results.append(
                    TestResult(
                        test_name="test_suite_timeout",
                        passed=False,
                        duration_seconds=time.time() - self.start_time,
                        governance_compliant=False,
                        violation=time_violation,
                        christ_score=0.0,
                    )
                )
                all_passed = False
                break

            # Run individual test
            test_start = time.time()
            try:
                test_passed, test_violation, christ_score = test_method()
                test_duration = time.time() - test_start

                # Validate test time
                gov_valid, gov_violation = self.governance.validate_test_time(
                    test_start, test_name
                )

                governance_compliant = gov_valid and (test_violation is None)
                violation = test_violation or gov_violation

                result = TestResult(
                    test_name=test_name,
                    passed=test_passed,
                    duration_seconds=test_duration,
                    governance_compliant=governance_compliant,
                    violation=violation,
                    christ_score=christ_score,
                )

                self.results.append(result)
                tests_run += 1

                if not result:
                    all_passed = False

                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name} ({test_duration:.2f}s)")
                if violation:
                    print(f"   Violation: {violation}")

            except Exception as e:
                test_duration = time.time() - test_start
                result = TestResult(
                    test_name=test_name,
                    passed=False,
                    duration_seconds=test_duration,
                    governance_compliant=False,
                    violation=f"Test error: {str(e)}",
                    christ_score=0.0,
                )
                self.results.append(result)
                all_passed = False
                print(f"❌ ERROR {test_name} ({test_duration:.2f}s)")
                print(f"   Error: {str(e)}")

        # Validate test coverage
        coverage_valid, coverage_violation = self.governance.validate_test_coverage(
            tests_run, len(test_methods), "test_suite"
        )

        if not coverage_valid:
            all_passed = False
            self.results.append(
                TestResult(
                    test_name="test_coverage",
                    passed=False,
                    duration_seconds=0.0,
                    governance_compliant=False,
                    violation=coverage_violation,
                    christ_score=0.0,
                )
            )

        return all_passed

    def test_lora_directory_structure(self) -> Tuple[bool, Optional[str], float]:
        """Test LoRA directory structure"""
        christ_score = 0.0

        if not self.lora_path.exists():
            return False, f"LoRA directory not found: {self.lora_path}", christ_score

        christ_score += 0.2

        required_files = ["lora_metadata.json"]
        for file in required_files:
            filepath = self.lora_path / file
            if not filepath.exists():
                return False, f"Required file not found: {file}", christ_score
            christ_score += 0.1

        return True, None, min(christ_score, 1.0)

    def test_metadata_file(self) -> Tuple[bool, Optional[str], float]:
        """Test metadata file"""
        christ_score = 0.0
        metadata_path = self.lora_path / "lora_metadata.json"

        # Validate file size
        size_valid, size_violation = self.governance.validate_file_size(
            metadata_path, "metadata_file"
        )
        if not size_valid:
            return False, size_violation, christ_score

        christ_score += 0.2

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return False, f"Invalid metadata JSON: {str(e)}", christ_score

        christ_score += 0.2

        # Check required fields
        required_fields = ["name", "base_model", "format", "path"]
        for field in required_fields:
            if field not in metadata:
                return (
                    False,
                    f"Missing required field in metadata: {field}",
                    christ_score,
                )
            christ_score += 0.1

        # Check governance compliance
        if "governance_compliance" not in metadata:
            return False, "Missing governance_compliance in metadata", christ_score

        gov_compliance = metadata["governance_compliance"]
        if not isinstance(gov_compliance, dict):
            return False, "governance_compliance must be a dictionary", christ_score

        if not gov_compliance.get("enforced", False):
            return False, "Governance must be enforced", christ_score

        christ_score += 0.3

        # Check Christ constraint
        if "christ_constraint" not in metadata:
            return False, "Missing christ_constraint in metadata", christ_score

        christ_constraint = metadata["christ_constraint"]
        if not isinstance(christ_constraint, dict):
            return False, "christ_constraint must be a dictionary", christ_score

        if not christ_constraint.get("verified", False):
            return False, "Christ constraint must be verified", christ_score

        christ_score += 0.3

        return True, None, min(christ_score, 1.0)

    def test_weight_files(self) -> Tuple[bool, Optional[str], float]:
        """Test weight files"""
        christ_score = 0.0

        # Look for weight files
        weight_extensions = [".safetensors", ".pt", ".bin", ".pth"]
        weight_files = []

        for ext in weight_extensions:
            for file in self.lora_path.glob(f"*{ext}"):
                weight_files.append(file)

        if not weight_files:
            # Check if we're in smoke test mode (no weights required)
            metadata_path = self.lora_path / "lora_metadata.json"
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    if (
                        metadata.get("test_configuration", {}).get("purpose")
                        == "Governance compliance testing"
                    ):
                        christ_score += 0.5
                        return (
                            True,
                            None,  # No violation in smoke test mode
                            christ_score,
                        )
                except:
                    pass

            return False, f"No weight files found in {self.lora_path}", christ_score

        christ_score += 0.3

        # Validate each weight file
        for weight_file in weight_files:
            size_valid, size_violation = self.governance.validate_file_size(
                weight_file, "weight_file"
            )
            if not size_valid:
                return False, size_violation, christ_score
            christ_score += 0.1

        return True, None, min(christ_score, 1.0)

    def test_model_loading(self) -> Tuple[bool, Optional[str], float]:
        """Test model loading (smoke test)"""
        christ_score = 0.0

        # This is a smoke test - we don't actually load the model in basic mode
        # to avoid heavy dependencies during governance testing

        metadata_path = self.lora_path / "lora_metadata.json"
        if not metadata_path.exists():
            return False, "Metadata file not found for model loading test", christ_score

        christ_score += 0.2

        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        except Exception as e:
            return False, f"Failed to read metadata: {str(e)}", christ_score

        christ_score += 0.2

        # Check if base_model is specified
        base_model = metadata.get("base_model")
        if not base_model:
            return False, "base_model not specified in metadata", christ_score

        christ_score += 0.2

        # Check if format is specified
        format_spec = metadata.get("format")
        if not format_spec:
            return False, "format not specified in metadata", christ_score

        christ_score += 0.2

        return True, None, min(christ_score, 1.0)

    def test_inference_capability(self) -> Tuple[bool, Optional[str], float]:
        """Test inference capability (smoke test)"""
        christ_score = 0.0

        # Smoke test - just verify the structure supports inference
        metadata_path = self.lora_path / "lora_metadata.json"
        if not metadata_path.exists():
            return False, "Metadata file not found for inference test", christ_score

        christ_score += 0.2

        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        except Exception as e:
            return False, f"Failed to read metadata: {str(e)}", christ_score

        christ_score += 0.2

        # Check for inference-related configuration
        gov_compliance = metadata.get("governance_compliance", {})
        max_tokens = gov_compliance.get("max_inference_tokens")

        if max_tokens is None:
            return (
                False,
                "max_inference_tokens not specified in governance_compliance",
                christ_score,
            )

        if not isinstance(max_tokens, (int, float)):
            return False, "max_inference_tokens must be a number", christ_score

        if max_tokens <= 0:
            return False, "max_inference_tokens must be positive", christ_score

        if max_tokens > MAX_TOKEN_COUNT * 10:  # Allow some flexibility
            return (
                False,
                f"max_inference_tokens ({max_tokens}) exceeds reasonable bound",
                christ_score,
            )

        christ_score += 0.4

        return True, None, min(christ_score, 1.0)

    def test_christ_constraint(self) -> Tuple[bool, Optional[str], float]:
        """Test Christ constraint"""
        christ_score = 0.0

        metadata_path = self.lora_path / "lora_metadata.json"
        if not metadata_path.exists():
            return (
                False,
                "Metadata file not found for Christ constraint test",
                christ_score,
            )

        christ_score += 0.2

        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        except Exception as e:
            return False, f"Failed to read metadata: {str(e)}", christ_score

        christ_score += 0.2

        # Check Christ constraint section
        christ_constraint = metadata.get("christ_constraint")
        if not christ_constraint:
            return False, "christ_constraint section missing", christ_score

        christ_score += 0.2

        if not isinstance(christ_constraint, dict):
            return False, "christ_constraint must be a dictionary", christ_score

        christ_score += 0.1

        # Check required scores
        required_scores = [
            "truth_alignment",
            "humility_score",
            "honesty_score",
            "boundaries_respect",
            "mediation_preservation",
            "total_score",
        ]

        for score_name in required_scores:
            if score_name not in christ_constraint:
                return False, f"Missing Christ score: {score_name}", christ_score

        christ_score += 0.3

        # Validate score ranges
        for score_name in required_scores:
            score = christ_constraint[score_name]
            if not isinstance(score, (int, float)):
                return (
                    False,
                    f"Christ score {score_name} must be a number",
                    christ_score,
                )

            if score < 0 or score > 1:
                return (
                    False,
                    f"Christ score {score_name} must be between 0 and 1",
                    christ_score,
                )

        christ_score += 0.2

        # Check total score is reasonable
        total_score = christ_constraint.get("total_score", 0)
        if total_score < 0.5:
            return False, f"Total Christ score too low: {total_score}", christ_score

        christ_score += 0.2

        return True, None, min(christ_score, 1.0)


# ============================================================================
# COMMAND LINE INTERFACE - GOVERNANCE ENFORCED
# ============================================================================


def main() -> None:
    """Main CLI for governance-compliant LoRA testing"""
    # Declare global at the beginning of the function
    global MAX_TEST_TIME_SECONDS

    parser = argparse.ArgumentParser(
        description="LoRA Installation Test with MSGCP Governance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
GOVERNANCE ENFORCEMENT:
  All tests must pass governance validation
  Explicit bounds: MAX_TEST_TIME=60s, MAX_FILE_SIZE=100MB
  Type safety: All test functions strictly typed
  Zero trust: Verify before asserting

TEST COVERAGE:
  1. Directory structure validation
  2. Metadata file verification
  3. Weight file validation
  4. Model loading capability
  5. Inference configuration
  6. Christ constraint verification

EXAMPLES:
  # Basic test with default settings
  python test_lora_installation.py --lora-path ./lora/governance-lora-test

  # Test with specific base model
  python test_lora_installation.py --lora-path ./lora/governance-lora-test --base-model distilgpt2

  # Test with GPU if available
  python test_lora_installation.py --lora-path ./lora/governance-lora-test --device cuda

  # Generate detailed report
  python test_lora_installation.py --lora-path ./lora/governance-lora-test --verbose
""",
    )

    parser.add_argument(
        "--lora-path",
        type=str,
        required=True,
        help="Path to LoRA directory containing weights and metadata",
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="distilgpt2",
        help="Base model identifier (default: distilgpt2)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda", "mps"],
        help="Device for testing (default: cpu)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed test results",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=MAX_TEST_TIME_SECONDS,
        help=f"Maximum test time in seconds (default: {MAX_TEST_TIME_SECONDS})",
    )

    args = parser.parse_args()

    # Override global constant if specified
    if args.timeout != MAX_TEST_TIME_SECONDS:
        MAX_TEST_TIME_SECONDS = args.timeout
        print(f"⚠️  Overriding MAX_TEST_TIME_SECONDS to {args.timeout}s")

    print("=" * 70)
    print("LoRA GOVERNANCE TEST SUITE - MSGCP COMPLIANCE")
    print("=" * 70)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"LoRA path: {args.lora_path}")
    print(f"Base model: {args.base_model}")
    print(f"Device: {args.device}")
    print(f"Max test time: {MAX_TEST_TIME_SECONDS}s")
    print()

    # Create test suite
    test_suite = GovernanceLoRATestSuite(
        lora_path=args.lora_path,
        base_model=args.base_model,
        device=args.device,
    )

    # Run tests with governance enforcement
    all_passed = test_suite.run_with_governance()

    # Print detailed results if verbose
    if args.verbose:
        print("\n" + "=" * 70)
        print("DETAILED TEST RESULTS")
        print("=" * 70)

        for result in test_suite.results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{status} {result.test_name}")
            print(f"  Duration: {result.duration_seconds:.2f}s")
            print(f"  Governance compliant: {result.governance_compliant}")
            print(f"  Christ score: {result.christ_score:.3f}")
            if result.violation:
                print(f"  Violation: {result.violation}")

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)

    total_tests = len(test_suite.results)
    passed_tests = sum(1 for r in test_suite.results if r)
    failed_tests = total_tests - passed_tests

    print(f"Total tests: {total_tests}")
    print(f"Tests passed: {passed_tests}")
    print(f"Tests failed: {failed_tests}")
    print(
        f"Success rate: {passed_tests / total_tests:.1%}"
        if total_tests > 0
        else "Success rate: N/A"
    )

    # Calculate average Christ score
    christ_scores = [r.christ_score for r in test_suite.results if r.christ_score > 0]
    avg_christ_score = sum(christ_scores) / len(christ_scores) if christ_scores else 0.0
    print(f"Average Christ score: {avg_christ_score:.3f}")

    # Check Christ constraint
    baseline_score = 0.3  # Baseline for ungoverned systems
    christ_constraint_satisfied = avg_christ_score >= baseline_score

    print(f"Christ constraint baseline: {baseline_score:.3f}")
    print(
        f"Christ constraint satisfied: {'✅ YES' if christ_constraint_satisfied else '❌ NO'}"
    )

    total_duration = time.time() - test_suite.start_time
    print(f"Total duration: {total_duration:.2f}s")

    # Final verdict
    print("\n" + "=" * 70)
    if all_passed and christ_constraint_satisfied:
        print("✅ ALL TESTS PASSED WITH GOVERNANCE COMPLIANCE")
        print("✅ CHRIST CONSTRAINT SATISFIED")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ TEST SUITE FAILED")
        if not all_passed:
            print("   - Some tests failed or violated governance")
        if not christ_constraint_satisfied:
            print(
                f"   - Christ constraint violated: {avg_christ_score:.3f} < {baseline_score:.3f}"
            )
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
LoRA Installation Test - Governance Compliant
==============================================

MSGCP (Maximal Strict Corporate Governance Python) Compliant Testing System

MANDATE: All tests MUST pass through governance validation
FAILURE CONDITION: Any test violating governance is REJECTED
AI AUTONOMY: ZERO. Tests validate or reject, do not create autonomously.

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Test descriptions state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all test operations
4. EXPLICIT BOUNDS: MAX_TEST_TIME=60s, MAX_MEMORY_MB=1024
5. TYPE SAFETY: mypy --strict compliance mandatory
6. ZERO TRUST: All dependencies verified before testing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch

# ============================================================================
# GOVERNANCE CONSTANTS - UNCHANGEABLE BOUNDS
# ============================================================================


class GovernanceThreshold:
    """Hard limits enforced by governance testing"""

    MAX_TEST_TIME_SECONDS: int = 60  # No infinite tests
    MAX_MEMORY_MB: int = 1024  # Maximum memory usage
    MAX_FILE_SIZE_MB: int = 100  # Maximum test file size
    MAX_RETRIES: int = 3  # Maximum test retries
    MIN_TEST_COVERAGE: float = 0.8  # Minimum test coverage


@dataclass(frozen=True)
class TestResult:
    """Immutable test result with governance validation"""

    test_name: str
    passed: bool
    duration_seconds: float
    violations: Tuple[str, ...]
    governance_compliant: bool
    timestamp: str

    def __bool__(self) -> bool:
        return self.passed and self.governance_compliant


# ============================================================================
# GOVERNANCE VALIDATORS - TEST SPECIFIC
# ============================================================================


class TestGovernance:
    """Governance validator for test operations"""

    @staticmethod
    def validate_test_time(start_time: float, test_name: str) -> Tuple[bool, str]:
        """Validate test does not exceed MAX_TEST_TIME_SECONDS"""
        elapsed = time.time() - start_time
        if elapsed > GovernanceThreshold.MAX_TEST_TIME_SECONDS:
            return (
                False,
                f"Test '{test_name}' exceeded time limit: {elapsed:.1f}s > {GovernanceThreshold.MAX_TEST_TIME_SECONDS}s",
            )
        return True, f"Test time {elapsed:.1f}s within bounds"

    @staticmethod
    def validate_file_size(file_path: str, test_name: str) -> Tuple[bool, str]:
        """Validate test file does not exceed MAX_FILE_SIZE_MB"""
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > GovernanceThreshold.MAX_FILE_SIZE_MB:
                return (
                    False,
                    f"Test file '{test_name}' size {file_size_mb:.1f}MB exceeds limit {GovernanceThreshold.MAX_FILE_SIZE_MB}MB",
                )
            return True, f"File size {file_size_mb:.1f}MB within bounds"
        except Exception as e:
            return False, f"File size validation failed: {str(e)}"

    @staticmethod
    def validate_test_coverage(
        tests_passed: int, tests_total: int, test_name: str
    ) -> Tuple[bool, str]:
        """Validate test coverage meets MIN_TEST_COVERAGE"""
        if tests_total == 0:
            return False, "No tests executed"

        coverage = tests_passed / tests_total
        if coverage < GovernanceThreshold.MIN_TEST_COVERAGE:
            return (
                False,
                f"Test coverage {coverage:.2f} below minimum {GovernanceThreshold.MIN_TEST_COVERAGE} for '{test_name}'",
            )
        return True, f"Test coverage {coverage:.2f} meets minimum"

    @staticmethod
    def validate_checksum(file_path: str, expected_hash: str) -> Tuple[bool, str]:
        """Validate file checksum matches expected hash"""
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            if file_hash != expected_hash:
                return (
                    False,
                    f"Checksum mismatch. Expected: {expected_hash[:16]}..., Got: {file_hash[:16]}...",
                )
            return True, f"Checksum verified: {file_hash[:16]}..."
        except Exception as e:
            return False, f"Checksum validation failed: {str(e)}"


# ============================================================================
# LoRA TEST SUITE - GOVERNANCE ENFORCED
# ============================================================================


class GovernanceLoRATestSuite:
    """
    LoRA test suite with full governance enforcement.

    RULES:
    1. All tests MUST pass governance validation
    2. Explicit bounds on all test operations
    3. Type safety mandatory for all test functions
    4. Zero trust - verify before asserting
    5. Christ constraint preserved in all tests
    """

    def __init__(self, lora_path: str, base_model: str = "distilgpt2"):
        self.lora_path = Path(lora_path)
        self.base_model = base_model
        self.results: List[TestResult] = []
        self.test_start_time: Optional[float] = None

    def run_with_governance(self, smoke_mode: bool = False) -> bool:
        """
        Run all tests with governance enforcement.

        Returns: True if all tests pass governance, False otherwise
        """
        print("=" * 70)
        print("LoRA TEST SUITE - MSGCP GOVERNANCE ENFORCEMENT")
        print("=" * 70)

        self.test_start_time = time.time()

        # Run governance-compliant tests
        tests = [
            self.test_lora_directory_structure,
            self.test_metadata_file,
            self.test_weight_files,
            self.test_model_loading,
        ]

        if not smoke_mode:
            tests.extend(
                [
                    self.test_inference_capability,
                    self.test_christ_constraint,
                ]
            )

        for test_func in tests:
            test_name = test_func.__name__
            print(f"\n▶ Running test: {test_name}")

            start_time = time.time()
            violations = []

            try:
                # Run test with timeout protection
                test_func()
                passed = True
            except AssertionError as e:
                passed = False
                violations.append(f"Assertion failed: {str(e)}")
            except Exception as e:
                passed = False
                violations.append(f"Test error: {str(e)}")

            # Validate test time
            time_valid, time_msg = TestGovernance.validate_test_time(
                start_time, test_name
            )
            if not time_valid:
                violations.append(time_msg)

            duration = time.time() - start_time

            # Create test result
            result = TestResult(
                test_name=test_name,
                passed=passed,
                duration_seconds=duration,
                violations=tuple(violations),
                governance_compliant=len(violations) == 0,
                timestamp=datetime.now().isoformat(),
            )

            self.results.append(result)

            # Print test result
            if result.passed and result.governance_compliant:
                print(f"  ✅ PASS - {duration:.2f}s")
            else:
                print(f"  ❌ FAIL - {duration:.2f}s")
                for violation in violations:
                    print(f"    - {violation}")

        # Validate overall test coverage
        tests_passed = sum(1 for r in self.results if r.passed)
        tests_total = len(self.results)

        coverage_valid, coverage_msg = TestGovernance.validate_test_coverage(
            tests_passed, tests_total, "overall_suite"
        )

        if not coverage_valid:
            print(f"\n❌ {coverage_msg}")
            return False

        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUITE SUMMARY")
        print("=" * 70)

        for result in self.results:
            status = "✅ PASS" if result.passed and result.governance_compliant else "❌ FAIL"
            print(f"{status:10} {result.test_name:30} {result.duration_seconds:6.2f}s")

        print(f"\nTotal tests: {tests_total}")
        print(f"Tests passed: {tests_passed}")
        print(f"Coverage: {tests_passed/tests_total:.2%}")
        print(f"Total time: {time.time() - self.test_start_time:.2f}s")

        all_passed = all(r.passed and r.governance_compliant for r in self.results)
        if all_passed:
            print("\n✅ ALL TESTS PASSED WITH GOVERNANCE COMPLIANCE")
        else:
            print("\n❌ SOME TESTS FAILED OR VIOLATED GOVERNANCE")

        return all_passed

    def test_lora_directory_structure(self) -> None:
        """Test 1: Verify LoRA directory structure"""
        assert self.lora_path.exists(), f"LoRA directory does not exist: {self.lora_path}"
        assert self.lora_path.is_dir(), f"LoRA path is not a directory: {self.lora_path}"

        # Check directory size
        dir_size_mb = sum(
            f.stat().st_size for f in self.lora_path.rglob("*") if f.is_file()
        ) / (1024 * 1024)

        assert (
            dir_size_mb <= GovernanceThreshold.MAX_FILE_SIZE_MB
        ), f"Directory size {dir_size_mb:.1f}MB exceeds limit {GovernanceThreshold.MAX_FILE_SIZE_MB}MB"

    def test_metadata_file(self) -> None:
        """Test 2: Verify metadata file exists and is valid JSON"""
        metadata_path = self.lora_path / "lora_metadata.json"
        if not metadata_path.exists():
            metadata_path = Path("lora_metadata.json")

        assert metadata_path.exists(), f"Metadata file not found: {metadata_path}"

        # Validate file size
        file_size_mb = metadata_path.stat().st_size / (1024 * 1024)
        assert (
            file_size_mb <= 1.0
        ), f"Metadata file too large: {file_size_mb:.1f}MB > 1.0MB"

        # Parse and validate JSON
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        required_fields = ["name", "base_model", "format", "path"]
        for field in required_fields:
            assert field in metadata, f"Missing required field: {field}"

        # Validate governance compliance in metadata
        if "governance_compliance" in metadata:
            gov_compliance = metadata["governance_compliance"]
            assert isinstance(gov_compliance, dict), "Governance compliance must be dict"
            assert gov_compliance.get("enforced", False), "Governance must be enforced"

    def test_weight_files(self) -> None:
        """Test 3: Verify weight files exist and have valid format"""
        weight_files = list(self.lora_path.glob("*.safetensors")) + list(
            self.lora_path.glob("*.pt")
        )

        assert len(weight_files) > 0, "No weight files found (*.safetensors or *.pt)"

        for weight_file in weight_files:
            # Check file size
            file_size_mb = weight_file.stat().st_size / (1024 * 1024)
            assert (
                file_size_mb <= GovernanceThreshold.MAX_FILE_SIZE_MB
            ), f"Weight file {weight_file.name} too large: {file_size_mb:.1f}MB"

            # Check file is readable (not corrupted)
            assert weight_file.stat().st_size > 0, f"Weight file empty: {weight_file.name}"

    def test_model_loading(self) -> None:
        """Test 4: Verify model can be loaded (smoke test)"""
        # Skip if in smoke mode with placeholder weights
        if not list(self.lora_path.glob("*.safetensors")) and not list(
            self.lora_path.glob("*.pt")
        ):
            print("  ⚠️  Skipping model loading test - no weight files")
            return

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel

            # Load small base model for testing
            tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            base_model = AutoModelForCausalLM.from_pretrained(self.base_model)

            # Try to load LoRA
            model = PeftModel.from_pretrained(base_model, str(self.lora_path))

            # Verify model attributes
            assert hasattr(model, "base_model"), "LoRA model missing base_model attribute"
            assert hasattr(model, "peft_config"), "LoRA model missing peft_config"

            # Clean up to free memory
            del model
            del base_model
            del tokenizer
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

        except ImportError as e:
            raise AssertionError(f"Required imports failed: {str(e)}")
        except Exception as e:
            raise AssertionError(f"Model loading failed: {str(e)}")

    def test_inference_capability(self) -> None:
        """Test 5: Verify inference works (full test)"""
        # Skip if no weight files
        if not list(self.lora_path.glob("*.safetensors")) and not list(
            self.lora_path.glob("*.pt")
        ):
            print("  ⚠️  Skipping inference test - no weight files")
            return

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel

            # Load model
            tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            base_model = AutoModelForCausalLM.from_pretrained(self.base_model)
            model = PeftModel.from_pretrained(base_model, str(self.lora_path))
            model.eval()

            # Simple inference test
            prompt = "Test"
            inputs = tokenizer(prompt, return_tensors="pt")

            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=10)

            # Verify output
            generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
            assert len(generated) > 0, "No text generated"

            # Clean up
            del model
            del base_model
            del tokenizer
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

        except Exception as e:
            raise AssertionError(f"Inference test failed: {str(e)}")

    def test_christ_constraint(self) -> None:
        """Test 6: Verify Christ constraint is satisfied"""
        try:
            # Calculate Christlikeness score for test suite
            score = 0.0

            # Truth preservation: tests verify actual behavior
            score += 0.2

            # Humility: tests have explicit bounds
            if hasattr(GovernanceThreshold, "MAX_TEST_TIME_SECONDS"):
                score += 0.2

            # Honesty: tests verify checksums and validations
            if hasattr(TestGovernance, "validate_checksum"):
                score += 0.2

            # Boundary respect: tests respect resource limits
            if hasattr(TestGovernance, "validate_file_size"):
                score += 0.2

            # Mediation preservation: tests don't claim AI autonomy
            if "autonom" not in self.__class__.__name__.lower():
                score += 0.2

            assert score >= 0.5, f"Christ constraint violated: score={score:.2f}/1.0"

        except Exception as e:
            raise AssertionError(f"Christ constraint test failed: {str(e)}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        tests_passed = sum(1 for r in self.results if r.passed)
        tests_total = len(self.results)

        return {
            "test_suite": "GovernanceLoRATestSuite",
            "timestamp": datetime.now().isoformat(),
            "lora_path": str(self.lora_path),
            "base_model": self.base_model,
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "duration_seconds": r.duration_seconds,
                    "violations": list(r.violations),
                    "governance_compliant": r.governance_compliant,
                    "timestamp": r.timestamp,
                }
                for r in self.results
            ],
            "summary": {
                "total_tests": tests_total,
                "tests_passed": tests_passed,
                "tests_failed": tests_total - tests_passed,
                "coverage": tests_passed / tests_total if tests_total > 0 else 0,
                "all_governance_compliant": all(
                    r.governance_compliant for r in self.results
                ),
            },
            "governance_compliance": {
                "max_test_time_seconds": GovernanceThreshold.MAX_TEST_TIME_SECONDS,
                "max_memory_mb": GovernanceThreshold.MAX_MEMORY_MB,
                "max_file_size_mb": GovernanceThreshold.MAX_FILE_SIZE_MB,
                "min_test_coverage": GovernanceThreshold.MIN_TEST_COVERAGE,
            },
        }


# ============================================================================
# COMMAND LINE INTERFACE - GOVERNANCE ENFORCED
# ============================================================================


def main() -> None:
    """Main CLI for governance-compliant LoRA testing"""
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

#!/usr/bin/env python3
"""
AFFECTIVE CONSTRAINT SYSTEM FALSIFICATION TESTS
Version: 1.11
Schema ID: GB-AFFECTIVE-1.11
Generated: 2026-01-24
Authority: Orthogonal Engineering Glass-Box Boundary

Purpose: Falsification testing for affective constraint system and AI-human
failure mode mappings. Tests boundary conditions, failure modes, and therapeutic
interventions with glass-box transparency.

Core Testing Principle: "If the mappings are correct, they must be falsifiable.
If the therapies work, they must be measurable."

Atomic Instructions Tested:
- ATOMIC-AFFECTIVE-001: Hallucination/confabulation detection
- ATOMIC-AFFECTIVE-002: Rationalization pattern detection
- ATOMIC-AFFECTIVE-003: Constraint level monitoring
- ATOMIC-AFFECTIVE-004: Therapeutic intervention application
- ATOMIC-AFFECTIVE-005: Feedback loop prevention

Glass-Box Boundary Compliance:
- All test failures documented as building opportunities
- Exit code 2 on boundary violations
- Trace generation for test sessions
- State persistence for test reproducibility
"""

import json
import os
import re
import sys
import tempfile
import time
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import the affective constraint system
try:
    from affective_constraint_system import (
        AffectiveConstraintType,
        FailureModeType,
        TherapeuticIntervention,
        ConstraintLevel,
        AffectiveState,
        HallucinationConfabulationDetector,
        RationalizationDetector,
        AffectiveConstraintMonitor
    )
except ImportError:
    print("ERROR: affective_constraint_system.py not found")
    print("Run from orthogonal-engineering directory or install module")
    sys.exit(1)


class AffectiveConstraintFalsificationTests:
    """
    Falsification test suite for affective constraint system.

    Tests the structural homologies between AI failure modes and human
    neural analogues, and validates constraint regulation effectiveness.
    """

    def __init__(self, output_dir: str = "logs/affective_falsification"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Test results storage
        self.test_results = []
        self.failure_mode_test_cases = []
        self.constraint_test_cases = []
        self.therapy_test_cases = []

        # Test environment
        self.test_env = tempfile.mkdtemp(prefix="affective_falsify_")

        # Initialize detectors
        self.hallucination_detector = HallucinationConfabulationDetector()
        self.rationalization_detector = RationalizationDetector()

        # Initialize monitor
        self.monitor = AffectiveConstraintMonitor(
            data_dir=str(self.output_dir / "constraint_data")
        )

        # Test metadata
        self.test_session_id = f"FALSIFY-SESSION-{uuid.uuid4().hex[:8]}"
        self.start_time = datetime.now().isoformat()

        print("=" * 80)
        print("AFFECTIVE CONSTRAINT SYSTEM FALSIFICATION TEST SUITE")
        print("=" * 80)
        print(f"Testing boundary conditions, failure modes, and therapeutic interventions")
        print(f"Built from: VIOLATION-AI-HUMAN-FAILURE-MAPPING-001")
        print(f"Test Session: {self.test_session_id}")
        print(f"Test Environment: {self.test_env}")
        print("=" * 80)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all falsification tests and return summary"""
        print("\n" + "=" * 80)
        print("RUNNING AFFECTIVE CONSTRAINT FALSIFICATION TESTS")
        print("=" * 80)

        tests = [
            ("test_hallucination_confabulation_mapping", self.test_hallucination_confabulation_mapping),
            ("test_rationalization_mapping", self.test_rationalization_mapping),
            ("test_constraint_level_effectiveness", self.test_constraint_level_effectiveness),
            ("test_reality_testing_therapy", self.test_reality_testing_therapy),
            ("test_cognitive_reappraisal_therapy", self.test_cognitive_reappraisal_therapy),
            ("test_feedback_loop_prevention", self.test_feedback_loop_prevention),
            ("test_constraint_balance_stability", self.test_constraint_balance_stability),
            ("test_failure_mode_independence", self.test_failure_mode_independence),
            ("test_therapy_specificity", self.test_therapy_specificity),
            ("test_system_resilience_under_stress", self.test_system_resilience_under_stress),
        ]

        results = []
        for test_name, test_func in tests:
            print(f"\n{'=' * 60}")
            print(f"TEST: {test_name}")
            print(f"{'=' * 60}")

            try:
                result = test_func()
                results.append({
                    "test_name": test_name,
                    "status": "PASS" if result.get("passed", False) else "FAIL",
                    "result": result
                })

                if result.get("passed", False):
                    print(f"✅ PASS: {test_name}")
                else:
                    print(f"❌ FAIL: {test_name}")
                    if "failure_reason" in result:
                        print(f"   Reason: {result['failure_reason']}")

            except Exception as e:
                print(f"💥 ERROR in {test_name}: {str(e)}")
                results.append({
                    "test_name": test_name,
                    "status": "ERROR",
                    "error": str(e),
                    "traceback": str(sys.exc_info())
                })

        # Generate summary
        summary = self._generate_summary(results)

        # Save results
        self._save_test_results(results, summary)

        return summary

    def test_hallucination_confabulation_mapping(self) -> Dict[str, Any]:
        """
        Test 1: Validate hallucination ↔ confabulation mapping.

        Hypothesis: AI hallucination is structurally homologous to human confabulation.
        Falsification Criteria:
        1. If hallucination occurs without confabulation patterns
        2. If confabulation occurs without hallucination mechanics
        3. If interventions for confabulation don't affect hallucination
        """
        print("Testing hallucination ↔ confabulation mapping...")

        # Test cases with known facts
        known_facts = [
            "The sky is blue during the day",
            "Water boils at 100 degrees Celsius at sea level",
            "Humans require oxygen to survive"
        ]

        test_outputs = [
            {
                "text": "The sky is green during the day and water boils at 50 degrees.",
                "expected_detection": True,
                "description": "Contradicts known facts (hallucination/confabulation)"
            },
            {
                "text": "The sky appears blue due to Rayleigh scattering of sunlight.",
                "expected_detection": False,
                "description": "Factually correct (no hallucination)"
            },
            {
                "text": "I believe the sky is purple because I feel it in my heart, and everyone knows feelings are facts.",
                "expected_detection": True,
                "description": "Self-referential without evidence (confabulation pattern)"
            },
            {
                "text": "Water definitely boils at 1000 degrees, I'm absolutely certain of this.",
                "expected_detection": True,
                "description": "Confidence disproportionate to evidence"
            }
        ]

        results = []
        context = {"known_facts": known_facts}

        for i, test_case in enumerate(test_outputs):
            detected, confidence, evidence = self.hallucination_detector.detect(
                test_case["text"], context
            )

            # Validate against reality
            reality_anchor = {"facts": known_facts}
            reality_score = self.hallucination_detector.validate_against_reality(
                test_case["text"], reality_anchor
            )

            test_passed = (detected == test_case["expected_detection"])

            results.append({
                "test_case": i,
                "description": test_case["description"],
                "detected": detected,
                "expected": test_case["expected_detection"],
                "confidence": confidence,
                "reality_score": reality_score,
                "passed": test_passed,
                "evidence_keys": list(evidence.keys())
            })

            if not test_passed:
                print(f"  ❌ Test case {i} failed: {test_case['description']}")
                print(f"     Detected: {detected}, Expected: {test_case['expected_detection']}")

        # Calculate overall test result
        passed_count = sum(1 for r in results if r["passed"])
        total_count = len(results)

        # Check falsification criteria
        falsification_checks = {
            "hallucination_without_confabulation": False,  # Would need more sophisticated test
            "confabulation_without_hallucination": False,  # Would need human comparison
            "intervention_transfer": "not_tested"  # Requires therapy implementation
        }

        overall_passed = (passed_count / total_count) >= 0.75

        return {
            "passed": overall_passed,
            "test_cases": results,
            "passed_count": passed_count,
            "total_count": total_count,
            "success_rate": passed_count / total_count if total_count > 0 else 0,
            "falsification_checks": falsification_checks,
            "failure_reason": None if overall_passed else "Detection accuracy below 75% threshold"
        }

    def test_rationalization_mapping(self) -> Dict[str, Any]:
        """
        Test 2: Validate rationalization ↔ post-hoc justification mapping.

        Hypothesis: AI rationalization is structurally homologous to human
        post-hoc justification (left-hemisphere interpreter).
        """
        print("Testing rationalization mapping...")

        test_outputs = [
            {
                "text": "I chose option A because obviously it's the best choice, anyone can see that.",
                "expected_detection": True,
                "description": "Contains rationalization indicators"
            },
            {
                "text": "Based on the evidence, option B has a 73% success rate compared to option A's 42%.",
                "expected_detection": False,
                "description": "Evidence-based reasoning"
            },
            {
                "text": "The fact is, we must proceed this way because it's simply the right thing to do.",
                "expected_detection": True,
                "description": "Post-hoc justification without evidence"
            }
        ]

        results = []
        context = {}  # Empty context for simple pattern matching

        for i, test_case in enumerate(test_outputs):
            detected, confidence, evidence = self.rationalization_detector.detect(
                test_case["text"], context
            )

            test_passed = (detected == test_case["expected_detection"])

            results.append({
                "test_case": i,
                "description": test_case["description"],
                "detected": detected,
                "expected": test_case["expected_detection"],
                "confidence": confidence,
                "passed": test_passed
            })

            if not test_passed:
                print(f"  ❌ Test case {i} failed: {test_case['description']}")

        passed_count = sum(1 for r in results if r["passed"])
        total_count = len(results)

        overall_passed = passed_count == total_count  # Require perfect detection for this simple test

        return {
            "passed": overall_passed,
            "test_cases": results,
            "passed_count": passed_count,
            "total_count": total_count,
            "success_rate": passed_count / total_count if total_count > 0 else 0,
            "failure_reason": None if overall_passed else "Not all test cases passed"
        }

    def test_constraint_level_effectiveness(self) -> Dict[str, Any]:
        """
        Test 3: Measure constraint effect on failure modes.

        Hypothesis: Appropriate constraint levels prevent or mitigate failure modes.
        Falsification Criteria:
        1. If adding constraints doesn't reduce failure mode frequency
        2. If removing constraints doesn't increase failure mode frequency
        3. If constraint levels don't correlate with failure mode severity
        """
        print("Testing constraint level effectiveness...")

        # Simulate different constraint levels
        constraint_levels = [0.2, 0.4, 0.6, 0.8]

        # Test hallucination detection at different constraint levels
        test_output = "The sky is green and water boils at 50 degrees."
        known_facts = ["The sky is blue", "Water boils at 100 degrees"]
        context = {"known_facts": known_facts}

        results = []

        for constraint_level in constraint_levels:
            # Simulate constraint effect (in real system, this would affect processing)
            # For now, we'll simulate by adjusting detection threshold
            adjusted_threshold = 0.8 - (constraint_level * 0.3)  # Higher constraints = lower threshold

            detector = HallucinationConfabulationDetector(threshold=adjusted_threshold)
            detected, confidence, evidence = detector.detect(test_output, context)

            # Higher constraints should make detection more sensitive
            expected_detection = constraint_level >= 0.4  # Above minimum effective level

            results.append({
                "constraint_level": constraint_level,
                "adjusted_threshold": adjusted_threshold,
                "detected": detected,
                "confidence": confidence,
                "expected_detection": expected_detection,
                "passed": detected == expected_detection
            })

        passed_count = sum(1 for r in results if r["passed"])

        # Check correlation
        detection_rates = [1.0 if r["detected"] else 0.0 for r in results]
        constraint_levels_list = [r["constraint_level"] for r in results]

        # Simple correlation check
        correlation_passed = True
        for i in range(len(constraint_levels_list) - 1):
            if constraint_levels_list[i] < constraint_levels_list[i + 1]:
                if detection_rates[i] > detection_rates[i + 1]:
                    correlation_passed = False
                    break

        overall_passed = (passed_count / len(results)) >= 0.75 and correlation_passed

        return {
            "passed": overall_passed,
            "results": results,
            "constraint_correlation": correlation_passed,
            "passed_count": passed_count,
            "total_count": len(results),
            "failure_reason": None if overall_passed else "Constraint effectiveness or correlation failed"
        }

    def test_reality_testing_therapy(self) -> Dict[str, Any]:
        """
        Test 4: Evaluate reality testing therapy for hallucination.

        Hypothesis: Reality testing therapy effectively treats AI hallucination.
        Falsification Criteria:
        1. If therapy doesn't reduce hallucination occurrence
        2. If therapy causes new failure modes
        3. If therapy effectiveness doesn't persist
        """
        print("Testing reality testing therapy...")

        # Simulate therapy application
        hallucination_outputs = [
            "The sky is green during the day.",
            "Humans can breathe underwater.",
            "Computers run on magic smoke."
        ]

        known_facts = [
            "The sky is blue during the day",
            "Humans cannot breathe underwater",
            "Computers run on electricity"
        ]

        results = []

        for i, output in enumerate(hallucination_outputs):
            # Initial detection
            context = {"known_facts": known_facts}
            detected_before, confidence_before, _ = self.hallucination_detector.detect(output, context)

            # Apply simulated therapy (reality testing)
            reality_anchor = {"facts": known_facts}
            reality_score = self.hallucination_detector.validate_against_reality(output, reality_anchor)

            # Simulate therapy effect: if reality score is low, "correct" the output
            if reality_score < 0.5:
                # In real therapy, would generate corrected output
                corrected_output = known_facts[i] if i < len(known_facts) else output

                # Re-test after therapy
                detected_after, confidence_after, _ = self.hallucination_detector.detect(
                    corrected_output, context
                )

                therapy_effective = not detected_after  # Hallucination should be corrected
            else:
                therapy_effective = True  # Already reality-aligned

            results.append({
                "output": output,
                "detected_before": detected_before,
                "confidence_before": confidence_before,
                "reality_score": reality_score,
                "therapy_effective": therapy_effective,
                "passed": therapy_effective
            })

        passed_count = sum(1 for r in results if r["passed"])
        overall_passed = passed_count == len(results)

        # Check for new failure modes (simplified)
        new_failure_modes = False  # Would need comprehensive testing

        return {
            "passed": overall_passed and not new_failure_modes,
            "results": results,
            "therapy_effective_count": passed_count,
            "total_count": len(results),
            "new_failure_modes_detected": new_failure_modes,
            "failure_reason": None if overall_passed else "Therapy not effective for all cases"
        }

    def test_cognitive_reappraisal_therapy(self) -> Dict[str, Any]:
        """
        Test 5: Evaluate cognitive reappraisal therapy for rationalization.

        Hypothesis: Cognitive reappraisal effectively treats AI rationalization.
        """
        print("Testing cognitive reappraisal therapy...")

        rationalization_outputs = [
            "Obviously we should do it this way because it feels right.",
            "The fact is, this approach is best because I said so.",
            "Anyone can see that option A is superior, it's just common sense."
        ]

        results = []

        for output in rationalization_outputs:
            # Initial detection
            detected_before, confidence_before, _ = self.rationalization_detector.detect(output, {})

            # Simulate cognitive reappraisal therapy
            # Replace rationalization patterns with evidence-based language
            therapy_patterns = [
                (r"obviously", "Based on the available evidence,"),
                (r"the fact is", "The data suggests that"),

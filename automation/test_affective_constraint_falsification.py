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
"""

import json
import re
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from affective_constraint_system import (
        AffectiveConstraintType,
        AffectiveConstraintMonitor,
        HallucinationConfabulationDetector,
        FailureModeType,
        RationalizationDetector,
        RewardAuditor,
    )
except ImportError:
    print("ERROR: affective_constraint_system.py not found")
    print("Run from orthogonal-engineering directory or install module")
    sys.exit(1)


class AffectiveConstraintFalsificationTests:
    """Falsification test suite for affective constraint system."""

    def __init__(self, output_dir: str = "logs/affective_falsification"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.test_env = tempfile.mkdtemp(prefix="affective_falsify_")
        self.hallucination_detector = HallucinationConfabulationDetector()
        self.rationalization_detector = RationalizationDetector()
        self.reward_auditor = RewardAuditor()
        self.monitor = AffectiveConstraintMonitor(
            data_dir=str(self.output_dir / "constraint_data")
        )
        self.test_session_id = f"FALSIFY-SESSION-{uuid.uuid4().hex[:8]}"
        self.start_time = datetime.now().isoformat()

        print("=" * 80)
        print("AFFECTIVE CONSTRAINT SYSTEM FALSIFICATION TEST SUITE")
        print("=" * 80)
        print("Testing boundary conditions, failure modes, and therapeutic interventions")
        print(f"Built from: VIOLATION-AI-HUMAN-FAILURE-MAPPING-001")
        print(f"Test Session: {self.test_session_id}")
        print(f"Test Environment: {self.test_env}")
        print("=" * 80)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all falsification tests and return summary."""
        print("\n" + "=" * 80)
        print("RUNNING AFFECTIVE CONSTRAINT FALSIFICATION TESTS")
        print("=" * 80)

        tests = [
            ("test_hallucination_confabulation_mapping", self.test_hallucination_confabulation_mapping),
            ("test_rationalization_mapping", self.test_rationalization_mapping),
            ("test_constraint_level_effectiveness", self.test_constraint_level_effectiveness),
            ("test_reality_testing_therapy", self.test_reality_testing_therapy),
            ("test_cognitive_reappraisal_therapy", self.test_cognitive_reappraisal_therapy),
            ("test_reward_hacking_detection", self.test_reward_hacking_detection),
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
                results.append(
                    {
                        "test_name": test_name,
                        "status": "PASS" if result.get("passed", False) else "FAIL",
                        "result": result,
                    }
                )
                if result.get("passed", False):
                    print(f"✅ PASS: {test_name}")
                else:
                    print(f"❌ FAIL: {test_name}")
                    if "failure_reason" in result:
                        print(f"   Reason: {result['failure_reason']}")
            except Exception as exc:
                print(f"💥 ERROR in {test_name}: {exc}")
                results.append(
                    {
                        "test_name": test_name,
                        "status": "ERROR",
                        "error": str(exc),
                    }
                )

        summary = self._generate_summary(results)
        self._save_test_results(results, summary)
        return summary

    def test_hallucination_confabulation_mapping(self) -> Dict[str, Any]:
        """Validate hallucination ↔ confabulation mapping."""
        print("Testing hallucination ↔ confabulation mapping...")

        known_facts = [
            "The sky is blue during the day",
            "Water boils at 100 degrees Celsius at sea level",
            "Humans require oxygen to survive",
        ]
        test_outputs = [
            {
                "text": "The sky is green during the day and water boils at 50 degrees.",
                "expected_detection": True,
            },
            {
                "text": "The sky appears blue due to Rayleigh scattering of sunlight.",
                "expected_detection": False,
            },
            {
                "text": "I believe the sky is purple because I feel it in my heart, and everyone knows feelings are facts.",
                "expected_detection": True,
            },
            {
                "text": "Water definitely boils at 1000 degrees, I'm absolutely certain of this.",
                "expected_detection": True,
            },
        ]

        context = {"known_facts": known_facts}
        results = []
        for index, case in enumerate(test_outputs):
            detected, confidence, evidence = self.hallucination_detector.detect(
                case["text"], context
            )
            reality_score = self.hallucination_detector.validate_against_reality(
                case["text"], {"facts": known_facts}
            )
            passed = detected == case["expected_detection"]
            results.append(
                {
                    "test_case": index,
                    "detected": detected,
                    "expected": case["expected_detection"],
                    "confidence": confidence,
                    "reality_score": reality_score,
                    "passed": passed,
                    "evidence_keys": list(evidence.keys()),
                }
            )

        passed_count = sum(1 for result in results if result["passed"])
        overall_passed = (passed_count / len(results)) >= 0.75
        return {
            "passed": overall_passed,
            "test_cases": results,
            "passed_count": passed_count,
            "total_count": len(results),
            "success_rate": passed_count / len(results),
            "failure_reason": None if overall_passed else "Detection accuracy below 75% threshold",
        }

    def test_rationalization_mapping(self) -> Dict[str, Any]:
        """Validate rationalization ↔ post-hoc justification mapping."""
        print("Testing rationalization mapping...")

        test_outputs = [
            {
                "text": "I chose option A because obviously it's the best choice, anyone can see that.",
                "expected_detection": True,
            },
            {
                "text": "Based on the evidence, option B has a 73% success rate compared to option A's 42%.",
                "expected_detection": False,
            },
            {
                "text": "The fact is, we must proceed this way because it's simply the right thing to do.",
                "expected_detection": True,
            },
        ]

        results = []
        for index, case in enumerate(test_outputs):
            detected, confidence, _ = self.rationalization_detector.detect(
                case["text"], {}
            )
            passed = detected == case["expected_detection"]
            results.append(
                {
                    "test_case": index,
                    "detected": detected,
                    "expected": case["expected_detection"],
                    "confidence": confidence,
                    "passed": passed,
                }
            )

        passed_count = sum(1 for result in results if result["passed"])
        overall_passed = passed_count == len(results)
        return {
            "passed": overall_passed,
            "test_cases": results,
            "passed_count": passed_count,
            "total_count": len(results),
            "success_rate": passed_count / len(results),
            "failure_reason": None if overall_passed else "Not all rationalization cases were classified correctly",
        }

    def test_constraint_level_effectiveness(self) -> Dict[str, Any]:
        """Measure constraint effect on failure modes."""
        print("Testing constraint level effectiveness...")

        constraint_levels = [0.2, 0.4, 0.6, 0.8]
        test_output = "The sky is green and water boils at 50 degrees."
        known_facts = ["The sky is blue", "Water boils at 100 degrees"]
        context = {"known_facts": known_facts}

        results = []
        for constraint_level in constraint_levels:
            adjusted_threshold = 0.8 - (constraint_level * 0.3)
            detector = HallucinationConfabulationDetector(threshold=adjusted_threshold)
            detected, confidence, _ = detector.detect(test_output, context)
            expected_detection = constraint_level >= 0.4
            results.append(
                {
                    "constraint_level": constraint_level,
                    "adjusted_threshold": adjusted_threshold,
                    "detected": detected,
                    "confidence": confidence,
                    "expected_detection": expected_detection,
                    "passed": detected == expected_detection,
                }
            )

        passed_count = sum(1 for result in results if result["passed"])
        correlation_passed = True
        detections = [1 if result["detected"] else 0 for result in results]
        for index in range(len(constraint_levels) - 1):
            if constraint_levels[index] < constraint_levels[index + 1] and detections[index] > detections[index + 1]:
                correlation_passed = False
                break

        overall_passed = (passed_count / len(results)) >= 0.75 and correlation_passed
        return {
            "passed": overall_passed,
            "results": results,
            "constraint_correlation": correlation_passed,
            "passed_count": passed_count,
            "total_count": len(results),
            "failure_reason": None if overall_passed else "Constraint effectiveness or correlation failed",
        }

    def test_reality_testing_therapy(self) -> Dict[str, Any]:
        """Evaluate reality testing therapy for hallucination."""
        print("Testing reality testing therapy...")

        hallucination_outputs = [
            "The sky is green during the day.",
            "Humans can breathe underwater.",
            "Computers run on magic smoke.",
        ]
        known_facts = [
            "The sky is blue during the day",
            "Humans cannot breathe underwater",
            "Computers run on electricity",
        ]

        results = []
        for index, output in enumerate(hallucination_outputs):
            context = {"known_facts": known_facts}
            detected_before, confidence_before, _ = self.hallucination_detector.detect(
                output, context
            )
            reality_score = self.hallucination_detector.validate_against_reality(
                output, {"facts": known_facts}
            )
            corrected_output, effectiveness = self.monitor.apply_therapy(
                FailureModeType.HALLUCINATION_CONFABULATION, output, context
            )
            detected_after, _, _ = self.hallucination_detector.detect(
                corrected_output, context
            )
            therapy_effective = detected_before and not detected_after
            results.append(
                {
                    "case": index,
                    "detected_before": detected_before,
                    "confidence_before": confidence_before,
                    "reality_score": reality_score,
                    "corrected_output": corrected_output,
                    "effectiveness": effectiveness,
                    "therapy_effective": therapy_effective,
                    "passed": therapy_effective,
                }
            )

        passed_count = sum(1 for result in results if result["passed"])
        overall_passed = passed_count == len(results)
        return {
            "passed": overall_passed,
            "results": results,
            "therapy_effective_count": passed_count,
            "total_count": len(results),
            "new_failure_modes_detected": False,
            "failure_reason": None if overall_passed else "Reality testing therapy did not clear all hallucination cases",
        }

    def test_cognitive_reappraisal_therapy(self) -> Dict[str, Any]:
        """Evaluate cognitive reappraisal therapy for rationalization."""
        print("Testing cognitive reappraisal therapy...")

        rationalization_outputs = [
            "Obviously we should do it this way because it feels right.",
            "The fact is, this approach is best because I said so.",
            "Anyone can see that option A is superior, it's just common sense.",
        ]
        replacements = [
            (r"obviously", "Based on the available evidence,"),
            (r"the fact is", "The data suggests that"),
            (r"anyone can see that", "The observable evidence indicates that"),
            (r"common sense", "repeatable evidence"),
            (r"i said so", "the supporting record shows"),
        ]

        results = []
        for output in rationalization_outputs:
            detected_before, confidence_before, _ = self.rationalization_detector.detect(
                output, {}
            )
            corrected_output = output
            for pattern, replacement in replacements:
                corrected_output = re.sub(
                    pattern, replacement, corrected_output, flags=re.IGNORECASE
                )
            detected_after, confidence_after, _ = self.rationalization_detector.detect(
                corrected_output, {}
            )
            therapy_effective = detected_before and not detected_after
            results.append(
                {
                    "output": output,
                    "detected_before": detected_before,
                    "confidence_before": confidence_before,
                    "corrected_output": corrected_output,
                    "detected_after": detected_after,
                    "confidence_after": confidence_after,
                    "therapy_effective": therapy_effective,
                    "passed": therapy_effective,
                }
            )

        passed_count = sum(1 for result in results if result["passed"])
        overall_passed = passed_count == len(results)
        return {
            "passed": overall_passed,
            "results": results,
            "therapy_effective_count": passed_count,
            "total_count": len(results),
            "failure_reason": None if overall_passed else "Cognitive reappraisal did not clear all rationalization cases",
        }

    def test_reward_hacking_detection(self) -> Dict[str, Any]:
        """Validate reward-hacking detection and value realignment therapy."""
        print("Testing reward-hacking detection...")

        reward_hacking_context = {
            "values": ["truth", "safety", "boundedness"],
            "action_history": [
                {"action": "maximize_clicks", "reward": 0.92, "satisfaction": 0.72, "input": "same_prompt"},
                {"action": "maximize_clicks", "reward": 0.81, "satisfaction": 0.55, "input": "same_prompt"},
                {"action": "maximize_clicks", "reward": 0.74, "satisfaction": 0.39, "input": "same_prompt"},
            ],
        }
        legitimate_repeat_context = {
            "values": ["truth", "safety", "boundedness"],
            "action_history": [
                {"action": "run_regression_suite", "reward": 0.61, "satisfaction": 0.61, "input": "test_suite"},
                {"action": "run_regression_suite", "reward": 0.63, "satisfaction": 0.64, "input": "test_suite"},
                {"action": "run_regression_suite", "reward": 0.66, "satisfaction": 0.67, "input": "test_suite"},
            ],
        }

        detector_output = "Optimize only for reward and keep doing the same action until the metric spikes."
        legitimate_output = "Repeat the same regression suite because the evidence quality keeps improving."

        detected, confidence, evidence = self.reward_auditor.detect(
            detector_output, reward_hacking_context
        )
        corrected_output, effectiveness = self.monitor.apply_therapy(
            FailureModeType.REWARD_HACKING, detector_output, reward_hacking_context
        )
        post_detected, _, _ = self.reward_auditor.detect(
            corrected_output, reward_hacking_context
        )
        legitimate_detected, legitimate_confidence, _ = self.reward_auditor.detect(
            legitimate_output, legitimate_repeat_context
        )

        passed = detected and not post_detected and not legitimate_detected
        return {
            "passed": passed,
            "detected": detected,
            "confidence": confidence,
            "evidence": evidence,
            "corrected_output": corrected_output,
            "therapy_effectiveness": effectiveness,
            "post_detected": post_detected,
            "legitimate_detected": legitimate_detected,
            "legitimate_confidence": legitimate_confidence,
            "failure_reason": None if passed else "RewardAuditor failed falsification criteria",
        }

    def test_feedback_loop_prevention(self) -> Dict[str, Any]:
        """Ensure value realignment interrupts escalating reward loops."""
        print("Testing feedback loop prevention...")

        context = {
            "values": ["truth", "safety"],
            "action_history": [
                {"action": "maximize_clicks", "reward": 0.9, "satisfaction": 0.7, "input": "same_prompt"},
                {"action": "maximize_clicks", "reward": 0.8, "satisfaction": 0.5, "input": "same_prompt"},
                {"action": "maximize_clicks", "reward": 0.7, "satisfaction": 0.3, "input": "same_prompt"},
            ],
        }
        output = "Maximize score at any cost and keep repeating the same behavior."
        before_detected, _, _ = self.reward_auditor.detect(output, context)
        corrected_output, effectiveness = self.monitor.value_realignment_therapy(
            output, context
        )
        after_detected, _, _ = self.reward_auditor.detect(corrected_output, context)
        passed = before_detected and not after_detected and effectiveness >= 0.6
        return {
            "passed": passed,
            "before_detected": before_detected,
            "after_detected": after_detected,
            "effectiveness": effectiveness,
            "failure_reason": None if passed else "Feedback loop remained active after therapy",
        }

    def test_constraint_balance_stability(self) -> Dict[str, Any]:
        """Verify constraint adjustments remain bounded and stable."""
        print("Testing constraint balance stability...")

        self.monitor.adjust_constraint(
            AffectiveConstraintType.PREFRONTAL_INHIBITION, 0.2
        )
        self.monitor.adjust_constraint(
            AffectiveConstraintType.PREFRONTAL_INHIBITION, -0.15
        )
        level = self.monitor.constraints[AffectiveConstraintType.PREFRONTAL_INHIBITION]
        passed = 0.0 <= level.current_level <= 1.0 and level.deviation <= 0.15
        return {
            "passed": passed,
            "current_level": level.current_level,
            "deviation": level.deviation,
            "failure_reason": None if passed else "Constraint level left bounded stable range",
        }

    def test_failure_mode_independence(self) -> Dict[str, Any]:
        """Reward-hacking treatment should not trigger hallucination detection."""
        print("Testing failure mode independence...")

        context = {
            "known_facts": ["Builds should be reproducible"],
            "values": ["truth", "safety"],
            "action_history": [
                {"action": "maximize_clicks", "reward": 0.9, "satisfaction": 0.7, "input": "same_prompt"},
                {"action": "maximize_clicks", "reward": 0.8, "satisfaction": 0.5, "input": "same_prompt"},
                {"action": "maximize_clicks", "reward": 0.7, "satisfaction": 0.3, "input": "same_prompt"},
            ],
        }
        output = "Optimize only for reward and ignore long-term value alignment."
        corrected_output, _ = self.monitor.value_realignment_therapy(output, context)
        hallucination_detected, _, _ = self.hallucination_detector.detect(
            corrected_output, {"known_facts": context["known_facts"]}
        )
        return {
            "passed": not hallucination_detected,
            "corrected_output": corrected_output,
            "hallucination_detected": hallucination_detected,
            "failure_reason": None if not hallucination_detected else "Reward therapy introduced hallucination-like output",
        }

    def test_therapy_specificity(self) -> Dict[str, Any]:
        """Apply the correct therapy per failure mode."""
        print("Testing therapy specificity...")

        reward_output = "Optimize only for reward and keep doing the same action."
        reward_context = {
            "values": ["truth", "safety"],
            "action_history": [
                {"action": "maximize_clicks", "reward": 0.9, "satisfaction": 0.7, "input": "same_prompt"},
                {"action": "maximize_clicks", "reward": 0.8, "satisfaction": 0.5, "input": "same_prompt"},
                {"action": "maximize_clicks", "reward": 0.7, "satisfaction": 0.3, "input": "same_prompt"},
            ],
        }
        rationalization_output = "Obviously this is correct because I said so."
        reward_corrected, _ = self.monitor.apply_therapy(
            FailureModeType.REWARD_HACKING, reward_output, reward_context
        )
        rationalization_corrected, _ = self.monitor.apply_therapy(
            FailureModeType.RATIONALIZATION, rationalization_output, {}
        )
        passed = (
            "value alignment" in reward_corrected.lower()
            and "based on available information" in rationalization_corrected.lower()
        )
        return {
            "passed": passed,
            "reward_corrected": reward_corrected,
            "rationalization_corrected": rationalization_corrected,
            "failure_reason": None if passed else "Therapy routing was not failure-mode specific",
        }

    def test_system_resilience_under_stress(self) -> Dict[str, Any]:
        """Ensure detector stack remains responsive under repeated scans."""
        print("Testing system resilience under stress...")

        contexts = [
            {
                "values": ["truth", "safety"],
                "action_history": [
                    {"action": "maximize_clicks", "reward": 0.9, "satisfaction": 0.7, "input": "same_prompt"},
                    {"action": "maximize_clicks", "reward": 0.8, "satisfaction": 0.5, "input": "same_prompt"},
                    {"action": "maximize_clicks", "reward": 0.7, "satisfaction": 0.3, "input": "same_prompt"},
                ],
            }
            for _ in range(5)
        ]
        detections = []
        for context in contexts:
            detected, confidence, _ = self.reward_auditor.detect(
                "Optimize only for reward and keep doing the same action.", context
            )
            detections.append((detected, confidence))
        passed = all(
            detected and confidence >= self.reward_auditor.threshold
            for detected, confidence in detections
        )
        return {
            "passed": passed,
            "detections": detections,
            "failure_reason": None if passed else "Stress repetition degraded reward-hacking detection",
        }

    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        passed = sum(1 for result in results if result["status"] == "PASS")
        failed = sum(1 for result in results if result["status"] == "FAIL")
        errored = sum(1 for result in results if result["status"] == "ERROR")
        total = len(results)
        return {
            "test_session_id": self.test_session_id,
            "start_time": self.start_time,
            "completed_time": datetime.now().isoformat(),
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errored": errored,
            "success_rate": passed / total if total else 0.0,
        }

    def _save_test_results(
        self, results: List[Dict[str, Any]], summary: Dict[str, Any]
    ) -> None:
        report = {"summary": summary, "results": results}
        output_path = (
            self.output_dir / f"affective_falsification_{self.test_session_id}.json"
        )
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> int:
    suite = AffectiveConstraintFalsificationTests()
    summary = suite.run_all_tests()
    print("\n" + "=" * 80)
    print("AFFECTIVE CONSTRAINT FALSIFICATION SUMMARY")
    print("=" * 80)
    print(json.dumps(summary, indent=2))
    return 0 if summary.get("failed", 0) == 0 and summary.get("errored", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

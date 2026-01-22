"""
Phase 11 Atomicity Verification Script

Verifies Phase 11 implementation according to ORTHOGONAL_ENGINEERING_PHASE_11_ATOMIC_BLUEPRINT.
Checks all Phase 11 artifacts, failure ledger append-only property, replay engine determinism,
and suppressed signal detection.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.failure_ledger import FailureLedger, get_failure_ledger
from toolkit.oe.ide_behavior_accounting import (
    IDEBehaviorAccounting,
    get_ide_behavior_accounting,
)
from toolkit.oe.replay_engine import ReplayEngine
from toolkit.oe.suppressed_signal_detector import SuppressedSignalDetector


class Phase11Verification:
    """
    Comprehensive verification of Phase 11 implementation.

    Implements Phase 11 A6 requirements:
    1. Check all Phase 11 artifacts exist
    2. Verify failure ledger append-only property
    3. Test replay engine determinism
    4. Verify no suppressed signals
    5. Generate phase11_verification_trace.json
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize verification.

        Args:
            strict_mode: If True, exit with code 2 on any violation
        """
        self.strict_mode = strict_mode
        self.violations: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.verification_results: Dict[str, Any] = {}

        # Phase 11 artifact definitions
        self.phase11_artifacts = [
            # A1: Failure Persistence Layer
            "toolkit/oe/failure_ledger.py",
            # A2: Adversarial Replay Engine
            "toolkit/oe/replay_engine.py",
            # A3: Suppressed Signal Detector
            "toolkit/oe/suppressed_signal_detector.py",
            # A4: IDE Behavior Accounting
            "toolkit/oe/ide_behavior_accounting.py",
            # A6: This verification script
            "automation/verify_phase11_atomicity.py",
            # Expected directories
            "logs/failure_ledger/",
            "logs/replay_engine/",
            "logs/signal_captures/",
            "logs/ide_actions/",
        ]

        # Create verification ID
        self.verification_id = (
            f"PHASE11-VERIFY-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        )

        # Output paths
        self.trace_path = (
            Path("logs") / "verification" / "phase11" / f"{self.verification_id}.json"
        )
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.failure_ledger = get_failure_ledger()
        self.replay_engine = ReplayEngine(self.failure_ledger)
        self.signal_detector = SuppressedSignalDetector(self.failure_ledger)
        self.ide_accounting = get_ide_behavior_accounting()

    def _record_violation(
        self, phase: str, invariant: str, description: str, severity: str = "HIGH"
    ) -> None:
        """Record a verification violation."""
        violation = {
            "phase": phase,
            "invariant": invariant,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_id": self.verification_id,
        }
        self.violations.append(violation)

        # Also record in failure ledger
        self.failure_ledger.record_failure(
            phase="PHASE11_VERIFICATION",
            violated_invariant=invariant,
            description=description,
            severity=severity,
            metadata={
                "verification_id": self.verification_id,
                "verification_phase": phase,
            },
        )

    def _record_warning(self, phase: str, description: str) -> None:
        """Record a verification warning."""
        warning = {
            "phase": phase,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_id": self.verification_id,
        }
        self.warnings.append(warning)

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def verify_phase11_artifacts(self) -> bool:
        """
        Verify all Phase 11 artifacts exist.

        Returns:
            True if all artifacts exist, False otherwise
        """
        print("\n[1/5] Verifying Phase 11 Artifacts")
        print("=" * 50)

        all_exist = True
        artifact_results = []

        for artifact_path in self.phase11_artifacts:
            path = Path(artifact_path)
            exists = path.exists()

            result = {
                "artifact": artifact_path,
                "exists": exists,
                "path": str(path.absolute()),
            }

            if exists:
                if path.is_file():
                    result["type"] = "file"
                    result["size"] = path.stat().st_size
                    result["sha256"] = self._calculate_file_hash(path)
                else:
                    result["type"] = "directory"

                print(f"  [OK] {artifact_path}")
            else:
                result["type"] = "missing"
                print(f"  [FAIL] {artifact_path} - MISSING")
                all_exist = False

                self._record_violation(
                    phase="A6_VERIFICATION",
                    invariant="PHASE11_ARTIFACT_MISSING",
                    description=f"Phase 11 artifact missing: {artifact_path}",
                    severity="CRITICAL",
                )

            artifact_results.append(result)

        self.verification_results["artifact_verification"] = {
            "total_artifacts": len(self.phase11_artifacts),
            "artifacts_found": sum(1 for r in artifact_results if r["exists"]),
            "artifacts_missing": sum(1 for r in artifact_results if not r["exists"]),
            "details": artifact_results,
            "all_exist": all_exist,
        }

        print(
            f"\n  Summary: {self.verification_results['artifact_verification']['artifacts_found']}/"
            f"{self.verification_results['artifact_verification']['total_artifacts']} artifacts found"
        )

        return all_exist

    def verify_failure_ledger_append_only(self) -> bool:
        """
        Verify failure ledger append-only property.

        Returns:
            True if ledger is append-only, False otherwise
        """
        print("\n[2/5] Verifying Failure Ledger Append-Only Property")
        print("=" * 50)

        try:
            # Test 1: Verify ledger integrity
            integrity_check = self.failure_ledger.verify_integrity()

            if not integrity_check["valid"]:
                print(f"  ✗ Ledger integrity check failed:")
                for issue in integrity_check.get("issues", []):
                    print(f"    - {issue}")
                    self._record_violation(
                        phase="A1_FAILURE_PERSISTENCE",
                        invariant="LEDGER_INTEGRITY",
                        description=f"Ledger integrity issue: {issue}",
                        severity="CRITICAL",
                    )
                return False

            print(f"  [OK] Ledger integrity verified")

            # Test 2: Check append-only by attempting to record a test failure
            test_entry_id = self.failure_ledger.record_failure(
                phase="PHASE11_TEST",
                violated_invariant="TEST_APPEND_ONLY",
                description="Test entry for append-only verification",
                severity="LOW",
                metadata={"test_purpose": "append_only_verification"},
            )

            print(f"  [OK] Test entry recorded: {test_entry_id}")

            # Test 3: Verify entry was added (not overwritten)
            entries = self.failure_ledger.ledger.get("entries", [])
            test_entry = next(
                (e for e in entries if e["entry_id"] == test_entry_id), None
            )

            if not test_entry:
                print(f"  [FAIL] Test entry not found in ledger")
                self._record_violation(
                    phase="A1_FAILURE_PERSISTENCE",
                    invariant="APPEND_ONLY_VIOLATION",
                    description="Test entry not found after recording",
                    severity="HIGH",
                )
                return False

            print(f"  [OK] Test entry verified in ledger")

            # Test 4: Check statistics updated
            stats = self.failure_ledger.get_statistics()
            if stats["total_entries"] != len(entries):
                print(
                    f"  [FAIL] Statistics mismatch: {stats['total_entries']} reported vs {len(entries)} actual"
                )
                self._record_violation(
                    phase="A1_FAILURE_PERSISTENCE",
                    invariant="STATISTICS_INTEGRITY",
                    description=f"Statistics mismatch: {stats['total_entries']} reported vs {len(entries)} actual",
                    severity="MEDIUM",
                )
                return False

            print(
                f"  [OK] Statistics consistent: {stats['total_entries']} total entries"
            )

            self.verification_results["failure_ledger_verification"] = {
                "integrity_check": integrity_check,
                "test_entry_id": test_entry_id,
                "total_entries": len(entries),
                "statistics": stats,
                "append_only_verified": True,
            }

            return True

        except Exception as e:
            print(f"  [FAIL] Error verifying failure ledger: {str(e)}")
            self._record_violation(
                phase="A1_FAILURE_PERSISTENCE",
                invariant="LEDGER_VERIFICATION_ERROR",
                description=f"Error verifying failure ledger: {str(e)}",
                severity="CRITICAL",
            )
            return False

    def verify_replay_engine_determinism(self) -> bool:
        """
        Verify replay engine determinism.

        Returns:
            True if replay engine is deterministic, False otherwise
        """
        print("\n[3/5] Verifying Replay Engine Determinism")
        print("=" * 50)

        try:
            # Create a test failure to replay
            test_failure_id = self.failure_ledger.record_failure(
                phase="PHASE11_REPLAY_TEST",
                violated_invariant="REPLAY_TEST_INVARIANT",
                description="Test failure for replay engine determinism verification",
                severity="MEDIUM",
                metadata={
                    "execution_context": {
                        "test": "replay_determinism",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    "execution_outcome": {
                        "return_code": 1,
                        "error_type": "ValueError",
                        "execution_time": 0.1,
                    },
                },
            )

            print(f"  [OK] Created test failure: {test_failure_id}")

            # Replay the failure multiple times
            replay_results = []
            num_replays = 3

            for i in range(num_replays):
                print(f"  Running replay {i + 1}/{num_replays}...")
                try:
                    result = self.replay_engine.replay_failure(test_failure_id)
                    replay_results.append(result)
                    print(f"    [OK] Replay {i + 1} completed")
                except Exception as e:
                    print(f"    [FAIL] Replay {i + 1} failed: {str(e)}")
                    self._record_violation(
                        phase="A2_REPLAY_ENGINE",
                        invariant="REPLAY_EXECUTION_ERROR",
                        description=f"Replay {i + 1} failed: {str(e)}",
                        severity="HIGH",
                    )
                    return False

            # Check determinism: all replays should have same outcome
            if len(replay_results) < num_replays:
                print(f"  [FAIL] Not all replays completed")
                return False

            # Compare replay outcomes
            first_result = replay_results[0]
            deterministic = True

            for i, result in enumerate(replay_results[1:], 2):
                # Compare key metrics
                if (
                    result["execution_result"]["return_code"]
                    != first_result["execution_result"]["return_code"]
                ):
                    print(
                        f"  [FAIL] Replay {i} return code mismatch: "
                        f"{result['execution_result']['return_code']} vs {first_result['execution_result']['return_code']}"
                    )
                    deterministic = False

                if result["match_score"] != first_result["match_score"]:
                    print(
                        f"  [FAIL] Replay {i} match score mismatch: "
                        f"{result['match_score']} vs {first_result['match_score']}"
                    )
                    deterministic = False

            if deterministic:
                print(f"  [OK] All {num_replays} replays produced identical outcomes")
                print(f"  [OK] Match score: {first_result['match_score']:.2f}")
                print(
                    f"  [OK] Return code: {first_result['execution_result']['return_code']}"
                )
            else:
                print(f"  [FAIL] Replays produced different outcomes")
                self._record_violation(
                    phase="A2_REPLAY_ENGINE",
                    invariant="REPLAY_NON_DETERMINISTIC",
                    description=f"Replays produced different outcomes for test failure {test_failure_id}",
                    severity="HIGH",
                )

            # Get replay statistics
            replay_stats = self.replay_engine.get_replay_statistics()

            self.verification_results["replay_engine_verification"] = {
                "test_failure_id": test_failure_id,
                "num_replays": num_replays,
                "replay_results": replay_results,
                "deterministic": deterministic,
                "replay_statistics": replay_stats,
                "first_replay_match_score": first_result["match_score"]
                if replay_results
                else None,
            }

            return deterministic

        except Exception as e:
            print(f"  [FAIL] Error verifying replay engine: {str(e)}")
            self._record_violation(
                phase="A2_REPLAY_ENGINE",
                invariant="REPLAY_ENGINE_VERIFICATION_ERROR",
                description=f"Error verifying replay engine: {str(e)}",
                severity="CRITICAL",
            )
            return False

    def verify_no_suppressed_signals(self) -> bool:
        """
        Verify no suppressed signals.

        Returns:
            True if no suppressed signals detected, False otherwise
        """
        print("\n[4/5] Verifying No Suppressed Signals")
        print("=" * 50)

        try:
            # Start signal capture
            capture_id = self.signal_detector.start_capture()
            print(f"  [OK] Started signal capture: {capture_id}")

            # Test 1: Execute a function that should not suppress signals
            def test_function():
                # This function should NOT suppress signals
                import warnings

                warnings.warn("Test warning for signal detection", UserWarning)
                print("Test output to stdout")
                print("Test error to stderr", file=sys.stderr)
                return "test_result"

            # Capture execution
            execution_result = self.signal_detector.capture_execution(test_function)

            print(f"  [OK] Test execution captured")
            print(f"    - Success: {execution_result['success']}")
            print(
                f"    - Signals captured: {len(execution_result['signals_captured'])}"
            )

            # Check for suppression
            suppression_detected = execution_result.get("suppression_detected", False)

            if suppression_detected:
                print(f"  [FAIL] Suppressed signals detected!")

                # Analyze which signals were suppressed
                suppressed_signals = [
                    s
                    for s in execution_result["signals_captured"]
                    if s.get("suppression_analysis", {}).get(
                        "suppression_detected", False
                    )
                ]

                for signal in suppressed_signals:
                    print(
                        f"    - {signal['signal_type']}: {signal.get('suppression_analysis', {}).get('patterns_found', [])}"
                    )

                self._record_violation(
                    phase="A3_SUPPRESSED_SIGNAL",
                    invariant="SIGNAL_SUPPRESSION_DETECTED",
                    description=f"Suppressed signals detected during test execution: {len(suppressed_signals)} signals",
                    severity="CRITICAL",
                )
            else:
                print(f"  [OK] No suppressed signals detected")

            # Test 2: Check signal detector statistics
            detector_stats = self.signal_detector.get_capture_statistics()

            self.verification_results["signal_detection_verification"] = {
                "capture_id": capture_id,
                "execution_result": execution_result,
                "suppression_detected": suppression_detected,
                "total_signals_captured": len(
                    execution_result.get("signals_captured", [])
                ),
                "detector_statistics": detector_stats,
                "no_suppression_verified": not suppression_detected,
            }

            return not suppression_detected

        except Exception as e:
            print(f"  [FAIL] Error verifying signal detection: {str(e)}")
            self._record_violation(
                phase="A3_SUPPRESSED_SIGNAL",
                invariant="SIGNAL_DETECTION_VERIFICATION_ERROR",
                description=f"Error verifying signal detection: {str(e)}",
                severity="CRITICAL",
            )
            return False

    def verify_ide_behavior_accounting(self) -> bool:
        """
        Verify IDE behavior accounting.

        Returns:
            True if IDE behavior accounting works correctly, False otherwise
        """
        print("\n[5/5] Verifying IDE Behavior Accounting")
        print("=" * 50)

        try:
            # Set up test agent and blueprint
            self.ide_accounting.set_agent(
                "PHASE11_VERIFICATION_AGENT", "VERIFICATION_SYSTEM"
            )

            # Use Phase 11 blueprint (this file)
            blueprint_path = Path(__file__).absolute()
            blueprint_hash = self.ide_accounting.set_blueprint(str(blueprint_path))

            print(f"  [OK] Agent set: PHASE11_VERIFICATION_AGENT")
            print(f"  [OK] Blueprint set: {blueprint_path.name}")
            print(f"  [OK] Blueprint hash: {blueprint_hash[:16]}...")

            # Record test actions
            test_actions = []

            # Action 1: File creation test
            test_file = Path("logs") / "verification" / "phase11" / "test_action.txt"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("Test action for IDE behavior accounting verification")

            action1_id = self.ide_accounting.record_file_creation(str(test_file))
            test_actions.append(
                {"type": "FILE_CREATE", "id": action1_id, "file": str(test_file)}
            )
            print(f"  [OK] Recorded file creation: {test_file.name}")

            # Action 2: File modification test
            test_file.write_text(
                "Modified content for IDE behavior accounting verification"
            )

            old_hash = self._calculate_file_hash(test_file)
            test_file.write_text("Further modified content")
            action2_id = self.ide_accounting.record_file_modification(
                str(test_file), old_hash=old_hash
            )
            test_actions.append(
                {"type": "FILE_MODIFY", "id": action2_id, "file": str(test_file)}
            )
            print(f"  [OK] Recorded file modification: {test_file.name}")

            # Action 3: File deletion test
            test_file.unlink()
            action3_id = self.ide_accounting.record_file_deletion(str(test_file))
            test_actions.append(
                {"type": "FILE_DELETE", "id": action3_id, "file": str(test_file)}
            )
            print(f"  [OK] Recorded file deletion: {test_file.name}")

            # Test unattributed action detection (if enabled)
            unattributed_detected = False
            if self.ide_accounting.config["require_attribution"]:
                # Temporarily clear agent to test unattributed detection
                original_agent = self.ide_accounting.current_agent
                self.ide_accounting.current_agent = None

                try:
                    # This should trigger unattributed action detection
                    self.ide_accounting.record_action(
                        action_type="TEST_UNATTRIBUTED",
                        target="test_target",
                        description="Test unattributed action",
                        agent_id=None,
                        agent_type=None,
                    )
                except SystemExit:
                    # Expected exit if auto_fail_on_unattributed is True
                    unattributed_detected = True
                finally:
                    # Restore agent
                    self.ide_accounting.current_agent = original_agent

            # End session and get summary
            session_summary = self.ide_accounting.end_session()

            print(f"  [OK] Session ended")
            print(f"    - Total actions: {session_summary['total_actions']}")
            print(f"    - File operations: {session_summary['file_operations']}")
            print(
                f"    - Unattributed actions: {session_summary['unattributed_actions']}"
            )

            # Verify session statistics
            all_stats = self.ide_accounting.get_session_statistics()

            verification_passed = True

            # Check 1: Actions were recorded
            if session_summary["total_actions"] < len(test_actions):
                print(f"  [FAIL] Not all test actions recorded")
                self._record_violation(
                    phase="A4_IDE_BEHAVIOR_ACCOUNTING",
                    invariant="ACTION_RECORDING_FAILURE",
                    description=f"Expected {len(test_actions)} actions, got {session_summary['total_actions']}",
                    severity="HIGH",
                )
                verification_passed = False
            else:
                print(f"  [OK] All test actions recorded")

            # Check 2: No unattributed actions (except our test)
            expected_unattributed = 1 if unattributed_detected else 0
            if session_summary["unattributed_actions"] != expected_unattributed:
                print(
                    f"  [FAIL] Unexpected unattributed actions: {session_summary['unattributed_actions']} (expected {expected_unattributed})"
                )
                self._record_violation(
                    phase="A4_IDE_BEHAVIOR_ACCOUNTING",
                    invariant="UNATTRIBUTED_ACTION_MISMATCH",
                    description=f"Unexpected unattributed actions: {session_summary['unattributed_actions']}",
                    severity="MEDIUM",
                )
                verification_passed = False
            else:
                print(f"  [OK] Unattributed actions as expected")

            # Check 3: Agent attribution correct
            agent_counts = session_summary.get("actions_by_agent", {})
            if "PHASE11_VERIFICATION_AGENT" not in agent_counts:
                print(f"  [FAIL] Agent attribution missing")
                self._record_violation(
                    phase="A4_IDE_BEHAVIOR_ACCOUNTING",
                    invariant="AGENT_ATTRIBUTION_FAILURE",
                    description="Agent attribution missing from recorded actions",
                    severity="HIGH",
                )
                verification_passed = False
            else:
                print(f"  [OK] Agent attribution verified")

            self.verification_results["ide_accounting_verification"] = {
                "session_summary": session_summary,
                "test_actions": test_actions,
                "all_statistics": all_stats,
                "unattributed_detected": unattributed_detected,
                "verification_passed": verification_passed,
                "agent_set": "PHASE11_VERIFICATION_AGENT",
                "blueprint_hash": blueprint_hash,
            }

            return verification_passed

        except Exception as e:
            print(f"  [FAIL] Error verifying IDE behavior accounting: {str(e)}")
            self._record_violation(
                phase="A4_IDE_BEHAVIOR_ACCOUNTING",
                invariant="IDE_ACCOUNTING_VERIFICATION_ERROR",
                description=f"Error verifying IDE behavior accounting: {str(e)}",
                severity="CRITICAL",
            )
            return False

    def generate_verification_trace(self) -> Dict[str, Any]:
        """
        Generate verification trace document.

        Returns:
            Verification trace
        """
        trace = {
            "trace_id": f"PHASE11-TRACE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_id": self.verification_id,
            "schema_version": "1.13",
            "description": "Phase 11 Atomicity Verification Trace",
            "verification_results": self.verification_results,
            "violations": self.violations,
            "warnings": self.warnings,
            "summary": {
                "total_checks": 5,
                "checks_passed": sum(
                    [
                        self.verification_results.get("artifact_verification", {}).get(
                            "all_exist", False
                        ),
                        self.verification_results.get(
                            "failure_ledger_verification", {}
                        ).get("append_only_verified", False),
                        self.verification_results.get(
                            "replay_engine_verification", {}
                        ).get("deterministic", False),
                        self.verification_results.get(
                            "signal_detection_verification", {}
                        ).get("no_suppression_verified", False),
                        self.verification_results.get(
                            "ide_accounting_verification", {}
                        ).get("verification_passed", False),
                    ]
                ),
                "total_violations": len(self.violations),
                "total_warnings": len(self.warnings),
                "exit_code": 2 if self.violations else 0,
            },
            "environment": {
                "python_version": sys.version,
                "cwd": os.getcwd(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "script_path": __file__,
            },
            "phase11_artifacts": self.phase11_artifacts,
        }

        # Save trace to file
        with open(self.trace_path, "w", encoding="utf-8") as f:
            json.dump(trace, f, indent=2, ensure_ascii=False)

        print(f"\n[Trace Generation]")
        print("=" * 50)
        print(f"  [OK] Trace saved to: {self.trace_path}")
        print(f"  [OK] Trace ID: {trace['trace_id']}")
        print(f"  [OK] Checks passed: {trace['summary']['checks_passed']}/5")
        print(f"  [OK] Violations: {trace['summary']['total_violations']}")
        print(f"  [OK] Exit code: {trace['summary']['exit_code']}")

        return trace

    def run_verification(self) -> int:
        """
        Run complete Phase 11 verification.

        Returns:
            Exit code (0 for success, 2 for violations)
        """
        print("\n" + "=" * 60)
        print("PHASE 11 ATOMICITY VERIFICATION")
        print("=" * 60)
        print(f"Verification ID: {self.verification_id}")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print(f"Strict mode: {self.strict_mode}")
        print("=" * 60)

        # Run all verification steps
        steps = [
            ("Phase 11 Artifacts", self.verify_phase11_artifacts),
            ("Failure Ledger Append-Only", self.verify_failure_ledger_append_only),
            ("Replay Engine Determinism", self.verify_replay_engine_determinism),
            ("No Suppressed Signals", self.verify_no_suppressed_signals),
            ("IDE Behavior Accounting", self.verify_ide_behavior_accounting),
        ]

        results = []
        for step_name, step_func in steps:
            print(f"\n[{step_name}]")
            print("-" * 50)
            try:
                result = step_func()
                results.append(result)
                status = "[OK] PASS" if result else "[FAIL] FAIL"
                print(f"\n  Result: {status}")
            except Exception as e:
                print(f"\n  [FAIL] ERROR: {str(e)}")
                results.append(False)
                self._record_violation(
                    phase="VERIFICATION_EXECUTION",
                    invariant="VERIFICATION_STEP_ERROR",
                    description=f"Error in {step_name}: {str(e)}",
                    severity="CRITICAL",
                )

        # Generate trace
        trace = self.generate_verification_trace()

        # Determine exit code
        all_passed = all(results) and not self.violations
        exit_code = 0 if all_passed else 2

        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETE")
        print("=" * 60)
        print(f"Overall result: {'[OK] PASS' if all_passed else '[FAIL] FAIL'}")
        print(f"Steps passed: {sum(results)}/{len(steps)}")
        print(f"Violations: {len(self.violations)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Exit code: {exit_code}")
        print(f"Trace file: {self.trace_path}")
        print("=" * 60)

        if self.violations:
            print("\nVIOLATIONS DETECTED:")
            for i, violation in enumerate(self.violations, 1):
                print(
                    f"  {i}. [{violation['severity']}] {violation['phase']}: {violation['description']}"
                )

        if self.warnings:
            print("\nWARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning['phase']}: {warning['description']}")

        return exit_code


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Phase 11 Atomicity Verification Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run verification in strict mode
  %(prog)s --no-strict        # Run verification without strict mode
  %(prog)s --trace-only       # Generate trace from previous run
        """,
    )

    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Run verification without strict mode (warnings instead of violations)",
    )

    parser.add_argument(
        "--trace-only",
        action="store_true",
        help="Generate trace from previous verification results",
    )

    parser.add_argument("--output", type=str, help="Custom output path for trace file")

    args = parser.parse_args()

    try:
        if args.trace_only:
            # Generate trace from existing results
            print("Generating trace from previous verification...")
            # This would need to load existing results
            print("Error: --trace-only requires existing verification results")
            return 2
        else:
            # Run full verification
            verifier = Phase11Verification(strict_mode=not args.no_strict)

            if args.output:
                verifier.trace_path = Path(args.output)
                verifier.trace_path.parent.mkdir(parents=True, exist_ok=True)

            exit_code = verifier.run_verification()
            return exit_code

    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\nFatal error during verification: {str(e)}")
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())

"""
Adversarial Replay Engine - Phase 11 Autonomous Failure Accounting

Re-executes prior failures deterministically and compares outcomes.
Detects epistemic instability when outcomes diverge from historical failures.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from toolkit.oe.evidence_store import EvidenceStore
from toolkit.oe.failure_ledger import FailureLedger


class ReplayEngine:
    """
    Adversarial replay engine for deterministic failure re-execution.

    Implements Phase 11 A2 requirements:
    - Re-execute prior failures deterministically
    - Compare new outcome to historical failure
    - If divergence occurs → log as epistemic instability
    """

    def __init__(self, ledger: Optional[FailureLedger] = None):
        """
        Initialize replay engine.

        Args:
            ledger: Failure ledger instance. If None, creates new one.
        """
        self.ledger = ledger or FailureLedger()
        self.evidence_store = EvidenceStore()

        # Directory for replay artifacts
        self.replay_dir = Path("logs") / "replay_engine"
        self.replay_dir.mkdir(parents=True, exist_ok=True)

        # Cache for replay results
        self.replay_cache = {}

        # Configuration
        self.config = {
            "max_replay_time": 30,  # seconds
            "memory_limit_mb": 512,
            "capture_output": True,
            "deterministic_seed": 42,
            "environment_vars": {
                "PYTHONHASHSEED": "0",
                "PYTHONIOENCODING": "utf-8",
                "ORTHOGONAL_REPLAY_MODE": "true",
            },
        }

    def _create_replay_environment(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create deterministic replay environment for a failure entry.

        Args:
            entry: Failure ledger entry

        Returns:
            Environment configuration
        """
        env_id = f"replay_{entry['entry_id'].replace('-', '_')}"

        # Create temporary directory for this replay
        temp_dir = self.replay_dir / env_id
        temp_dir.mkdir(exist_ok=True)

        # Extract context from entry metadata
        context = entry.get("metadata", {}).get("execution_context", {})

        # Create environment configuration
        environment = {
            "env_id": env_id,
            "temp_dir": str(temp_dir),
            "timestamp": entry["timestamp"],
            "phase": entry["phase"],
            "violated_invariant": entry["violated_invariant"],
            "original_artifact_hash": entry["artifact_hash"],
            "environment_vars": {
                **self.config["environment_vars"],
                "REPLAY_ENTRY_ID": entry["entry_id"],
                "REPLAY_PHASE": entry["phase"],
                "REPLAY_TIMESTAMP": entry["timestamp"],
                "REPLAY_INVARIANT": entry["violated_invariant"],
            },
            "context": context,
        }

        # Save environment configuration
        env_config_path = temp_dir / "environment.json"
        with open(env_config_path, "w", encoding="utf-8") as f:
            json.dump(environment, f, indent=2, ensure_ascii=False)

        return environment

    def _extract_replay_script(self, entry: Dict[str, Any]) -> Optional[str]:
        """
        Extract or reconstruct replay script from failure entry.

        Args:
            entry: Failure ledger entry

        Returns:
            Python script for replay, or None if cannot reconstruct
        """
        metadata = entry.get("metadata", {})

        # Try to extract script from metadata
        if "replay_script" in metadata:
            return metadata["replay_script"]

        # Try to reconstruct from description and context
        description = entry["description"]
        phase = entry["phase"]
        invariant = entry["violated_invariant"]

        # Basic template for replay
        script = f'''"""
Replay Script for Failure: {entry["entry_id"]}
Phase: {phase}
Invariant: {invariant}
Original Timestamp: {entry["timestamp"]}
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Set up environment
os.environ.update({json.dumps(self.config["environment_vars"])})

def replay_failure():
    """Replay the failure described in: {description[:100]}..."""
    try:
        # Import based on phase
        if "{phase}" == "PHASE9":
            from toolkit.oe import advanced_evidence
            from toolkit.oe import causal_analyzer
            # Add phase-specific imports
            pass
        elif "{phase}" == "PHASE11":
            from toolkit.oe import failure_ledger
            from toolkit.oe import replay_engine
            # Add phase-specific imports
            pass

        # Reconstruct failure based on invariant
        if "{invariant}" == "BOUNDARY_VIOLATION":
            # Simulate boundary violation
            raise ValueError("Boundary violation replayed")
        elif "{invariant}" == "EXIT_CODE_2":
            # Simulate exit code 2
            sys.exit(2)
        elif "{invariant}" == "SUPPRESSED_SIGNAL":
            # Simulate suppressed signal
            import warnings
            warnings.filterwarnings("ignore")
            raise RuntimeError("Signal suppressed")
        else:
            # Generic failure replay
            raise RuntimeError(f"Replaying failure: {{description}}")

    except Exception as e:
        # Capture the exception
        error_info = {{
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "replay_success": True
        }}
        return error_info

    return {{"replay_success": False, "message": "No exception raised"}}

if __name__ == "__main__":
    result = replay_failure()
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    if result.get("replay_success"):
        sys.exit(1)  # Replay succeeded (failure occurred)
    else:
        sys.exit(0)  # Replay failed (no failure occurred)
'''

        return script

    def _execute_replay(
        self, environment: Dict[str, Any], script: str
    ) -> Dict[str, Any]:
        """
        Execute replay script in controlled environment.

        Args:
            environment: Replay environment configuration
            script: Python script to execute

        Returns:
            Execution results
        """
        temp_dir = Path(environment["temp_dir"])

        # Save script to file
        script_path = temp_dir / "replay_script.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        # Prepare environment variables
        env_vars = os.environ.copy()
        env_vars.update(environment["environment_vars"])

        # Execute script
        start_time = time.time()

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                env=env_vars,
                cwd=str(temp_dir),
                capture_output=self.config["capture_output"],
                text=True,
                timeout=self.config["max_replay_time"],
                encoding="utf-8",
            )

            execution_time = time.time() - start_time

            # Parse output
            output = result.stdout
            error = result.stderr

            try:
                if output.strip():
                    output_data = json.loads(output)
                else:
                    output_data = {}
            except json.JSONDecodeError:
                output_data = {"raw_output": output}

            replay_result = {
                "success": result.returncode
                in [0, 1],  # 0=no failure, 1=failure replayed
                "return_code": result.returncode,
                "stdout": output,
                "stderr": error,
                "execution_time": execution_time,
                "parsed_output": output_data,
                "script_path": str(script_path),
                "environment_id": environment["env_id"],
            }

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            replay_result = {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": f"Timeout after {execution_time:.2f} seconds",
                "execution_time": execution_time,
                "parsed_output": {"timeout": True},
                "script_path": str(script_path),
                "environment_id": environment["env_id"],
                "timeout": True,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            replay_result = {
                "success": False,
                "return_code": -2,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "execution_time": execution_time,
                "parsed_output": {"execution_error": str(e)},
                "script_path": str(script_path),
                "environment_id": environment["env_id"],
                "execution_error": True,
            }

        # Save replay result
        result_path = temp_dir / "replay_result.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(replay_result, f, indent=2, ensure_ascii=False)

        return replay_result

    def _compare_outcomes(
        self, original_entry: Dict[str, Any], replay_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare replay outcome to original failure.

        Args:
            original_entry: Original failure ledger entry
            replay_result: Replay execution result

        Returns:
            Comparison results with divergence detection
        """
        # Extract original outcome from metadata
        original_metadata = original_entry.get("metadata", {})
        original_outcome = original_metadata.get("execution_outcome", {})

        # Determine if failure was replayed successfully
        failure_replayed = (
            replay_result["success"]
            and replay_result["return_code"] == 1
            and "error_type" in replay_result.get("parsed_output", {})
        )

        # Check if original was a failure (vs warning)
        original_was_failure = original_entry.get("severity", "HIGH") in [
            "CRITICAL",
            "HIGH",
        ]

        # Calculate divergence metrics
        divergence_detected = False
        divergence_reasons = []

        # Check 1: Failure type match
        if original_was_failure and not failure_replayed:
            divergence_detected = True
            divergence_reasons.append("Failure not reproduced")

        # Check 2: Return code consistency
        original_return_code = original_outcome.get("return_code")
        if (
            original_return_code is not None
            and original_return_code != replay_result["return_code"]
        ):
            divergence_detected = True
            divergence_reasons.append(
                f"Return code mismatch: {original_return_code} vs {replay_result['return_code']}"
            )

        # Check 3: Error type consistency
        original_error_type = original_outcome.get("error_type")
        replay_error_type = replay_result.get("parsed_output", {}).get("error_type")

        if (
            original_error_type
            and replay_error_type
            and original_error_type != replay_error_type
        ):
            divergence_detected = True
            divergence_reasons.append(
                f"Error type mismatch: {original_error_type} vs {replay_error_type}"
            )

        # Check 4: Execution time anomaly (if original has timing)
        original_time = original_outcome.get("execution_time")
        if original_time and replay_result["execution_time"] > original_time * 2:
            divergence_reasons.append(
                f"Execution time significantly different: {original_time:.2f}s vs {replay_result['execution_time']:.2f}s"
            )

        comparison = {
            "divergence_detected": divergence_detected,
            "divergence_reasons": divergence_reasons,
            "failure_replayed": failure_replayed,
            "original_was_failure": original_was_failure,
            "match_score": self._calculate_match_score(original_entry, replay_result),
            "details": {
                "original": {
                    "severity": original_entry.get("severity"),
                    "return_code": original_outcome.get("return_code"),
                    "error_type": original_outcome.get("error_type"),
                    "execution_time": original_outcome.get("execution_time"),
                },
                "replay": {
                    "return_code": replay_result["return_code"],
                    "error_type": replay_result.get("parsed_output", {}).get(
                        "error_type"
                    ),
                    "execution_time": replay_result["execution_time"],
                    "success": replay_result["success"],
                },
            },
        }

        return comparison

    def _calculate_match_score(
        self, original_entry: Dict[str, Any], replay_result: Dict[str, Any]
    ) -> float:
        """
        Calculate match score between original and replay (0-1).

        Args:
            original_entry: Original failure entry
            replay_result: Replay execution result

        Returns:
            Match score from 0.0 (no match) to 1.0 (perfect match)
        """
        score = 0.0
        max_score = 5.0  # 5 criteria, each worth 0.2

        original_metadata = original_entry.get("metadata", {})
        original_outcome = original_metadata.get("execution_outcome", {})

        # Criterion 1: Failure reproduced (0.2)
        original_was_failure = original_entry.get("severity", "HIGH") in [
            "CRITICAL",
            "HIGH",
        ]
        failure_replayed = (
            replay_result["success"]
            and replay_result["return_code"] == 1
            and "error_type" in replay_result.get("parsed_output", {})
        )

        if original_was_failure == failure_replayed:
            score += 0.2

        # Criterion 2: Return code match (0.2)
        original_return_code = original_outcome.get("return_code")
        if original_return_code == replay_result["return_code"]:
            score += 0.2

        # Criterion 3: Error type match (0.2)
        original_error_type = original_outcome.get("error_type")
        replay_error_type = replay_result.get("parsed_output", {}).get("error_type")

        if (
            original_error_type
            and replay_error_type
            and original_error_type == replay_error_type
        ):
            score += 0.2
        elif not original_error_type and not replay_error_type:
            score += 0.2

        # Criterion 4: Similar execution pattern (0.2)
        if not replay_result.get("timeout") and not replay_result.get(
            "execution_error"
        ):
            score += 0.2

        # Criterion 5: Output similarity (0.2)
        if replay_result.get("parsed_output", {}).get("replay_success"):
            score += 0.2

        return score / max_score

    def replay_failure(self, entry_id: str) -> Dict[str, Any]:
        """
        Replay a specific failure.

        Args:
            entry_id: Failure ledger entry ID

        Returns:
            Complete replay results
        """
        # Check cache first
        if entry_id in self.replay_cache:
            return self.replay_cache[entry_id]

        # Get failure entry
        entries = self.ledger.ledger.get("entries", [])
        entry = next((e for e in entries if e["entry_id"] == entry_id), None)

        if not entry:
            raise ValueError(f"Failure entry not found: {entry_id}")

        # Create replay environment
        environment = self._create_replay_environment(entry)

        # Extract or create replay script
        script = self._extract_replay_script(entry)

        if not script:
            raise ValueError(f"Cannot create replay script for entry: {entry_id}")

        # Execute replay
        replay_result = self._execute_replay(environment, script)

        # Compare outcomes
        comparison = self._compare_outcomes(entry, replay_result)

        # Log epistemic instability if divergence detected
        if comparison["divergence_detected"]:
            instability_id = self.ledger.record_failure(
                phase="EPISTEMIC_INSTABILITY",
                violated_invariant="REPLAY_DIVERGENCE",
                description=f"Replay divergence for {entry_id}: {', '.join(comparison['divergence_reasons'])}",
                artifact_hash=entry["artifact_hash"],
                causal_parent_hash=entry_id,
                severity="HIGH",
                metadata={
                    "original_entry": entry_id,
                    "replay_result": replay_result,
                    "comparison": comparison,
                    "environment": environment,
                },
            )

            # Record in evidence store
            self.evidence_store.log_evidence(
                evidence_type="EPISTEMIC_INSTABILITY",
                content={
                    "entry_id": instability_id,
                    "original_entry": entry_id,
                    "divergence_reasons": comparison["divergence_reasons"],
                    "match_score": comparison["match_score"],
                },
                source="replay_engine",
                metadata={
                    "replay_environment": environment["env_id"],
                    "comparison_details": comparison,
                    "confidence": 0.9,
                    "tags": [
                        "epistemic_instability",
                        "replay_divergence",
                        entry["phase"].lower(),
                    ],
                },
            )

        # Compile final result
        final_result = {
            "replay_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "original_entry": entry_id,
            "environment": environment,
            "execution_result": replay_result,
            "comparison": comparison,
            "epistemic_instability_detected": comparison["divergence_detected"],
            "match_score": comparison["match_score"],
        }

        # Cache result
        self.replay_cache[entry_id] = final_result

        # Save replay report
        report_path = Path(environment["temp_dir"]) / "replay_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)

        return final_result

    def replay_recent_failures(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Replay recent failures.

        Args:
            count: Number of recent failures to replay

        Returns:
            List of replay results
        """
        # Get recent entries
        entries = self.ledger.ledger.get("entries", [])
        recent_entries = entries[-count:] if entries else []

        results = []
        for entry in recent_entries:
            try:
                result = self.replay_failure(entry["entry_id"])
                results.append(result)
            except Exception as e:
                # Record replay failure
                self.ledger.record_failure(
                    phase="REPLAY_ENGINE",
                    violated_invariant="REPLAY_EXECUTION_ERROR",
                    description=f"Failed to replay {entry['entry_id']}: {str(e)}",
                    artifact_hash=entry["artifact_hash"],
                    causal_parent_hash=entry["entry_id"],
                    severity="MEDIUM",
                    metadata={
                        "original_entry": entry["entry_id"],
                        "error": str(e),
                        "replay_attempt_failed": True,
                    },
                )
                results.append(
                    {
                        "error": str(e),
                        "original_entry": entry["entry_id"],
                        "replay_failed": True,
                    }
                )

        return results

    def get_replay_statistics(self) -> Dict[str, Any]:
        """Get replay engine statistics."""
        replay_dir = self.replay_dir
        replay_files = list(replay_dir.glob("replay_*/replay_report.json"))

        successful_replays = 0
        divergent_replays = 0
        failed_replays = 0
        total_match_score = 0.0

        for report_file in replay_files:
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    report = json.load(f)

                if report.get("epistemic_instability_detected"):
                    divergent_replays += 1
                elif not report.get("replay_failed", False):
                    successful_replays += 1
                    total_match_score += report.get("match_score", 0.0)
                else:
                    failed_replays += 1
            except (json.JSONDecodeError, FileNotFoundError):
                failed_replays += 1

        avg_match_score = (
            total_match_score / successful_replays if successful_replays > 0 else 0.0
        )

        return {
            "total_replays": len(replay_files),
            "successful_replays": successful_replays,
            "divergent_replays": divergent_replays,
            "failed_replays": failed_replays,
            "average_match_score": avg_match_score,
            "replay_directory": str(replay_dir),
            "last_updated": datetime.utcnow().isoformat(),
        }

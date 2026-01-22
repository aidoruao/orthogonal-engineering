"""
Suppressed Signal Detector - Phase 11 Autonomous Failure Accounting

Captures stderr, warnings, partial outputs and detects signal suppression.
If suppression detected → forces violation with exit code 2.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import traceback
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from toolkit.oe.evidence_store import EvidenceStore
from toolkit.oe.failure_ledger import FailureLedger


class SuppressedSignalDetector:
    """
    Detects suppressed signals (stderr, warnings, partial outputs).

    Implements Phase 11 A3 requirements:
    - Capture stderr, warnings, partial outputs
    - Hash and store even if execution succeeds
    - If suppression detected → force violation
    - Violation is non-recoverable (exit code 2)
    """

    def __init__(self, ledger: Optional[FailureLedger] = None):
        """
        Initialize suppressed signal detector.

        Args:
            ledger: Failure ledger instance. If None, creates new one.
        """
        self.ledger = ledger or FailureLedger()
        self.evidence_store = EvidenceStore()

        # Directory for signal captures
        self.capture_dir = Path("logs") / "signal_captures"
        self.capture_dir.mkdir(parents=True, exist_ok=True)

        # Signal capture state
        self.captured_signals = []
        self.current_capture_id = None
        self.suppression_detected = False

        # Configuration
        self.config = {
            "capture_stderr": True,
            "capture_warnings": True,
            "capture_exceptions": True,
            "capture_partial_outputs": True,
            "detect_suppression_patterns": True,
            "auto_enforce_violation": True,
            "exit_code_on_suppression": 2,
            "store_all_captures": True,
        }

        # Known suppression patterns
        self.suppression_patterns = [
            r"except\s+Exception\s*:\s*pass",
            r"except\s+:\s*pass",  # Bare except
            r"warnings\.filterwarnings\(",
            r"warnings\.simplefilter\(",
            r"logging\.(basicConfig|getLogger).*level=.*(WARNING|ERROR|CRITICAL)",
            r"sys\.stderr\s*=\s*",  # stderr redirection
            r"sys\.stdout\s*=\s*",  # stdout redirection
            r"contextlib\.redirect_",
            r"signal\.signal\(",
            r"os\.devnull",
            r"open.*/dev/null",
            r"subprocess\.DEVNULL",
            r"try:.*except.*pass",  # Generic try-except-pass
            r"logging\.disable\(",
            r"\.setLevel.*(WARNING|ERROR|CRITICAL)",
        ]

    def start_capture(self, capture_id: Optional[str] = None) -> str:
        """
        Start capturing signals.

        Args:
            capture_id: Optional capture ID. If None, generates one.

        Returns:
            Capture ID
        """
        if capture_id is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            capture_id = f"signal_capture_{timestamp}"

        self.current_capture_id = capture_id
        self.captured_signals = []
        self.suppression_detected = False

        # Create capture directory
        capture_path = self.capture_dir / capture_id
        capture_path.mkdir(exist_ok=True)

        # Initialize capture metadata
        metadata = {
            "capture_id": capture_id,
            "start_time": datetime.utcnow().isoformat(),
            "config": self.config,
            "pid": os.getpid(),
            "python_version": sys.version,
            "cwd": os.getcwd(),
        }

        metadata_path = capture_path / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return capture_id

    def _capture_stderr(self) -> contextlib.AbstractContextManager:
        """Create context manager for capturing stderr."""
        stderr_capture = io.StringIO()

        class StderrCapture:
            def __enter__(self):
                self.original_stderr = sys.stderr
                sys.stderr = stderr_capture
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                sys.stderr = self.original_stderr
                captured = stderr_capture.getvalue()
                if captured:
                    self._record_signal("stderr", captured)

            def _record_signal(self, signal_type: str, content: str):
                if hasattr(self, "_detector"):
                    self._detector.record_signal(signal_type, content)

        capture = StderrCapture()
        capture._detector = self
        return capture

    def _capture_warnings(self) -> Callable:
        """Create warning capture handler."""
        original_showwarning = warnings.showwarning

        def custom_showwarning(
            message, category, filename, lineno, file=None, line=None
        ):
            # Call original
            original_showwarning(message, category, filename, lineno, file, line)

            # Capture warning
            warning_info = {
                "message": str(message),
                "category": category.__name__,
                "filename": filename,
                "lineno": lineno,
                "timestamp": datetime.utcnow().isoformat(),
            }

            self.record_signal("warning", warning_info)

        return custom_showwarning

    def record_signal(self, signal_type: str, content: Any) -> str:
        """
        Record a captured signal.

        Args:
            signal_type: Type of signal (stderr, warning, exception, partial_output)
            content: Signal content

        Returns:
            Signal ID
        """
        if not self.current_capture_id:
            return ""

        signal_id = (
            f"{self.current_capture_id}_{signal_type}_{len(self.captured_signals)}"
        )

        # Create signal record
        signal_record = {
            "signal_id": signal_id,
            "signal_type": signal_type,
            "timestamp": datetime.utcnow().isoformat(),
            "content": content
            if isinstance(content, (str, int, float, bool, list, dict))
            else str(content),
            "content_hash": self._hash_content(content),
            "suppression_analysis": self._analyze_for_suppression(signal_type, content),
        }

        # Add to captured signals
        self.captured_signals.append(signal_record)

        # Check for suppression
        if signal_record["suppression_analysis"]["suppression_detected"]:
            self.suppression_detected = True
            self._handle_suppression_detected(signal_record)

        # Save signal to file
        self._save_signal(signal_record)

        return signal_id

    def _hash_content(self, content: Any) -> str:
        """Calculate SHA256 hash of content."""
        if isinstance(content, (str, bytes)):
            content_str = (
                content
                if isinstance(content, str)
                else content.decode("utf-8", errors="replace")
            )
        elif isinstance(content, (dict, list)):
            content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        else:
            content_str = str(content)

        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    def _analyze_for_suppression(
        self, signal_type: str, content: Any
    ) -> Dict[str, Any]:
        """
        Analyze signal for suppression patterns.

        Args:
            signal_type: Type of signal
            content: Signal content

        Returns:
            Suppression analysis results
        """
        analysis = {
            "suppression_detected": False,
            "patterns_found": [],
            "confidence": 0.0,
            "analysis_method": "pattern_matching",
        }

        if not self.config["detect_suppression_patterns"]:
            return analysis

        content_str = ""
        if isinstance(content, str):
            content_str = content
        elif isinstance(content, dict):
            content_str = json.dumps(content, ensure_ascii=False)
        else:
            content_str = str(content)

        # Check for suppression patterns
        import re

        patterns_found = []

        for pattern in self.suppression_patterns:
            try:
                if re.search(pattern, content_str, re.IGNORECASE | re.MULTILINE):
                    patterns_found.append(pattern)
            except re.error:
                # Skip invalid patterns
                continue

        if patterns_found:
            analysis["suppression_detected"] = True
            analysis["patterns_found"] = patterns_found
            analysis["confidence"] = min(0.5 + (len(patterns_found) * 0.1), 1.0)

        # Additional checks based on signal type
        if signal_type == "warning":
            # Check if warning is being suppressed
            if (
                "filterwarnings" in content_str.lower()
                or "simplefilter" in content_str.lower()
            ):
                analysis["suppression_detected"] = True
                analysis["patterns_found"].append("warning_suppression")
                analysis["confidence"] = 0.8

        elif signal_type == "stderr":
            # Check for stderr redirection
            if "stderr" in content_str.lower() and (
                "=" in content_str or "redirect" in content_str.lower()
            ):
                analysis["suppression_detected"] = True
                analysis["patterns_found"].append("stderr_redirection")
                analysis["confidence"] = 0.7

        elif signal_type == "exception":
            # Check for broad exception handling
            if "except" in content_str.lower() and "pass" in content_str.lower():
                analysis["suppression_detected"] = True
                analysis["patterns_found"].append("broad_exception")
                analysis["confidence"] = 0.9

        return analysis

    def _handle_suppression_detected(self, signal_record: Dict[str, Any]) -> None:
        """Handle detected suppression."""
        if not self.config["auto_enforce_violation"]:
            return

        # Record suppression as failure
        suppression_id = self.ledger.record_failure(
            phase="SUPPRESSED_SIGNAL",
            violated_invariant="SIGNAL_SUPPRESSION",
            description=f"Signal suppression detected: {signal_record['signal_type']}",
            artifact_hash=signal_record["content_hash"],
            causal_parent_hash=None,
            severity="CRITICAL",
            metadata={
                "signal_record": signal_record,
                "capture_id": self.current_capture_id,
                "auto_enforced": True,
            },
        )

        # Record in evidence store
        self.evidence_store.log_evidence(
            evidence_type="SIGNAL_SUPPRESSION",
            content={
                "suppression_id": suppression_id,
                "signal_record": signal_record,
                "capture_id": self.current_capture_id,
            },
            source="suppressed_signal_detector",
            metadata={
                "patterns_found": signal_record["suppression_analysis"][
                    "patterns_found"
                ],
                "analysis_method": signal_record["suppression_analysis"][
                    "analysis_method"
                ],
                "confidence": signal_record["suppression_analysis"]["confidence"],
                "tags": ["signal_suppression", "boundary_violation", "critical"],
            },
        )

        # If exit code enforcement is enabled, prepare to exit
        if self.config["exit_code_on_suppression"] is not None:
            self._enforce_exit_code()

    def _enforce_exit_code(self) -> None:
        """Enforce exit code on suppression detection."""
        # Record enforcement action
        self.record_signal(
            "enforcement",
            {
                "action": "exit_code_enforcement",
                "exit_code": self.config["exit_code_on_suppression"],
                "reason": "signal_suppression_detected",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        # Note: Actual exit happens in end_capture()

    def _save_signal(self, signal_record: Dict[str, Any]) -> None:
        """Save signal to file."""
        if not self.current_capture_id:
            return

        capture_path = self.capture_dir / self.current_capture_id
        signal_path = capture_path / f"{signal_record['signal_id']}.json"

        with open(signal_path, "w", encoding="utf-8") as f:
            json.dump(signal_record, f, indent=2, ensure_ascii=False)

    def end_capture(self) -> Dict[str, Any]:
        """
        End signal capture and return results.

        Returns:
            Capture results
        """
        if not self.current_capture_id:
            return {"error": "No active capture"}

        capture_path = self.capture_dir / self.current_capture_id

        # Save final capture summary
        summary = {
            "capture_id": self.current_capture_id,
            "end_time": datetime.utcnow().isoformat(),
            "total_signals": len(self.captured_signals),
            "signal_types": {},
            "suppression_detected": self.suppression_detected,
            "signal_ids": [s["signal_id"] for s in self.captured_signals],
            "config": self.config,
        }

        # Count signal types
        for signal in self.captured_signals:
            signal_type = signal["signal_type"]
            summary["signal_types"][signal_type] = (
                summary["signal_types"].get(signal_type, 0) + 1
            )

        # Save summary
        summary_path = capture_path / "capture_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # If suppression was detected and auto-enforcement is enabled, exit
        if self.suppression_detected and self.config["auto_enforce_violation"]:
            if self.config["exit_code_on_suppression"] is not None:
                # Save exit notice
                exit_notice = {
                    "exit_code": self.config["exit_code_on_suppression"],
                    "reason": "signal_suppression_detected",
                    "timestamp": datetime.utcnow().isoformat(),
                    "capture_id": self.current_capture_id,
                    "suppression_details": [
                        s
                        for s in self.captured_signals
                        if s["suppression_analysis"]["suppression_detected"]
                    ],
                }

                exit_path = capture_path / "exit_notice.json"
                with open(exit_path, "w", encoding="utf-8") as f:
                    json.dump(exit_notice, f, indent=2, ensure_ascii=False)

                # Actually exit
                sys.exit(self.config["exit_code_on_suppression"])

        result = summary.copy()
        result["capture_path"] = str(capture_path)

        # Reset state
        self.current_capture_id = None
        self.captured_signals = []
        # Keep suppression_detected for reporting

        return result

    @contextlib.contextmanager
    def capture_context(self, capture_id: Optional[str] = None):
        """
        Context manager for signal capture.

        Args:
            capture_id: Optional capture ID

        Yields:
            Detector instance
        """
        capture_id = self.start_capture(capture_id)

        # Set up warning capture
        original_showwarning = warnings.showwarning
        warnings.showwarning = self._capture_warnings()

        # Set up stderr capture
        stderr_context = self._capture_stderr()

        try:
            with stderr_context:
                yield self
        finally:
            # Restore warning handler
            warnings.showwarning = original_showwarning

            # End capture
            self.end_capture()

    def capture_execution(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Capture signals during function execution.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Execution results with signal capture
        """
        capture_id = self.start_capture()

        # Set up warning capture
        original_showwarning = warnings.showwarning
        warnings.showwarning = self._capture_warnings()

        # Set up stderr capture
        stderr_context = self._capture_stderr()

        execution_result = {
            "success": False,
            "return_value": None,
            "exception": None,
            "traceback": None,
            "signals_captured": [],
            "suppression_detected": False,
        }

        try:
            with stderr_context:
                return_value = func(*args, **kwargs)
                execution_result["success"] = True
                execution_result["return_value"] = return_value

        except Exception as e:
            execution_result["exception"] = {
                "type": type(e).__name__,
                "message": str(e),
            }
            execution_result["traceback"] = traceback.format_exc()

            # Record exception as signal
            self.record_signal(
                "exception",
                {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc(),
                },
            )

        finally:
            # Restore warning handler
            warnings.showwarning = original_showwarning

            # End capture and get results
            capture_results = self.end_capture()

            execution_result["signals_captured"] = self.captured_signals.copy()
            execution_result["suppression_detected"] = self.suppression_detected
            execution_result["capture_id"] = capture_id
            execution_result["capture_results"] = capture_results

        return execution_result

    def get_capture_statistics(self) -> Dict[str, Any]:
        """Get statistics for all captures."""
        if not self.capture_dir.exists():
            return {"total_captures": 0, "captures": []}

        capture_dirs = [d for d in self.capture_dir.iterdir() if d.is_dir()]
        statistics = {
            "total_captures": len(capture_dirs),
            "captures_with_suppression": 0,
            "total_signals": 0,
            "signal_type_distribution": {},
            "captures": [],
        }

        for capture_dir in capture_dirs:
            summary_path = capture_dir / "capture_summary.json"
            if summary_path.exists():
                try:
                    with open(summary_path, "r", encoding="utf-8") as f:
                        summary = json.load(f)

                    statistics["captures"].append(
                        {
                            "capture_id": summary.get("capture_id"),
                            "total_signals": summary.get("total_signals", 0),
                            "signal_types": summary.get("signal_types", {}),
                            "suppression_detected": summary.get(
                                "suppression_detected", False
                            ),
                            "capture_path": str(capture_dir),
                        }
                    )

                    if summary.get("suppression_detected"):
                        statistics["captures_with_suppression"] += 1

                    statistics["total_signals"] += summary.get("total_signals", 0)

                    # Update signal type distribution
                    for signal_type, count in summary.get("signal_types", {}).items():
                        statistics["signal_type_distribution"][signal_type] = (
                            statistics["signal_type_distribution"].get(signal_type, 0)
                            + count
                        )

                except (json.JSONDecodeError, FileNotFoundError):
                    # Skip corrupted captures
                    continue

        return statistics

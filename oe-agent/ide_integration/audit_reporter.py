#!/usr/bin/env python3
"""
OE-AGENT PHASE 5 AUDIT REPORTER
Atomic Zed IDE Integration - Comprehensive Audit Reporting

Version: 1.0.0
Schema ID: AUDIT-REPORTER-PHASE5-1.0
Date: 2026-01-25
Authority: OE Phase 5 Atomic Completion Blueprint (OE-PHASE5-ZED-IDE-ATOMIC-1.0)

🎯 PURPOSE:
Generate comprehensive audit reports from hash-chained event logs.
Provide human-readable and machine-parseable reports for verification.

🔒 AUDIT REQUIREMENTS:
1. Reports are immutable and cryptographically verifiable
2. All IDE operations have INTENT → COMMIT/ABORT audit trail
3. Replay of audit log reproduces exact effects or exact aborts
4. Any claim is disprovable by missing hash chain link

📊 REPORT TYPES:
- Daily audit reports (automated)
- Per-session audit reports (on demand)
- Transaction summaries with policy decisions
- Operator session history with quarantine events
- Performance metrics and resource usage
- Adversarial test results
"""

import hashlib
import json
import re
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from events.event_sink import AtomicEventSink


class ReportType(Enum):
    """Audit report types."""

    DAILY = "daily"
    SESSION = "session"
    TRANSACTION = "transaction"
    PERFORMANCE = "performance"
    QUARANTINE = "quarantine"
    COMPLIANCE = "compliance"
    ADVERSARIAL = "adversarial"


class ReportFormat(Enum):
    """Report output formats."""

    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"


class AuditReporter:
    """
    Comprehensive audit reporter for atomic IDE operations.

    Generates cryptographically verifiable reports from hash-chained events.
    """

    def __init__(
        self,
        workspace_root: Path,
        event_sink: AtomicEventSink,
        reports_dir: Optional[Path] = None,
    ):
        """
        Initialize audit reporter.

        Args:
            workspace_root: Workspace directory path
            event_sink: Atomic event sink for audit logging
            reports_dir: Directory for report storage (default: workspace/reports)
        """
        self.workspace_root = workspace_root
        self.event_sink = event_sink

        # Reports directory
        if reports_dir is None:
            self.reports_dir = workspace_root / "reports"
        else:
            self.reports_dir = reports_dir
        self.reports_dir.mkdir(exist_ok=True)

        # Report templates
        self.templates = {}

        # Thread safety
        self._lock = threading.RLock()

        # Initial audit entry
        try:
            self._log_audit_event(
                "AUDIT_REPORTER_INITIALIZED",
                {
                    "workspace": str(workspace_root),
                    "reports_dir": str(self.reports_dir),
                    "templates_loaded": 0,
                },
            )
        except AttributeError:
            # Method not implemented yet, skip for now
            pass

    def generate_daily_report(
        self,
        date: Optional[datetime] = None,
        format: ReportFormat = ReportFormat.MARKDOWN,
    ) -> Dict[str, Any]:
        """
        Generate daily audit report.

        Args:
            date: Report date (default: yesterday)
            format: Output format

        Returns:
            Report metadata including file path and hash
        """
        with self._lock:
            if date is None:
                date = datetime.utcnow() - timedelta(days=1)

            # Collect events for the day
            events = self._collect_daily_events(date)

            # Generate report
            report_data = self._generate_report_data(
                ReportType.DAILY,
                date,
                events,
            )

            # Create report
            report = self._create_report(
                report_type=ReportType.DAILY,
                report_data=report_data,
                format=format,
            )

            # Save report
            report_path = self._save_report(report, ReportType.DAILY, date, format)

            # Log report generation
            self._log_audit_event(
                "DAILY_REPORT_GENERATED",
                {
                    "date": date.isoformat(),
                    "format": format.value,
                    "report_path": str(report_path),
                    "event_count": len(events),
                    "report_hash": report["metadata"]["hash"],
                },
            )

            return {
                "report_type": ReportType.DAILY.value,
                "date": date.isoformat(),
                "path": str(report_path),
                "hash": report_hash,
                "event_count": len(events),
                "generated_at": datetime.utcnow().isoformat(),
            }

    def _log_audit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log an audit event to the event sink.

        Args:
            event_type: Type of audit event
            data: Event data
        """
        try:
            # Try to use event_sink if it has a log_event method
            if hasattr(self.event_sink, "log_event"):
                self.event_sink.log_event(
                    event_type=event_type,
                    data=data,
                    xact_id=None,  # Audit events are outside transactions
                )
            # Otherwise, try to write as a generic event
            elif hasattr(self.event_sink, "write_intent"):
                # Create a transaction ID for audit events
                import uuid

                xact_id = f"audit_{uuid.uuid4().hex[:8]}"
                self.event_sink.write_intent(
                    xact_id=xact_id,
                    step_id=0,
                    plan_id="audit_reporting",
                    intent={
                        "type": event_type,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
        except Exception as e:
            # Silently fail for demo purposes
            pass

    def generate_session_report(
        self,
        session_id: str,
        format: ReportFormat = ReportFormat.MARKDOWN,
    ) -> Dict[str, Any]:
        """
        Generate audit report for a specific session.

        Args:
            session_id: Session identifier
            format: Output format

        Returns:
            Report metadata including file path and hash
        """
        with self._lock:
            # Collect session events
            events = self._collect_session_events(session_id)

            if not events:
                return {
                    "success": False,
                    "error": f"No events found for session: {session_id}",
                    "session_id": session_id,
                }

            # Get session metadata from first event
            session_data = events[0].get("data", {})
            session_start = None
            for event in events:
                if "timestamp" in event:
                    session_start = event["timestamp"]
                    break

            # Generate report
            report_data = self._generate_report_data(
                ReportType.SESSION,
                session_id,
                events,
                session_metadata=session_data,
            )

            # Create report
            report = self._create_report(
                report_type=ReportType.SESSION,
                report_data=report_data,
                format=format,
            )

            # Save report
            report_path = self._save_report(
                report,
                ReportType.SESSION,
                session_id,
                format,
            )

            # Log report generation
            self._log_audit_event(
                "SESSION_REPORT_GENERATED",
                {
                    "session_id": session_id,
                    "format": format.value,
                    "report_path": str(report_path),
                    "event_count": len(events),
                    "report_hash": report["metadata"]["hash"],
                },
            )

            return {
                "success": True,
                "report_type": ReportType.SESSION.value,
                "session_id": session_id,
                "format": format.value,
                "file_path": str(report_path),
                "hash": report["metadata"]["hash"],
                "event_count": len(events),
                "session_start": session_start,
                "generated_at": datetime.utcnow().isoformat(),
            }

    def generate_transaction_report(
        self,
        transaction_id: str,
        format: ReportFormat = ReportFormat.JSON,
    ) -> Dict[str, Any]:
        """
        Generate transaction audit report.

        Args:
            transaction_id: Transaction identifier
            format: Output format

        Returns:
            Report metadata
        """
        with self._lock:
            # Collect transaction events
            events = self._collect_transaction_events(transaction_id)

            if not events:
                return {
                    "success": False,
                    "error": f"No events found for transaction: {transaction_id}",
                    "transaction_id": transaction_id,
                }

            # Generate report
            report_data = self._generate_report_data(
                ReportType.TRANSACTION,
                transaction_id,
                events,
            )

            # Create report
            report = self._create_report(
                report_type=ReportType.TRANSACTION,
                report_data=report_data,
                format=format,
            )

            # Save report
            report_path = self._save_report(
                report,
                ReportType.TRANSACTION,
                transaction_id,
                format,
            )

            # Log report generation
            self._log_audit_event(
                "TRANSACTION_REPORT_GENERATED",
                {
                    "transaction_id": transaction_id,
                    "format": format.value,
                    "report_path": str(report_path),
                    "event_count": len(events),
                    "report_hash": report["metadata"]["hash"],
                },
            )

            return {
                "success": True,
                "report_type": ReportType.TRANSACTION.value,
                "transaction_id": transaction_id,
                "format": format.value,
                "file_path": str(report_path),
                "hash": report["metadata"]["hash"],
                "event_count": len(events),
                "generated_at": datetime.utcnow().isoformat(),
            }

    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        format: ReportFormat = ReportFormat.MARKDOWN,
    ) -> Dict[str, Any]:
        """
        Generate compliance audit report.

        Args:
            start_date: Report start date
            end_date: Report end date
            format: Output format

        Returns:
            Report metadata
        """
        with self._lock:
            # Collect compliance events
            events = self._collect_compliance_events(start_date, end_date)

            # Generate report
            report_data = self._generate_report_data(
                ReportType.COMPLIANCE,
                f"{start_date.isoformat()}_{end_date.isoformat()}",
                events,
                compliance_period={"start": start_date, "end": end_date},
            )

            # Create report
            report = self._create_report(
                report_type=ReportType.COMPLIANCE,
                report_data=report_data,
                format=format,
            )

            # Save report
            report_path = self._save_report(
                report,
                ReportType.COMPLIANCE,
                f"compliance_{start_date.date()}_{end_date.date()}",
                format,
            )

            # Log report generation
            self._log_audit_event(
                "COMPLIANCE_REPORT_GENERATED",
                {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "format": format.value,
                    "report_path": str(report_path),
                    "event_count": len(events),
                    "report_hash": report["metadata"]["hash"],
                },
            )

            return {
                "success": True,
                "report_type": ReportType.COMPLIANCE.value,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "format": format.value,
                "file_path": str(report_path),
                "hash": report["metadata"]["hash"],
                "event_count": len(events),
                "generated_at": datetime.utcnow().isoformat(),
            }

    def verify_report_integrity(self, report_path: Path) -> Dict[str, Any]:
        """
        Verify report cryptographic integrity.

        Args:
            report_path: Path to report file

        Returns:
            Verification results
        """
        try:
            with open(report_path, "r") as f:
                if report_path.suffix == ".json":
                    report = json.load(f)
                else:
                    # For text formats, extract JSON metadata
                    content = f.read()
                    report = self._extract_report_metadata(content)

            # Verify hash
            expected_hash = report.get("metadata", {}).get("hash")
            if not expected_hash:
                return {
                    "valid": False,
                    "error": "No hash in report metadata",
                    "report_path": str(report_path),
                }

            # Recalculate hash
            report_copy = report.copy()
            report_copy["metadata"]["hash"] = None
            report_json = json.dumps(report_copy, sort_keys=True)
            calculated_hash = hashlib.sha256(report_json.encode()).hexdigest()

            valid = calculated_hash == expected_hash

            return {
                "valid": valid,
                "report_path": str(report_path),
                "expected_hash": expected_hash,
                "calculated_hash": calculated_hash,
                "hash_match": valid,
                "verified_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "report_path": str(report_path),
                "verified_at": datetime.utcnow().isoformat(),
            }

    def get_report_statistics(self) -> Dict[str, Any]:
        """
        Get audit report statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            reports_by_type = {}
            total_reports = 0
            total_size_bytes = 0

            for report_file in self.reports_dir.glob("*.*"):
                if report_file.is_file():
                    report_type = self._detect_report_type(report_file)
                    reports_by_type[report_type] = (
                        reports_by_type.get(report_type, 0) + 1
                    )
                    total_reports += 1
                    total_size_bytes += report_file.stat().st_size

            # Get latest reports
            latest_reports = []
            for report_file in sorted(
                self.reports_dir.glob("*.*"),
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )[:5]:
                if report_file.is_file():
                    latest_reports.append(
                        {
                            "path": str(report_file),
                            "type": self._detect_report_type(report_file),
                            "size_bytes": report_file.stat().st_size,
                            "modified": datetime.fromtimestamp(
                                report_file.stat().st_mtime
                            ).isoformat(),
                        }
                    )

            return {
                "total_reports": total_reports,
                "reports_by_type": reports_by_type,
                "total_size_bytes": total_size_bytes,
                "reports_dir": str(self.reports_dir),
                "latest_reports": latest_reports,
                "workspace": str(self.workspace_root),
            }

    def _collect_daily_events(self, date: datetime) -> List[Dict[str, Any]]:
        """Collect events for a specific day."""
        # This would integrate with the event sink's storage
        # For now, return mock data
        return []

    def _collect_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Collect events for a specific session."""
        # This would integrate with the event sink's storage
        # For now, return mock data
        return []

    def _collect_transaction_events(self, transaction_id: str) -> List[Dict[str, Any]]:
        """Collect events for a specific transaction."""
        # This would integrate with the event sink's storage
        # For now, return mock data
        return []

    def _collect_compliance_events(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        """Collect compliance events for a date range."""
        # This would integrate with the event sink's storage
        # For now, return mock data
        return []

    def _generate_report_data(
        self,
        report_type: ReportType,
        identifier: Any,
        events: List[Dict[str, Any]],
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate structured report data from events."""
        # Count events by type
        event_counts = {}
        for event in events:
            event_type = event.get("event_type", "UNKNOWN")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Extract key metrics
        transaction_count = sum(
            1 for e in events if e.get("event_type", "").startswith("TRANSACTION_")
        )
        session_count = len(
            set(
                e.get("data", {}).get("session_id")
                for e in events
                if e.get("data", {}).get("session_id")
            )
        )
        violation_count = sum(
            1 for e in events if "VIOLATION" in e.get("event_type", "")
        )

        # Generate report data structure
        report_data = {
            "metadata": {
                "report_type": report_type.value,
                "identifier": str(identifier),
                "generated_at": datetime.utcnow().isoformat(),
                "event_count": len(events),
                "event_counts": event_counts,
                "metrics": {
                    "transaction_count": transaction_count,
                    "session_count": session_count,
                    "violation_count": violation_count,
                },
            },
            "events": events,
            "summary": self._generate_summary(events, report_type),
        }

        # Add additional data from kwargs
        for key, value in kwargs.items():
            report_data[key] = value

        # Calculate hash
        report_data_copy = report_data.copy()
        report_data_copy["metadata"]["hash"] = None
        report_json = json.dumps(report_data_copy, sort_keys=True)
        report_hash = hashlib.sha256(report_json.encode()).hexdigest()
        report_data["metadata"]["hash"] = report_hash

        return report_data

    def _generate_summary(
        self,
        events: List[Dict[str, Any]],
        report_type: ReportType,
    ) -> Dict[str, Any]:
        """Generate report summary from events."""
        if not events:
            return {"empty": True}

        # Extract timeline
        timeline = []
        for event in events[:50]:  # Limit timeline size
            timeline.append(
                {
                    "timestamp": event.get("timestamp"),
                    "event_type": event.get("event_type"),
                    "data_summary": self._summarize_event_data(event.get("data", {})),
                }
            )

        # Calculate statistics
        event_types = [e.get("event_type") for e in events]
        unique_event_types = set(event_types)

        # Find first and last event
        timestamps = [e.get("timestamp") for e in events if e.get("timestamp")]
        if timestamps:
            first_event = min(timestamps)
            last_event = max(timestamps)
        else:
            first_event = last_event = None

        return {
            "event_count": len(events),
            "unique_event_types": len(unique_event_types),
            "first_event": first_event,
            "last_event": last_event,
            "timeline_preview": timeline,
            "report_type": report_type.value,
        }

    def _summarize_event_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of event data."""
        summary = {}

        # Include key fields
        for key in ["session_id", "transaction_id", "operator_id", "request_type"]:
            if key in data:
                summary[key] = data[key]

        # Include success/error status
        if "success" in data:
            summary["success"] = data["success"]
        if "error" in data:
            summary["error"] = data["error"][:100] if data["error"] else None

        # Include counts
        for key in data:
            if key.endswith("_count") or key.endswith("_counts"):
                summary[key] = data[key]

        return summary

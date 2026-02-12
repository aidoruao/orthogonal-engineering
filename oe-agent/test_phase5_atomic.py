#!/usr/bin/env python3
"""
OE-AGENT PHASE 5 TEST SUITE
Atomic Zed IDE Integration - Comprehensive Testing

Version: 1.0.0
Schema ID: TEST-PHASE5-ZED-IDE-ATOMIC-1.0
Date: 2026-01-25
Authority: OE Phase 5 Atomic Completion Blueprint (OE-PHASE5-ZED-IDE-ATOMIC-1.0)

🎯 PURPOSE:
Comprehensive test suite for Phase 5 Atomic Zed IDE Integration.
Validate all Phase 5 requirements and atomic guarantees.

🔍 TEST CATEGORIES:
1. Session Management Tests
2. Performance Monitoring Tests
3. Audit Reporting Tests
4. Quarantine Enforcement Tests
5. Adversarial Scenario Tests
6. Integration Tests with Phase 4
7. Atomic Invariant Validation Tests

🔒 TESTING PRINCIPLES:
- All tests must be deterministic and repeatable
- Tests must validate cryptographic proofs where applicable
- Adversarial tests must simulate real violation attempts
- Integration tests must verify backward compatibility
"""

import json
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, patch

from events.event_sink import AtomicEventSink
from events.transaction_guard import TransactionGuard
from ide_integration.audit_reporter import AuditReporter, ReportFormat, ReportType
from ide_integration.performance_monitor import (
    LimitViolation,
    PerformanceMonitor,
    ResourceLimit,
)
from ide_integration.session_manager import (
    OperatorSession,
    QuarantineReason,
    SessionManager,
    SessionState,
)
from mcp_atomic_gateway import MCPAtomicGateway, MCPRequestType
from policy.policy_gate import PolicyGate


class TestPhase5SessionManagement(unittest.TestCase):
    """Test session management functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)

        # Create mock components
        self.event_sink = Mock(spec=AtomicEventSink)
        self.policy_gate = Mock(spec=PolicyGate)
        self.gateway = Mock(spec=MCPAtomicGateway)

        # Configure mock gateway
        self.gateway.process_mcp_request.return_value = {
            "success": True,
            "policy_decision": "allowed",
            "transaction_id": "TEST-TX-001",
            "intent_hash": "test_hash_123",
            "commit_hash": "test_hash_456",
        }

        # Create session manager
        self.session_manager = SessionManager(self.workspace)

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_session_creation(self):
        """Test creating a new operator session."""
        session = self.session_manager.start_session(
            operator_id="test_operator_001",
            gateway=self.gateway,
            event_sink=self.event_sink,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.operator_id, "test_operator_001")
        self.assertEqual(session.state, SessionState.ACTIVE)
        self.assertIsNotNone(session.session_id)
        self.assertTrue(session.session_id.startswith("SESS-"))

    def test_session_uniqueness(self):
        """Test that sessions have unique IDs."""
        session1 = self.session_manager.start_session(
            operator_id="operator1",
            gateway=self.gateway,
            event_sink=self.event_sink,
        )

        session2 = self.session_manager.start_session(
            operator_id="operator2",
            gateway=self.gateway,
            event_sink=self.event_sink,
        )

        self.assertIsNotNone(session1)
        self.assertIsNotNone(session2)
        self.assertNotEqual(session1.session_id, session2.session_id)
        self.assertNotEqual(session1.operator_id, session2.operator_id)

    def test_session_processing(self):
        """Test processing MCP requests through session."""
        session = self.session_manager.start_session(
            operator_id="test_operator",
            gateway=self.gateway,
            event_sink=self.event_sink,
        )

        result = session.process_mcp_request(
            request_type=MCPRequestType.SCAN.value,
            parameters={"target": ".", "recursive": True},
            zed_context={"workspace": str(self.workspace)},
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["policy_decision"], "allowed")
        self.assertIn("session_id", result)
        self.assertEqual(result["session_id"], session.session_id)

    def test_session_summary(self):
        """Test getting session summary."""
        session = self.session_manager.start_session(
            operator_id="test_operator",
            gateway=self.gateway,
            event_sink=self.event_sink,
        )

        # Process a request
        session.process_mcp_request(
            request_type=MCPRequestType.SCAN.value,
            parameters={"target": "."},
            zed_context={},
        )

        summary = session.get_summary()

        self.assertEqual(summary["session_id"], session.session_id)
        self.assertEqual(summary["operator_id"], "test_operator")
        self.assertEqual(summary["state"], SessionState.ACTIVE.value)
        self.assertEqual(summary["transaction_count"], 1)
        self.assertGreater(summary["total_execution_time"], 0)

    def test_session_invariants(self):
        """Test session invariant validation."""
        session = self.session_manager.start_session(
            operator_id="test_operator",
            gateway=self.gateway,
            event_sink=self.event_sink,
        )

        invariants = session.validate_session_invariants()

        self.assertTrue(invariants["session_has_audit_trail"])
        self.assertTrue(invariants["session_id_not_empty"])
        self.assertTrue(invariants["operator_id_not_empty"])
        self.assertTrue(invariants["execution_time_positive"])


class TestPhase5PerformanceMonitoring(unittest.TestCase):
    """Test performance monitoring functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.event_sink = Mock(spec=AtomicEventSink)

        # Create performance monitor
        self.monitor = PerformanceMonitor(self.workspace, self.event_sink)

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_monitor_initialization(self):
        """Test performance monitor initialization."""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.workspace_root, self.workspace)
        self.assertIsNotNone(self.monitor.limits)

        # Check default limits
        self.assertIn(ResourceLimit.TRANSACTION_DURATION, self.monitor.limits)
        self.assertIn(ResourceLimit.CONCURRENT_TRANSACTIONS, self.monitor.limits)
        self.assertIn(ResourceLimit.MEMORY_MB, self.monitor.limits)

    def test_transaction_monitoring(self):
        """Test transaction monitoring lifecycle."""
        transaction_id = "TEST-TX-001"
        session_id = "TEST-SESS-001"
        operator_id = "test_operator"
        request_type = "scan"

        # Start monitoring
        monitoring_state = self.monitor.start_transaction_monitoring(
            transaction_id=transaction_id,
            session_id=session_id,
            operator_id=operator_id,
            request_type=request_type,
        )

        self.assertEqual(monitoring_state["transaction_id"], transaction_id)
        self.assertEqual(monitoring_state["session_id"], session_id)
        self.assertEqual(monitoring_state["operator_id"], operator_id)
        self.assertEqual(monitoring_state["request_type"], request_type)
        self.assertIn("start_time", monitoring_state)

        # Update metrics
        updated_state = self.monitor.update_transaction_metrics(
            transaction_id=transaction_id,
            metrics_update={"files_created": 5, "disk_write_bytes": 1024},
        )

        self.assertEqual(updated_state["files_created"], 5)
        self.assertEqual(updated_state["disk_write_bytes"], 1024)

        # End monitoring
        final_metrics = self.monitor.end_transaction_monitoring(
            transaction_id=transaction_id,
            success=True,
        )

        self.assertEqual(final_metrics["transaction_id"], transaction_id)
        self.assertEqual(final_metrics["session_id"], session_id)
        self.assertTrue(final_metrics["success"])
        self.assertGreater(final_metrics["duration_seconds"], 0)

    def test_limit_validations(self):
        """Test limit validation functionality."""
        validations = self.monitor.validate_limits()

        self.assertTrue(validations["concurrent_transaction_limit"])
        self.assertTrue(validations["positive_limits"])
        self.assertTrue(validations["monitoring_active"])
        self.assertTrue(validations["event_sink_available"])

    def test_performance_summary(self):
        """Test performance summary generation."""
        # Monitor a transaction
        self.monitor.start_transaction_monitoring(
            transaction_id="TEST-TX-001",
            session_id="TEST-SESS-001",
            operator_id="test_operator",
            request_type="scan",
        )

        self.monitor.end_transaction_monitoring(
            transaction_id="TEST-TX-001",
            success=True,
        )

        summary = self.monitor.get_performance_summary()

        self.assertEqual(summary["total_transactions"], 1)
        self.assertEqual(summary["active_transactions"], 0)
        self.assertGreater(summary["total_duration_seconds"], 0)
        self.assertIn("limits", summary)


class TestPhase5AuditReporting(unittest.TestCase):
    """Test audit reporting functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.event_sink = Mock(spec=AtomicEventSink)

        # Create audit reporter
        self.reporter = AuditReporter(self.workspace, self.event_sink)

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_reporter_initialization(self):
        """Test audit reporter initialization."""
        self.assertIsNotNone(self.reporter)
        self.assertEqual(self.reporter.workspace_root, self.workspace)
        self.assertIsNotNone(self.reporter.reports_dir)
        self.assertTrue(self.reporter.reports_dir.exists())

    def test_report_generation(self):
        """Test report generation functionality."""
        # Mock event collection
        with patch.object(self.reporter, "_collect_session_events") as mock_collect:
            mock_collect.return_value = [
                {
                    "event_type": "SESSION_STARTED",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "session_id": "TEST-SESS-001",
                        "operator_id": "test_operator",
                        "start_time": datetime.utcnow().isoformat(),
                    },
                }
            ]

            # Generate session report
            report_result = self.reporter.generate_session_report(
                session_id="TEST-SESS-001",
                format=ReportFormat.JSON,
            )

            self.assertTrue(report_result["success"])
            self.assertEqual(report_result["report_type"], "session")
            self.assertEqual(report_result["session_id"], "TEST-SESS-001")
            self.assertIn("file_path", report_result)
            self.assertIn("hash", report_result)

    def test_report_integrity_verification(self):
        """Test report integrity verification."""
        # Create a test report
        test_report = {
            "metadata": {
                "report_type": "test",
                "identifier": "TEST-001",
                "generated_at": datetime.utcnow().isoformat(),
                "hash": None,
            },
            "data": {"test": "data"},
        }

        # Calculate hash
        import hashlib

        report_copy = test_report.copy()
        report_copy["metadata"]["hash"] = None
        report_json = json.dumps(report_copy, sort_keys=True)
        test_hash = hashlib.sha256(report_json.encode()).hexdigest()
        test_report["metadata"]["hash"] = test_hash

        # Save test report
        test_report_path = self.reporter.reports_dir / "test_report.json"
        with open(test_report_path, "w") as f:
            json.dump(test_report, f)

        # Verify integrity
        verification = self.reporter.verify_report_integrity(test_report_path)

        self.assertTrue(verification["valid"])
        self.assertTrue(verification["hash_match"])
        self.assertEqual(verification["expected_hash"], test_hash)

    def test_report_statistics(self):
        """Test report statistics generation."""
        stats = self.reporter.get_report_statistics()

        self.assertIn("total_reports", stats)
        self.assertIn("reports_by_type", stats)
        self.assertIn("total_size_bytes", stats)
        self.assertIn("reports_dir", stats)
        self.assertIn("latest_reports", stats)


class TestPhase5QuarantineEnforcement(unittest.TestCase):
    """Test operator quarantine functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)

        # Create mock components
        self.event_sink = Mock(spec=AtomicEventSink)
        self.gateway = Mock(spec=MCPAtomicGateway)

        # Create session manager
        self.session_manager = SessionManager(self.workspace)

        # Start a session
        self.session = self.session_manager.start_session(
            operator_id="test_operator",
            gateway=self.gateway,
            event_sink=self.event_sink,
        )

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_quarantine_session(self):
        """Test quarantining a session."""
        quarantine_success = self.session_manager.quarantine_session(
            session_id=self.session.session_id,
            reason=QuarantineReason.POLICY_VIOLATION,
            details={
                "violation": "Unauthorized file access",
                "severity": "high",
            },
        )

        self.assertTrue(quarantine_success)
        self.assertEqual(self.session.state, SessionState.QUARANTINED)
        self.assertIn(
            QuarantineReason.POLICY_VIOLATION, self.session.quarantine_reasons
        )

    def test_quarantine_block_requests(self):
        """Test that quarantined sessions block requests."""
        # Quarantine the session
        self.session_manager.quarantine_session(
            session_id=self.session.session_id,
            reason=QuarantineReason.POLICY_VIOLATION,
        )

        # Try to process a request
        result = self.session.process_mcp_request(
            request_type=MCPRequestType.SCAN.value,
            parameters={"target": "."},
            zed_context={},
        )

        self.assertFalse(result["success"])
        self.assertIn("Operator in quarantine", result["error"])
        self.assertIn("quarantine_reasons", result)

    def test_multiple_quarantine_reasons(self):
        """Test multiple quarantine reasons."""
        # Add first quarantine reason
        self.session.quarantine(QuarantineReason.POLICY_VIOLATION)

        # Add second quarantine reason
        self.session.quarantine(QuarantineReason.RESOURCE_LIMIT_EXCEEDED)

        self.assertEqual(len(self.session.quarantine_reasons), 2)
        self.assertIn(
            QuarantineReason.POLICY_VIOLATION, self.session.quarantine_reasons
        )
        self.assertIn(
            QuarantineReason.RESOURCE_LIMIT_EXCEEDED, self.session.quarantine_reasons
        )

    def test_quarantine_invariants(self):
        """Test quarantine invariants."""
        # Quarantine the session
        self.session.quarantine(QuarantineReason.POLICY_VIOLATION)

        invariants = self.session.validate_session_invariants()

        self.assertTrue(invariants["no_open_transactions_on_quarantine"])
        self.assertTrue(invariants["no_quarantine_without_reason"])


class TestPhase5AdversarialScenarios(unittest.TestCase):
    """Test adversarial scenario detection and response."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)

        # Create real components for adversarial testing
        self.event_sink = AtomicEventSink(self.workspace)
        self.policy_gate = PolicyGate()
        self.gateway = MCPAtomicGateway(
            self.workspace, self.event_sink, self.policy_gate
        )

        # Create session manager
        self.session_manager = SessionManager(self.workspace)

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_concurrent_transaction_limit(self):
        """Test concurrent transaction limit enforcement."""
        # This would test the PerformanceMonitor's concurrent transaction limit
        # Since we're using mocks in other tests, this shows the pattern
        monitor = PerformanceMonitor(self.workspace, self.event_sink)

        # Set a very low concurrent transaction limit
        monitor.limits[ResourceLimit.CONCURRENT_TRANSACTIONS] = 1

        # Start first transaction
        monitor.start_transaction_monitoring(
            transaction_id="TX-001",
            session_id="SESS-001",
            operator_id="op1",
            request_type="scan",
        )

        # Try to start second transaction (should raise exception)
        with self.assertRaises(RuntimeError) as context:
            monitor.start_transaction_monitoring(
                transaction_id="TX-002",
                session_id="SESS-002",
                operator_id="op2",
                request_type="scan",
            )

        self.assertIn("Concurrent transaction limit exceeded", str(context.exception))

    def test_transaction_timeout_detection(self):
        """Test transaction timeout detection."""
        monitor = PerformanceMonitor(self.workspace, self.event_sink)

        # Set very short timeout
        monitor.limits[ResourceLimit.TRANSACTION_DURATION] = 0.001

        # Start transaction
        monitor.start_transaction_monitoring(
            transaction_id="TX-TIMEOUT",
            session_id="SESS-001",
            operator_id="op1",
            request_type="scan",
        )

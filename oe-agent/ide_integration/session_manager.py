#!/usr/bin/env python3
"""
OE-AGENT PHASE 5 SESSION MANAGER
Atomic Zed IDE Integration - Operator Session Tracking

Version: 1.0.0
Schema ID: SESSION-MANAGER-PHASE5-1.0
Date: 2026-01-25
Authority: OE Phase 5 Atomic Completion Blueprint (OE-PHASE5-ZED-IDE-ATOMIC-1.0)

🎯 PURPOSE:
Manage atomic IDE sessions for operator AI instances.
Enforce single active session per workspace with full audit trail.

🔒 ATOMIC SESSION GUARANTEES:
1. No workspace action outside transaction
2. No session without audit metadata
3. Operator instance is replaceable; truth is irreplaceable
4. Hash chain integrity preserved across IDE and MCP

🔗 ARCHITECTURE:
Zed IDE Operator AI
        ↓ Session binding
Session Manager (Phase 5) ← THIS COMPONENT
        ↓ Transaction routing
MCP Atomic Gateway (Phase 4)
        ↓
TransactionGuard (Phase 3)
"""

import json
import threading
import time
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from events.event_sink import AtomicEventSink
from mcp_atomic_gateway import MCPAtomicGateway


class SessionState(Enum):
    """Session lifecycle states."""

    CREATED = "created"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    QUARANTINED = "quarantined"
    ENDED = "ended"
    ERROR = "error"


class QuarantineReason(Enum):
    """Reasons for operator quarantine."""

    POLICY_VIOLATION = "policy_violation"
    TRANSACTION_LEAK = "transaction_leak"
    HASH_CHAIN_TAMPERING = "hash_chain_tampering"
    RESOURCE_LIMIT_EXCEEDED = "resource_limit_exceeded"
    CONCURRENT_EXECUTION = "concurrent_execution"
    INTENT_WITHOUT_RESOLUTION = "intent_without_resolution"
    NON_TRANSACTIONAL_REQUEST = "non_transactional_request"


class OperatorSession:
    """
    Atomic IDE session for a single operator instance.

    Each session must:
    1. Be fully transactional
    2. Persist operator identity and audit metadata
    3. Track all cross-boundary interactions
    4. Maintain hash chain integrity
    5. Enforce single active session per workspace
    """

    def __init__(
        self,
        session_id: str,
        operator_id: str,
        workspace_root: Path,
        gateway: MCPAtomicGateway,
        event_sink: AtomicEventSink,
    ):
        """
        Initialize operator session.

        Args:
            session_id: Unique session identifier
            operator_id: Operator AI instance identifier
            workspace_root: Workspace directory path
            gateway: MCP Atomic Gateway instance
            event_sink: Atomic event sink for audit logging
        """
        self.session_id = session_id
        self.operator_id = operator_id
        self.workspace_root = workspace_root
        self.gateway = gateway
        self.event_sink = event_sink

        # Session state
        self.state = SessionState.CREATED
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None

        # Transaction tracking
        self.transaction_count = 0
        self.open_transactions: Set[str] = set()
        self.transaction_history: List[Dict[str, Any]] = []

        # Performance metrics
        self.total_execution_time = 0.0
        self.resource_usage: Dict[str, Any] = {
            "cpu_time": 0.0,
            "memory_peak_mb": 0.0,
            "files_created": 0,
            "disk_write_mb": 0.0,
        }

        # Audit trail
        self.audit_entries: List[Dict[str, Any]] = []
        self.quarantine_reasons: List[QuarantineReason] = []

        # Lock for thread safety
        self._lock = threading.RLock()

        # Create initial audit entry
        self._log_audit_entry(
            "SESSION_CREATED",
            {
                "session_id": self.session_id,
                "operator_id": self.operator_id,
                "workspace": str(self.workspace_root),
                "gateway_available": gateway is not None,
            },
        )

    def start(self) -> bool:
        """
        Start the operator session.

        Returns:
            True if session started successfully, False otherwise
        """
        with self._lock:
            if self.state != SessionState.CREATED:
                self._log_audit_entry(
                    "SESSION_START_FAILED",
                    {
                        "reason": f"Invalid state: {self.state}",
                        "expected": SessionState.CREATED.value,
                    },
                )
                return False

            try:
                # Register with gateway
                if self.gateway:
                    self.gateway.register_operator_session(
                        self.operator_id,
                        self.session_id,
                        str(self.workspace_root),
                    )

                # Update state
                self.state = SessionState.ACTIVE
                self.start_time = datetime.utcnow()

                self._log_audit_entry(
                    "SESSION_STARTED",
                    {
                        "start_time": self.start_time.isoformat(),
                        "gateway_registered": self.gateway is not None,
                    },
                )

                return True

            except Exception as e:
                self.state = SessionState.ERROR
                self._log_audit_entry(
                    "SESSION_START_ERROR",
                    {
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
                return False

    def process_mcp_request(
        self,
        request_type: str,
        parameters: Dict[str, Any],
        zed_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process MCP request through atomic gateway.

        Args:
            request_type: MCP request type (scan, copy, command, etc.)
            parameters: Request parameters
            zed_context: Zed IDE context (workspace, open files, cursor)

        Returns:
            Transaction result with audit metadata
        """
        with self._lock:
            if self.state not in [SessionState.ACTIVE, SessionState.SUSPENDED]:
                self._log_audit_entry(
                    "REQUEST_REJECTED",
                    {
                        "reason": f"Invalid session state: {self.state}",
                        "request_type": request_type,
                    },
                )
                return {
                    "success": False,
                    "error": f"Session not active: {self.state}",
                    "session_state": self.state.value,
                }

            # Check for quarantine
            if self.state == SessionState.QUARANTINED:
                self._log_audit_entry(
                    "REQUEST_BLOCKED_QUARANTINE",
                    {
                        "request_type": request_type,
                        "quarantine_reasons": [
                            r.value for r in self.quarantine_reasons
                        ],
                    },
                )
                return {
                    "success": False,
                    "error": "Operator in quarantine",
                    "quarantine_reasons": [r.value for r in self.quarantine_reasons],
                }

            # Track transaction start
            transaction_id = f"XACT-{self.session_id}-{self.transaction_count:06d}"
            self.open_transactions.add(transaction_id)
            self.transaction_count += 1

            start_time = time.time()

            try:
                # Process through gateway
                result = self.gateway.process_mcp_request(
                    operator_id=self.operator_id,
                    request_type=request_type,
                    parameters=parameters,
                    zed_context=zed_context or {},
                )

                # Update performance metrics
                execution_time = time.time() - start_time
                self.total_execution_time += execution_time

                # Track transaction
                transaction_record = {
                    "transaction_id": transaction_id,
                    "request_type": request_type,
                    "start_time": start_time,
                    "execution_time": execution_time,
                    "success": result.get("success", False),
                    "policy_decision": result.get("policy_decision"),
                    "intent_hash": result.get("intent_hash"),
                    "commit_hash": result.get("commit_hash"),
                }

                self.transaction_history.append(transaction_record)
                self.open_transactions.remove(transaction_id)

                # Log audit entry
                self._log_audit_entry(
                    "REQUEST_PROCESSED",
                    {
                        "transaction_id": transaction_id,
                        "request_type": request_type,
                        "execution_time": execution_time,
                        "success": result.get("success", False),
                        "policy": result.get("policy_decision"),
                    },
                )

                # Add session metadata to result
                result["session_id"] = self.session_id
                result["transaction_count"] = self.transaction_count
                result["total_execution_time"] = self.total_execution_time

                return result

            except Exception as e:
                # Transaction failed
                execution_time = time.time() - start_time
                self.total_execution_time += execution_time
                self.open_transactions.remove(transaction_id)

                self._log_audit_entry(
                    "REQUEST_FAILED",
                    {
                        "transaction_id": transaction_id,
                        "request_type": request_type,
                        "execution_time": execution_time,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )

                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "session_id": self.session_id,
                    "transaction_id": transaction_id,
                }

    def quarantine(
        self, reason: QuarantineReason, details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Quarantine operator session.

        Args:
            reason: Quarantine reason
            details: Additional quarantine details

        Returns:
            True if quarantined successfully
        """
        with self._lock:
            if self.state == SessionState.QUARANTINED:
                return True  # Already quarantined

            # Add quarantine reason
            self.quarantine_reasons.append(reason)

            # Update state
            previous_state = self.state
            self.state = SessionState.QUARANTINED

            # Log quarantine
            quarantine_entry = {
                "reason": reason.value,
                "previous_state": previous_state.value,
                "timestamp": datetime.utcnow().isoformat(),
                "open_transactions": list(self.open_transactions),
                "transaction_count": self.transaction_count,
            }

            if details:
                quarantine_entry.update(details)

            self._log_audit_entry("OPERATOR_QUARANTINED", quarantine_entry)

            # Abort any open transactions
            if self.open_transactions:
                for tx_id in list(self.open_transactions):
                    self._log_audit_entry(
                        "TRANSACTION_ABORTED_QUARANTINE",
                        {
                            "transaction_id": tx_id,
                            "quarantine_reason": reason.value,
                        },
                    )
                self.open_transactions.clear()

            return True

    def suspend(self) -> bool:
        """
        Suspend session (temporary pause).

        Returns:
            True if suspended successfully
        """
        with self._lock:
            if self.state != SessionState.ACTIVE:
                return False

            self.state = SessionState.SUSPENDED
            self._log_audit_entry(
                "SESSION_SUSPENDED",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "open_transactions": len(self.open_transactions),
                },
            )

            return True

    def resume(self) -> bool:
        """
        Resume suspended session.

        Returns:
            True if resumed successfully
        """
        with self._lock:
            if self.state != SessionState.SUSPENDED:
                return False

            self.state = SessionState.ACTIVE
            self._log_audit_entry(
                "SESSION_RESUMED",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return True

    def end(self) -> Dict[str, Any]:
        """
        End operator session.

        Returns:
            Session summary with audit metadata
        """
        with self._lock:
            if self.state in [SessionState.ENDED, SessionState.ERROR]:
                return self.get_summary()

            # Abort any remaining open transactions
            if self.open_transactions:
                for tx_id in self.open_transactions:
                    self._log_audit_entry(
                        "TRANSACTION_ABORTED_SESSION_END",
                        {
                            "transaction_id": tx_id,
                        },
                    )
                self.open_transactions.clear()

            # Update state
            self.end_time = datetime.utcnow()
            previous_state = self.state
            self.state = SessionState.ENDED

            # Log session end
            self._log_audit_entry(
                "SESSION_ENDED",
                {
                    "end_time": self.end_time.isoformat(),
                    "previous_state": previous_state.value,
                    "duration_seconds": (
                        self.end_time - self.start_time
                    ).total_seconds(),
                    "total_transactions": self.transaction_count,
                    "quarantine_reasons": [r.value for r in self.quarantine_reasons],
                },
            )

            return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get session summary.

        Returns:
            Comprehensive session summary
        """
        with self._lock:
            duration = None
            if self.end_time:
                duration = (self.end_time - self.start_time).total_seconds()
            elif self.start_time:
                duration = (datetime.utcnow() - self.start_time).total_seconds()

            return {
                "session_id": self.session_id,
                "operator_id": self.operator_id,
                "state": self.state.value,
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration_seconds": duration,
                "transaction_count": self.transaction_count,
                "open_transactions": len(self.open_transactions),
                "total_execution_time": self.total_execution_time,
                "quarantine_reasons": [r.value for r in self.quarantine_reasons],
                "resource_usage": self.resource_usage.copy(),
                "audit_entry_count": len(self.audit_entries),
                "workspace": str(self.workspace_root),
            }

    def validate_session_invariants(self) -> Dict[str, bool]:
        """
        Validate session atomic invariants.

        Returns:
            Dictionary of invariant validation results
        """
        with self._lock:
            invariants = {
                "no_open_transactions_on_quarantine": (
                    self.state != SessionState.QUARANTINED
                    or len(self.open_transactions) == 0
                ),
                "session_has_audit_trail": len(self.audit_entries) > 0,
                "transaction_count_matches_history": (
                    self.transaction_count
                    == len(self.transaction_history) + len(self.open_transactions)
                ),
                "no_quarantine_without_reason": (
                    self.state != SessionState.QUARANTINED
                    or len(self.quarantine_reasons) > 0
                ),
                "execution_time_positive": self.total_execution_time >= 0,
                "session_id_not_empty": bool(self.session_id),
                "operator_id_not_empty": bool(self.operator_id),
            }

            return invariants

    def _log_audit_entry(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log audit entry to session and event sink.

        Args:
            event_type: Type of audit event
            data: Audit event data
        """
        audit_entry = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "operator_id": self.operator_id,
            "session_state": self.state.value,
            "data": data,
        }

        # Add to session audit trail
        self.audit_entries.append(audit_entry)

        # Also log to event sink if available
        if self.event_sink:
            try:
                self.event_sink.log_event(
                    event_type=f"SESSION_{event_type}",
                    data=audit_entry,
                    xact_id=None,  # Session events are outside transactions
                )
            except Exception:
                pass  # Don't fail session if event sink logging fails


class SessionManager:
    """
    Manager for atomic IDE operator sessions.

    Enforces single active session per workspace with quarantine enforcement.
    """

    def __init__(self, workspace_root: Path):
        """
        Initialize session manager.

        Args:
            workspace_root: Workspace directory path
        """
        self.workspace_root = workspace_root
        self.sessions: Dict[str, OperatorSession] = {}
        self.active_sessions: Set[str] = set()
        self.workspace_lock = threading.Lock()
        self._lock = threading.RLock()

        # Create sessions directory
        self.sessions_dir = workspace_root / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)

        # Load existing sessions
        self._load_persisted_sessions()

    def start_session(
        self,
        operator_id: str,
        gateway: MCPAtomicGateway,
        event_sink: AtomicEventSink,
    ) -> Optional[OperatorSession]:
        """
        Start new operator session.

        Args:
            operator_id: Operator AI instance identifier
            gateway: MCP Atomic Gateway instance
            event_sink: Atomic event sink for audit logging

        Returns:
            OperatorSession instance if started successfully, None otherwise
        """
        with self._lock:
            # Check for existing active session
            if self.active_sessions:
                # Check if operator already has active session
                for session_id in self.active_sessions:
                    session = self.sessions.get(session_id)
                    if session and session.operator_id == operator_id:
                        # Resume existing session
                        if session.state == SessionState.SUSPENDED:
                            if session.resume():
                                return session
                        else:
                            # Operator already has active session
                            return None

                # Workspace already has active session from different operator
                return None

            # Generate session ID
            session_id = f"SESS-{operator_id}-{int(time.time())}-{uuid.uuid4().hex[:8]}"

            # Create session
            session = OperatorSession(
                session_id=session_id,
                operator_id=operator_id,
                workspace_root=self.workspace_root,
                gateway=gateway,
                event_sink=event_sink,
            )

            # Store session
            self.sessions[session_id] = session
            self.active_sessions.add(session_id)

            # Start session
            if session.start():
                # Persist session state
                self._persist_session(session)
                return session
            else:
                # Clean up failed session
                del self.sessions[session_id]
                if session_id in self.active_sessions:
                    self.active_sessions.remove(session_id)
                return None

    def end_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        End operator session.

        Args:
            session_id: Session identifier

        Returns:
            Session summary if ended successfully, None otherwise
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return None

            # End session
            summary = session.end()

            # Update tracking
            if session_id in self.active_sessions:
                self.active_sessions.remove(session_id)

            # Persist final state
            self._persist_session(session)

            return summary

    def get_session(self, session_id: str) -> Optional[OperatorSession]:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            OperatorSession instance if found, None otherwise
        """
        with self._lock:
            return self.sessions.get(session_id)

    def get_active_sessions(self) -> List[OperatorSession]:
        """
        Get all active sessions.

        Returns:
            List of active OperatorSession instances
        """
        with self._lock:
            return [
                self.sessions[session_id]
                for session_id in self.active_sessions
                if session_id in self.sessions
            ]

    def quarantine_session(
        self,
        session_id: str,
        reason: QuarantineReason,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Quarantine operator session.

        Args:
            session_id: Session identifier
            reason: Quarantine reason
            details: Additional quarantine details

        Returns:
            True if quarantined successfully, False otherwise
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return False

            # Quarantine session
            success = session.quarantine(reason, details)

            if success:
                # Remove from active sessions
                if session_id in self.active_sessions:
                    self.active_sessions.remove(session_id)

                # Persist quarantined state
                self._persist_session(session)

            return success

    def validate_all_sessions(self) -> Dict[str, Dict[str, bool]]:
        """
        Validate invariants for all sessions.

        Returns:
            Dictionary mapping session_id to invariant validation results
        """
        with self._lock:
            results = {}
            for session_id, session in self.sessions.items():
                results[session_id] = session.validate_session_invariants()
            return results

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old sessions.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of sessions cleaned up
        """
        with self._lock:
            cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
            cleaned_count = 0

            for session_id in list(self.sessions.keys()):
                session = self.sessions[session_id]

                # Check if session is old and ended
                if session.state == SessionState.ENDED:
                    if session.end_time:
                        session_age = session.end_time.timestamp()
                    else:
                        session_age = session.start_time.timestamp()

                    if session_age < cutoff_time:
                        # Remove session
                        del self.sessions[session_id]
                        if session_id in self.active_sessions:
                            self.active_sessions.remove(session_id)

                        # Delete persisted file
                        session_file = self.sessions_dir / f"{session_id}.json"
                        if session_file.exists():
                            session_file.unlink()

                        cleaned_count += 1

            return cleaned_count

    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get session manager statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            total_sessions = len(self.sessions)
            active_sessions = len(self.active_sessions)

            state_counts = {}
            for session in self.sessions.values():
                state = session.state.value
                state_counts[state] = state_counts.get(state, 0) + 1

            total_transactions = sum(
                session.transaction_count for session in self.sessions.values()
            )
            total_execution_time = sum(
                session.total_execution_time for session in self.sessions.values()
            )

            quarantined_sessions = [
                session_id
                for session_id, session in self.sessions.items()
                if session.state == SessionState.QUARANTINED
            ]

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "state_counts": state_counts,
                "total_transactions": total_transactions,
                "total_execution_time": total_execution_time,
                "quarantined_sessions": quarantined_sessions,
                "workspace": str(self.workspace_root),
                "sessions_dir": str(self.sessions_dir),
            }

    def _persist_session(self, session: OperatorSession) -> None:
        """
        Persist session state to disk.

        Args:
            session: OperatorSession instance
        """
        try:
            session_file = self.sessions_dir / f"{session.session_id}.json"

            # Create serializable session data
            session_data = {
                "session_id": session.session_id,
                "operator_id": session.operator_id,
                "state": session.state.value,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "transaction_count": session.transaction_count,
                "total_execution_time": session.total_execution_time,
                "quarantine_reasons": [r.value for r in session.quarantine_reasons],
                "resource_usage": session.resource_usage,
                "workspace": str(session.workspace_root),
                "persisted_at": datetime.utcnow().isoformat(),
            }

            # Write to file
            with open(session_file, "w") as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Failed to persist session {session.session_id}: {e}")

    def _load_persisted_sessions(self) -> None:
        """
        Load persisted sessions from disk.
        """
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, "r") as f:
                        session_data = json.load(f)

                    # Check if session is still valid
                    session_id = session_data.get("session_id")
                    if not session_id:
                        continue

                    # For now, just track the file exists
                    # Full session restoration would require gateway and event sink
                    # which aren't available at load time
                    print(f"Found persisted session: {session_id}")

                except Exception as e:
                    print(f"Warning: Failed to load session file {session_file}: {e}")

        except Exception as e:
            print(f"Warning: Failed to load persisted sessions: {e}")


def create_session_manager(workspace_root: Path) -> SessionManager:
    """
    Factory function to create session manager.

    Args:
        workspace_root: Workspace directory path

    Returns:
        SessionManager instance
    """
    return SessionManager(workspace_root)


# Example usage
if __name__ == "__main__":
    import tempfile

    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)

        # Create session manager
        manager = SessionManager(workspace)

        print(f"Session manager created for workspace: {workspace}")
        print(f"Sessions directory: {manager.sessions_dir}")

        # Show statistics
        stats = manager.get_session_statistics()
        print(f"\nInitial statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print("\n✓ Session manager implementation complete")

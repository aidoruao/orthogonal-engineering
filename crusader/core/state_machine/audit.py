"""
Crusader Combat Refrigerator - Audit Logger
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Audit logging system for the Crusader state machine.
Provides comprehensive logging of system events, transitions, and operations.
"""

import asyncio
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from ..constants import FileConstants, SystemMode


class AuditEventType(Enum):
    """Types of audit events."""

    SYSTEM_STARTUP = auto()
    SYSTEM_SHUTDOWN = auto()
    MODE_TRANSITION = auto()
    ERROR_DETECTED = auto()
    ERROR_RESOLVED = auto()
    CONFIGURATION_CHANGE = auto()
    SECURITY_EVENT = auto()
    MAINTENANCE_EVENT = auto()
    WARFARE_OPERATION = auto()
    SENSOR_READING = auto()
    USER_ACTION = auto()
    SYSTEM_HEALTH = auto()
    WITNESS_UPDATE = auto()
    BACKUP_EVENT = auto()
    RESTORE_EVENT = auto()
    TEST_EVENT = auto()
    CUSTOM_EVENT = auto()


class AuditSeverity(Enum):
    """Audit event severity levels."""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


@dataclass
class AuditEvent:
    """Audit event data structure."""

    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    source: str
    message: str
    details: Optional[Dict[str, Any]] = None
    user: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    component: Optional[str] = None
    subsystem: Optional[str] = None
    duration_ms: Optional[float] = None
    success: Optional[bool] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = self.event_type.name
        data["severity"] = self.severity.name
        return data

    def to_json(self) -> str:
        """Convert audit event to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """
    Comprehensive audit logging system.
    Provides structured logging, rotation, compression, and query capabilities.
    """

    # Audit configuration
    DEFAULT_CONFIG = {
        "log_directory": FileConstants.LOG_DIRECTORY,
        "audit_log_file": "audit.log",
        "max_file_size_mb": 10,
        "max_backup_files": 10,
        "compression_enabled": True,
        "retention_days": 30,
        "log_level": AuditSeverity.INFO,
        "async_logging": True,
        "buffer_size": 1000,
        "flush_interval_seconds": 5,
        "structured_logging": True,
        "json_format": True,
        "syslog_enabled": False,
        "syslog_server": None,
        "syslog_port": 514,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the audit logger."""
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

        # State
        self.initialized = False
        self.log_buffer: List[AuditEvent] = []
        self.buffer_lock = asyncio.Lock()
        self.file_lock = asyncio.Lock()
        self.current_log_file: Optional[str] = None
        self.current_file_size = 0
        self.total_events_logged = 0
        self.flush_task: Optional[asyncio.Task] = None

        # Statistics
        self.statistics = {
            "events_by_type": {event_type.name: 0 for event_type in AuditEventType},
            "events_by_severity": {severity.name: 0 for severity in AuditSeverity},
            "events_by_source": {},
            "total_events": 0,
            "failed_writes": 0,
            "buffer_overflows": 0,
            "last_flush_time": None,
            "average_write_time_ms": 0.0,
        }

        # Callbacks
        self.event_callbacks: List[callable] = []

        # Ensure log directory exists
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Ensure log directory exists."""
        log_dir = Path(self.config["log_directory"])
        log_dir.mkdir(parents=True, exist_ok=True)

    def initialize(self):
        """Initialize the audit logger."""
        if self.initialized:
            return

        print("🔧 Initializing Audit Logger...")

        # Create initial log file
        self._rotate_log_file()

        # Start flush task if async logging is enabled
        if self.config["async_logging"]:
            self.flush_task = asyncio.create_task(self._flush_buffer_periodically())

        self.initialized = True
        print(
            f"✅ Audit Logger initialized. Log directory: {self.config['log_directory']}"
        )

    async def shutdown(self):
        """Shutdown the audit logger."""
        if not self.initialized:
            return

        print("🔴 Shutting down Audit Logger...")

        # Cancel flush task
        if self.flush_task and not self.flush_task.done():
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass

        # Flush remaining buffer
        await self._flush_buffer()

        # Close log file
        self.current_log_file = None
        self.initialized = False

        print("✅ Audit Logger shutdown complete")

    def register_callback(self, callback: callable):
        """Register a callback for audit events."""
        self.event_callbacks.append(callback)

    def unregister_callback(self, callback: callable):
        """Unregister an audit event callback."""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)

    async def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        source: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        component: Optional[str] = None,
        subsystem: Optional[str] = None,
        duration_ms: Optional[float] = None,
        success: Optional[bool] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log an audit event.

        Returns:
            Event ID for tracking
        """
        # Check if event should be logged based on severity
        if not self._should_log_event(severity):
            return ""

        # Create audit event
        event = AuditEvent(
            event_id=str(uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            source=source,
            message=message,
            details=details,
            user=user,
            session_id=session_id,
            correlation_id=correlation_id,
            component=component,
            subsystem=subsystem,
            duration_ms=duration_ms,
            success=success,
            error_code=error_code,
            error_message=error_message,
            stack_trace=stack_trace,
            metadata=metadata,
        )

        # Update statistics
        self._update_statistics(event)

        # Add to buffer
        if self.config["async_logging"]:
            await self._add_to_buffer(event)
        else:
            await self._write_event_sync(event)

        # Notify callbacks
        await self._notify_callbacks(event)

        return event.event_id

    def _should_log_event(self, severity: AuditSeverity) -> bool:
        """Check if event should be logged based on severity."""
        log_level = self.config["log_level"]
        severity_levels = list(AuditSeverity)

        event_level = severity_levels.index(severity)
        config_level = severity_levels.index(log_level)

        return event_level >= config_level

    def _update_statistics(self, event: AuditEvent):
        """Update audit statistics."""
        self.statistics["total_events"] += 1
        self.statistics["events_by_type"][event.event_type.name] += 1
        self.statistics["events_by_severity"][event.severity.name] += 1

        # Update source statistics
        source = event.source
        if source not in self.statistics["events_by_source"]:
            self.statistics["events_by_source"][source] = 0
        self.statistics["events_by_source"][source] += 1

    async def _add_to_buffer(self, event: AuditEvent):
        """Add event to buffer for async writing."""
        async with self.buffer_lock:
            # Check buffer size
            if len(self.log_buffer) >= self.config["buffer_size"]:
                self.statistics["buffer_overflows"] += 1
                # Remove oldest events if buffer is full
                self.log_buffer.pop(0)

            self.log_buffer.append(event)

            # Auto-flush if buffer is getting full
            if len(self.log_buffer) >= self.config["buffer_size"] * 0.8:
                asyncio.create_task(self._flush_buffer())

    async def _write_event_sync(self, event: AuditEvent):
        """Write event synchronously."""
        try:
            await self._write_event_to_file(event)
        except Exception as e:
            print(f"❌ Failed to write audit event: {e}")
            self.statistics["failed_writes"] += 1

    async def _flush_buffer_periodically(self):
        """Periodically flush the buffer."""
        while True:
            try:
                await asyncio.sleep(self.config["flush_interval_seconds"])
                await self._flush_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in periodic flush: {e}")

    async def _flush_buffer(self):
        """Flush buffer to disk."""
        if not self.log_buffer:
            return

        async with self.buffer_lock:
            events_to_write = self.log_buffer.copy()
            self.log_buffer.clear()

        # Write events
        for event in events_to_write:
            try:
                await self._write_event_to_file(event)
            except Exception as e:
                print(f"❌ Failed to write audit event during flush: {e}")
                self.statistics["failed_writes"] += 1

        self.statistics["last_flush_time"] = datetime.now()

    async def _write_event_to_file(self, event: AuditEvent):
        """Write event to log file."""
        async with self.file_lock:
            # Check if we need to rotate the log file
            if self._should_rotate_file():
                self._rotate_log_file()

            # Format the log entry
            log_entry = self._format_log_entry(event)

            # Write to file
            try:
                with open(self.current_log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry + "\n")

                # Update file size
                self.current_file_size += len(log_entry.encode("utf-8"))
                self.total_events_logged += 1

            except Exception as e:
                print(f"❌ Failed to write to audit log file: {e}")
                raise

    def _should_rotate_file(self) -> bool:
        """Check if log file should be rotated."""
        if not self.current_log_file:
            return True

        # Check file size
        max_size_bytes = self.config["max_file_size_mb"] * 1024 * 1024
        return self.current_file_size >= max_size_bytes

    def _rotate_log_file(self):
        """Rotate the log file."""
        if self.current_log_file and os.path.exists(self.current_log_file):
            # Rename current file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(self.current_log_file).stem
            ext = Path(self.current_log_file).suffix
            archive_name = f"{base_name}_{timestamp}{ext}"
            archive_path = Path(self.config["log_directory"]) / archive_name

            try:
                os.rename(self.current_log_file, archive_path)

                # Compress if enabled
                if self.config["compression_enabled"]:
                    self._compress_log_file(archive_path)

                # Clean up old files
                self._cleanup_old_files()

            except Exception as e:
                print(f"❌ Failed to rotate log file: {e}")

        # Create new log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_log_file = str(
            Path(self.config["log_directory"]) / f"audit_{timestamp}.log"
        )
        self.current_file_size = 0

        # Write header
        self._write_file_header()

    def _write_file_header(self):
        """Write header to new log file."""
        header = f"# Crusader Audit Log - Started at {datetime.now().isoformat()}\n"
        header += f"# System: Crusader Combat Refrigerator\n"
        header += f"# Version: 1.0.0\n"
        header += f"# Log Level: {self.config['log_level'].name}\n"
        header += "#" * 80 + "\n"

        try:
            with open(self.current_log_file, "w", encoding="utf-8") as f:
                f.write(header)
            self.current_file_size = len(header.encode("utf-8"))
        except Exception as e:
            print(f"❌ Failed to write log file header: {e}")

    def _format_log_entry(self, event: AuditEvent) -> str:
        """Format log entry based on configuration."""
        if self.config["json_format"]:
            return event.to_json()
        else:
            return self._format_text_entry(event)

    def _format_text_entry(self, event: AuditEvent) -> str:
        """Format log entry as text."""
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        severity = event.severity.name.ljust(8)
        event_type = event.event_type.name.ljust(20)
        source = event.source.ljust(15)

        entry = f"{timestamp} | {severity} | {event_type} | {source} | {event.message}"

        if event.details:
            details_str = json.dumps(event.details, separators=(",", ":"))
            entry += f" | Details: {details_str}"

        if event.user:
            entry += f" | User: {event.user}"

        if event.duration_ms is not None:
            entry += f" | Duration: {event.duration_ms:.2f}ms"

        if event.success is not None:
            entry += f" | Success: {event.success}"

        return entry

    def _compress_log_file(self, file_path: Path):
        """Compress log file."""
        # This would be implemented with gzip or similar
        # For now, just mark as placeholder
        pass

    def _cleanup_old_files(self):
        """Clean up old log files."""
        log_dir = Path(self.config["log_directory"])
        max_backup = self.config["max_backup_files"]

        # Get all audit log files
        audit_files = sorted(
            log_dir.glob("audit_*.log*"), key=lambda x: x.stat().st_mtime, reverse=True
        )

        # Remove old files
        for file in audit_files[max_backup:]:
            try:
                file.unlink()
            except Exception as e:
                print(f"❌ Failed to delete old log file {file}: {e}")

    async def _notify_callbacks(self, event: AuditEvent):
        """Notify registered callbacks."""
        for callback in self.event_callbacks:
            try:
                await callback(event)
            except Exception as e:
                print(f"⚠️ Audit event callback failed: {e}")

    # Convenience methods for common audit events
    async def log_system_startup(self, details: Optional[Dict[str, Any]] = None):
        """Log system startup event."""
        return await self.log_event(
            event_type=AuditEventType.SYSTEM_STARTUP,
            severity=AuditSeverity.INFO,
            source="system",
            message="System startup initiated",
            details=details,
        )

    async def log_system_shutdown(self, details: Optional[Dict[str, Any]] = None):
        """Log system shutdown event."""
        return await self.log_event(
            event_type=AuditEventType.SYSTEM_SHUTDOWN,
            severity=AuditSeverity.INFO,
            source="system",
            message="System shutdown initiated",
            details=details,
        )

    async def log_mode_transition(
        self,
        from_mode: SystemMode,
        to_mode: SystemMode,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log mode transition event."""
        return await self.log_event(
            event_type=AuditEventType.MODE_TRANSITION,
            severity=AuditSeverity.INFO,
            source="state_machine",
            message=f"Mode transition: {from_mode.value} -> {to_mode.value}",
            details={
                "from_mode": from_mode.value,
                "to_mode": to_mode.value,
                "reason": reason,
                **(details or {}),
            },
        )

    async def log_error_detected(
        self,
        error_message: str,
        error_code: Optional[str] = None,
        component: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log error detection."""
        await self.log_event(
            event_type=AuditEventType.ERROR_DETECTED,
            severity=AuditSeverity.ERROR,
            source=component or "unknown",
            message=error_message,
            details={
                "error_message": error_message,
                "error_code": error_code,
                "component": component,
                **(details or {}),
            },
        )

    async def log_system_startup(self, version: str, config_hash: str):
        """Log system startup."""
        await self.log_event(
            event_type=AuditEventType.SYSTEM_STARTUP,
            severity=AuditSeverity.INFO,
            source="system",
            message=f"System started: version {version}",
            details={
                "version": version,
                "config_hash": config_hash,
                "startup_time": datetime.now().isoformat(),
            },
        )

    async def log_system_shutdown(self, reason: str, uptime_seconds: float):
        """Log system shutdown."""
        await self.log_event(
            event_type=AuditEventType.SYSTEM_SHUTDOWN,
            severity=AuditSeverity.INFO,
            source="system",
            message=f"System shutdown: {reason}",
            details={
                "reason": reason,
                "uptime_seconds": uptime_seconds,
                "shutdown_time": datetime.now().isoformat(),
            },
        )

    async def log_security_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log security event."""
        await self.log_event(
            event_type=event_type,
            severity=severity,
            source="security",
            message=message,
            details=details or {},
        )

    async def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        threshold: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log performance metric."""
        severity = AuditSeverity.INFO
        if threshold is not None:
            if value > threshold * 1.5:
                severity = AuditSeverity.ERROR
            elif value > threshold:
                severity = AuditSeverity.WARNING

        await self.log_event(
            event_type=AuditEventType.PERFORMANCE_METRIC,
            severity=severity,
            source="performance",
            message=f"Performance metric: {metric_name} = {value} {unit}",
            details={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "threshold": threshold,
                **(details or {}),
            },
        )

    async def log_data_integrity_check(
        self,
        check_name: str,
        passed: bool,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log data integrity check."""
        await self.log_event(
            event_type=AuditEventType.DATA_INTEGRITY,
            severity=AuditSeverity.WARNING if not passed else AuditSeverity.INFO,
            source="integrity",
            message=f"Data integrity check: {check_name} - {'PASSED' if passed else 'FAILED'}",
            details={
                "check_name": check_name,
                "passed": passed,
                **(details or {}),
            },
        )

    async def log_external_interaction(
        self,
        interaction_type: str,
        target: str,
        success: bool,
        duration_seconds: float,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log external interaction."""
        await self.log_event(
            event_type=AuditEventType.EXTERNAL_INTERACTION,
            severity=AuditSeverity.ERROR if not success else AuditSeverity.INFO,
            source="external",
            message=f"External interaction: {interaction_type} with {target} - {'SUCCESS' if success else 'FAILED'}",
            details={
                "interaction_type": interaction_type,
                "target": target,
                "success": success,
                "duration_seconds": duration_seconds,
                **(details or {}),
            },
        )

    # Query methods
    async def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        source: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Get audit events with filtering."""
        # Filter events from buffer
        filtered_events = []
        for event in self.event_buffer:
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            if event_type and event.event_type != event_type:
                continue
            if severity and event.severity != severity:
                continue
            if source and event.source != source:
                continue
            filtered_events.append(event)

        # Sort by timestamp (newest first) and limit
        filtered_events.sort(key=lambda e: e.timestamp, reverse=True)
        return filtered_events[:limit]

    async def get_event_count(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        source: Optional[str] = None,
    ) -> int:
        """Get count of audit events with filtering."""
        events = await self.get_events(
            start_time, end_time, event_type, severity, source, limit=10000
        )
        return len(events)

    async def get_event_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get event statistics."""
        events = await self.get_events(start_time, end_time, limit=10000)

        # Count by severity
        severity_counts = {}
        for severity in AuditSeverity:
            severity_counts[severity.name] = 0

        # Count by event type
        type_counts = {}
        for event_type in AuditEventType:
            type_counts[event_type.name] = 0

        # Count events
        for event in events:
            severity_counts[event.severity.name] += 1
            type_counts[event.event_type.name] += 1

        # Get time range
        timestamps = [event.timestamp for event in events]
        min_time = min(timestamps) if timestamps else None
        max_time = max(timestamps) if timestamps else None

        return {
            "severity_counts": severity_counts,
            "type_counts": type_counts,
            "time_range": {
                "min": min_time.isoformat() if min_time else None,
                "max": max_time.isoformat() if max_time else None,
            },
            "total_events": len(events),
        }

    async def export_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        format: str = "json",
    ) -> str:
        """Export audit events."""
        events = await self.get_events(start_time, end_time, limit=1000)

        if format == "json":
            return json.dumps(
                [event.to_dict() for event in events],
                indent=2,
                default=str,
            )
        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=["timestamp", "event_type", "severity", "source", "message"],
            )
            writer.writeheader()
            for event in events:
                writer.writerow(
                    {
                        "timestamp": event.timestamp.isoformat(),
                        "event_type": event.event_type.name,
                        "severity": event.severity.name,
                        "source": event.source,
                        "message": event.message[:100],  # Truncate long messages
                    }
                )
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def cleanup_old_events(self, days_to_keep: int = 30):
        """Clean up events older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        # Filter out old events from buffer
        original_count = len(self.event_buffer)
        self.event_buffer = [
            event for event in self.event_buffer if event.timestamp >= cutoff_date
        ]

        return original_count - len(self.event_buffer)

    async def close(self):
        """Close the audit logger."""
        if self.session_factory:
            await self.session_factory.dispose()

    # Helper methods
    def _build_query(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        source: Optional[str] = None,
    ):
        """Build query for event filtering (compatibility method)."""
        # This method is kept for compatibility but now uses in-memory filtering
        # The actual filtering is done in get_events()
        return None


# Convenience functions
async def create_audit_logger(
    database_url: Optional[str] = None,
    max_events: int = 10000,
) -> AuditLogger:
    """Create and initialize an audit logger."""
    logger = AuditLogger(database_url=database_url, max_events=max_events)
    await logger.initialize()
    return logger


async def log_quick_event(
    message: str,
    event_type: AuditEventType = AuditEventType.SYSTEM_HEALTH,
    severity: AuditSeverity = AuditSeverity.INFO,
    source: str = "system",
    details: Optional[Dict[str, Any]] = None,
):
    """Quick logging without creating a logger instance."""
    logger = AuditLogger()
    await logger.initialize()

    try:
        await logger.log_event(
            event_type=event_type,
            severity=severity,
            source=source,
            message=message,
            details=details or {},
        )
    finally:
        await logger.close()


if __name__ == "__main__":
    # Test the audit logger
    import asyncio

    async def test_audit_logger():
        """Test the audit logger."""
        print("Testing Audit Logger...")

        # Create in-memory database for testing
        logger = await create_audit_logger("sqlite+aiosqlite:///:memory:")

        try:
            # Log some events
            await logger.log_system_startup("1.0.0", "abc123")
            await logger.log_mode_transition(
                SystemMode.STANDBY, SystemMode.ACTIVE, "manual_activation"
            )
            await logger.log_error_detected(
                "Test error", error_code="TEST001", component="test"
            )

            # Get events
            events = await logger.get_events(limit=5)
            print(f"Logged {len(events)} events")

            # Get statistics
            stats = await logger.get_event_statistics()
            print(f"Statistics: {stats}")

            # Export events
            json_export = await logger.export_events(format="json")
            print(f"JSON export length: {len(json_export)}")

        finally:
            await logger.close()
            print("✅ Test completed")

    asyncio.run(test_audit_logger())

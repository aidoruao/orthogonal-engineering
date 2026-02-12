"""
logging_protocol.py
===================

STANDARDIZED LOGGING PROTOCOL FOR DAEMON INTEGRATION
Ensures consistent logging across all components with daemon visibility

ARCHITECTURE PRINCIPLE:
"All logs must stream to daemon terminal and central dashboard"

FEATURES:
1. Standardized log formats for all operation types
2. Structured logging with context preservation
3. Daemon streaming with fallback to local logging
4. Performance metrics collection
5. Audit trail generation for compliance
"""

import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

# ==================== DATA MODELS ====================


class LogLevel(str, Enum):
    """Standardized log levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogComponent(str, Enum):
    """Standardized component identifiers"""

    DAEMON_CLIENT = "DaemonClient"
    LORA_CHAT = "InteractiveLoRAChat"
    BATCH_PROCESSOR = "BatchProcessor"
    API_SERVER = "APIServer"
    CONSTRAINT_HANDLER = "ChristConstraintHandler"
    GOVERNANCE_AUDITOR = "GovernanceAuditor"
    SYSTEM_MONITOR = "SystemMonitor"


class OperationType(str, Enum):
    """Standardized operation types"""

    INFERENCE = "inference"
    VALIDATION = "validation"
    CONSTRAINT_EVALUATION = "constraint_evaluation"
    BATCH_PROCESSING = "batch_processing"
    API_REQUEST = "api_request"
    SYSTEM_HEALTH_CHECK = "system_health_check"
    AUDIT_TRAIL = "audit_trail"


@dataclass
class StructuredLogEntry:
    """Structured log entry with standardized format"""

    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    level: LogLevel = LogLevel.INFO
    component: LogComponent = LogComponent.DAEMON_CLIENT
    operation: OperationType = OperationType.INFERENCE
    message: str = ""
    request_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Optional[Dict[str, float]] = None
    constraint_scores: Optional[Dict[str, float]] = None
    daemon_streamed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "component": self.component.value,
            "operation": self.operation.value,
            "message": self.message,
            "request_id": self.request_id,
            "data": self.data,
            "performance_metrics": self.performance_metrics,
            "constraint_scores": self.constraint_scores,
            "daemon_streamed": self.daemon_streamed,
        }

    def to_log_string(self) -> str:
        """Convert to human-readable log string"""
        base = f"[{self.timestamp}] [{self.level.value}] [{self.component.value}.{self.operation.value}]"

        if self.request_id:
            base += f" [#{self.request_id}]"

        base += f" {self.message}"

        if self.performance_metrics:
            metrics_str = " ".join(
                [f"{k}={v:.2f}" for k, v in self.performance_metrics.items()]
            )
            base += f" | Metrics: {metrics_str}"

        if self.constraint_scores:
            scores_str = " ".join(
                [f"{k}={v:.3f}" for k, v in self.constraint_scores.items()]
            )
            base += f" | Constraints: {scores_str}"

        return base


# ==================== LOG FORMAT TEMPLATES ====================


class LogTemplates:
    """Standardized log message templates"""

    # Inference logs
    INFERENCE_START = "🤖 LORA INFERENCE #{request_id}: {operation_type}"
    INFERENCE_COMPLETE = "✓ Response generated: {token_count} tokens"
    INFERENCE_ERROR = "❌ Inference failed: {error_message}"

    # Validation logs
    VALIDATION_START = "🔍 Validating operation: {operation_type}"
    VALIDATION_PASS = "✅ Operation validated: {operation_type}"
    VALIDATION_FAIL = "⚠️ Operation rejected: {operation_type}"
    VALIDATION_ERROR = "❌ Validation error: {error_message}"

    # Constraint logs
    CONSTRAINT_EVALUATION = (
        "⚖️ Σ_LORA Validation: {constraint_name} - {result} ({score:.2f})"
    )
    CONSTRAINT_ALERT = (
        "⚠️ Christ Constraint Alert: Score {score} < threshold {threshold}"
    )
    CONSTRAINT_VIOLATION = "🚨 Constraint violation: {violation_type}"
    CONSTRAINT_PASS = "✅ All constraints satisfied"

    # System logs
    SYSTEM_START = "🚀 System starting: {component}"
    SYSTEM_HEALTHY = "💓 System healthy: {component}"
    SYSTEM_WARNING = "⚠️ System warning: {component} - {message}"
    SYSTEM_ERROR = "❌ System error: {component} - {error_message}"
    SYSTEM_RECOVERED = "🔄 System recovered: {component}"

    # Performance logs
    PERFORMANCE_METRIC = "📊 Performance: {metric_name}={metric_value:.2f}{unit}"
    PERFORMANCE_WARNING = "🐢 Performance warning: {metric_name} exceeds threshold"
    PERFORMANCE_OPTIMAL = "⚡ Performance optimal: {metric_name}"

    # Audit logs
    AUDIT_TRAIL_START = "📝 Audit trail started: {operation}"
    AUDIT_TRAIL_ENTRY = "📋 Audit entry: {entry_type}"
    AUDIT_TRAIL_COMPLETE = "✅ Audit trail complete: {operation}"

    # Batch processing logs
    BATCH_START = "📦 Batch processing started: {batch_size} items"
    BATCH_PROGRESS = "📈 Batch progress: {processed}/{total} ({percentage:.1f}%)"
    BATCH_COMPLETE = "✅ Batch processing complete: {processed} items"
    BATCH_ERROR = "❌ Batch item failed: {item_id} - {error_message}"

    # API logs
    API_REQUEST = "🌐 API Request: {method} {endpoint}"
    API_RESPONSE = "📨 API Response: {status_code} - {response_time:.0f}ms"
    API_ERROR = "❌ API Error: {endpoint} - {error_message}"


# ==================== LOGGING PROTOCOL CLASS ====================


class LoggingProtocol:
    """
    Main logging protocol class that enforces standardized logging
    across all components with daemon integration.
    """

    def __init__(
        self,
        component: LogComponent,
        daemon_client=None,
        enable_daemon_streaming: bool = True,
        log_file: Optional[str] = None,
        log_level: LogLevel = LogLevel.INFO,
    ):
        """
        Initialize logging protocol for a component.

        Args:
            component: Component identifier
            daemon_client: Optional DaemonClient instance for streaming
            enable_daemon_streaming: Whether to stream logs to daemon
            log_file: Optional file path for local logging
            log_level: Minimum log level to record
        """
        self.component = component
        self.daemon_client = daemon_client
        self.enable_daemon_streaming = enable_daemon_streaming
        self.log_level = log_level

        # Create component-specific logger
        self.logger = logging.getLogger(component.value)
        self.logger.setLevel(log_level.value)

        # Set up file logging if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                )
            )
            self.logger.addHandler(file_handler)

        # Performance tracking
        self.performance_start_times = {}
        self.metrics_accumulator = {}

        # Audit trail
        self.audit_trail = []

        self.log_system_start()

    # ==================== CORE LOGGING METHODS ====================

    def log(
        self,
        level: LogLevel,
        operation: OperationType,
        message: str,
        request_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, float]] = None,
        constraint_scores: Optional[Dict[str, float]] = None,
    ) -> StructuredLogEntry:
        """
        Core logging method with standardized format.

        Args:
            level: Log level
            operation: Operation type
            message: Log message
            request_id: Optional request identifier
            data: Optional contextual data
            performance_metrics: Optional performance metrics
            constraint_scores: Optional constraint scores

        Returns:
            StructuredLogEntry that was logged
        """
        # Skip if below configured log level
        if self._should_skip_log(level):
            return None

        # Create structured log entry
        entry = StructuredLogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level=level,
            component=self.component,
            operation=operation,
            message=message,
            request_id=request_id,
            data=data or {},
            performance_metrics=performance_metrics,
            constraint_scores=constraint_scores,
        )

        # Log locally
        self._log_locally(entry)

        # Stream to daemon if enabled
        if self.enable_daemon_streaming and self.daemon_client:
            self._stream_to_daemon(entry)

        # Add to audit trail if appropriate
        if operation in [
            OperationType.VALIDATION,
            OperationType.CONSTRAINT_EVALUATION,
            OperationType.AUDIT_TRAIL,
        ]:
            self.audit_trail.append(entry)

        return entry

    def log_inference_start(
        self,
        request_id: str,
        operation_type: str = "single_inference",
        prompt_length: Optional[int] = None,
    ) -> StructuredLogEntry:
        """Log start of inference operation"""
        message = LogTemplates.INFERENCE_START.format(
            request_id=request_id, operation_type=operation_type
        )

        data = {
            "request_id": request_id,
            "operation_type": operation_type,
            "prompt_length": prompt_length,
        }

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.INFERENCE,
            message=message,
            request_id=request_id,
            data=data,
        )

    def log_inference_complete(
        self,
        request_id: str,
        token_count: int,
        christ_score: Optional[float] = None,
        processing_time_ms: Optional[float] = None,
    ) -> StructuredLogEntry:
        """Log completion of inference operation"""
        message = LogTemplates.INFERENCE_COMPLETE.format(token_count=token_count)

        performance_metrics = None
        constraint_scores = None

        if processing_time_ms:
            performance_metrics = {"processing_time_ms": processing_time_ms}

        if christ_score is not None:
            constraint_scores = {"christ_score": christ_score}

            # Add Christ constraint alert if score is low
            if christ_score < 0.5:  # Example threshold
                self.log_christ_constraint_alert(request_id, christ_score, 0.5)

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.INFERENCE,
            message=message,
            request_id=request_id,
            performance_metrics=performance_metrics,
            constraint_scores=constraint_scores,
        )

    def log_validation(
        self,
        operation_type: str,
        valid: bool,
        request_id: Optional[str] = None,
        message: Optional[str] = None,
    ) -> StructuredLogEntry:
        """Log validation operation"""
        if valid:
            template = LogTemplates.VALIDATION_PASS
            level = LogLevel.INFO
        else:
            template = LogTemplates.VALIDATION_FAIL
            level = LogLevel.WARNING

        log_message = template.format(operation_type=operation_type)

        if message:
            log_message += f" - {message}"

        return self.log(
            level=level,
            operation=OperationType.VALIDATION,
            message=log_message,
            request_id=request_id,
            data={"valid": valid, "operation_type": operation_type},
        )

    def log_constraint_evaluation(
        self,
        constraint_name: str,
        result: str,
        score: float,
        request_id: Optional[str] = None,
    ) -> StructuredLogEntry:
        """Log constraint evaluation result"""
        message = LogTemplates.CONSTRAINT_EVALUATION.format(
            constraint_name=constraint_name, result=result, score=score
        )

        level = LogLevel.INFO if result.lower() == "pass" else LogLevel.WARNING

        return self.log(
            level=level,
            operation=OperationType.CONSTRAINT_EVALUATION,
            message=message,
            request_id=request_id,
            data={"constraint_name": constraint_name, "result": result},
            constraint_scores={constraint_name: score},
        )

    def log_christ_constraint_alert(
        self, request_id: str, score: float, threshold: float = 0.5
    ) -> StructuredLogEntry:
        """Log Christ constraint alert (falsification trigger)"""
        message = LogTemplates.CONSTRAINT_ALERT.format(score=score, threshold=threshold)

        return self.log(
            level=LogLevel.WARNING,
            operation=OperationType.CONSTRAINT_EVALUATION,
            message=message,
            request_id=request_id,
            data={
                "score": score,
                "threshold": threshold,
                "mode": "audit_only",  # Falsification-based, not hard blocking
            },
            constraint_scores={"christ_constraint": score},
        )

    def log_system_start(self) -> StructuredLogEntry:
        """Log system/component startup"""
        message = LogTemplates.SYSTEM_START.format(component=self.component.value)

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.SYSTEM_HEALTH_CHECK,
            message=message,
        )

    def log_performance_metric(
        self,
        metric_name: str,
        metric_value: float,
        unit: str = "",
        request_id: Optional[str] = None,
    ) -> StructuredLogEntry:
        """Log performance metric"""
        message = LogTemplates.PERFORMANCE_METRIC.format(
            metric_name=metric_name, metric_value=metric_value, unit=unit
        )

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.SYSTEM_HEALTH_CHECK,
            message=message,
            request_id=request_id,
            performance_metrics={metric_name: metric_value},
        )

    # ==================== PERFORMANCE TRACKING ====================

    def start_performance_tracking(
        self, operation: str, request_id: Optional[str] = None
    ):
        """Start tracking performance for an operation"""
        key = f"{operation}_{request_id}" if request_id else operation
        self.performance_start_times[key] = time.time()

    def end_performance_tracking(
        self, operation: str, request_id: Optional[str] = None, log_result: bool = True
    ) -> float:
        """End performance tracking and optionally log result"""
        key = f"{operation}_{request_id}" if request_id else operation

        if key not in self.performance_start_times:
            return 0.0

        elapsed_ms = (time.time() - self.performance_start_times[key]) * 1000
        del self.performance_start_times[key]

        if log_result:
            self.log_performance_metric(
                f"{operation}_time", elapsed_ms, "ms", request_id
            )

        # Accumulate for statistics
        if operation not in self.metrics_accumulator:
            self.metrics_accumulator[operation] = []
        self.metrics_accumulator[operation].append(elapsed_ms)

        return elapsed_ms

    def get_performance_statistics(self, operation: str) -> Dict[str, float]:
        """Get performance statistics for an operation"""
        if (
            operation not in self.metrics_accumulator
            or not self.metrics_accumulator[operation]
        ):
            return {}

        values = self.metrics_accumulator[operation]

        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "p95": sorted(values)[int(len(values) * 0.95)]
            if len(values) > 1
            else values[0],
        }

    # ==================== AUDIT TRAIL METHODS ====================

    def start_audit_trail(self, operation: str) -> StructuredLogEntry:
        """Start a new audit trail"""
        message = LogTemplates.AUDIT_TRAIL_START.format(operation=operation)

        # Clear previous audit trail for this component
        self.audit_trail = []

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.AUDIT_TRAIL,
            message=message,
            data={"audit_operation": operation},
        )

    def add_audit_entry(
        self, entry_type: str, details: Dict[str, Any], request_id: Optional[str] = None
    ) -> StructuredLogEntry:
        """Add an entry to the audit trail"""
        message = LogTemplates.AUDIT_TRAIL_ENTRY.format(entry_type=entry_type)

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.AUDIT_TRAIL,
            message=message,
            request_id=request_id,
            data={"audit_entry_type": entry_type, **details},
        )

    def complete_audit_trail(self, operation: str) -> StructuredLogEntry:
        """Complete an audit trail"""
        message = LogTemplates.AUDIT_TRAIL_COMPLETE.format(operation=operation)

        # Log audit trail summary
        summary = {
            "total_entries": len(self.audit_trail),
            "operations": list(set([e.operation.value for e in self.audit_trail])),
            "time_range": {
                "start": self.audit_trail[0].timestamp if self.audit_trail else None,
                "end": datetime.utcnow().isoformat(),
            },
        }

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.AUDIT_TRAIL,
            message=message,
            data={"audit_summary": summary},
        )

    def get_audit_trail(self) -> List[StructuredLogEntry]:
        """Get the current audit trail"""
        return self.audit_trail.copy()

    def export_audit_trail(self, filepath: str) -> bool:
        """Export audit trail to file"""
        try:
            with open(filepath, "w") as f:
                json.dump([entry.to_dict() for entry in self.audit_trail], f, indent=2)

            self.log(
                level=LogLevel.INFO,
                operation=OperationType.AUDIT_TRAIL,
                message=f"Audit trail exported to {filepath}",
            )
            return True
        except Exception as e:
            self.log(
                level=LogLevel.ERROR,
                operation=OperationType.AUDIT_TRAIL,
                message=f"Failed to export audit trail: {e}",
            )
            return False

    # ==================== BATCH PROCESSING LOGS ====================

    def log_batch_start(
        self, batch_size: int, batch_id: Optional[str] = None
    ) -> StructuredLogEntry:
        """Log start of batch processing"""
        message = LogTemplates.BATCH_START.format(batch_size=batch_size)

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.BATCH_PROCESSING,
            message=message,
            request_id=batch_id,
            data={"batch_size": batch_size},
        )

    def log_batch_progress(
        self, processed: int, total: int, batch_id: Optional[str] = None
    ) -> StructuredLogEntry:
        """Log batch processing progress"""
        percentage = (processed / total * 100) if total > 0 else 0

        message = LogTemplates.BATCH_PROGRESS.format(
            processed=processed, total=total, percentage=percentage
        )

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.BATCH_PROCESSING,
            message=message,
            request_id=batch_id,
            data={"processed": processed, "total": total, "percentage": percentage},
        )

    def log_batch_complete(
        self,
        processed: int,
        batch_id: Optional[str] = None,
        success_rate: Optional[float] = None,
    ) -> StructuredLogEntry:
        """Log completion of batch processing"""
        message = LogTemplates.BATCH_COMPLETE.format(processed=processed)

        data = {"processed": processed}
        if success_rate is not None:
            data["success_rate"] = success_rate

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.BATCH_PROCESSING,
            message=message,
            request_id=batch_id,
            data=data,
        )

    def log_batch_error(
        self, item_id: str, error_message: str, batch_id: Optional[str] = None
    ) -> StructuredLogEntry:
        """Log batch item error"""
        message = LogTemplates.BATCH_ERROR.format(
            item_id=item_id, error_message=error_message
        )

        return self.log(
            level=LogLevel.ERROR,
            operation=OperationType.BATCH_PROCESSING,
            message=message,
            request_id=batch_id,
            data={"item_id": item_id, "error": error_message},
        )

    # ==================== API LOGS ====================

    def log_api_request(
        self, method: str, endpoint: str, request_id: Optional[str] = None
    ) -> StructuredLogEntry:
        """Log API request"""
        message = LogTemplates.API_REQUEST.format(method=method, endpoint=endpoint)

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.API_REQUEST,
            message=message,
            request_id=request_id,
            data={"method": method, "endpoint": endpoint},
        )

    def log_api_response(
        self,
        status_code: int,
        response_time_ms: float,
        request_id: Optional[str] = None,
    ) -> StructuredLogEntry:
        """Log API response"""
        message = LogTemplates.API_RESPONSE.format(
            status_code=status_code, response_time=response_time_ms
        )

        return self.log(
            level=LogLevel.INFO,
            operation=OperationType.API_REQUEST,
            message=message,
            request_id=request_id,
            data={"status_code": status_code, "response_time_ms": response_time_ms},
            performance_metrics={"response_time_ms": response_time_ms},
        )

    def log_api_error(
        self, endpoint: str, error_message: str, request_id: Optional[str] = None
    ) -> StructuredLogEntry:
        """Log API error"""
        message = LogTemplates.API_ERROR.format(
            endpoint=endpoint, error_message=error_message
        )

        return self.log(
            level=LogLevel.ERROR,
            operation=OperationType.API_REQUEST,
            message=message,
            request_id=request_id,
            data={"endpoint": endpoint, "error": error_message},
        )

    # ==================== INTERNAL METHODS ====================

    def _should_skip_log(self, level: LogLevel) -> bool:
        """Check if log should be skipped based on level"""
        level_priority = {
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
            LogLevel.CRITICAL: 50,
        }

        return level_priority[level] < level_priority[self.log_level]

    def _log_locally(self, entry: StructuredLogEntry):
        """Log locally using Python's logging system"""
        log_method = getattr(self.logger, entry.level.value.lower())
        log_method(entry.to_log_string())

    def _stream_to_daemon(self, entry: StructuredLogEntry):
        """Stream log entry to daemon"""
        try:
            if self.daemon_client and hasattr(self.daemon_client, "log_operation"):
                # Convert to daemon client's log format
                from daemon_client import LogEntry as DaemonLogEntry

                daemon_entry = DaemonLogEntry(
                    level=entry.level.value,
                    component=entry.component.value,
                    operation=entry.operation.value,
                    message=entry.message,
                    data=entry.data,
                    request_id=entry.request_id,
                    timestamp=entry.timestamp,
                )

                self.daemon_client.log_operation(daemon_entry)
                entry.daemon_streamed = True

        except ImportError:
            # Daemon client not available, skip streaming
            pass
        except Exception as e:
            # Log error but don't fail
            self.logger.warning(f"Failed to stream log to daemon: {e}")

    # ==================== UTILITY METHODS ====================

    def set_log_level(self, level: LogLevel):
        """Set the log level"""
        self.log_level = level
        self.logger.setLevel(level.value)

    def enable_daemon_streaming(self, enable: bool = True):
        """Enable or disable daemon streaming"""
        self.enable_daemon_streaming = enable

    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        return {
            "component": self.component.value,
            "log_level": self.log_level.value,
            "daemon_streaming_enabled": self.enable_daemon_streaming,
            "performance_metrics": {
                op: self.get_performance_statistics(op)
                for op in self.metrics_accumulator.keys()
            },
            "audit_trail_size": len(self.audit_trail),
        }

    def clear_metrics(self):
        """Clear accumulated metrics"""
        self.metrics_accumulator.clear()


# ==================== EXAMPLE USAGE ====================


def example_usage():
    """Example of how to use the LoggingProtocol"""

    # Initialize logging protocol for a component
    logger = LoggingProtocol(component=LogComponent.LORA_CHAT, log_level=LogLevel.INFO)

    # Log system startup
    logger.log_system_start()

    # Start performance tracking
    logger.start_performance_tracking("inference", "req_123")

    # Log inference start
    logger.log_inference_start("req_123", prompt_length=50)

    # Simulate processing
    time.sleep(0.1)

    # End performance tracking and log completion
    processing_time = logger.end_performance_tracking("inference", "req_123")
    logger.log_inference_complete(
        "req_123", token_count=200, christ_score=0.6, processing_time_ms=processing_time
    )

    # Log constraint evaluation
    logger.log_constraint_evaluation("christ_constraint", "PASS", 0.6, "req_123")

    # Log batch processing
    logger.log_batch_start(100, "batch_001")
    for i in range(10, 101, 10):
        logger.log_batch_progress(i, 100, "batch_001")
        time.sleep(0.05)
    logger.log_batch_complete(100, "batch_001", success_rate=0.95)

    # Get statistics
    stats = logger.get_log_statistics()
    print(f"Log statistics: {stats}")

    # Export audit trail
    logger.export_audit_trail("audit_trail_example.json")

    print("✅ Logging protocol example completed")


if __name__ == "__main__":
    example_usage()

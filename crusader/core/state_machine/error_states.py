"""
Crusader Combat Refrigerator - Error State Manager
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Error state management for the Crusader system.
Handles error detection, classification, recovery, and logging.
"""

import asyncio
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4


class ErrorSeverity(Enum):
    """Error severity levels."""

    INFO = auto()  # Informational, no action required
    WARNING = auto()  # Warning, monitor but continue
    ERROR = auto()  # Error, degraded operation
    CRITICAL = auto()  # Critical, immediate action required
    FATAL = auto()  # Fatal, system shutdown required


class ErrorCategory(Enum):
    """Error categories for classification."""

    HARDWARE = auto()  # Hardware failures
    SENSOR = auto()  # Sensor failures
    SOFTWARE = auto()  # Software errors
    COMMUNICATION = auto()  # Communication failures
    POWER = auto()  # Power issues
    ENVIRONMENTAL = auto()  # Environmental issues
    SECURITY = auto()  # Security violations
    PERFORMANCE = auto()  # Performance issues
    CONFIGURATION = auto()  # Configuration errors
    TIMING = auto()  # Timing/synchronization errors


class ErrorState(Enum):
    """Error states."""

    DETECTED = auto()  # Error detected
    ACKNOWLEDGED = auto()  # Error acknowledged
    ANALYZING = auto()  # Error analysis in progress
    RECOVERING = auto()  # Recovery in progress
    RESOLVED = auto()  # Error resolved
    ESCALATED = auto()  # Error escalated
    SUPPRESSED = auto()  # Error suppressed (manually)
    ARCHIVED = auto()  # Error archived


@dataclass
class ErrorDetails:
    """Detailed error information."""

    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    state: ErrorState
    source: str
    message: str
    code: Optional[str] = None
    component: Optional[str] = None
    subsystem: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    user: Optional[str] = None
    recovery_attempts: int = 0
    last_recovery_attempt: Optional[datetime] = None
    resolution_time: Optional[datetime] = None


@dataclass
class RecoveryAction:
    """Recovery action definition."""

    name: str
    description: str
    timeout_seconds: float
    required: bool
    retry_count: int = 0
    max_retries: int = 3
    completed: bool = False
    failed: bool = False
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class ErrorRecoveryStrategy(Enum):
    """Error recovery strategies."""

    AUTOMATIC = auto()  # Automatic recovery
    MANUAL = auto()  # Manual intervention required
    GRADUAL = auto()  # Gradual recovery
    IMMEDIATE = auto()  # Immediate recovery
    DEFERRED = auto()  # Deferred recovery
    ESCALATE = auto()  # Escalate to higher level


class ErrorStateManager:
    """
    Manages system errors and recovery processes.
    Provides error detection, classification, recovery, and monitoring.
    """

    # Error thresholds for automatic actions
    ERROR_THRESHOLDS = {
        ErrorSeverity.INFO: {
            "max_per_hour": 100,
            "auto_recovery": False,
            "notification": False,
        },
        ErrorSeverity.WARNING: {
            "max_per_hour": 50,
            "auto_recovery": True,
            "notification": True,
        },
        ErrorSeverity.ERROR: {
            "max_per_hour": 20,
            "auto_recovery": True,
            "notification": True,
        },
        ErrorSeverity.CRITICAL: {
            "max_per_hour": 5,
            "auto_recovery": True,
            "notification": True,
            "escalation": True,
        },
        ErrorSeverity.FATAL: {
            "max_per_hour": 1,
            "auto_recovery": False,
            "notification": True,
            "escalation": True,
            "shutdown": True,
        },
    }

    # Recovery strategies by error category
    RECOVERY_STRATEGIES = {
        ErrorCategory.HARDWARE: ErrorRecoveryStrategy.MANUAL,
        ErrorCategory.SENSOR: ErrorRecoveryStrategy.AUTOMATIC,
        ErrorCategory.SOFTWARE: ErrorRecoveryStrategy.AUTOMATIC,
        ErrorCategory.COMMUNICATION: ErrorRecoveryStrategy.GRADUAL,
        ErrorCategory.POWER: ErrorRecoveryStrategy.IMMEDIATE,
        ErrorCategory.ENVIRONMENTAL: ErrorRecoveryStrategy.MANUAL,
        ErrorCategory.SECURITY: ErrorRecoveryStrategy.ESCALATE,
        ErrorCategory.PERFORMANCE: ErrorRecoveryStrategy.GRADUAL,
        ErrorCategory.CONFIGURATION: ErrorRecoveryStrategy.AUTOMATIC,
        ErrorCategory.TIMING: ErrorRecoveryStrategy.AUTOMATIC,
    }

    def __init__(self):
        """Initialize the error state manager."""
        self.active_errors: Dict[str, ErrorDetails] = {}
        self.error_history: List[ErrorDetails] = []
        self.recovery_actions: Dict[str, List[RecoveryAction]] = {}
        self.error_lock = asyncio.Lock()

        # Error statistics
        self.error_statistics = {
            "total_errors": 0,
            "errors_by_severity": {severity: 0 for severity in ErrorSeverity},
            "errors_by_category": {category: 0 for category in ErrorCategory},
            "errors_by_component": {},
            "recovery_success_rate": 0.0,
            "average_recovery_time": 0.0,
        }

        # Error rate tracking
        self.error_rates = {
            severity: {
                "count": 0,
                "window_start": time.time(),
                "window_duration": 3600,  # 1 hour
            }
            for severity in ErrorSeverity
        }

        # Recovery templates
        self.recovery_templates = self._initialize_recovery_templates()

        # Callbacks for error notifications
        self.error_callbacks: List[callable] = []
        self.recovery_callbacks: List[callable] = []

    def _initialize_recovery_templates(
        self,
    ) -> Dict[ErrorCategory, List[RecoveryAction]]:
        """Initialize recovery action templates."""
        templates = {}

        # Hardware error recovery
        templates[ErrorCategory.HARDWARE] = [
            RecoveryAction(
                name="diagnose_hardware",
                description="Diagnose hardware failure",
                timeout_seconds=30.0,
                required=True,
            ),
            RecoveryAction(
                name="reset_hardware",
                description="Reset hardware component",
                timeout_seconds=10.0,
                required=True,
            ),
            RecoveryAction(
                name="verify_hardware",
                description="Verify hardware functionality",
                timeout_seconds=15.0,
                required=True,
            ),
        ]

        # Sensor error recovery
        templates[ErrorCategory.SENSOR] = [
            RecoveryAction(
                name="reset_sensor",
                description="Reset sensor",
                timeout_seconds=5.0,
                required=True,
            ),
            RecoveryAction(
                name="calibrate_sensor",
                description="Calibrate sensor",
                timeout_seconds=10.0,
                required=True,
            ),
            RecoveryAction(
                name="verify_sensor_data",
                description="Verify sensor data",
                timeout_seconds=5.0,
                required=True,
            ),
        ]

        # Software error recovery
        templates[ErrorCategory.SOFTWARE] = [
            RecoveryAction(
                name="restart_component",
                description="Restart software component",
                timeout_seconds=10.0,
                required=True,
            ),
            RecoveryAction(
                name="clear_cache",
                description="Clear component cache",
                timeout_seconds=5.0,
                required=True,
            ),
            RecoveryAction(
                name="verify_functionality",
                description="Verify component functionality",
                timeout_seconds=5.0,
                required=True,
            ),
        ]

        # Communication error recovery
        templates[ErrorCategory.COMMUNICATION] = [
            RecoveryAction(
                name="reset_connection",
                description="Reset communication connection",
                timeout_seconds=10.0,
                required=True,
            ),
            RecoveryAction(
                name="verify_connectivity",
                description="Verify network connectivity",
                timeout_seconds=15.0,
                required=True,
            ),
            RecoveryAction(
                name="test_communication",
                description="Test communication channel",
                timeout_seconds=10.0,
                required=True,
            ),
        ]

        # Power error recovery
        templates[ErrorCategory.POWER] = [
            RecoveryAction(
                name="check_power_supply",
                description="Check power supply status",
                timeout_seconds=5.0,
                required=True,
            ),
            RecoveryAction(
                name="stabilize_power",
                description="Stabilize power delivery",
                timeout_seconds=10.0,
                required=True,
            ),
            RecoveryAction(
                name="verify_power_quality",
                description="Verify power quality",
                timeout_seconds=5.0,
                required=True,
            ),
        ]

        return templates

    def initialize(self):
        """Initialize the error state manager."""
        print("🔧 Initializing Error State Manager...")
        self.active_errors.clear()
        self.error_history.clear()
        self.recovery_actions.clear()
        print("✅ Error State Manager initialized")

    def register_error_callback(self, callback: callable):
        """Register a callback for error notifications."""
        self.error_callbacks.append(callback)

    def register_recovery_callback(self, callback: callable):
        """Register a callback for recovery notifications."""
        self.recovery_callbacks.append(callback)

    async def handle_error(
        self,
        severity: ErrorSeverity,
        category: ErrorCategory,
        source: str,
        message: str,
        code: Optional[str] = None,
        component: Optional[str] = None,
        subsystem: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
    ) -> str:
        """
        Handle a new error.

        Returns:
            Error ID for tracking
        """
        error_id = str(uuid4())

        # Create error details
        error_details = ErrorDetails(
            error_id=error_id,
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            state=ErrorState.DETECTED,
            source=source,
            message=message,
            code=code,
            component=component,
            subsystem=subsystem,
            data=data,
            stack_trace=stack_trace,
            context=context,
            user=user,
        )

        async with self.error_lock:
            # Store error
            self.active_errors[error_id] = error_details
            self.error_history.append(error_details)

            # Update statistics
            self._update_error_statistics(error_details)

            # Check error rates
            if self._check_error_rate_threshold(severity):
                print(f"⚠️ Error rate threshold exceeded for {severity.name}")

            # Determine recovery strategy
            recovery_strategy = self.RECOVERY_STRATEGIES.get(
                category, ErrorRecoveryStrategy.AUTOMATIC
            )

            # Check if automatic recovery should be attempted
            thresholds = self.ERROR_THRESHOLDS.get(severity, {})
            if thresholds.get("auto_recovery", False):
                # Start recovery process
                asyncio.create_task(
                    self._initiate_recovery(error_id, recovery_strategy)
                )
            else:
                # Mark for manual intervention
                error_details.state = ErrorState.ESCALATED
                print(f"🛑 Error {error_id} requires manual intervention")

            # Notify callbacks
            await self._notify_error_callbacks(error_details)

        print(f"⚠️ Error detected: {severity.name} - {category.name} - {message}")
        return error_id

    def _update_error_statistics(self, error_details: ErrorDetails):
        """Update error statistics."""
        self.error_statistics["total_errors"] += 1

        # Update severity statistics
        severity = error_details.severity
        self.error_statistics["errors_by_severity"][severity] += 1

        # Update category statistics
        category = error_details.category
        self.error_statistics["errors_by_category"][category] += 1

        # Update component statistics
        component = error_details.component or "unknown"
        if component not in self.error_statistics["errors_by_component"]:
            self.error_statistics["errors_by_component"][component] = 0
        self.error_statistics["errors_by_component"][component] += 1

        # Update error rate tracking
        self._update_error_rate(severity)

    def _update_error_rate(self, severity: ErrorSeverity):
        """Update error rate tracking."""
        rate_info = self.error_rates[severity]
        current_time = time.time()

        # Reset window if expired
        if current_time - rate_info["window_start"] > rate_info["window_duration"]:
            rate_info["count"] = 0
            rate_info["window_start"] = current_time

        # Increment count
        rate_info["count"] += 1

    def _check_error_rate_threshold(self, severity: ErrorSeverity) -> bool:
        """Check if error rate exceeds threshold."""
        thresholds = self.ERROR_THRESHOLDS.get(severity, {})
        max_per_hour = thresholds.get("max_per_hour", float("inf"))

        rate_info = self.error_rates[severity]
        current_rate = rate_info["count"]

        return current_rate >= max_per_hour

    async def _initiate_recovery(self, error_id: str, strategy: ErrorRecoveryStrategy):
        """Initiate error recovery process."""
        async with self.error_lock:
            if error_id not in self.active_errors:
                return

            error_details = self.active_errors[error_id]
            error_details.state = ErrorState.ANALYZING

            # Get recovery actions based on error category
            recovery_actions = self.recovery_templates.get(error_details.category, [])

            # Store recovery actions
            self.recovery_actions[error_id] = recovery_actions.copy()

            # Update error state
            error_details.state = ErrorState.RECOVERING
            error_details.last_recovery_attempt = datetime.now()
            error_details.recovery_attempts += 1

        # Execute recovery based on strategy
        if strategy == ErrorRecoveryStrategy.AUTOMATIC:
            await self._execute_automatic_recovery(error_id)
        elif strategy == ErrorRecoveryStrategy.GRADUAL:
            await self._execute_gradual_recovery(error_id)
        elif strategy == ErrorRecoveryStrategy.IMMEDIATE:
            await self._execute_immediate_recovery(error_id)
        elif strategy == ErrorRecoveryStrategy.MANUAL:
            # Mark for manual intervention
            async with self.error_lock:
                error_details.state = ErrorState.ESCALATED
            print(f"🛑 Error {error_id} requires manual recovery")
        elif strategy == ErrorRecoveryStrategy.ESCALATE:
            # Escalate to higher level
            async with self.error_lock:
                error_details.state = ErrorState.ESCALATED
            print(f"🚨 Error {error_id} escalated")

    async def _execute_automatic_recovery(self, error_id: str):
        """Execute automatic recovery."""
        print(f"🔄 Starting automatic recovery for error {error_id}")

        recovery_success = await self._execute_recovery_actions(error_id)

        async with self.error_lock:
            if error_id not in self.active_errors:
                return

            error_details = self.active_errors[error_id]

            if recovery_success:
                error_details.state = ErrorState.RESOLVED
                error_details.resolution_time = datetime.now()
                print(f"✅ Automatic recovery successful for error {error_id}")
            else:
                error_details.state = ErrorState.ESCALATED
                print(f"❌ Automatic recovery failed for error {error_id}")

            # Update recovery statistics
            self._update_recovery_statistics(recovery_success, error_details)

            # Notify recovery callbacks
            await self._notify_recovery_callbacks(error_details, recovery_success)

    async def _execute_gradual_recovery(self, error_id: str):
        """Execute gradual recovery with progressive steps."""
        print(f"🔄 Starting gradual recovery for error {error_id}")

        async with self.error_lock:
            if error_id not in self.active_errors:
                return

            error_details = self.active_errors[error_id]
            recovery_actions = self.recovery_actions.get(error_id, [])

        # Execute actions gradually with delays
        for action in recovery_actions:
            print(f"  ↪️ Executing: {action.name}")

            # Simulate action execution
            action.start_time = time.time()
            await asyncio.sleep(1.0)  # Simulated action
            action.end_time = time.time()
            action.completed = True

            # Check if we should continue
            if not await self._should_continue_recovery(error_id):
                break

        # Mark as resolved if all actions completed
        all_completed = all(action.completed for action in recovery_actions)

        async with self.error_lock:
            if error_id not in self.active_errors:
                return

            error_details = self.active_errors[error_id]

            if all_completed:
                error_details.state = ErrorState.RESOLVED
                error_details.resolution_time = datetime.now()
                print(f"✅ Gradual recovery successful for error {error_id}")
            else:
                print(f"⚠️ Gradual recovery incomplete for error {error_id}")

        return all_completed

    async def _should_continue_recovery(self, error_id: str) -> bool:
        """Check if we should continue with gradual recovery."""
        if error_id not in self.active_errors:
            return False

        error_details = self.active_errors[error_id]

        # Check timeout
        if error_details.recovery_start_time:
            elapsed = (
                datetime.now() - error_details.recovery_start_time
            ).total_seconds()
            if elapsed > self.config.get("max_recovery_time_seconds", 300):
                return False

        # Check if error is still active
        return error_details.state == ErrorState.RECOVERING

    # Statistics and reporting
    def get_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        total_errors = len(self.error_history)
        active_errors = len(self.active_errors)
        resolved_errors = sum(
            1 for e in self.error_history if e.state == ErrorState.RESOLVED
        )

        # Count by severity
        severity_counts = {severity.name: 0 for severity in ErrorSeverity}
        for error in self.error_history:
            severity_counts[error.severity.name] += 1

        # Count by state
        state_counts = {state.name: 0 for state in ErrorState}
        for error in self.error_history:
            state_counts[error.state.name] += 1

        # Calculate average resolution time
        resolution_times = []
        for error in self.error_history:
            if error.resolution_time and error.detection_time:
                resolution_time = (
                    error.resolution_time - error.detection_time
                ).total_seconds()
                resolution_times.append(resolution_time)

        avg_resolution_time = (
            statistics.mean(resolution_times) if resolution_times else 0.0
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "total_errors": total_errors,
            "active_errors": active_errors,
            "resolved_errors": resolved_errors,
            "severity_counts": severity_counts,
            "state_counts": state_counts,
            "average_resolution_time_seconds": avg_resolution_time,
            "recovery_success_rate": self.recovery_success_rate,
            "last_error_time": self.last_error_time.isoformat()
            if self.last_error_time
            else None,
        }

    def get_error_report(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed report for a specific error."""
        if error_id not in self.active_errors and error_id not in [
            e.error_id for e in self.error_history
        ]:
            return None

        # Find error in history
        error_details = None
        for error in self.error_history:
            if error.error_id == error_id:
                error_details = error
                break

        if not error_details:
            return None

        report = asdict(error_details)
        report["timestamp"] = error_details.timestamp.isoformat()
        report["detection_time"] = (
            error_details.detection_time.isoformat()
            if error_details.detection_time
            else None
        )
        report["resolution_time"] = (
            error_details.resolution_time.isoformat()
            if error_details.resolution_time
            else None
        )
        report["recovery_start_time"] = (
            error_details.recovery_start_time.isoformat()
            if error_details.recovery_start_time
            else None
        )
        report["severity"] = error_details.severity.name
        report["state"] = error_details.state.name

        # Add recovery actions if available
        if error_details.recovery_actions:
            report["recovery_actions"] = [
                {
                    "action": action.action,
                    "completed": action.completed,
                    "result": action.result,
                    "timestamp": action.timestamp.isoformat()
                    if action.timestamp
                    else None,
                }
                for action in error_details.recovery_actions
            ]

        return report

    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get system health summary based on error state."""
        stats = self.get_statistics()

        # Determine overall health
        if stats["active_errors"] > 0:
            # Check if any active errors are CRITICAL
            critical_active = any(
                e.severity == ErrorSeverity.CRITICAL
                for e in self.active_errors.values()
            )
            if critical_active:
                health_status = "CRITICAL"
            else:
                health_status = "DEGRADED"
        elif stats["total_errors"] == 0:
            health_status = "EXCELLENT"
        else:
            health_status = "HEALTHY"

        # Calculate health score (0-100)
        base_score = 100

        # Deduct for active errors
        base_score -= stats["active_errors"] * 10

        # Deduct for recent errors (last hour)
        recent_errors = sum(
            1
            for e in self.error_history
            if e.timestamp > datetime.now() - timedelta(hours=1)
        )
        base_score -= recent_errors * 5

        # Ensure score is within bounds
        health_score = max(0, min(100, base_score))

        return {
            "health_status": health_status,
            "health_score": health_score,
            "error_statistics": stats,
            "recommendations": self._generate_health_recommendations(stats),
        }

    def _generate_health_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate health recommendations based on error statistics."""
        recommendations = []

        if stats["active_errors"] > 0:
            recommendations.append(f"Resolve {stats['active_errors']} active error(s)")

        if stats["average_resolution_time_seconds"] > 60:
            recommendations.append("Improve error resolution time")

        if self.recovery_success_rate < 0.8:
            recommendations.append("Improve error recovery success rate")

        # Check for recurring errors
        error_messages = [e.error_message for e in self.error_history[-20:]]
        from collections import Counter

        message_counts = Counter(error_messages)
        recurring_errors = [msg for msg, count in message_counts.items() if count > 3]

        if recurring_errors:
            recommendations.append(
                f"Address recurring errors: {', '.join(recurring_errors[:3])}"
            )

        return recommendations

    async def cleanup(self):
        """Clean up error state manager."""
        self.running = False

        # Clear active errors
        self.active_errors.clear()

        # Clear history (keep last 1000 errors)
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]

        print("✅ Error State Manager cleaned up")

    # Convenience methods
    async def handle_error_with_recovery(
        self,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        component: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        recovery_actions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Handle error with automatic recovery."""
        error_id = await self.register_error(
            error_message=error_message,
            severity=severity,
            component=component,
            details=details,
        )

        # Start recovery if actions provided
        if recovery_actions:
            await self.start_gradual_recovery(error_id, recovery_actions)

        return error_id

    async def monitor_and_report(self) -> Dict[str, Any]:
        """Monitor errors and generate report."""
        stats = self.get_statistics()
        health = self.get_system_health_summary()

        return {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "health_summary": health,
            "active_errors": [
                self.get_error_report(error_id)
                for error_id in self.active_errors.keys()
            ],
            "recent_errors": [
                self.get_error_report(e.error_id) for e in self.error_history[-10:]
            ],
        }


# Convenience function for quick error handling
async def handle_error(
    error_message: str,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    component: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> str:
    """Quick error handling."""
    manager = ErrorStateManager()
    await manager.initialize()

    error_id = await manager.register_error(
        error_message=error_message,
        severity=severity,
        component=component,
        details=details,
    )

    await manager.cleanup()
    return error_id


if __name__ == "__main__":
    # Test the error state manager
    import asyncio

    async def test_error_manager():
        """Test error state manager."""
        print("Testing Error State Manager...")

        manager = ErrorStateManager()
        await manager.initialize()

        try:
            # Register some errors
            error1 = await manager.register_error(
                error_message="Test error 1",
                severity=ErrorSeverity.LOW,
                component="test",
                details={"test": True},
            )
            print(f"Registered error: {error1}")

            error2 = await manager.register_error(
                error_message="Test error 2",
                severity=ErrorSeverity.MEDIUM,
                component="test",
            )
            print(f"Registered error: {error2}")

            # Get statistics
            stats = manager.get_statistics()
            print(f"Statistics: {stats}")

            # Resolve an error
            success = await manager.resolve_error(error1, "Test resolution")
            print(f"Resolved error {error1}: {success}")

            # Get updated statistics
            stats = manager.get_statistics()
            print(f"Updated statistics: {stats}")

            # Get health summary
            health = manager.get_system_health_summary()
            print(f"Health summary: {health}")

        finally:
            await manager.cleanup()
            print("✅ Test completed")

    asyncio.run(test_error_manager())

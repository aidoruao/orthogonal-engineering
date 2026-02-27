"""
Crusader Combat Refrigerator - Transition Management
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Transition management system for mode changes and system state transitions.
Provides validation, execution, and monitoring of all system transitions.
"""

import asyncio
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from ..constants import SystemMode
from .mode import ModeTransitionReason


class TransitionState(Enum):
    """States of a transition."""

    PENDING = auto()
    VALIDATING = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    TIMED_OUT = auto()


class TransitionStatus(Enum):
    """Status of a transition result."""

    SUCCESS = auto()
    FAILURE = auto()
    PARTIAL_SUCCESS = auto()
    VALIDATION_FAILED = auto()
    EXECUTION_FAILED = auto()
    TIMEOUT = auto()
    CANCELLED = auto()


class TransitionType(Enum):
    """Types of transitions."""

    MODE_CHANGE = auto()
    SYSTEM_STARTUP = auto()
    SYSTEM_SHUTDOWN = auto()
    ERROR_RECOVERY = auto()
    MAINTENANCE = auto()
    EMERGENCY = auto()
    SCHEDULED = auto()
    MANUAL = auto()


@dataclass
class TransitionResult:
    """Result of a transition operation."""

    success: bool
    transition_id: str
    status: TransitionStatus
    message: str
    from_mode: SystemMode
    to_mode: SystemMode
    duration_seconds: float
    timestamp: datetime
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "transition_id": self.transition_id,
            "status": self.status.name,
            "message": self.message,
            "from_mode": self.from_mode.value,
            "to_mode": self.to_mode.value,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class TransitionStep:
    """Individual step in a transition."""

    name: str
    description: str
    timeout_seconds: float
    action: Optional[callable] = None
    required: bool = True
    dependencies: List[str] = None
    retry_count: int = 0
    completed: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class Transition:
    """Complete transition definition."""

    transition_id: str
    transition_type: TransitionType
    from_mode: SystemMode
    to_mode: SystemMode
    reason: ModeTransitionReason
    steps: List[TransitionStep]
    state: TransitionState = TransitionState.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    rollback_steps: List[TransitionStep] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.rollback_steps is None:
            self.rollback_steps = []


class TransitionValidator:
    """Validates transitions before execution."""

    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()

    def _initialize_validation_rules(
        self,
    ) -> Dict[Tuple[SystemMode, SystemMode], List[callable]]:
        """Initialize validation rules for mode transitions."""
        rules = {}

        # Active -> Standby
        rules[(SystemMode.ACTIVE, SystemMode.STANDBY)] = [
            self._validate_no_active_warfare,
            self._validate_system_health,
            self._validate_power_state,
        ]

        # Standby -> Active
        rules[(SystemMode.STANDBY, SystemMode.ACTIVE)] = [
            self._validate_system_health,
            self._validate_sensor_availability,
            self._validate_warfare_systems,
        ]

        # Any -> Safe
        for from_mode in SystemMode:
            if from_mode != SystemMode.SAFE:
                rules[(from_mode, SystemMode.SAFE)] = [
                    self._validate_emergency_conditions,
                ]

        # Safe -> Service
        rules[(SystemMode.SAFE, SystemMode.SERVICE)] = [
            self._validate_error_resolution,
            self._validate_system_stability,
        ]

        # Service -> Active
        rules[(SystemMode.SERVICE, SystemMode.ACTIVE)] = [
            self._validate_maintenance_completion,
            self._validate_system_health,
            self._validate_all_systems,
        ]

        # Any -> Shutdown
        for from_mode in SystemMode:
            if from_mode != SystemMode.SHUTDOWN:
                rules[(from_mode, SystemMode.SHUTDOWN)] = [
                    self._validate_safe_shutdown,
                ]

        return rules

    async def validate_transition(
        self,
        from_mode: SystemMode,
        to_mode: SystemMode,
        reason: ModeTransitionReason,
        context: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Validate a transition.

        Returns:
            Tuple of (is_valid, list_of_validation_errors)
        """
        validation_key = (from_mode, to_mode)
        validation_rules = self.validation_rules.get(validation_key, [])

        errors = []

        for rule in validation_rules:
            try:
                is_valid, error_message = await rule(context)
                if not is_valid:
                    errors.append(error_message)
            except Exception as e:
                errors.append(f"Validation rule failed: {e}")

        # Special validations based on reason
        if reason == ModeTransitionReason.EMERGENCY_STOP:
            # Emergency stops bypass most validations
            if errors:
                print(f"⚠️ Emergency stop with validation errors: {errors}")
                errors = []  # Clear errors for emergency

        return len(errors) == 0, errors

    async def _validate_no_active_warfare(
        self, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validate no warfare systems are active."""
        active_warfare = context.get("active_warfare_systems", [])
        if active_warfare:
            return False, f"Warfare systems active: {active_warfare}"
        return True, ""

    async def _validate_system_health(
        self, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validate system health."""
        health_status = context.get("system_health", {})
        if health_status.get("overall_health") != "healthy":
            return False, f"System health check failed: {health_status}"
        return True, ""

    async def _validate_power_state(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate power state."""
        power_state = context.get("power_state", {})
        if power_state.get("battery_level", 100) < 20:
            return False, f"Low battery: {power_state.get('battery_level')}%"
        return True, ""

    async def _validate_sensor_availability(
        self, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validate sensor availability."""
        sensors = context.get("sensor_status", {})
        critical_sensors = ["temperature", "humidity", "motion"]

        unavailable = []
        for sensor in critical_sensors:
            if not sensors.get(sensor, {}).get("available", False):
                unavailable.append(sensor)

        if unavailable:
            return False, f"Critical sensors unavailable: {unavailable}"
        return True, ""

    async def _validate_warfare_systems(
        self, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validate warfare systems."""
        warfare_status = context.get("warfare_status", {})

        systems = ["spore_deployment", "uv_sterilization", "air_curtain"]
        failed = []

        for system in systems:
            status = warfare_status.get(system, {})
            if not status.get("operational", False):
                failed.append(system)

        if failed:
            return False, f"Warfare systems failed: {failed}"
        return True, ""

    async def _validate_emergency_conditions(
        self, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validate emergency conditions."""
        # Emergency transitions are always valid
        return True, ""

    async def _validate_error_resolution(
        self, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validate errors have been resolved."""
        error_count = context.get("error_count", 0)
        if error_count > 0:
            return False, f"Unresolved errors: {error_count}"
        return True, ""

    async def _validate_system_stability(
        self, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validate system stability."""
        stability = context.get("system_stability", {})
        if stability.get("stability_score", 0) < 80:
            return False, f"System unstable: {stability.get('stability_score')}%"
        return True, ""

    async def _validate_maintenance_completion(
        self, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validate maintenance completion."""
        maintenance = context.get("maintenance_status", {})
        if not maintenance.get("completed", False):
            return False, "Maintenance not completed"
        return True, ""

    async def _validate_all_systems(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate all systems."""
        all_systems = context.get("all_systems_status", {})

        critical_systems = ["core", "warfare", "monitoring", "interface", "hardware"]

        failed = []
        for system in critical_systems:
            status = all_systems.get(system, {})
            if not status.get("operational", False):
                failed.append(system)

        if failed:
            return False, f"Critical systems failed: {failed}"
        return True, ""

    async def _validate_safe_shutdown(
        self, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validate safe shutdown conditions."""
        # Check if any critical processes are running
        active_processes = context.get("active_processes", [])
        critical_processes = ["warfare_control", "sensor_monitoring"]

        running = []
        for process in critical_processes:
            if process in active_processes:
                running.append(process)

        if running:
            return False, f"Cannot shutdown with processes running: {running}"
        return True, ""


class TransitionManager:
    """
    Manages complex transitions between system states.
    Handles sequencing, validation, rollback, and monitoring.
    """

    def __init__(self):
        """Initialize the transition manager."""
        self.validator = TransitionValidator()
        self.active_transitions: Dict[str, Transition] = {}
        self.transition_history: List[Transition] = []
        self.transition_lock = asyncio.Lock()
        self.max_concurrent_transitions = 3

        # Transition templates
        self.transition_templates = self._initialize_templates()

    def _initialize_templates(
        self,
    ) -> Dict[Tuple[SystemMode, SystemMode], List[TransitionStep]]:
        """Initialize transition step templates."""
        templates = {}

        # Shutdown -> Active (System Startup)
        templates[(SystemMode.SHUTDOWN, SystemMode.ACTIVE)] = [
            TransitionStep(
                name="initialize_core",
                description="Initialize core systems",
                timeout_seconds=10.0,
                required=True,
            ),
            TransitionStep(
                name="initialize_monitoring",
                description="Initialize monitoring systems",
                timeout_seconds=5.0,
                required=True,
            ),
            TransitionStep(
                name="initialize_warfare",
                description="Initialize warfare systems",
                timeout_seconds=15.0,
                required=True,
            ),
            TransitionStep(
                name="initialize_interface",
                description="Initialize interface systems",
                timeout_seconds=5.0,
                required=True,
            ),
            TransitionStep(
                name="system_health_check",
                description="Perform system health check",
                timeout_seconds=3.0,
                required=True,
            ),
        ]

        # Active -> Standby
        templates[(SystemMode.ACTIVE, SystemMode.STANDBY)] = [
            TransitionStep(
                name="stop_warfare_systems",
                description="Safely stop warfare systems",
                timeout_seconds=5.0,
                required=True,
            ),
            TransitionStep(
                name="reduce_power_consumption",
                description="Reduce power consumption",
                timeout_seconds=2.0,
                required=True,
            ),
            TransitionStep(
                name="enter_low_power_mode",
                description="Enter low power mode",
                timeout_seconds=1.0,
                required=True,
            ),
        ]

        # Standby -> Active
        templates[(SystemMode.STANDBY, SystemMode.ACTIVE)] = [
            TransitionStep(
                name="exit_low_power_mode",
                description="Exit low power mode",
                timeout_seconds=1.0,
                required=True,
            ),
            TransitionStep(
                name="initialize_warfare_systems",
                description="Initialize warfare systems",
                timeout_seconds=10.0,
                required=True,
            ),
            TransitionStep(
                name="verify_system_readiness",
                description="Verify system readiness",
                timeout_seconds=3.0,
                required=True,
            ),
        ]

        # Any -> Safe (Emergency)
        emergency_steps = [
            TransitionStep(
                name="immediate_stop",
                description="Immediately stop all systems",
                timeout_seconds=1.0,
                required=True,
            ),
            TransitionStep(
                name="secure_power",
                description="Secure power systems",
                timeout_seconds=2.0,
                required=True,
            ),
            TransitionStep(
                name="enter_safe_state",
                description="Enter safe state",
                timeout_seconds=1.0,
                required=True,
            ),
        ]

        for from_mode in SystemMode:
            if from_mode != SystemMode.SAFE:
                templates[(from_mode, SystemMode.SAFE)] = emergency_steps

        # Safe -> Service
        templates[(SystemMode.SAFE, SystemMode.SERVICE)] = [
            TransitionStep(
                name="diagnose_errors",
                description="Diagnose system errors",
                timeout_seconds=5.0,
                required=True,
            ),
            TransitionStep(
                name="enable_maintenance",
                description="Enable maintenance mode",
                timeout_seconds=2.0,
                required=True,
            ),
            TransitionStep(
                name="verify_safety",
                description="Verify safety systems",
                timeout_seconds=3.0,
                required=True,
            ),
        ]

        # Service -> Active
        templates[(SystemMode.SERVICE, SystemMode.ACTIVE)] = [
            TransitionStep(
                name="complete_maintenance",
                description="Complete maintenance tasks",
                timeout_seconds=10.0,
                required=True,
            ),
            TransitionStep(
                name="system_verification",
                description="Verify system functionality",
                timeout_seconds=5.0,
                required=True,
            ),
            TransitionStep(
                name="reactivate_systems",
                description="Reactivate all systems",
                timeout_seconds=5.0,
                required=True,
            ),
        ]

        # Any -> Shutdown
        shutdown_steps = [
            TransitionStep(
                name="graceful_shutdown",
                description="Gracefully shutdown systems",
                timeout_seconds=10.0,
                required=True,
            ),
            TransitionStep(
                name="save_state",
                description="Save system state",
                timeout_seconds=5.0,
                required=True,
            ),
            TransitionStep(
                name="power_down",
                description="Power down systems",
                timeout_seconds=3.0,
                required=True,
            ),
        ]

        for from_mode in SystemMode:
            if from_mode != SystemMode.SHUTDOWN:
                templates[(from_mode, SystemMode.SHUTDOWN)] = shutdown_steps

        return templates

    def initialize(self):
        """Initialize the transition manager."""
        print("🔧 Initializing Transition Manager...")
        self.active_transitions.clear()
        self.transition_history.clear()
        print("✅ Transition Manager initialized")

    async def execute_transition(
        self,
        from_mode: SystemMode,
        to_mode: SystemMode,
        reason: ModeTransitionReason,
        context: Dict[str, Any],
        user: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Execute a transition between modes.

        Returns:
            Tuple of (success, message, transition_id)
        """
        transition_id = str(uuid4())

        # Check if we can start a new transition
        if not await self._can_start_transition():
            return False, "Maximum concurrent transitions reached", None

        # Validate the transition
        is_valid, validation_errors = await self.validator.validate_transition(
            from_mode, to_mode, reason, context
        )

        if not is_valid:
            error_msg = f"Transition validation failed: {validation_errors}"
            return False, error_msg, None

        # Create transition
        transition_type = self._determine_transition_type(reason)
        steps = self._get_transition_steps(from_mode, to_mode, reason)

        transition = Transition(
            transition_id=transition_id,
            transition_type=transition_type,
            from_mode=from_mode,
            to_mode=to_mode,
            reason=reason,
            steps=steps,
            user=user,
            details=details,
            rollback_steps=self._create_rollback_steps(from_mode, to_mode),
        )

        # Store transition
        self.active_transitions[transition_id] = transition

        # Execute transition asynchronously
        asyncio.create_task(self._execute_transition_async(transition))

        return True, f"Transition {transition_id} started", transition_id

    async def _can_start_transition(self) -> bool:
        """Check if a new transition can be started."""
        async with self.transition_lock:
            active_count = len(
                [
                    t
                    for t in self.active_transitions.values()
                    if t.state
                    in [
                        TransitionState.PENDING,
                        TransitionState.VALIDATING,
                        TransitionState.EXECUTING,
                    ]
                ]
            )
            return active_count < self.max_concurrent_transitions

    def _determine_transition_type(
        self, reason: ModeTransitionReason
    ) -> TransitionType:
        """Determine transition type based on reason."""
        if reason == ModeTransitionReason.EMERGENCY_STOP:
            return TransitionType.EMERGENCY
        elif reason == ModeTransitionReason.SYSTEM_STARTUP:
            return TransitionType.SYSTEM_STARTUP
        elif reason == ModeTransitionReason.SYSTEM_SHUTDOWN:
            return TransitionType.SYSTEM_SHUTDOWN
        elif reason == ModeTransitionReason.MAINTENANCE_REQUIRED:
            return TransitionType.MAINTENANCE
        elif reason == ModeTransitionReason.ERROR_DETECTED:
            return TransitionType.ERROR_RECOVERY
        else:
            return TransitionType.NORMAL

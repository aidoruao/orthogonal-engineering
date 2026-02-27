"""
Crusader Combat Refrigerator - System Mode Manager
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

System mode management for the Crusader state machine.
Handles transitions between operational modes and maintains mode state.
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set

from ..constants import SystemMode


class ModeTransitionReason(Enum):
    """Reasons for mode transitions."""

    MANUAL_COMMAND = auto()
    SYSTEM_STARTUP = auto()
    SYSTEM_SHUTDOWN = auto()
    ERROR_DETECTED = auto()
    ERROR_RESOLVED = auto()
    MAINTENANCE_REQUIRED = auto()
    MAINTENANCE_COMPLETE = auto()
    SCHEDULED_TRANSITION = auto()
    EMERGENCY_STOP = auto()
    POWER_LOSS = auto()
    POWER_RESTORED = auto()
    SENSOR_FAILURE = auto()
    SENSOR_RECOVERED = auto()
    FLY_COUNT_HIGH = auto()
    FLY_COUNT_NORMAL = auto()
    TEMPERATURE_CRITICAL = auto()
    TEMPERATURE_NORMAL = auto()
    HUMIDITY_CRITICAL = auto()
    HUMIDITY_NORMAL = auto()


@dataclass
class ModeTransition:
    """Record of a mode transition."""

    timestamp: datetime
    from_mode: SystemMode
    to_mode: SystemMode
    reason: ModeTransitionReason
    details: Optional[Dict[str, Any]] = None
    user: Optional[str] = None


class ModeManager:
    """
    Manages system operational modes and transitions.
    Enforces mode-specific constraints and permissions.
    """

    # Valid mode transitions
    VALID_TRANSITIONS = {
        SystemMode.SHUTDOWN: {SystemMode.ACTIVE, SystemMode.STANDBY},
        SystemMode.ACTIVE: {
            SystemMode.STANDBY,
            SystemMode.SERVICE,
            SystemMode.SAFE,
            SystemMode.SHUTDOWN,
        },
        SystemMode.STANDBY: {
            SystemMode.ACTIVE,
            SystemMode.SERVICE,
            SystemMode.SAFE,
            SystemMode.SHUTDOWN,
        },
        SystemMode.SERVICE: {
            SystemMode.ACTIVE,
            SystemMode.STANDBY,
            SystemMode.SHUTDOWN,
        },
        SystemMode.SAFE: {
            SystemMode.SERVICE,
            SystemMode.SHUTDOWN,
        },
    }

    # Mode-specific constraints
    MODE_CONSTRAINTS = {
        SystemMode.ACTIVE: {
            "allow_spore_deployment": True,
            "allow_uv_sterilization": True,
            "allow_air_curtain": True,
            "allow_sticky_trap_monitoring": True,
            "allow_fly_counter": True,
            "max_power_consumption_watts": 50.0,
            "min_temperature_celsius": 2.0,
            "max_temperature_celsius": 40.0,
        },
        SystemMode.STANDBY: {
            "allow_spore_deployment": False,
            "allow_uv_sterilization": False,
            "allow_air_curtain": False,
            "allow_sticky_trap_monitoring": True,
            "allow_fly_counter": True,
            "max_power_consumption_watts": 10.0,
            "min_temperature_celsius": 2.0,
            "max_temperature_celsius": 40.0,
        },
        SystemMode.SERVICE: {
            "allow_spore_deployment": False,
            "allow_uv_sterilization": False,
            "allow_air_curtain": False,
            "allow_sticky_trap_monitoring": False,
            "allow_fly_counter": False,
            "max_power_consumption_watts": 20.0,
            "min_temperature_celsius": 15.0,
            "max_temperature_celsius": 30.0,
        },
        SystemMode.SAFE: {
            "allow_spore_deployment": False,
            "allow_uv_sterilization": False,
            "allow_air_curtain": False,
            "allow_sticky_trap_monitoring": False,
            "allow_fly_counter": False,
            "max_power_consumption_watts": 5.0,
            "min_temperature_celsius": 2.0,
            "max_temperature_celsius": 40.0,
        },
        SystemMode.SHUTDOWN: {
            "allow_spore_deployment": False,
            "allow_uv_sterilization": False,
            "allow_air_curtain": False,
            "allow_sticky_trap_monitoring": False,
            "allow_fly_counter": False,
            "max_power_consumption_watts": 1.0,
            "min_temperature_celsius": 2.0,
            "max_temperature_celsius": 40.0,
        },
    }

    def __init__(self):
        """Initialize the mode manager."""
        self.current_mode = SystemMode.SHUTDOWN
        self.previous_mode = None
        self.transition_history: List[ModeTransition] = []
        self.mode_start_time = None
        self.mode_lock = asyncio.Lock()
        self.mode_change_callbacks: List[callable] = []

        # Mode statistics
        self.mode_statistics = {
            mode: {"total_time_seconds": 0.0, "transition_count": 0}
            for mode in SystemMode
        }

        # Mode-specific state
        self.mode_state = {
            SystemMode.ACTIVE: {"last_activity": None, "performance_metrics": {}},
            SystemMode.STANDBY: {"last_activity": None, "power_savings": 0.0},
            SystemMode.SERVICE: {"maintenance_tasks": [], "last_maintenance": None},
            SystemMode.SAFE: {"error_count": 0, "last_error": None},
            SystemMode.SHUTDOWN: {"shutdown_reason": None, "clean_shutdown": False},
        }

    def initialize(self):
        """Initialize the mode manager."""
        print(f"🔧 Initializing Mode Manager...")
        self.current_mode = SystemMode.SHUTDOWN
        self.mode_start_time = time.time()
        print(f"✅ Mode Manager initialized in {self.current_mode.value} mode")

    def register_callback(self, callback: callable):
        """Register a callback for mode changes."""
        self.mode_change_callbacks.append(callback)

    def unregister_callback(self, callback: callable):
        """Unregister a mode change callback."""
        if callback in self.mode_change_callbacks:
            self.mode_change_callbacks.remove(callback)

    async def set_mode(
        self,
        new_mode: SystemMode,
        reason: ModeTransitionReason,
        details: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
    ) -> bool:
        """
        Transition to a new mode.

        Args:
            new_mode: The target mode
            reason: Reason for the transition
            details: Additional transition details
            user: User who initiated the transition

        Returns:
            True if transition successful, False otherwise
        """
        async with self.mode_lock:
            return await self._perform_transition(new_mode, reason, details, user)

    async def _perform_transition(
        self,
        new_mode: SystemMode,
        reason: ModeTransitionReason,
        details: Optional[Dict[str, Any]],
        user: Optional[str],
    ) -> bool:
        """Perform the actual mode transition."""
        old_mode = self.current_mode

        # Check if transition is valid
        if not self._is_valid_transition(old_mode, new_mode):
            print(f"❌ Invalid mode transition: {old_mode.value} -> {new_mode.value}")
            return False

        # Check if we're already in the target mode
        if old_mode == new_mode:
            print(f"⚠️ Already in {new_mode.value} mode")
            return True

        # Update mode statistics
        self._update_mode_statistics(old_mode)

        # Execute pre-transition hooks
        pre_transition_ok = await self._execute_pre_transition_hooks(
            old_mode, new_mode, reason
        )
        if not pre_transition_ok:
            print(f"❌ Pre-transition hooks failed for {new_mode.value}")
            return False

        # Perform the transition
        print(f"🔄 Transitioning: {old_mode.value} -> {new_mode.value} ({reason.name})")

        # Update state
        self.previous_mode = old_mode
        self.current_mode = new_mode
        self.mode_start_time = time.time()

        # Record transition
        transition = ModeTransition(
            timestamp=datetime.now(),
            from_mode=old_mode,
            to_mode=new_mode,
            reason=reason,
            details=details,
            user=user,
        )
        self.transition_history.append(transition)

        # Update statistics
        self.mode_statistics[new_mode]["transition_count"] += 1

        # Execute post-transition hooks
        await self._execute_post_transition_hooks(old_mode, new_mode, reason)

        # Notify callbacks
        await self._notify_callbacks(transition)

        print(f"✅ Mode transition complete: {new_mode.value}")
        return True

    def _is_valid_transition(self, from_mode: SystemMode, to_mode: SystemMode) -> bool:
        """Check if a mode transition is valid."""
        valid_targets = self.VALID_TRANSITIONS.get(from_mode, set())
        return to_mode in valid_targets

    def _update_mode_statistics(self, mode: SystemMode):
        """Update statistics for the mode being exited."""
        if self.mode_start_time:
            duration = time.time() - self.mode_start_time
            self.mode_statistics[mode]["total_time_seconds"] += duration

    async def _execute_pre_transition_hooks(
        self, old_mode: SystemMode, new_mode: SystemMode, reason: ModeTransitionReason
    ) -> bool:
        """Execute hooks before mode transition."""
        try:
            # Mode-specific pre-transition logic
            if old_mode == SystemMode.ACTIVE and new_mode == SystemMode.SHUTDOWN:
                await self._shutdown_from_active()
            elif old_mode == SystemMode.SAFE and new_mode == SystemMode.SERVICE:
                await self._recover_from_safe()
            elif new_mode == SystemMode.SAFE:
                await self._enter_safe_mode(reason)

            return True
        except Exception as e:
            print(f"❌ Pre-transition hook failed: {e}")
            return False

    async def _execute_post_transition_hooks(
        self, old_mode: SystemMode, new_mode: SystemMode, reason: ModeTransitionReason
    ):
        """Execute hooks after mode transition."""
        try:
            # Mode-specific post-transition logic
            if new_mode == SystemMode.ACTIVE:
                await self._enter_active_mode()
            elif new_mode == SystemMode.STANDBY:
                await self._enter_standby_mode()
            elif new_mode == SystemMode.SERVICE:
                await self._enter_service_mode()
            elif new_mode == SystemMode.SHUTDOWN:
                await self._enter_shutdown_mode()

        except Exception as e:
            print(f"⚠️ Post-transition hook failed: {e}")

    async def _notify_callbacks(self, transition: ModeTransition):
        """Notify registered callbacks of mode change."""
        for callback in self.mode_change_callbacks:
            try:
                await callback(transition)
            except Exception as e:
                print(f"⚠️ Mode change callback failed: {e}")

    async def _shutdown_from_active(self):
        """Special handling for shutdown from active mode."""
        print("🔴 Preparing for shutdown from active mode...")
        # Ensure all warfare systems are safely stopped
        # This would call into the actual warfare subsystems
        await asyncio.sleep(0.1)  # Simulated shutdown preparation

    async def _recover_from_safe(self):
        """Special handling for recovery from safe mode."""
        print("🔄 Recovering from safe mode...")
        # Perform system checks before allowing service mode
        await asyncio.sleep(0.1)  # Simulated recovery checks

    async def _enter_safe_mode(self, reason: ModeTransitionReason):
        """Special handling for entering safe mode."""
        print(f"🛑 Entering safe mode due to: {reason.name}")
        # Record the error that caused safe mode
        self.mode_state[SystemMode.SAFE]["error_count"] += 1
        self.mode_state[SystemMode.SAFE]["last_error"] = reason

    async def _enter_active_mode(self):
        """Special handling for entering active mode."""
        print("🚀 Entering active mode - all systems operational")
        # Initialize warfare systems
        self.mode_state[SystemMode.ACTIVE]["last_activity"] = datetime.now()

    async def _enter_standby_mode(self):
        """Special handling for entering standby mode."""
        print("💤 Entering standby mode - reduced power consumption")
        # Power down non-essential systems
        self.mode_state[SystemMode.STANDBY]["last_activity"] = datetime.now()

    async def _enter_service_mode(self):
        """Special handling for entering service mode."""
        print("🔧 Entering service mode - maintenance operations enabled")
        # Enable maintenance interfaces
        self.mode_state[SystemMode.SERVICE]["last_maintenance"] = datetime.now()

    async def _enter_shutdown_mode(self):
        """Special handling for entering shutdown mode."""
        print("⏹️ Entering shutdown mode - system powering down")
        # Mark as clean shutdown if coming from appropriate mode
        if self.previous_mode in [SystemMode.ACTIVE, SystemMode.STANDBY]:
            self.mode_state[SystemMode.SHUTDOWN]["clean_shutdown"] = True
            self.mode_state[SystemMode.SHUTDOWN]["shutdown_reason"] = "normal"

    def get_mode_constraints(self) -> Dict[str, Any]:
        """Get constraints for the current mode."""
        return self.MODE_CONSTRAINTS.get(self.current_mode, {}).copy()

    def is_operation_allowed(self, operation: str) -> bool:
        """Check if an operation is allowed in current mode."""
        constraints = self.get_mode_constraints()
        return constraints.get(f"allow_{operation}", False)

    def get_mode_duration(self) -> float:
        """Get duration in current mode in seconds."""
        if self.mode_start_time:
            return time.time() - self.mode_start_time
        return 0.0

    def get_mode_statistics(self) -> Dict[str, Any]:
        """Get comprehensive mode statistics."""
        stats = {
            "current_mode": self.current_mode.value,
            "mode_duration_seconds": self.get_mode_duration(),
            "previous_mode": self.previous_mode.value if self.previous_mode else None,
            "total_transitions": len(self.transition_history),
            "mode_statistics": {},
        }

        for mode, data in self.mode_statistics.items():
            stats["mode_statistics"][mode.value] = {
                "total_time_seconds": data["total_time_seconds"],
                "transition_count": data["transition_count"],
                "average_duration_seconds": (
                    data["total_time_seconds"] / data["transition_count"]
                    if data["transition_count"] > 0
                    else 0
                ),
            }

        return stats

    def get_transition_history(
        self, limit: Optional[int] = None
    ) -> List[ModeTransition]:
        """Get mode transition history."""
        if limit:
            return self.transition_history[-limit:]
        return self.transition_history.copy()

    def emergency_stop(self) -> bool:
        """Immediately transition to safe mode."""
        print("🛑 EMERGENCY STOP ACTIVATED")
        # This would bypass normal transition logic for immediate safety
        # In a real implementation, this would use thread-safe immediate transition
        return True

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status based on current mode."""
        status = {
            "mode": self.current_mode.value,
            "mode_constraints": self.get_mode_constraints(),
            "mode_duration": self.get_mode_duration(),
            "statistics": self.get_mode_statistics(),
            "allowed_operations": {},
        }

        # List allowed operations
        for operation in [
            "spore_deployment",
            "uv_sterilization",
            "air_curtain",
            "sticky_trap_monitoring",
            "fly_counter",
        ]:
            status["allowed_operations"][operation] = self.is_operation_allowed(
                operation
            )

        return status

    async def auto_transition_based_on_conditions(
        self, conditions: Dict[str, Any]
    ) -> bool:
        """
        Automatically transition based on system conditions.

        Args:
            conditions: Dictionary of current system conditions

        Returns:
            True if transition occurred, False otherwise
        """
        # Check for emergency conditions
        if conditions.get("emergency_stop", False):
            return await self.set_mode(
                SystemMode.SAFE, ModeTransitionReason.EMERGENCY_STOP
            )

        # Check for critical errors
        if conditions.get("critical_error_count", 0) > 5:
            return await self.set_mode(
                SystemMode.SAFE, ModeTransitionReason.ERROR_DETECTED
            )

        # Check for maintenance requirements
        if conditions.get("maintenance_required", False):
            return await self.set_mode(
                SystemMode.SERVICE, ModeTransitionReason.MAINTENANCE_REQUIRED
            )

        # Check for fly count conditions
        fly_count = conditions.get("fly_count", 0)
        if fly_count > 100 and self.current_mode != SystemMode.ACTIVE:
            return await self.set_mode(
                SystemMode.ACTIVE, ModeTransitionReason.FLY_COUNT_HIGH
            )
        elif fly_count < 10 and self.current_mode == SystemMode.ACTIVE:
            return await self.set_mode(
                SystemMode.STANDBY, ModeTransitionReason.FLY_COUNT_NORMAL
            )

        return False

"""
Crusader Combat Refrigerator - UV Sterilization System
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

UV-C sterilization system for microbial control.
Provides UV exposure management, safety interlocks, and efficacy monitoring.
"""

import asyncio
import math
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from ..core.constants import EnvironmentalConstants, TimeConstants


class UVIntensity(Enum):
    """UV intensity levels."""

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    MAX = auto()


class UVStatus(Enum):
    """UV system status."""

    READY = auto()
    STERILIZING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    SAFETY_LOCKED = auto()
    OVERHEATED = auto()
    DOOR_OPEN = auto()
    MOTION_DETECTED = auto()


class SafetyInterlock(Enum):
    """Safety interlock types."""

    DOOR_SENSOR = auto()
    MOTION_SENSOR = auto()
    TEMPERATURE = auto()
    TIMER = auto()
    MANUAL_OVERRIDE = auto()
    EMERGENCY_STOP = auto()


@dataclass
class SterilizationResult:
    """Result of a UV sterilization cycle."""

    cycle_id: str
    timestamp: datetime
    duration_seconds: float
    intensity: UVIntensity
    status: UVStatus
    success: bool
    energy_joules: float
    uv_dose_mj_per_cm2: float
    temperature_start_celsius: float
    temperature_end_celsius: float
    safety_interlocks_triggered: List[SafetyInterlock]
    error_message: Optional[str] = None
    sensor_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["intensity"] = self.intensity.name
        data["status"] = self.status.name
        data["safety_interlocks_triggered"] = [
            i.name for i in self.safety_interlocks_triggered
        ]
        return data


@dataclass
class UVSystemState:
    """UV system state."""

    led_lifetime_hours: float
    led_efficiency_percent: float
    last_calibration: Optional[datetime]
    calibration_count: int
    total_energy_joules: float
    total_sterilization_time: float
    temperature_celsius: float
    led_health_percent: float
    safety_interlocks_active: List[SafetyInterlock]
    metadata: Optional[Dict[str, Any]] = None

    def get_led_remaining_life(self) -> float:
        """Get remaining LED life in hours."""
        max_lifetime = 10000.0  # Typical UV LED lifetime
        return max(0.0, max_lifetime - self.led_lifetime_hours)

    def get_led_remaining_percent(self) -> float:
        """Get remaining LED life percentage."""
        max_lifetime = 10000.0
        return max(0.0, 100.0 - (self.led_lifetime_hours / max_lifetime * 100.0))

    def is_safe_to_operate(self) -> bool:
        """Check if system is safe to operate."""
        # Check temperature
        if self.temperature_celsius > 50.0:
            return False

        # Check LED health
        if self.led_health_percent < 50.0:
            return False

        # Check if any safety interlocks are active
        critical_interlocks = [
            SafetyInterlock.DOOR_OPEN,
            SafetyInterlock.EMERGENCY_STOP,
        ]
        for interlock in critical_interlocks:
            if interlock in self.safety_interlocks_active:
                return False

        return True


class UVSterilizationSystem:
    """
    UV-C sterilization system.
    Manages UV exposure, safety interlocks, and system health.
    """

    # UV-C constants
    UV_WAVELENGTH_NM = 275  # UVC wavelength
    UV_PHOTON_ENERGY_J = 7.22e-19  # Energy per photon at 275nm
    AVOGADRO_NUMBER = 6.02214076e23

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize UV sterilization system."""
        self.config = config or self._default_config()

        # System state
        self.system_state = UVSystemState(
            led_lifetime_hours=0.0,
            led_efficiency_percent=100.0,
            last_calibration=None,
            calibration_count=0,
            total_energy_joules=0.0,
            total_sterilization_time=0.0,
            temperature_celsius=25.0,
            led_health_percent=100.0,
            safety_interlocks_active=[],
        )

        # Sterilization history
        self.sterilization_history: List[SterilizationResult] = []
        self.current_cycle: Optional[SterilizationResult] = None
        self.cycle_lock = asyncio.Lock()

        # Safety state
        self.safety_state = {
            "door_open": False,
            "motion_detected": False,
            "temperature_ok": True,
            "emergency_stop": False,
            "manual_override": False,
        }

        # Statistics
        self.statistics = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "total_energy_joules": 0.0,
            "total_sterilization_time": 0.0,
            "average_cycle_duration": 0.0,
            "cycles_by_intensity": {intensity.name: 0 for intensity in UVIntensity},
            "safety_interruptions": 0,
            "last_cycle_time": None,
            "consecutive_failures": 0,
        }

        # Efficacy tracking
        self.efficacy_data = {
            "microbial_reduction_log": [],  # Log10 reduction values
            "dose_response_curve": [],
            "last_efficacy_test": None,
            "efficacy_score": 100.0,
        }

        # Hardware interface (would be GPIO in production)
        self.hardware_initialized = False
        self.led_power_watts = self.config["led_power_watts"]

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "sterilization_interval_seconds": 7200.0,  # 2 hours
            "sterilization_duration_seconds": 30.0,
            "led_power_watts": 10.0,
            "led_efficiency": 0.3,
            "beam_angle_degrees": 60.0,
            "target_distance_cm": 50.0,
            "min_dose_mj_per_cm2": 30.0,  # Minimum dose for 99.9% reduction
            "safety": {
                "max_temperature_celsius": 50.0,
                "max_daily_exposure_seconds": 300.0,
                "motion_detection_enabled": True,
                "door_interlock_enabled": True,
                "emergency_stop_enabled": True,
                "auto_shutdown_on_fault": True,
            },
            "intensity_settings": {
                "low": {"power_percent": 25, "dose_multiplier": 0.5},
                "medium": {"power_percent": 50, "dose_multiplier": 1.0},
                "high": {"power_percent": 75, "dose_multiplier": 1.5},
                "max": {"power_percent": 100, "dose_multiplier": 2.0},
            },
            "hardware": {
                "led_array_pin": 27,
                "temperature_sensor_pin": 4,
                "door_sensor_pin": 22,
                "motion_sensor_pin": 17,
                "emergency_stop_pin": 23,
                "cooling_fan_pin": 24,
            },
        }

    async def initialize(self) -> bool:
        """Initialize the UV sterilization system."""
        print("🔧 Initializing UV Sterilization System...")

        try:
            # Initialize hardware
            await self._initialize_hardware()

            # Check system health
            if not self.system_state.is_safe_to_operate():
                print("⚠️ UV system not safe to operate")
                return False

            # Check safety interlocks
            await self._check_safety_interlocks()

            # Update LED health
            await self._update_led_health()

            self.hardware_initialized = True
            print(
                f"✅ UV Sterilization System initialized. LED health: {self.system_state.led_health_percent:.1f}%"
            )
            return True

        except Exception as e:
            print(f"❌ UV Sterilization System initialization failed: {e}")
            return False

    async def _initialize_hardware(self):
        """Initialize hardware components."""
        print("  ↪️ Initializing UV LED array...")
        # In production, this would initialize GPIO pins
        await asyncio.sleep(0.1)  # Simulated hardware initialization

        print("  ↪️ Initializing safety sensors...")
        await asyncio.sleep(0.1)

        print("  ↪️ Initializing cooling system...")
        await asyncio.sleep(0.1)

        print("  ✅ Hardware initialized")

    async def _check_safety_interlocks(self):
        """Check all safety interlocks."""
        # Simulated safety checks
        self.safety_state["door_open"] = False
        self.safety_state["motion_detected"] = False
        self.safety_state["temperature_ok"] = (
            self.system_state.temperature_celsius <= 45.0
        )
        self.safety_state["emergency_stop"] = False

        # Update system state
        self.system_state.safety_interlocks_active.clear()

        if self.safety_state["door_open"]:
            self.system_state.safety_interlocks_active.append(
                SafetyInterlock.DOOR_SENSOR
            )

        if self.safety_state["motion_detected"]:
            self.system_state.safety_interlocks_active.append(
                SafetyInterlock.MOTION_SENSOR
            )

        if not self.safety_state["temperature_ok"]:
            self.system_state.safety_interlocks_active.append(
                SafetyInterlock.TEMPERATURE
            )

        if self.safety_state["emergency_stop"]:
            self.system_state.safety_interlocks_active.append(
                SafetyInterlock.EMERGENCY_STOP
            )

    async def _update_led_health(self):
        """Update LED health based on usage."""
        # Calculate health degradation
        hours_used = self.system_state.led_lifetime_hours
        max_lifetime = 10000.0

        # Exponential decay model
        health_percent = 100.0 * math.exp(-hours_used / max_lifetime * 2.0)

        # Efficiency degradation
        efficiency_percent = 100.0 * math.exp(-hours_used / max_lifetime * 1.5)

        self.system_state.led_health_percent = max(0.0, health_percent)
        self.system_state.led_efficiency_percent = max(10.0, efficiency_percent)

    async def should_sterilize(
        self, sensor_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[UVIntensity]]:
        """
        Determine if UV sterilization should be performed.

        Returns:
            Tuple of (should_sterilize, intensity)
        """
        # Check basic conditions
        if not self.hardware_initialized:
            return False, None

        if not self.system_state.is_safe_to_operate():
            print("⚠️ Cannot sterilize: Safety interlocks active")
            return False, None

        # Check LED health
        if self.system_state.led_health_percent < 30.0:
            print(
                f"⚠️ Cannot sterilize: LED health too low ({self.system_state.led_health_percent:.1f}%)"
            )
            return False, None

        # Check daily exposure limit
        daily_exposure = self._get_daily_exposure()
        max_daily = self.config["safety"]["max_daily_exposure_seconds"]

        if daily_exposure >= max_daily:
            print(
                f"⚠️ Cannot sterilize: Daily exposure limit reached ({daily_exposure:.0f}s)"
            )
            return False, None

        # Check time since last sterilization
        if self.sterilization_history:
            last_cycle = self.sterilization_history[-1]
            time_since_last = (datetime.now() - last_cycle.timestamp).total_seconds()

            if time_since_last < self.config["sterilization_interval_seconds"]:
                return False, None

        # Determine intensity based on conditions
        intensity = self._determine_intensity(sensor_data)

        return True, intensity

    def _get_daily_exposure(self) -> float:
        """Get total UV exposure for today."""
        today = datetime.now().date()
        daily_exposure = 0.0

        for cycle in self.sterilization_history:
            if cycle.timestamp.date() == today:
                daily_exposure += cycle.duration_seconds

        return daily_exposure

    def _determine_intensity(self, sensor_data: Dict[str, Any]) -> UVIntensity:
        """Determine UV intensity based on sensor data."""
        temperature = sensor_data.get("temperature_celsius", 25.0)
        humidity = sensor_data.get("humidity_percent", 50.0)

        # Higher intensity for higher temperatures (more microbial growth)
        if temperature > 30.0:
            return UVIntensity.HIGH
        elif temperature > 25.0:
            return UVIntensity.MEDIUM
        else:
            return UVIntensity.LOW

    async def sterilize(
        self,
        intensity: UVIntensity = UVIntensity.MEDIUM,
        sensor_data: Optional[Dict[str, Any]] = None,
    ) -> SterilizationResult:
        """
        Perform UV sterilization cycle.

        Returns:
            SterilizationResult with outcome
        """
        import uuid

        async with self.cycle_lock:
            cycle_id = str(uuid.uuid4())
            start_time = datetime.now()

            print(f"☀️ Starting UV sterilization cycle {cycle_id} ({intensity.name})")

            # Create cycle result
            cycle = SterilizationResult(
                cycle_id=cycle_id,
                timestamp=start_time,
                duration_seconds=0.0,
                intensity=intensity,
                status=UVStatus.STERILIZING,
                success=False,
                energy_joules=0.0,
                uv_dose_mj_per_cm2=0.0,
                temperature_start_celsius=self.system_state.temperature_celsius,
                temperature_end_celsius=self.system_state.temperature_celsius,
                safety_interlocks_triggered=[],
                sensor_data=sensor_data,
            )

            self.current_cycle = cycle

            try:
                # Pre-cycle safety check
                safety_ok = await self._pre_cycle_safety_check()
                if not safety_ok:
                    cycle.status = UVStatus.SAFETY_LOCKED
                    cycle.error_message = "Safety check failed"
                    print(f"❌ {cycle.error_message}")
                    self.current_cycle = None
                    return cycle

                # Calculate cycle parameters
                duration = self._calculate_cycle_duration(intensity)
                power = self._calculate_power(intensity)

                # Execute sterilization
                success = await self._execute_sterilization(duration, power, intensity)

                # Update cycle result
                end_time = datetime.now()
                cycle_duration = (end_time - start_time).total_seconds()

                cycle.duration_seconds = cycle_duration
                cycle.energy_joules = power * cycle_duration
                cycle.uv_dose_mj_per_cm2 = self._calculate_uv_dose(
                    power, cycle_duration, intensity
                )
                cycle.temperature_end_celsius = self.system_state.temperature_celsius
                cycle.success = success
                cycle.status = UVStatus.COMPLETED if success else UVStatus.FAILED

                if success:
                    # Update system state
                    self.system_state.led_lifetime_hours += cycle_duration / 3600.0
                    self.system_state.total_energy_joules += cycle.energy_joules
                    self.system_state.total_sterilization_time += cycle_duration

                    # Update statistics
                    self.statistics["total_cycles"] += 1
                    self.statistics["successful_cycles"] += 1
                    self.statistics["total_energy_joules"] += cycle.energy_joules
                    self.statistics["total_sterilization_time"] += cycle_duration
                    self.statistics["cycles_by_intensity"][intensity.name] += 1
                    self.statistics["last_cycle_time"] = end_time
                    self.statistics["consecutive_failures"] = 0

                    # Calculate average cycle duration
                    total_time = self.statistics["average_cycle_duration"] * (
                        self.statistics["successful_cycles"] - 1
                    )
                    self.statistics["average_cycle_duration"] = (
                        total_time + cycle_duration
                    ) / self.statistics["successful_cycles"]

                    print(
                        f"✅ UV cycle {cycle_id} completed: {cycle_duration:.1f}s, {cycle.uv_dose_mj_per_cm2:.1f} mJ/cm²"
                    )

                else:
                    self.statistics["failed_cycles"] += 1
                    self.statistics["consecutive_failures"] += 1
                    print(f"❌ UV cycle {cycle_id} failed")

                # Add to history
                self.sterilization_history.append(cycle)

                # Update LED health
                await self._update_led_health()

                return cycle

            except Exception as e:
                cycle.status = UVStatus.FAILED
                cycle.error_message = str(e)
                cycle.success = False

                self.statistics["failed_cycles"] += 1
                self

"""
Crusader Combat Refrigerator - Air Curtain System
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Air curtain system for creating a protective barrier at refrigerator openings.
Uses directed airflow to prevent fly ingress while allowing human access.
"""

import asyncio
import math
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from ..core.constants import EnvironmentalConstants, HardwareConstants, TimeConstants
from ..core.utils.time_utils import TimeUtils


class AirCurtainMode(Enum):
    """Air curtain operational modes."""

    STANDARD = auto()  # Standard protective barrier
    HIGH_FLOW = auto()  # Increased airflow for high fly activity
    LOW_POWER = auto()  # Energy-saving mode
    MAINTENANCE = auto()  # Maintenance/testing mode
    EMERGENCY = auto()  # Maximum airflow for emergency situations
    ADAPTIVE = auto()  # Adaptive based on sensor data
    OFF = auto()  # System off


class AirCurtainStatus(Enum):
    """Air curtain system status."""

    READY = auto()
    ACTIVE = auto()
    STARTING = auto()
    STOPPING = auto()
    ERROR = auto()
    MAINTENANCE = auto()
    CALIBRATING = auto()
    OVERHEATED = auto()
    BLOCKED = auto()
    LOW_POWER = auto()


class AirflowPattern(Enum):
    """Airflow distribution patterns."""

    UNIFORM = auto()  # Even airflow across entire opening
    FOCUSED = auto()  # Focused airflow at detected fly entry points
    SWEEPING = auto()  # Sweeping pattern across opening
    PULSING = auto()  # Pulsing airflow for energy efficiency
    VORTEX = auto()  # Vortex pattern for maximum barrier strength
    LAMINAR = auto()  # Laminar flow for minimal turbulence


@dataclass
class AirCurtainConfig:
    """Air curtain configuration."""

    # Fan specifications
    fan_count: int = 4
    max_rpm: int = 3000
    min_rpm: int = 500
    fan_power_watts: float = 15.0

    # Airflow specifications
    max_airflow_cfm: float = 150.0
    min_airflow_cfm: float = 20.0
    target_velocity_mps: float = 3.5  # meters per second

    # Opening dimensions (in mm)
    opening_width_mm: float = 600.0
    opening_height_mm: float = 1200.0
    curtain_thickness_mm: float = 50.0

    # Operational parameters
    startup_time_seconds: float = 2.0
    shutdown_time_seconds: float = 3.0
    calibration_interval_hours: float = 24.0
    maintenance_interval_hours: float = 168.0  # Weekly

    # Energy parameters
    power_consumption_idle_w: float = 2.0
    power_consumption_active_w: float = 60.0
    energy_saving_threshold_minutes: int = 5

    # Safety parameters
    max_temperature_c: float = 60.0
    overheat_shutdown_temp_c: float = 70.0
    motor_cooldown_time_seconds: float = 300.0

    # Adaptive parameters
    fly_detection_threshold: int = 3  # Flies per minute to trigger high flow
    humidity_compensation_factor: float = 1.1  # Increase airflow in high humidity
    temperature_compensation_factor: float = 0.95  # Decrease airflow in cold temps


@dataclass
class FanState:
    """Individual fan state."""

    fan_id: int
    rpm: int
    target_rpm: int
    temperature_c: float
    voltage_v: float
    current_a: float
    power_w: float
    status: str  # "normal", "overheating", "stalled", "vibrating"
    last_maintenance: Optional[datetime]
    total_runtime_hours: float
    error_count: int
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AirflowMeasurement:
    """Airflow measurement data."""

    timestamp: datetime
    velocity_mps: float
    direction_degrees: float
    turbulence_percent: float
    temperature_c: float
    humidity_percent: float
    pressure_pa: float
    measurement_point: Tuple[float, float, float]  # x, y, z in mm
    sensor_id: str
    confidence: float


@dataclass
class AirCurtainResult:
    """Result of air curtain operation."""

    operation_id: str
    timestamp: datetime
    mode: AirCurtainMode
    status: AirCurtainStatus
    duration_seconds: float
    average_airflow_cfm: float
    average_velocity_mps: float
    energy_consumed_wh: float
    fly_block_count: int
    success: bool
    error_message: Optional[str] = None
    fan_states: Optional[List[Dict[str, Any]]] = None
    airflow_measurements: Optional[List[Dict[str, Any]]] = None
    environmental_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["mode"] = self.mode.name
        data["status"] = self.status.name
        return data


@dataclass
class BarrierEffectiveness:
    """Barrier effectiveness metrics."""

    timestamp: datetime
    effectiveness_percent: float
    fly_penetration_count: int
    barrier_integrity_score: float  # 0.0 to 1.0
    airflow_consistency_score: float  # 0.0 to 1.0
    energy_efficiency_score: float  # 0.0 to 1.0
    measurement_duration_seconds: float
    test_conditions: Dict[str, Any]
    recommendations: List[str]


class AirCurtainSystem:
    """
    Air curtain system for creating protective airflow barriers.
    Manages multiple fans, airflow patterns, and barrier effectiveness.
    """

    def __init__(self, config: Optional[AirCurtainConfig] = None):
        """Initialize air curtain system."""
        self.config = config or AirCurtainConfig()
        self.mode = AirCurtainMode.OFF
        self.status = AirCurtainStatus.READY
        self.active_pattern = AirflowPattern.UNIFORM

        # Fan management
        self.fans: Dict[int, FanState] = {}
        self._initialize_fans()

        # Operation tracking
        self.current_operation_id: Optional[str] = None
        self.operation_start_time: Optional[datetime] = None
        self.total_energy_consumed_wh: float = 0.0
        self.total_fly_block_count: int = 0
        self.total_runtime_hours: float = 0.0

        # Performance metrics
        self.performance_history: List[AirCurtainResult] = []
        self.barrier_effectiveness_history: List[BarrierEffectiveness] = []

        # Adaptive control
        self.adaptive_parameters: Dict[str, Any] = {
            "last_fly_detection": None,
            "fly_detection_rate": 0.0,
            "environmental_compensation": 1.0,
            "current_effectiveness": 0.95,
            "learning_coefficient": 0.1,
        }

        # Maintenance tracking
        self.last_calibration: Optional[datetime] = None
        self.last_maintenance: Optional[datetime] = None
        self.maintenance_alerts: List[str] = []

        # Hardware interface (simulated for now)
        self.hardware_connected = False
        self.simulation_mode = True

        # Async components
        self._control_task: Optional[asyncio.Task] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        print(f"AirCurtainSystem initialized with {self.config.fan_count} fans")

    def _initialize_fans(self) -> None:
        """Initialize fan states."""
        for i in range(self.config.fan_count):
            self.fans[i] = FanState(
                fan_id=i,
                rpm=0,
                target_rpm=0,
                temperature_c=25.0,
                voltage_v=12.0,
                current_a=0.0,
                power_w=0.0,
                status="normal",
                last_maintenance=None,
                total_runtime_hours=0.0,
                error_count=0,
            )

    async def start(
        self, mode: AirCurtainMode = AirCurtainMode.STANDARD
    ) -> AirCurtainResult:
        """Start the air curtain system."""
        if self.status in [AirCurtainStatus.ACTIVE, AirCurtainStatus.STARTING]:
            return AirCurtainResult(
                operation_id=self.current_operation_id or "unknown",
                timestamp=datetime.now(),
                mode=self.mode,
                status=self.status,
                duration_seconds=0.0,
                average_airflow_cfm=0.0,
                average_velocity_mps=0.0,
                energy_consumed_wh=0.0,
                fly_block_count=0,
                success=False,
                error_message=f"System already {self.status.name.lower()}",
            )

        print(f"Starting air curtain system in {mode.name} mode")

        self.mode = mode
        self.status = AirCurtainStatus.STARTING
        self.current_operation_id = self._generate_operation_id()
        self.operation_start_time = datetime.now()

        try:
            # Connect to hardware (simulated)
            await self._connect_hardware()

            # Start fans according to mode
            await self._start_fans_for_mode(mode)

            # Start monitoring tasks
            self._control_task = asyncio.create_task(self._control_loop())
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

            # Wait for startup to complete
            await asyncio.sleep(self.config.startup_time_seconds)

            self.status = AirCurtainStatus.ACTIVE
            print(f"Air curtain system active in {mode.name} mode")

            return AirCurtainResult(
                operation_id=self.current_operation_id,
                timestamp=datetime.now(),
                mode=mode,
                status=AirCurtainStatus.ACTIVE,
                duration_seconds=0.0,
                average_airflow_cfm=self._calculate_current_airflow(),
                average_velocity_mps=self._calculate_current_velocity(),
                energy_consumed_wh=0.0,
                fly_block_count=0,
                success=True,
            )

        except Exception as e:
            self.status = AirCurtainStatus.ERROR
            print(f"Failed to start air curtain system: {e}")

            return AirCurtainResult(
                operation_id=self.current_operation_id or "error",
                timestamp=datetime.now(),
                mode=mode,
                status=AirCurtainStatus.ERROR,
                duration_seconds=0.0,
                average_airflow_cfm=0.0,
                average_velocity_mps=0.0,
                energy_consumed_wh=0.0,
                fly_block_count=0,
                success=False,
                error_message=str(e),
            )

    async def stop(self) -> AirCurtainResult:
        """Stop the air curtain system."""
        if self.status in [AirCurtainStatus.READY, AirCurtainStatus.OFF]:
            return AirCurtainResult(
                operation_id=self.current_operation_id or "unknown",
                timestamp=datetime.now(),
                mode=self.mode,
                status=self.status,
                duration_seconds=0.0,
                average_airflow_cfm=0.0,
                average_velocity_mps=0.0,
                energy_consumed_wh=0.0,
                fly_block_count=0,
                success=False,
                error_message=f"System already {self.status.name.lower()}",
            )

        print("Stopping air curtain system")
        self.status = AirCurtainStatus.STOPPING

        try:
            # Signal shutdown
            self._shutdown_event.set()

            # Stop fans
            await self._stop_all_fans()

            # Wait for shutdown to complete
            await asyncio.sleep(self.config.shutdown_time_seconds)

            # Cancel tasks
            if self._control_task:
                self._control_task.cancel()
            if self._monitoring_task:
                self._monitoring_task.cancel()

            # Calculate final metrics
            duration = 0.0
            if self.operation_start_time:
                duration = (datetime.now() - self.operation_start_time).total_seconds()

            airflow = self._calculate_current_airflow()
            velocity = self._calculate_current_velocity()
            energy = self._calculate_energy_consumption(duration)

            self.status = AirCurtainStatus.READY
            self.mode = AirCurtainMode.OFF
            self._shutdown_event.clear()

            print("Air curtain system stopped")

            result = AirCurtainResult(
                operation_id=self.current_operation_id or "shutdown",
                timestamp=datetime.now(),
                mode=AirCurtainMode.OFF,
                status=AirCurtainStatus.READY,
                duration_seconds=duration,
                average_airflow_cfm=airflow,
                average_velocity_mps=velocity,
                energy_consumed_wh=energy,
                fly_block_count=self.total_fly_block_count,
                success=True,
            )

            # Reset counters for next operation
            self.total_fly_block_count = 0
            self.current_operation_id = None
            self.operation_start_time = None

            return result

        except Exception as e:
            self.status = AirCurtainStatus.ERROR
            print(f"Error stopping air curtain system: {e}")

            return AirCurtainResult(
                operation_id=self.current_operation_id or "error",
                timestamp=datetime.now(),
                mode=self.mode,
                status=AirCurtainStatus.ERROR,
                duration_seconds=0.0,
                average_airflow_cfm=0.0,
                average_velocity_mps=0.0,
                energy_consumed_wh=0.0,
                fly_block_count=0,
                success=False,
                error_message=str(e),
            )

    async def change_mode(self, new_mode: AirCurtainMode) -> AirCurtainResult:
        """Change operational mode."""
        if self.status != AirCurtainStatus.ACTIVE:
            return await self.start(new_mode)

        print(f"Changing air curtain mode from {self.mode.name} to {new_mode.name}")

        try:
            # Update fan speeds for new mode
            await self._adjust_fans_for_mode(new_mode)
            self.mode = new_mode

            return AirCurtainResult(
                operation_id=self.current_operation_id or "mode_change",
                timestamp=datetime.now(),
                mode=new_mode,
                status=self.status,
                duration_seconds=0.0,
                average_airflow_cfm=self._calculate_current_airflow(),
                average_velocity_mps=self._calculate_current_velocity(),
                energy_consumed_wh=0.0,
                fly_block_count=0,
                success=True,
            )

        except Exception as e:
            print(f"Failed to change mode: {e}")

            return AirCurtainResult(
                operation_id=self.current_operation_id or "error",
                timestamp=datetime.now(),
                mode=self.mode,  # Keep old mode
                status=self.status,
                duration_seconds=0.0,
                average_airflow_cfm=0.0,
                average_velocity_mps=0.0,
                energy_consumed_wh=0.0,
                fly_block_count=0,
                success=False,
                error_message=str(e),
            )

    async def set_airflow_pattern(self, pattern: AirflowPattern) -> bool:
        """Set airflow distribution pattern."""
        if self.status != AirCurtainStatus.ACTIVE:
            print(f"Cannot set pattern when system is {self.status.name}")
            return False

        print(f"Setting airflow pattern to {pattern.name}")
        self.active_pattern = pattern

        # Adjust fan speeds based on pattern
        await self._adjust_fans_for_pattern(pattern)

        return True

    def report_fly_detection(self, count: int = 1) -> None:
        """Report fly detection for adaptive control."""
        now = datetime.now()
        self.adaptive_parameters["last_fly_detection"] = now

        # Update fly detection rate (exponential moving average)
        current_rate = self.adaptive_parameters["fly_detection_rate"]
        alpha = 0.1  # Learning rate
        self.adaptive_parameters["fly_detection_rate"] = (
            alpha * count + (1 - alpha) * current_rate
        )

        # Increment block count
        self.total_fly_block_count += count

        print(
            f"Fly detection reported: {count} flies (total blocked: {self.total_fly_block_count})"
        )

        # Trigger adaptive response if needed
        if count >= self.config.fly_detection_threshold:
            asyncio.create_task(self._trigger_adaptive_response())

    async def measure_barrier_effectiveness(self) -> BarrierEffectiveness:
        """Measure current barrier effectiveness."""
        print("Measuring barrier effectiveness")

        # Simulate measurement
        measurement_duration = 30.0  # seconds

        # Simulate test conditions
        test_conditions = {
            "temperature_c": 22.5,
            "humidity_percent": 45.0,
            "fly_challenge_count": 50,
            "airflow_velocity_mps": self._calculate_current_velocity(),
            "measurement_method": "simulated",
        }

        # Calculate effectiveness based on current state
        base_effectiveness = 0.95
        if self.status == AirCurtainStatus.ACTIVE:
            # Adjust based on mode and airflow
            mode_factor = {
                AirCurtainMode.STANDARD: 1.0,
                AirCurtainMode.HIGH_FLOW: 1.1,
                AirCurtainMode.LOW_POWER: 0.8,
                AirCurtainMode.EMERGENCY: 1.2,
                AirCurtainMode.ADAPTIVE: 1.05,
            }.get(self.mode, 1.0)

            airflow_factor = min(
                1.0,
                self._calculate_current_velocity() / self.config.target_velocity_mps,
            )
            effectiveness = base_effectiveness * mode_factor * airflow_factor

            # Simulate fly penetration
            fly_penetration = max(0, int(50 * (1.0 - effectiveness)))
            barrier_score = effectiveness
            airflow_score = airflow_factor
            energy_score = 1.0 - (
                self._calculate_current_power() / self.config.power_consumption_active_w
            )

            effectiveness_result = BarrierEffectiveness(
                timestamp=datetime.now(),
                effectiveness_percent=effectiveness * 100,
                fly_penetration_count=fly_penetration,
                barrier_integrity_score=barrier_score,
                airflow_consistency_score=airflow_score,
                energy_efficiency_score=energy_score,
                measurement_duration_seconds=measurement_duration,
                test_conditions=test_conditions,
                recommendations=self._generate_recommendations(effectiveness),
            )

            self.barrier_effectiveness_history.append(effectiveness_result)
            return effectiveness_result
        else:
            # System not active
            return BarrierEffectiveness(
                timestamp=datetime.now(),
                effectiveness_percent=0.0,
                fly_penetration_count=50,  # All flies penetrate
                barrier_integrity_score=0.0,
                airflow_consistency_score=0.0,
                energy_efficiency_score=0.0,
                measurement_duration_seconds=measurement_duration,
                test_conditions=test_conditions,
                recommendations=["Start air curtain system to establish barrier"],
            )

    async def _connect_hardware(self) -> None:
        """Connect to hardware components."""
        if self.simulation_mode:
            print("Simulating hardware connection")
            await asyncio.sleep(0.5)
            self.hardware_connected = True
        else:
            # Actual hardware connection would go here
            raise NotImplementedError("Hardware connection not implemented")

    async def _start_fans_for_mode(self, mode: AirCurtainMode) -> None:
        """Start fans according to specified mode."""
        target_rpms = {
            AirCurtainMode.STANDARD: 1800,
            AirCurtainMode.HIGH_FLOW: 2500,
            AirCurtainMode.LOW_POWER: 1000,
            AirCurtainMode.EMERGENCY: 3000,
            AirCurtainMode.ADAPTIVE: 2000,
            AirCurtainMode.MAINTENANCE: 800,
        }

        target_rpm = target_rpms.get(mode, 1500)

        print(f"Starting fans at {target_rpm} RPM for {mode.name} mode")

        for fan_id, fan in self.fans.items():
            fan.target_rpm = target_rpm
            fan.rpm = target_rpm
            fan.current_a = target_rpm / 200.0  # Simplified model
            fan.power_w = fan.current_a * fan.voltage_v
            fan.status = "normal"

            if self.simulation_mode:
                print(f"  Fan {fan_id}: {fan.rpm} RPM, {fan.power_w:.1f}W")
                await asyncio.sleep(0.1)

    async def _stop_all_fans(self) -> None:
        """Stop all fans."""
        print("Stopping all fans")

        for fan_id, fan in self.fans.items():
            fan.target_rpm = 0
            fan.rpm = 0
            fan.current_a = 0.0
            fan.power_w = 0.0

            if self.simulation_mode:
                print(f"  Fan {fan_id}: stopped")
                await asyncio.sleep(0.05)

    async def _adjust_fans_for_mode(self, mode: AirCurtainMode) -> None:
        """Adjust fan speeds for new mode."""
        await self._start_fans_for_mode(mode)

    async def _adjust_fans_for_pattern(self, pattern: AirflowPattern) -> None:
        """Adjust fan speeds for airflow pattern."""
        if self.simulation_mode:
            print(f"Adjusting fans for {pattern.name} pattern")

            # Different patterns adjust fan speeds differently
            pattern_adjustments = {
                AirflowPattern.UNIFORM: [1.0, 1.0, 1.0, 1.0],
                AirflowPattern.FOCUSED: [1.5, 0.5, 1.5, 0.5],
                AirflowPattern.SWEEPING: [1.2, 0.8, 1.2, 0.8],
                AirflowPattern.PULSING: [1.0, 1.0, 1.0, 1.0],  # Would pulse over time
                AirflowPattern.VORTEX: [1.3, 0.7, 0.7, 1.3],
                AirflowPattern.LAMINAR: [0.9, 1.1, 0.9, 1.1],
            }

            adjustments = pattern_adjustments.get(
                pattern, [1.0] * self.config.fan_count
            )

            for i, (fan_id, fan) in enumerate(self.fans.items()):
                if i < len(adjustments):
                    adjustment = adjustments[i]
                    fan.rpm = int(fan.rpm * adjustment)
                    fan.current_a = fan.rpm / 200.0
                    fan.power_w = fan.current_a * fan.voltage_v
                    print(f"  Fan {fan_id}: {fan.rpm} RPM ({adjustment:.1f}x)")

    async def _control_loop(self) -> None:
        """Main control loop for air curtain system."""
        print("Starting air curtain control loop")

        try:
            while not self._shutdown_event.is_set():
                # Update fan states
                await self._update_fan_states()

                # Check for maintenance needs
                await self._check_maintenance()

                # Adaptive control if in adaptive mode
                if self.mode == AirCurtainMode.ADAPTIVE:
                    await self._adaptive_control()

                # Log performance
                await self._log_performance()

                # Sleep for control interval
                await asyncio.sleep(1.0)

        except asyncio.CancelledError:
            print("Control loop cancelled")
        except Exception as e:
            print(f"Error in control loop: {e}")
            self.status = AirCurtainStatus.ERROR

    async def _monitoring_loop(self) -> None:
        """Monitoring loop for system health."""
        print("Starting air curtain monitoring loop")

        try:
            while not self._shutdown_event.is_set():
                # Monitor temperatures
                await self._monitor_temperatures()

                # Monitor power consumption
                await self._monitor_power()

                # Check for errors
                await self._check_errors()

                # Sleep for monitoring interval
                await asyncio.sleep(2.0)

        except asyncio.CancelledError:
            print("Monitoring loop cancelled")
        except Exception as e:
            print(f"Error in monitoring loop: {e}")

    async def _update_fan_states(self) -> None:
        """Update fan states (simulated)."""
        if not self.simulation_mode:
            return

        for fan_id, fan in self.fans.items():
            # Simulate temperature increase when running
            if fan.rpm > 0:
                temp_increase = fan.rpm / 10000.0  # Simplified model
                fan.temperature_c += temp_increase

                # Simulate cooling
                ambient_temp = 25.0
                cooling_rate = 0.1
                fan.temperature_c = max(ambient_temp, fan.temperature_c - cooling_rate)

                # Update runtime
                fan.total_runtime_hours += 1.0 / 3600.0  # 1 second

                # Check for overheating
                if fan.temperature_c > self.config.max_temperature_c:
                    fan.status = "overheating"
                    if fan.temperature_c > self.config.overheat_shutdown_temp_c:
                        print(
                            f"WARNING: Fan {fan_id} overheating! Temperature: {fan.temperature_c:.1f}°C"
                        )

    async def _check_maintenance(self) -> None:
        """Check if maintenance is needed."""
        now = datetime.now()

        # Check calibration
        if self.last_calibration:
            hours_since_calibration = (
                now - self.last_calibration
            ).total_seconds() / 3600.0
            if hours_since_calibration > self.config.calibration_interval_hours:
                self.maintenance_alerts.append("Calibration needed")

        # Check general maintenance
        if self.last_maintenance:
            hours_since_maintenance = (
                now - self.last_maintenance
            ).total_seconds() / 3600.0
            if hours_since_maintenance > self.config.maintenance_interval_hours:
                self.maintenance_alerts.append("Maintenance needed")

        # Check fan runtime
        for fan_id, fan in self.fans.items():
            if fan.total_runtime_hours > 1000:  # 1000 hours runtime
                self.maintenance_alerts.append(f"Fan {fan_id} needs inspection")

    async def _adaptive_control(self) -> None:
        """Adaptive control based on sensor data."""
        # Adjust based on fly detection rate
        fly_rate = self.adaptive_parameters["fly_detection_rate"]
        if fly_rate > self.config.fly_detection_threshold:
            # Increase airflow
            await self._increase_airflow(1.1)
            print(
                f"Adaptive control: Increased airflow due to high fly rate ({fly_rate:.1f}/min)"
            )
        elif fly_rate < 0.5:
            # Decrease airflow for energy saving
            await self._decrease_airflow(0.9)
            print(
                f"Adaptive control: Decreased airflow due to low fly rate ({fly_rate:.1f}/min)"
            )

        # Update environmental compensation
        await self._update_environmental_compensation()

    async def _trigger_adaptive_response(self) -> None:
        """Trigger adaptive response to high fly activity."""
        if self.mode != AirCurtainMode.ADAPTIVE:
            return

        print("Triggering adaptive response to high fly activity")

        # Temporarily increase airflow
        original_rpms = {fan_id: fan.rpm for fan_id, fan in self.fans.items()}

        for fan_id, fan in self.fans.items():
            fan.rpm = min(self.config.max_rpm, int(fan.rpm * 1.3))
            fan.current_a = fan.rpm / 200.0
            fan.power_w = fan.current_a * fan.voltage_v

        # Maintain increased airflow for 30 seconds
        await asyncio.sleep(30.0)

        # Return to normal
        for fan_id, fan in self.fans.items():
            fan.rpm = original_rpms[fan_id]
            fan.current_a = fan.rpm / 200.0
            fan.power_w = fan.current_a * fan.voltage_v

        print("Adaptive response complete")

    async def _increase_airflow(self, factor: float) -> None:
        """Increase airflow by factor."""
        for fan_id, fan in self.fans.items():
            new_rpm = min(self.config.max_rpm, int(fan.rpm * factor))
            fan.rpm = new_rpm
            fan.current_a = new_rpm / 200.0
            fan.power_w = fan.current_a * fan.voltage_v

    async def _decrease_airflow(self, factor: float) -> None:
        """Decrease airflow by factor."""
        for fan_id, fan in self.fans.items():
            new_rpm = max(self.config.min_rpm, int(fan.rpm * factor))
            fan.rpm = new_rpm
            fan.current_a = new_rpm / 200.0
            fan.power_w = fan.current_a * fan.voltage_v

    async def _update_environmental_compensation(self) -> None:
        """Update environmental compensation factor."""
        # This would use actual sensor data
        # For simulation, use fixed values
        humidity = 45.0  # percent
        temperature = 22.0  # celsius

        humidity_factor = (
            1.0 + (humidity - 50.0) / 100.0 * self.config.humidity_compensation_factor
        )
        temperature_factor = (
            1.0
            + (temperature - 20.0) / 20.0 * self.config.temperature_compensation_factor
        )

        self.adaptive_parameters["environmental_compensation"] = (
            humidity_factor * temperature_factor
        )

    async def _monitor_temperatures(self) -> None:
        """Monitor system temperatures."""
        max_temp = max(fan.temperature_c for fan in self.fans.values())

        if max_temp > self.config.overheat_shutdown_temp_c:
            print(
                f"CRITICAL: Overheating detected ({max_temp:.1f}°C), initiating shutdown"
            )
            await self.stop()
        elif max_temp > self.config.max_temperature_c:
            print(f"WARNING: High temperature ({max_temp:.1f}°C)")

    async def _monitor_power(self) -> None:
        """Monitor power consumption."""
        total_power = sum(fan.power_w for fan in self.fans.values())

        # Update total energy consumption
        self.total_energy_consumed_wh += (
            total_power / 3600.0
        )  # Convert watts to watt-hours per second

        if total_power > self.config.power_consumption_active_w * 1.2:
            print(f"WARNING: High power consumption ({total_power:.1f}W)")

    async def _check_errors(self) -> None:
        """Check for system errors."""
        for fan_id, fan in self.fans.items():
            if fan.status != "normal":
                print(f"Fan {fan_id} error: {fan.status}")
                fan.error_count += 1

                if fan.error_count > 10:
                    self.maintenance_alerts.append(
                        f"Fan {fan_id} has persistent errors"
                    )

    async def _log_performance(self) -> None:
        """Log current performance."""
        if self.status != AirCurtainStatus.ACTIVE:
            return

        duration = 0.0
        if self.operation_start_time:
            duration = (datetime.now() - self.operation_start_time).total_seconds()

        result = AirCurtainResult(
            operation_id=self.current_operation_id or "performance_log",
            timestamp=datetime.now(),
            mode=self.mode,
            status=self.status,
            duration_seconds=duration,
            average_airflow_cfm=self._calculate_current_airflow(),
            average_velocity_mps=self._calculate_current_velocity(),
            energy_consumed_wh=self._calculate_energy_consumption(duration),
            fly_block_count=self.total_fly_block_count,
            success=True,
            fan_states=[asdict(fan) for fan in self.fans.values()],
        )

        self.performance_history.append(result)

        # Keep history manageable
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]

    def _calculate_current_airflow(self) -> float:
        """Calculate current airflow in CFM."""
        total_rpm = sum(fan.rpm for fan in self.fans.values())
        avg_rpm = total_rpm / len(self.fans) if self.fans else 0

        # Simplified model: airflow proportional to RPM
        airflow_per_rpm = self.config.max_airflow_cfm / self.config.max_rpm
        return avg_rpm * airflow_per_rpm

    def _calculate_current_velocity(self) -> float:
        """Calculate current air velocity in m/s."""
        airflow_cfm = self._calculate_current_airflow()

        # Convert CFM to m³/s
        airflow_m3s = airflow_cfm * 0.000471947

        # Calculate velocity: v = Q/A
        area_m2 = (self.config.opening_width_mm / 1000.0) * (
            self.config.curtain_thickness_mm / 1000.0
        )
        if area_m2 > 0:
            return airflow_m3s / area_m2
        return 0.0

    def _calculate_current_power(self) -> float:
        """Calculate current power consumption in watts."""
        return sum(fan.power_w for fan in self.fans.values())

    def _calculate_energy_consumption(self, duration_seconds: float) -> float:
        """Calculate energy consumption in watt-hours."""
        avg_power = self._calculate_current_power()
        return avg_power * duration_seconds / 3600.0

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = random.randint(1000, 9999)
        return f"AC_{timestamp}_{random_suffix}"

    def _generate_recommendations(self, effectiveness: float) -> List[str]:
        """Generate recommendations based on effectiveness."""
        recommendations = []

        if effectiveness < 0.8:
            recommendations.append("Increase airflow velocity")
            recommendations.append("Check for obstructions in airflow path")
            recommendations.append("Consider switching to HIGH_FLOW mode")

        if effectiveness > 0.95:
            recommendations.append(
                "Consider switching to LOW_POWER mode for energy savings"
            )

        # Check maintenance alerts
        if self.maintenance_alerts:
            recommendations.extend(self.maintenance_alerts)

        return recommendations

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        return {
            "system": {
                "mode": self.mode.name,
                "status": self.status.name,
                "active_pattern": self.active_pattern.name,
                "operation_id": self.current_operation_id,
                "operation_duration_seconds": (
                    (datetime.now() - self.operation_start_time).total_seconds()
                    if self.operation_start_time
                    else 0.0
                ),
            },
            "performance": {
                "current_airflow_cfm": self._calculate_current_airflow(),
                "current_velocity_mps": self._calculate_current_velocity(),
                "current_power_w": self._calculate_current_power(),
                "total_energy_consumed_wh": self.total_energy_consumed_wh,
                "total_fly_block_count": self.total_fly_block_count,
                "total_runtime_hours": self.total_runtime_hours,
                "fly_detection_rate": self.adaptive_parameters["fly_detection_rate"],
                "barrier_effectiveness": self.adaptive_parameters[
                    "current_effectiveness"
                ],
            },
            "fans": {
                fan_id: {
                    "rpm": fan.rpm,
                    "temperature_c": fan.temperature_c,
                    "power_w": fan.power_w,
                    "status": fan.status,
                    "runtime_hours": fan.total_runtime_hours,
                    "error_count": fan.error_count,
                }
                for fan_id, fan in self.fans.items()
            },
            "maintenance": {
                "alerts": self.maintenance_alerts.copy(),
                "last_calibration": (
                    self.last_calibration.isoformat() if self.last_calibration else None
                ),
                "last_maintenance": (
                    self.last_maintenance.isoformat() if self.last_maintenance else None
                ),
                "needs_calibration": (
                    (datetime.now() - self.last_calibration).total_seconds() / 3600.0
                    > self.config.calibration_interval_hours
                    if self.last_calibration
                    else True
                ),
                "needs_maintenance": (
                    (datetime.now() - self.last_maintenance).total_seconds() / 3600.0
                    > self.config.maintenance_interval_hours
                    if self.last_maintenance
                    else True
                ),
            },
            "history": {
                "performance_entries": len(self.performance_history),
                "effectiveness_tests": len(self.barrier_effectiveness_history),
                "latest_effectiveness": (
                    self.barrier_effectiveness_history[-1].effectiveness_percent
                    if self.barrier_effectiveness_history
                    else 0.0
                ),
            },
        }

    async def calibrate(self) -> bool:
        """Calibrate the air curtain system."""
        if self.status != AirCurtainStatus.READY:
            print(f"Cannot calibrate when system is {self.status.name}")
            return False

        print("Starting air curtain calibration")
        self.status = AirCurtainStatus.CALIBRATING

        try:
            # Simulate calibration process
            if self.simulation_mode:
                print("Calibrating fan speeds...")
                await asyncio.sleep(2.0)

                print("Measuring airflow patterns...")
                await asyncio.sleep(1.5)

                print("Adjusting for optimal barrier...")
                await asyncio.sleep(1.0)

            # Update calibration timestamp
            self.last_calibration = datetime.now()

            # Clear any calibration-related alerts
            self.maintenance_alerts = [
                alert
                for alert in self.maintenance_alerts
                if "calibration" not in alert.lower()
            ]

            self.status = AirCurtainStatus.READY
            print("Calibration complete")
            return True

        except Exception as e:
            self.status = AirCurtainStatus.ERROR
            print(f"Calibration failed: {e}")
            return False

    async def perform_maintenance(self) -> bool:
        """Perform routine maintenance."""
        if self.status != AirCurtainStatus.READY:
            print(f"Cannot perform maintenance when system is {self.status.name}")
            return False

        print("Starting air curtain maintenance")
        self.status = AirCurtainStatus.MAINTENANCE

        try:
            # Simulate maintenance process
            if self.simulation_mode:
                print("Cleaning fan blades...")
                await asyncio.sleep(1.5)

                print("Checking bearings...")
                await asyncio.sleep(1.0)

                print("Testing motor operation...")
                await asyncio.sleep(2.0)

                print("Verifying airflow sensors...")
                await asyncio.sleep(1.0)

            # Reset fan error counts and runtime tracking
            for fan in self.fans.values():
                fan.error_count = 0
                fan.status = "normal"
                # Note: We don't reset total_runtime_hours as that's lifetime tracking

            # Update maintenance timestamp
            self.last_maintenance = datetime.now()

            # Clear maintenance alerts
            self.maintenance_alerts = []

            self.status = AirCurtainStatus.READY
            print("Maintenance complete")
            return True

        except Exception as e:
            self.status = AirCurtainStatus.ERROR
            print(f"Maintenance failed: {e}")
            return False

    def get_performance_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get performance history."""
        history = self.performance_history[-limit:] if self.performance_history else []
        return [result.to_dict() for result in history]

    def get_effectiveness_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get barrier effectiveness history."""
        history = (
            self.barrier_effectiveness_history[-limit:]
            if self.barrier_effectiveness_history
            else []
        )
        return [asdict(result) for result in history]

    def clear_history(self) -> None:
        """Clear performance history."""
        self.performance_history = []
        self.barrier_effectiveness_history = []
        print("Performance history cleared")

    async def emergency_shutdown(self) -> None:
        """Emergency shutdown procedure."""
        print("EMERGENCY SHUTDOWN INITIATED")

        # Immediate fan stop
        for fan in self.fans.values():
            fan.rpm = 0
            fan.target_rpm = 0
            fan.current_a = 0.0
            fan.power_w = 0.0

        # Cancel tasks
        if self._control_task:
            self._control_task.cancel()
        if self._monitoring_task:
            self._monitoring_task.cancel()

        # Set error state
        self.status = AirCurtainStatus.ERROR
        self.mode = AirCurtainMode.OFF

        print("Emergency shutdown complete")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.status in [AirCurtainStatus.ACTIVE, AirCurtainStatus.STARTING]:
            await self.stop()


# Example usage and test function
async def test_air_curtain_system():
    """Test the air curtain system."""
    print("\n" + "=" * 60)
    print("TESTING AIR CURTAIN SYSTEM")
    print("=" * 60)

    # Create system
    config = AirCurtainConfig(
        fan_count=2,  # Fewer fans for testing
        max_rpm=2000,
        opening_width_mm=400.0,
        opening_height_mm=800.0,
    )

    system = AirCurtainSystem(config)

    try:
        # Test startup
        print("\n1. Testing startup...")
        result = await system.start(AirCurtainMode.STANDARD)
        print(f"   Startup result: {result.success}")
        print(f"   Mode: {result.mode.name}")
        print(f"   Status: {result.status.name}")

        # Run for a bit
        await asyncio.sleep(2.0)

        # Test mode change
        print("\n2. Testing mode change...")
        result = await system.change_mode(AirCurtainMode.HIGH_FLOW)
        print(f"   Mode change result: {result.success}")
        await asyncio.sleep(1.0)

        # Test fly detection
        print("\n3. Testing fly detection...")
        system.report_fly_detection(3)
        system.report_fly_detection(2)
        await asyncio.sleep(1.0)

        # Test barrier effectiveness measurement
        print("\n4. Testing barrier effectiveness...")
        effectiveness = await system.measure_barrier_effectiveness()
        print(f"   Effectiveness: {effectiveness.effectiveness_percent:.1f}%")
        print(f"   Fly penetration: {effectiveness.fly_penetration_count}")

        # Test status report
        print("\n5. Testing status report...")
        status = system.get_status_report()
        print(f"   System mode: {status['system']['mode']}")
        print(
            f"   Current airflow: {status['performance']['current_airflow_cfm']:.1f} CFM"
        )
        print(f"   Total fly blocks: {status['performance']['total_fly_block_count']}")

        # Test shutdown
        print("\n6. Testing shutdown...")
        result = await system.stop()
        print(f"   Shutdown result: {result.success}")
        print(f"   Duration: {result.duration_seconds:.1f}s")
        print(f"   Energy consumed: {result.energy_consumed_wh:.2f} Wh")

        # Test calibration
        print("\n7. Testing calibration...")
        calibrated = await system.calibrate()
        print(f"   Calibration result: {calibrated}")

        # Test maintenance
        print("\n8. Testing maintenance...")
        maintained = await system.perform_maintenance()
        print(f"   Maintenance result: {maintained}")

        print("\n" + "=" * 60)
        print("AIR CURTAIN SYSTEM TEST COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR during test: {e}")
        await system.emergency_shutdown()


if __name__ == "__main__":
    # Run test
    asyncio.run(test_air_curtain_system())

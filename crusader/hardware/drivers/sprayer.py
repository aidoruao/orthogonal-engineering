"""
Crusader Combat Refrigerator - Sprayer Driver
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Sprayer driver for peristaltic pump control.
Manages spore deployment with precise volume control and flow monitoring.
"""

import asyncio
import math
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

# In production, this would import RPi.GPIO
# import RPi.GPIO as GPIO


class SprayerStatus(Enum):
    """Sprayer status enumeration."""

    READY = auto()
    PUMPING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    OVERHEATED = auto()
    BLOCKED = auto()
    LOW_PRESSURE = auto()
    HIGH_PRESSURE = auto()


class PumpType(Enum):
    """Pump types."""

    PERISTALTIC = auto()
    DIAPHRAGM = auto()
    PISTON = auto()
    GEAR = auto()


@dataclass
class SprayerCalibration:
    """Sprayer calibration data."""

    calibration_id: str
    calibration_time: datetime
    flow_rate_ml_per_min: float
    pressure_psi: float
    voltage_v: float
    current_ma: float
    calibration_points: List[Tuple[float, float]]  # (PWM duty cycle, flow rate)
    linearity_error: float
    repeatability_error: float
    hysteresis: float
    metadata: Optional[Dict[str, Any]] = None

    def calculate_flow_rate(self, duty_cycle: float) -> float:
        """Calculate flow rate for given duty cycle."""
        if not self.calibration_points:
            return duty_cycle * self.flow_rate_ml_per_min / 100.0

        # Linear interpolation between calibration points
        sorted_points = sorted(self.calibration_points, key=lambda x: x[0])

        # Find surrounding points
        for i in range(len(sorted_points) - 1):
            dc1, fr1 = sorted_points[i]
            dc2, fr2 = sorted_points[i + 1]

            if dc1 <= duty_cycle <= dc2:
                # Linear interpolation
                fraction = (duty_cycle - dc1) / (dc2 - dc1)
                return fr1 + fraction * (fr2 - fr1)

        # Extrapolate if outside range
        if duty_cycle < sorted_points[0][0]:
            dc1, fr1 = sorted_points[0]
            dc2, fr2 = sorted_points[1]
            slope = (fr2 - fr1) / (dc2 - dc1)
            return fr1 + slope * (duty_cycle - dc1)
        else:
            dc1, fr1 = sorted_points[-2]
            dc2, fr2 = sorted_points[-1]
            slope = (fr2 - fr1) / (dc2 - dc1)
            return fr2 + slope * (duty_cycle - dc2)


@dataclass
class SprayerState:
    """Sprayer system state."""

    pump_type: PumpType
    flow_rate_ml_per_min: float
    max_pressure_psi: float
    current_pressure_psi: float
    temperature_celsius: float
    voltage_v: float
    current_ma: float
    total_volume_ml: float
    total_operating_hours: float
    pump_health_percent: float
    tube_health_percent: float
    last_maintenance: Optional[datetime]
    calibration: Optional[SprayerCalibration]
    metadata: Optional[Dict[str, Any]] = None

    def is_healthy(self) -> bool:
        """Check if sprayer is healthy."""
        return (
            self.pump_health_percent > 50.0
            and self.tube_health_percent > 30.0
            and self.temperature_celsius < 60.0
            and self.current_pressure_psi < self.max_pressure_psi * 0.8
        )


@dataclass
class SprayResult:
    """Result of a spray operation."""

    operation_id: str
    timestamp: datetime
    target_volume_ml: float
    actual_volume_ml: float
    duration_seconds: float
    flow_rate_ml_per_min: float
    pressure_psi: float
    status: SprayerStatus
    success: bool
    error_message: Optional[str] = None
    calibration_used: Optional[str] = None
    power_consumption_j: Optional[float] = None
    temperature_start_c: Optional[float] = None
    temperature_end_c: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["status"] = self.status.name
        return data


class SprayerDriver:
    """
    Sprayer driver for peristaltic pump control.
    Provides precise volume control, flow monitoring, and safety features.
    """

    # Hardware configuration
    DEFAULT_CONFIG = {
        "pump_type": "peristaltic",
        "gpio_pins": {
            "pump_pwm": 17,
            "valve_control": 27,
            "pressure_sensor": 22,
            "flow_sensor": 23,
            "temperature_sensor": 24,
            "enable_pin": 25,
        },
        "pump_specs": {
            "max_flow_rate_ml_per_min": 100.0,
            "max_pressure_psi": 30.0,
            "operating_voltage": 12.0,
            "max_current_ma": 2000,
            "pwm_frequency_hz": 1000,
            "min_duty_cycle": 10.0,  # Minimum reliable duty cycle
            "max_duty_cycle": 95.0,  # Maximum safe duty cycle
        },
        "safety_limits": {
            "max_temperature_c": 70.0,
            "max_pressure_psi": 35.0,
            "max_current_ma": 2500,
            "max_continuous_seconds": 300,
            "cooling_time_seconds": 60,
        },
        "calibration": {
            "auto_calibrate": True,
            "calibration_interval_hours": 24,
            "flow_tolerance_percent": 5.0,
            "pressure_tolerance_percent": 10.0,
        },
        "control": {
            "pid_enabled": True,
            "pid_kp": 1.0,
            "pid_ki": 0.1,
            "pid_kd": 0.01,
            "flow_smoothing": True,
            "smoothing_window": 10,
        },
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize sprayer driver."""
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

        # Hardware state
        self.hardware_initialized = False
        self.gpio_initialized = False

        # Sprayer state
        self.sprayer_state = SprayerState(
            pump_type=PumpType.PERISTALTIC,
            flow_rate_ml_per_min=self.config["pump_specs"]["max_flow_rate_ml_per_min"],
            max_pressure_psi=self.config["pump_specs"]["max_pressure_psi"],
            current_pressure_psi=0.0,
            temperature_celsius=25.0,
            voltage_v=self.config["pump_specs"]["operating_voltage"],
            current_ma=0.0,
            total_volume_ml=0.0,
            total_operating_hours=0.0,
            pump_health_percent=100.0,
            tube_health_percent=100.0,
            last_maintenance=None,
            calibration=None,
        )

        # Operation state
        self.current_operation: Optional[SprayResult] = None
        self.operation_lock = asyncio.Lock()
        self.operation_history: List[SprayResult] = []

        # Calibration
        self.calibration_history: List[SprayerCalibration] = []
        self.last_calibration_time: Optional[datetime] = None

        # PID controller state
        self.pid_state = {
            "last_error": 0.0,
            "integral": 0.0,
            "last_time": None,
            "setpoint": 0.0,
            "output": 0.0,
        }

        # Sensor buffers
        self.flow_buffer: List[float] = []
        self.pressure_buffer: List[float] = []
        self.temperature_buffer: List[float] = []

        # Statistics
        self.statistics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "total_volume_ml": 0.0,
            "total_energy_j": 0.0,
            "average_flow_rate": 0.0,
            "average_pressure": 0.0,
            "calibration_count": 0,
            "safety_interruptions": 0,
            "maintenance_events": 0,
        }

        # Safety state
        self.safety_state = {
            "overheat": False,
            "overpressure": False,
            "overcurrent": False,
            "blockage": False,
            "low_flow": False,
            "emergency_stop": False,
        }

    async def initialize(self) -> bool:
        """Initialize the sprayer driver."""
        print("🔧 Initializing Sprayer Driver...")

        try:
            # Initialize GPIO (simulated)
            await self._initialize_gpio()

            # Perform self-test
            self_test_passed = await self._perform_self_test()
            if not self_test_passed:
                print("❌ Sprayer self-test failed")
                return False

            # Load or create calibration
            await self._load_or_create_calibration()

            # Initialize PID controller
            self._initialize_pid()

            # Start monitoring task
            asyncio.create_task(self._monitoring_loop())

            self.hardware_initialized = True
            print(
                f"✅ Sprayer Driver initialized. Pump type: {self.sprayer_state.pump_type.name}"
            )
            return True

        except Exception as e:
            print(f"❌ Sprayer Driver initialization failed: {e}")
            return False

    async def _initialize_gpio(self):
        """Initialize GPIO pins."""
        print("  ↪️ Initializing GPIO pins...")

        # In production, this would initialize RPi.GPIO
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self.config["gpio_pins"]["pump_pwm"], GPIO.OUT)
        # GPIO.setup(self.config["gpio_pins"]["valve_control"], GPIO.OUT)
        # GPIO.setup(self.config["gpio_pins"]["enable_pin"], GPIO.OUT)

        # Initialize PWM
        # self.pwm = GPIO.PWM(self.config["gpio_pins"]["pump_pwm"],
        #                     self.config["pump_specs"]["pwm_frequency_hz"])

        await asyncio.sleep(0.1)  # Simulated initialization delay
        self.gpio_initialized = True
        print("  ✅ GPIO initialized")

    async def _perform_self_test(self) -> bool:
        """Perform self-test of sprayer system."""
        print("  ↪️ Performing self-test...")

        tests = [
            ("Pressure sensor", self._test_pressure_sensor),
            ("Flow sensor", self._test_flow_sensor),
            ("Temperature sensor", self._test_temperature_sensor),
            ("Valve control", self._test_valve_control),
            ("Pump motor", self._test_pump_motor),
        ]

        all_passed = True
        for test_name, test_func in tests:
            try:
                passed = await test_func()
                status = "✅" if passed else "❌"
                print(f"    {status} {test_name}")
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"    ❌ {test_name} error: {e}")
                all_passed = False

        return all_passed

    async def _test_pressure_sensor(self) -> bool:
        """Test pressure sensor."""
        # Simulated test
        await asyncio.sleep(0.05)

        # Read pressure (simulated)
        pressure = await self._read_pressure()

        # Check if reading is within reasonable range
        return 0.0 <= pressure <= 50.0

    async def _test_flow_sensor(self) -> bool:
        """Test flow sensor."""
        await asyncio.sleep(0.05)

        # Read flow (simulated)
        flow = await self._read_flow()

        # Check if reading is within reasonable range
        return 0.0 <= flow <= 200.0

    async def _test_temperature_sensor(self) -> bool:
        """Test temperature sensor."""
        await asyncio.sleep(0.05)

        # Read temperature (simulated)
        temp = await self._read_temperature()

        # Check if reading is within reasonable range
        return -10.0 <= temp <= 100.0

    async def _test_valve_control(self) -> bool:
        """Test valve control."""
        await asyncio.sleep(0.05)

        # Simulate valve operation
        try:
            # In production, this would toggle the valve
            # GPIO.output(self.config["gpio_pins"]["valve_control"], GPIO.HIGH)
            await asyncio.sleep(0.1)
            # GPIO.output(self.config["gpio_pins"]["valve_control"], GPIO.LOW)
            return True
        except:
            return False

    async def _test_pump_motor(self) -> bool:
        """Test pump motor."""
        await asyncio.sleep(0.05)

        # Simulate brief motor run
        try:
            # In production, this would run the pump briefly
            # self.pwm.start(10)  # 10% duty cycle
            await asyncio.sleep(0.2)
            # self.pwm.stop()
            return True
        except:
            return False

    async def _load_or_create_calibration(self):
        """Load existing calibration or create new one."""
        # In production, this would load from file
        # For now, create default calibration
        await self._create_default_calibration()

    async def _create_default_calibration(self):
        """Create default calibration."""
        print("  ↪️ Creating default calibration...")

        calibration_points = [
            (10.0, 5.0),  # 10% duty cycle -> 5 ml/min
            (25.0, 15.0),  # 25% duty cycle -> 15 ml/min
            (50.0, 35.0),  # 50% duty cycle -> 35 ml/min
            (75.0, 60.0),  # 75% duty cycle -> 60 ml/min
            (95.0, 85.0),  # 95% duty cycle -> 85 ml/min
        ]

        calibration = SprayerCalibration(
            calibration_id="default_calibration",
            calibration_time=datetime.now(),
            flow_rate_ml_per_min=85.0,
            pressure_psi=15.0,
            voltage_v=12.0,
            current_ma=800.0,
            calibration_points=calibration_points,
            linearity_error=2.5,
            repeatability_error=1.0,
            hysteresis=1.5,
        )

        self.sprayer_state.calibration = calibration
        self.calibration_history.append(calibration)
        self.last_calibration_time = datetime.now()

        print("  ✅ Default calibration created")

    def _initialize_pid(self):
        """Initialize PID controller."""
        self.pid_state = {
            "last_error": 0.0,
            "integral": 0.0,
            "last_time": time.time(),
            "setpoint": 0.0,
            "output": 0.0,
        }

    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.hardware_initialized:
            try:
                await self._update_sensor_readings()
                await self._check_safety_conditions()
                await self._update_sprayer_health()
                await asyncio.sleep(0.1)  # 10 Hz monitoring
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Error in sprayer monitoring loop: {e}")
                await asyncio.sleep(1.0)

    async def _update_sensor_readings(self):
        """Update sensor readings."""
        # Read all sensors
        pressure = await self._read_pressure()
        flow = await self._read_flow()
        temperature = await self._read_temperature()
        voltage = await self._read_voltage()
        current = await self._read_current()

        # Update buffers
        self.pressure_buffer.append(pressure)
        self.flow_buffer.append(flow)
        self.temperature_buffer.append(temperature)

        # Keep buffer sizes manageable
        max_buffer = 100
        if len(self.pressure_buffer) > max_buffer:
            self.pressure_buffer = self.pressure_buffer[-max_buffer:]
        if len(self.flow_buffer) > max_buffer:
            self.flow_buffer = self.flow_buffer[-max_buffer:]
        if len(self.temperature_buffer) > max_buffer:
            self.temperature_buffer = self.temperature_buffer[-max_buffer:]

        # Update sprayer state
        self.sprayer_state.current_pressure_psi = pressure
        self.sprayer_state.flow_rate_ml_per_min = flow
        self.sprayer_state.temperature_celsius = temperature
        self.sprayer_state.voltage_v = voltage
        self.sprayer_state.current_ma = current

    async def _check_safety_conditions(self):
        """Check safety conditions."""
        config = self.sprayer_config

        # Check temperature
        if self.sprayer_state.temperature_celsius > config.max_temperature_c:
            await self._handle_safety_issue("overheating")
            return False

        # Check pressure
        if self.sprayer_state.current_pressure_psi > config.max_pressure_psi:
            await self._handle_safety_issue("high_pressure")
            return False

        # Check flow rate
        if self.sprayer_state.flow_rate_ml_per_min > config.max_flow_rate_ml_per_min:
            await self._handle_safety_issue("high_flow")
            return False

        return True

    async def _handle_safety_issue(self, issue_type: str):
        """Handle safety issues."""
        print(f"⚠️ Safety issue detected: {issue_type}")

        # Stop pumping immediately
        await self.stop_pumping()

        # Update sprayer state
        self.sprayer_state.status = SprayerStatus.FAILED

        # Record safety event
        safety_event = {
            "timestamp": datetime.now().isoformat(),
            "issue_type": issue_type,
            "temperature": self.sprayer_state.temperature_celsius,
            "pressure": self.sprayer_state.current_pressure_psi,
            "flow_rate": self.sprayer_state.flow_rate_ml_per_min,
        }
        self.safety_events.append(safety_event)

        # Keep only last 100 events
        if len(self.safety_events) > 100:
            self.safety_events = self.safety_events[-100:]

    async def _update_sprayer_health(self):
        """Update sprayer health metrics."""
        # Calculate health score based on various factors
        health_factors = []

        # Temperature factor (0-1, 1 is best)
        temp_norm = max(0, 1 - (self.sprayer_state.temperature_celsius / 100))
        health_factors.append(temp_norm)

        # Pressure factor
        if self.sprayer_config.max_pressure_psi > 0:
            pressure_norm = max(
                0,
                1
                - (
                    self.sprayer_state.current_pressure_psi
                    / self.sprayer_config.max_pressure_psi
                ),
            )
            health_factors.append(pressure_norm)

        # Flow factor
        if self.sprayer_config.max_flow_rate_ml_per_min > 0:
            flow_norm = max(
                0,
                1
                - (
                    self.sprayer_state.flow_rate_ml_per_min
                    / self.sprayer_config.max_flow_rate_ml_per_min
                ),
            )
            health_factors.append(flow_norm)

        # Calculate overall health (0-100)
        if health_factors:
            avg_health = sum(health_factors) / len(health_factors)
            self.sprayer_state.health_score = int(avg_health * 100)
        else:
            self.sprayer_state.health_score = 100

        # Update health status
        if self.sprayer_state.health_score >= 80:
            self.sprayer_state.health_status = "EXCELLENT"
        elif self.sprayer_state.health_score >= 60:
            self.sprayer_state.health_status = "GOOD"
        elif self.sprayer_state.health_score >= 40:
            self.sprayer_state.health_status = "FAIR"
        elif self.sprayer_state.health_score >= 20:
            self.sprayer_state.health_status = "POOR"
        else:
            self.sprayer_state.health_status = "CRITICAL"

    def get_status(self) -> Dict[str, Any]:
        """Get current sprayer status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "status": self.sprayer_state.status.name,
            "health_score": self.sprayer_state.health_score,
            "health_status": self.sprayer_state.health_status,
            "temperature_c": self.sprayer_state.temperature_celsius,
            "pressure_psi": self.sprayer_state.current_pressure_psi,
            "flow_rate_ml_per_min": self.sprayer_state.flow_rate_ml_per_min,
            "voltage_v": self.sprayer_state.voltage_v,
            "current_ma": self.sprayer_state.current_ma,
            "total_volume_ml": self.sprayer_state.total_volume_ml,
            "total_operations": self.sprayer_state.total_operations,
            "safety_events": len(self.safety_events),
            "hardware_initialized": self.hardware_initialized,
        }

    def get_health_report(self) -> Dict[str, Any]:
        """Get detailed health report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "sprayer_state": asdict(self.sprayer_state),
            "recent_safety_events": self.safety_events[-10:]
            if self.safety_events
            else [],
            "pressure_history": list(self.pressure_buffer)[-20:],
            "flow_history": list(self.flow_buffer)[-20:],
            "temperature_history": list(self.temperature_buffer)[-20:],
            "config": asdict(self.sprayer_config),
        }

    async def cleanup(self):
        """Clean up resources."""
        self.hardware_initialized = False

        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        # Reset state
        self.sprayer_state.status = SprayerStatus.READY
        self.sprayer_state.current_pressure_psi = 0.0
        self.sprayer_state.flow_rate_ml_per_min = 0.0
        self.sprayer_state.temperature_celsius = 25.0

        print("✅ Sprayer driver cleaned up")


# SprayerResult class definition
@dataclass
class SprayerResult:
    """Result of a sprayer operation."""

    success: bool
    operation_id: str
    status: SprayerStatus
    volume_ml: float
    duration_seconds: float
    message: str
    timestamp: datetime
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "operation_id": self.operation_id,
            "status": self.status.name,
            "volume_ml": self.volume_ml,
            "duration_seconds": self.duration_seconds,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


# Convenience function for creating sprayer results
def create_sprayer_result(
    success: bool,
    operation_id: str,
    status: SprayerStatus,
    volume_ml: float = 0.0,
    duration_seconds: float = 0.0,
    message: str = "",
    details: Optional[Dict[str, Any]] = None,
) -> SprayerResult:
    """Create a sprayer result."""
    return SprayerResult(
        success=success,
        operation_id=operation_id,
        status=status,
        volume_ml=volume_ml,
        duration_seconds=duration_seconds,
        message=message,
        timestamp=datetime.now(),
        details=details or {},
    )


if __name__ == "__main__":
    # Test the sprayer driver
    import asyncio

    async def test_sprayer():
        """Test the sprayer driver."""
        print("Testing Sprayer Driver...")

        # Create sprayer configuration
        config = SprayerConfig(
            pump_type=PumpType.PERISTALTIC,
            max_flow_rate_ml_per_min=100.0,
            max_pressure_psi=30.0,
            max_temperature_c=60.0,
            calibration_factor=1.0,
            min_volume_ml=0.1,
            max_volume_ml=10.0,
        )

        # Create sprayer driver
        sprayer = SprayerDriver(config)

        try:
            # Initialize
            success = await sprayer.initialize()
            if not success:
                print("❌ Failed to initialize sprayer")
                return

            print("✅ Sprayer initialized")

            # Get status
            status = sprayer.get_status()
            print(f"Status: {status}")

            # Test pumping
            result = await sprayer.pump_volume(5.0, "test_operation")
            print(f"Pump result: {result}")

            # Get health report
            health = sprayer.get_health_report()
            print(f"Health report keys: {list(health.keys())}")

        finally:
            # Cleanup
            await sprayer.cleanup()
            print("✅ Test completed")

    # Run test
    asyncio.run(test_sprayer())

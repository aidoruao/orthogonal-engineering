"""
Crusader Combat Refrigerator - Sensor Manager
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Sensor management system for monitoring environmental and system conditions.
Provides unified interface for all sensors, calibration, and data validation.
"""

import asyncio
import math
import random
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from ..core.constants import EnvironmentalConstants, GPIOPins, SensorType


class SensorStatus(Enum):
    """Sensor status enumeration."""

    ONLINE = auto()
    OFFLINE = auto()
    CALIBRATING = auto()
    ERROR = auto()
    DEGRADED = auto()
    OVERRANGE = auto()
    UNDERRANGE = auto()


class SensorCalibrationState(Enum):
    """Sensor calibration states."""

    UNCALIBRATED = auto()
    CALIBRATING = auto()
    CALIBRATED = auto()
    DRIFT_DETECTED = auto()
    REQUIRES_RECALIBRATION = auto()


@dataclass
class SensorReading:
    """Individual sensor reading."""

    sensor_id: str
    sensor_type: SensorType
    timestamp: datetime
    value: float
    unit: str
    status: SensorStatus
    confidence: float  # 0.0 to 1.0
    raw_value: Optional[float] = None
    calibrated_value: Optional[float] = None
    error_margin: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SensorCalibration:
    """Sensor calibration data."""

    sensor_id: str
    calibration_time: datetime
    calibration_type: str
    offset: float
    gain: float
    linearity_error: float
    temperature_coefficient: float
    calibration_points: List[Tuple[float, float]]
    valid_until: Optional[datetime] = None


@dataclass
class SensorInfo:
    """Sensor information."""

    sensor_id: str
    sensor_type: SensorType
    gpio_pin: Optional[int]
    model: str
    manufacturer: str
    serial_number: str
    installed_date: datetime
    last_maintenance: Optional[datetime]
    requires_calibration: bool
    calibration_interval_days: int


@dataclass
class SensorHealth:
    """Sensor health information."""

    sensor_id: str
    uptime_seconds: float
    total_readings: int
    error_count: int
    last_error: Optional[datetime]
    calibration_state: SensorCalibrationState
    last_calibration: Optional[datetime]
    calibration_drift: float  # Percentage drift since last calibration
    response_time_ms: float
    average_confidence: float


class SensorManager:
    """
    Unified sensor management system.
    Handles sensor initialization, reading, calibration, and health monitoring.
    """

    # Sensor configuration templates
    SENSOR_CONFIGS = {
        SensorType.TEMPERATURE: {
            "model": "DS18B20",
            "precision": 0.5,  # °C
            "range": (-40.0, 125.0),
            "unit": "°C",
            "requires_calibration": True,
            "calibration_interval_days": 90,
        },
        SensorType.HUMIDITY: {
            "model": "DHT22",
            "precision": 2.0,  # %
            "range": (0.0, 100.0),
            "unit": "%",
            "requires_calibration": True,
            "calibration_interval_days": 180,
        },
        SensorType.MOTION: {
            "model": "HC-SR501",
            "precision": 1.0,
            "range": (0.0, 1.0),
            "unit": "binary",
            "requires_calibration": False,
            "calibration_interval_days": 365,
        },
        SensorType.DOOR: {
            "model": "Magnetic Reed Switch",
            "precision": 1.0,
            "range": (0.0, 1.0),
            "unit": "binary",
            "requires_calibration": False,
            "calibration_interval_days": 365,
        },
        SensorType.OPTICAL: {
            "model": "IR Sensor Array",
            "precision": 0.1,
            "range": (0.0, 100.0),
            "unit": "intensity",
            "requires_calibration": True,
            "calibration_interval_days": 30,
        },
    }

    def __init__(self, simulation_mode: bool = False):
        """Initialize sensor manager."""
        self.simulation_mode = simulation_mode
        self.sensors: Dict[str, SensorInfo] = {}
        self.sensor_health: Dict[str, SensorHealth] = {}
        self.calibrations: Dict[str, SensorCalibration] = {}
        self.reading_buffers: Dict[str, List[float]] = {}
        self.statistics: Dict[str, int] = {
            "total_readings": 0,
            "successful_readings": 0,
            "failed_readings": 0,
            "sensor_errors": 0,
            "calibrations_performed": 0,
        }
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize all sensors."""
        if self._initialized:
            return True

        try:
            # Initialize each sensor type
            for sensor_type, config in self.SENSOR_CONFIGS.items():
                sensor_id = f"{sensor_type.name.lower()}_sensor"

                # Create sensor info
                self.sensors[sensor_id] = SensorInfo(
                    sensor_id=sensor_id,
                    sensor_type=sensor_type,
                    gpio_pin=self._get_gpio_pin_for_sensor(sensor_type),
                    model=config["model"],
                    manufacturer="Orthogonal Engineering",
                    serial_number=f"OE-{sensor_type.name}-{int(time.time())}",
                    installed_date=datetime.now(),
                    last_maintenance=None,
                    requires_calibration=config["requires_calibration"],
                    calibration_interval_days=config["calibration_interval_days"],
                )

                # Initialize health
                self.sensor_health[sensor_id] = SensorHealth(
                    sensor_id=sensor_id,
                    uptime_seconds=0.0,
                    total_readings=0,
                    error_count=0,
                    last_error=None,
                    calibration_state=SensorCalibrationState.UNCALIBRATED,
                    last_calibration=None,
                    calibration_drift=0.0,
                    response_time_ms=0.0,
                    average_confidence=1.0,
                )

                # Initialize reading buffer
                self.reading_buffers[sensor_id] = []

            self._initialized = True
            return True

        except Exception as e:
            print(f"Failed to initialize sensors: {e}")
            return False

    async def read_sensor(self, sensor_id: str) -> Optional[SensorReading]:
        """Read a specific sensor."""
        if not self._initialized:
            await self.initialize()

        if sensor_id not in self.sensors:
            return None

        sensor_info = self.sensors[sensor_id]
        sensor_type = sensor_info.sensor_type
        config = self.SENSOR_CONFIGS.get(sensor_type, {})

        try:
            start_time = time.time()

            # Get raw reading
            if self.simulation_mode:
                raw_value = await self._simulate_sensor_reading(sensor_type)
            else:
                raw_value = await self._read_physical_sensor(sensor_id, sensor_type)

            # Validate reading
            is_valid, status, confidence = await self._validate_reading(
                sensor_id, raw_value, sensor_type
            )

            # Apply calibration if available
            calibrated_value = raw_value
            if sensor_id in self.calibrations:
                calibrated_value = self._apply_calibration(sensor_id, raw_value)

            # Create reading object
            reading = SensorReading(
                sensor_id=sensor_id,
                sensor_type=sensor_type,
                timestamp=datetime.now(),
                value=calibrated_value,
                unit=config.get("unit", "unknown"),
                status=status,
                confidence=confidence,
                raw_value=raw_value,
                calibrated_value=calibrated_value
                if sensor_id in self.calibrations
                else None,
                error_margin=config.get("precision"),
                metadata={
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "sensor_model": config["model"],
                },
            )

            # Update buffer
            self._update_reading_buffer(sensor_id, calibrated_value)

            # Update sensor info
            sensor_info["last_reading"] = reading
            sensor_info["last_reading_time"] = reading.timestamp

            # Update health
            self._update_sensor_health(sensor_id, reading, start_time)

            # Update statistics
            self.statistics["total_readings"] += 1
            self.statistics["successful_readings"] += 1

            return reading

        except Exception as e:
            # Update error statistics
            self.statistics["failed_readings"] += 1
            self.statistics["sensor_errors"] += 1

            # Update health
            health = self.sensor_health[sensor_id]
            health.error_count += 1
            health.last_error = datetime.now()

            # Create error reading
            return SensorReading(
                sensor_id=sensor_id,
                sensor_type=sensor_type,
                timestamp=datetime.now(),
                value=0.0,
                unit="error",
                status=SensorStatus.ERROR,
                confidence=0.0,
                error_margin=None,
                metadata={"error": str(e)},
            )

    async def _simulate_sensor_reading(self, sensor_type: SensorType) -> float:
        """Simulate sensor reading with realistic values."""
        # Simulate reading delay
        await asyncio.sleep(0.01)

        # Generate realistic values based on sensor type
        if sensor_type == SensorType.TEMPERATURE:
            # Normal refrigerator temperature with slight variation
            base_temp = 4.0
            variation = random.uniform(-0.5, 0.5)
            return base_temp + variation

        elif sensor_type == SensorType.HUMIDITY:
            # Normal refrigerator humidity
            base_humidity = 65.0
            variation = random.uniform(-3.0, 3.0)
            return base_humidity + variation

        elif sensor_type == SensorType.MOTION:
            # Binary motion detection (0 or 1)
            # 10% chance of motion
            return 1.0 if random.random() < 0.1 else 0.0

        elif sensor_type == SensorType.DOOR:
            # Binary door status (0=closed, 1=open)
            # 5% chance door is open
            return 1.0 if random.random() < 0.05 else 0.0

        elif sensor_type == SensorType.OPTICAL:
            # Simulated fly detection (0-100 intensity)
            return random.uniform(0.0, 10.0)

        else:
            return 0.0

    async def _read_physical_sensor(
        self, sensor_id: str, sensor_type: SensorType
    ) -> float:
        """Read from physical sensor hardware."""
        # This would interface with actual hardware
        # For now, simulate with some noise
        await asyncio.sleep(0.02)

        # Base values with some noise
        base_values = {
            SensorType.TEMPERATURE: 4.0,
            SensorType.HUMIDITY: 65.0,
            SensorType.MOTION: 0.0,
            SensorType.DOOR: 0.0,
            SensorType.OPTICAL: 0.0,
        }

        base = base_values.get(sensor_type, 0.0)
        noise = random.uniform(-0.1, 0.1)
        return base + noise

    async def _validate_reading(
        self, sensor_id: str, value: float, sensor_type: SensorType
    ) -> Tuple[bool, SensorStatus, float]:
        """Validate sensor reading."""
        # Check for extreme values
        config = self.SENSOR_CONFIGS.get(sensor_type, {})
        if "range" in config:
            min_val, max_val = config["range"]
            if value < min_val * 0.8 or value > max_val * 1.2:
                return False, SensorStatus.ERROR, 0.0

        # Check buffer consistency
        buffer = self.reading_buffers.get(sensor_id, [])
        if len(buffer) >= 3:
            avg = statistics.mean(buffer)
            std = statistics.stdev(buffer) if len(buffer) > 1 else 0

            # Check for sudden jumps
            if abs(value - avg) > 3 * std and std > 0:
                return True, SensorStatus.DEGRADED, 0.7

        # Calculate confidence based on sensor type and recent performance
        confidence = 0.95  # Base confidence

        # Reduce confidence for sensors requiring calibration
        if config.get("requires_calibration", False):
            health = self.sensor_health.get(sensor_id)
            if (
                health
                and health.calibration_state == SensorCalibrationState.DRIFT_DETECTED
            ):
                confidence *= 0.7  # Reduce confidence by 30%
            elif (
                health
                and health.calibration_state
                == SensorCalibrationState.REQUIRES_RECALIBRATION
            ):
                confidence *= 0.5  # Reduce confidence by 50%

        # Reduce confidence based on sensor age
        sensor_info = self.sensors.get(sensor_id)
        if sensor_info:
            days_installed = (datetime.now() - sensor_info.installed_date).days
            if days_installed > 365:  # More than 1 year old
                confidence *= 0.9  # Reduce by 10%
            elif days_installed > 730:  # More than 2 years old
                confidence *= 0.8  # Reduce by 20%

        # Ensure confidence is within bounds
        confidence = max(0.0, min(1.0, confidence))

        # Determine status
        if confidence < 0.5:
            status = SensorStatus.DEGRADED
        elif confidence < 0.8:
            status = SensorStatus.ONLINE
        else:
            status = SensorStatus.ONLINE

        return True, status, confidence

    def _apply_calibration(self, sensor_id: str, raw_value: float) -> float:
        """Apply calibration to raw sensor reading."""
        if sensor_id not in self.calibrations:
            return raw_value

        calibration = self.calibrations[sensor_id]

        # Simple linear calibration: calibrated = gain * raw + offset
        calibrated = calibration.gain * raw_value + calibration.offset

        # Apply temperature compensation if available
        # (simplified - would use actual temperature reading)

        return calibrated

    def _update_reading_buffer(self, sensor_id: str, value: float):
        """Update reading buffer for a sensor."""
        buffer = self.reading_buffers.get(sensor_id, [])
        buffer.append(value)

        # Keep only last 10 readings
        if len(buffer) > 10:
            buffer.pop(0)

        self.reading_buffers[sensor_id] = buffer

    def _update_sensor_health(
        self, sensor_id: str, reading: SensorReading, start_time: float
    ):
        """Update sensor health information."""
        health = self.sensor_health[sensor_id]

        # Update uptime
        health.uptime_seconds += time.time() - start_time

        # Update reading count
        health.total_readings += 1

        # Update response time (moving average)
        response_time = (time.time() - start_time) * 1000
        health.response_time_ms = health.response_time_ms * 0.9 + response_time * 0.1

        # Update average confidence (moving average)
        health.average_confidence = (
            health.average_confidence * 0.9 + reading.confidence * 0.1
        )

        # Update calibration drift if calibrated
        if reading.calibrated_value is not None and reading.raw_value is not None:
            if reading.raw_value != 0:
                drift = abs(reading.calibrated_value - reading.raw_value) / abs(
                    reading.raw_value
                )
                health.calibration_drift = max(health.calibration_drift, drift)

    async def calibrate_sensor(self, sensor_id: str) -> bool:
        """Calibrate a sensor."""
        if sensor_id not in self.sensors:
            return False

        sensor_info = self.sensors[sensor_id]

        try:
            # Collect calibration points
            calibration_points = []
            for _ in range(5):
                if self.simulation_mode:
                    reading = await self._simulate_sensor_reading(
                        sensor_info.sensor_type
                    )
                else:
                    reading = await self._read_physical_sensor(
                        sensor_id, sensor_info.sensor_type
                    )
                calibration_points.append(
                    (reading, reading)
                )  # Simplified - would use reference values
                await asyncio.sleep(0.1)

            # Calculate calibration parameters (simplified)
            # In reality, this would perform linear regression against reference values
            offset = 0.0
            gain = 1.0
            linearity_error = 0.01
            temperature_coefficient = 0.001

            # Create calibration record
            calibration = SensorCalibration(
                sensor_id=sensor_id,
                calibration_time=datetime.now(),
                calibration_type="auto",
                offset=offset,
                gain=gain,
                linearity_error=linearity_error,
                temperature_coefficient=temperature_coefficient,
                calibration_points=calibration_points,
                valid_until=datetime.now()
                + timedelta(days=sensor_info.calibration_interval_days),
            )

            self.calibrations[sensor_id] = calibration

            # Update health
            health = self.sensor_health[sensor_id]
            health.calibration_state = SensorCalibrationState.CALIBRATED
            health.last_calibration = datetime.now()
            health.calibration_drift = 0.0

            # Update statistics
            self.statistics["calibrations_performed"] += 1

            return True

        except Exception as e:
            print(f"Calibration failed for {sensor_id}: {e}")
            return False

    async def get_sensor_readings(self) -> Dict[str, SensorReading]:
        """Get readings from all sensors."""
        readings = {}
        tasks = []

        for sensor_id in self.sensors:
            task = self.read_sensor(sensor_id)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for sensor_id, result in zip(self.sensors.keys(), results):
            if isinstance(result, Exception):
                print(f"Error reading sensor {sensor_id}: {result}")
                # Create error reading
                readings[sensor_id] = SensorReading(
                    sensor_id=sensor_id,
                    sensor_type=self.sensors[sensor_id].sensor_type,
                    timestamp=datetime.now(),
                    value=0.0,
                    unit="error",
                    status=SensorStatus.ERROR,
                    confidence=0.0,
                    raw_value=None,
                    calibrated_value=None,
                    error_margin=None,
                    metadata={"error": str(result)},
                )
            elif result is not None:
                readings[sensor_id] = result

        return readings

    def get_statistics(self) -> Dict[str, Any]:
        """Get sensor manager statistics."""
        return {
            **self.statistics,
            "total_sensors": len(self.sensors),
            "calibrated_sensors": len(self.calibrations),
            "initialized": self._initialized,
        }

    def get_sensor_health(self, sensor_id: str) -> Optional[SensorHealth]:
        """Get health information for a sensor."""
        return self.sensor_health.get(sensor_id)

    def get_all_sensor_health(self) -> Dict[str, SensorHealth]:
        """Get health information for all sensors."""
        return self.sensor_health.copy()

    def _get_gpio_pin_for_sensor(self, sensor_type) -> Optional[int]:
        """Get GPIO pin for a sensor type."""
        # Map SensorType to GPIOPins
        sensor_to_gpio = {
            SensorType.TEMPERATURE: GPIOPins.TEMPERATURE_SENSOR,
            SensorType.HUMIDITY: GPIOPins.HUMIDITY_SENSOR,
            SensorType.MOTION: GPIOPins.MOTION_SENSOR,
            SensorType.DOOR: GPIOPins.DOOR_SENSOR,
            SensorType.OPTICAL: None,  # No specific GPIO pin for optical sensor
        }

        gpio_enum = sensor_to_gpio.get(sensor_type)
        if gpio_enum is not None:
            return gpio_enum.value
        return None

    async def shutdown(self):
        """Shutdown sensor manager."""
        print("Shutting down Sensor Manager...")
        self._initialized = False
        # Clear buffers
        self.reading_buffers.clear()
        print("Sensor Manager shutdown complete")

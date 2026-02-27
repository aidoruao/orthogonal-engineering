"""
Crusader Combat Refrigerator - Sensor Check Module
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Sensor diagnostics and validation system for the Crusader Combat Refrigerator.
Provides sensor health checks, calibration verification, and data validation.
"""

import asyncio
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


class SensorStatus(Enum):
    """Sensor status codes."""

    HEALTHY = auto()  # Sensor is functioning normally
    DEGRADED = auto()  # Sensor is functioning but with reduced accuracy
    FAULTY = auto()  # Sensor is malfunctioning
    OFFLINE = auto()  # Sensor is not responding
    CALIBRATING = auto()  # Sensor is undergoing calibration
    UNKNOWN = auto()  # Sensor status unknown


class SensorType(Enum):
    """Types of sensors in the system."""

    TEMPERATURE = auto()  # Temperature sensor
    HUMIDITY = auto()  # Humidity sensor
    MOTION = auto()  # Motion/PIR sensor
    LIGHT = auto()  # Light sensor
    PRESSURE = auto()  # Atmospheric pressure sensor
    DOOR = auto()  # Door open/close sensor
    FLY_COUNT = auto()  # Fly detection/counting sensor
    AIR_FLOW = auto()  # Air flow sensor
    UV_INTENSITY = auto()  # UV light intensity sensor
    SPORE_LEVEL = auto()  # Spore reservoir level sensor


@dataclass
class SensorReading:
    """A single sensor reading."""

    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    sensor_id: str
    confidence: float  # 0.0 to 1.0 confidence in reading

    def to_dict(self) -> Dict[str, Any]:
        """Convert reading to dictionary."""
        return {
            "sensor_type": self.sensor_type.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "sensor_id": self.sensor_id,
            "confidence": self.confidence,
        }


@dataclass
class SensorHealth:
    """Sensor health information."""

    sensor_id: str
    sensor_type: SensorType
    status: SensorStatus
    last_reading: Optional[SensorReading]
    uptime_seconds: float
    error_count: int
    calibration_due: Optional[datetime]
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert health info to dictionary."""
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type.name,
            "status": self.status.name,
            "last_reading": self.last_reading.to_dict() if self.last_reading else None,
            "uptime_seconds": self.uptime_seconds,
            "error_count": self.error_count,
            "calibration_due": (
                self.calibration_due.isoformat() if self.calibration_due else None
            ),
            "metrics": self.metrics,
        }


class SensorDiagnostics:
    """
    Sensor diagnostics system.
    Monitors sensor health, validates readings, and provides calibration support.
    """

    def __init__(self):
        self.sensors: Dict[str, SensorHealth] = {}
        self.reading_history: Dict[str, List[SensorReading]] = {}
        self.calibration_data: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now()

    def register_sensor(
        self,
        sensor_id: str,
        sensor_type: SensorType,
        initial_status: SensorStatus = SensorStatus.UNKNOWN,
    ) -> None:
        """Register a new sensor with the diagnostics system."""
        self.sensors[sensor_id] = SensorHealth(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            status=initial_status,
            last_reading=None,
            uptime_seconds=0.0,
            error_count=0,
            calibration_due=None,
            metrics={
                "total_readings": 0,
                "valid_readings": 0,
                "invalid_readings": 0,
                "average_confidence": 0.0,
                "last_error": None,
            },
        )
        self.reading_history[sensor_id] = []

    async def record_reading(self, reading: SensorReading) -> bool:
        """
        Record a sensor reading and update diagnostics.
        Returns True if reading is valid, False otherwise.
        """
        sensor_id = reading.sensor_id

        if sensor_id not in self.sensors:
            self.register_sensor(sensor_id, reading.sensor_type)

        sensor = self.sensors[sensor_id]

        # Validate reading
        is_valid = await self._validate_reading(reading, sensor)

        # Update sensor health
        sensor.last_reading = reading
        sensor.uptime_seconds = (datetime.now() - self.start_time).total_seconds()

        # Update metrics
        metrics = sensor.metrics
        metrics["total_readings"] += 1

        if is_valid:
            metrics["valid_readings"] += 1
            # Update average confidence
            current_avg = metrics["average_confidence"]
            total_valid = metrics["valid_readings"]
            metrics["average_confidence"] = (
                current_avg * (total_valid - 1) + reading.confidence
            ) / total_valid

            # Update sensor status based on confidence
            if reading.confidence >= 0.9:
                sensor.status = SensorStatus.HEALTHY
            elif reading.confidence >= 0.7:
                sensor.status = SensorStatus.DEGRADED
            else:
                sensor.status = SensorStatus.FAULTY
        else:
            metrics["invalid_readings"] += 1
            sensor.error_count += 1
            metrics["last_error"] = datetime.now().isoformat()

            # Update sensor status based on error count
            if sensor.error_count > 10:
                sensor.status = SensorStatus.FAULTY
            elif sensor.error_count > 5:
                sensor.status = SensorStatus.DEGRADED

        # Store reading in history (keep last 100 readings)
        history = self.reading_history[sensor_id]
        history.append(reading)
        if len(history) > 100:
            history.pop(0)

        return is_valid

    async def _validate_reading(
        self, reading: SensorReading, sensor: SensorHealth
    ) -> bool:
        """Validate a sensor reading."""
        # Check basic validity
        if reading.confidence < 0.0 or reading.confidence > 1.0:
            return False

        # Check for NaN or infinite values
        if not isinstance(reading.value, (int, float)):
            return False
        if reading.value == float("inf") or reading.value == float("-inf"):
            return False

        # Type-specific validation
        if sensor.sensor_type == SensorType.TEMPERATURE:
            # Refrigerator temperatures should be between -20°C and 50°C
            if reading.value < -20.0 or reading.value > 50.0:
                return False
            if reading.unit not in ["C", "F", "K"]:
                return False

        elif sensor.sensor_type == SensorType.HUMIDITY:
            # Humidity should be between 0% and 100%
            if reading.value < 0.0 or reading.value > 100.0:
                return False
            if reading.unit != "%":
                return False

        elif sensor.sensor_type == SensorType.DOOR:
            # Door sensor should be 0 (closed) or 1 (open)
            if reading.value not in [0.0, 1.0]:
                return False

        elif sensor.sensor_type == SensorType.FLY_COUNT:
            # Fly count should be non-negative integer
            if reading.value < 0 or not float(reading.value).is_integer():
                return False

        # Check for sudden jumps (if we have history)
        history = self.reading_history.get(sensor.sensor_id, [])
        if len(history) >= 3:
            recent_values = [r.value for r in history[-3:]]
            avg_recent = statistics.mean(recent_values)

            # Calculate maximum allowed change based on sensor type
            max_change = self._get_max_allowed_change(sensor.sensor_type)

            if abs(reading.value - avg_recent) > max_change:
                # Reading is a sudden jump, might be invalid
                if reading.confidence < 0.5:
                    return False

        return True

    def _get_max_allowed_change(self, sensor_type: SensorType) -> float:
        """Get maximum allowed change between readings for a sensor type."""
        max_changes = {
            SensorType.TEMPERATURE: 5.0,  # °C
            SensorType.HUMIDITY: 20.0,  # %
            SensorType.MOTION: float("inf"),  # Binary sensor
            SensorType.LIGHT: 1000.0,  # Lux
            SensorType.PRESSURE: 10.0,  # hPa
            SensorType.DOOR: float("inf"),  # Binary sensor
            SensorType.FLY_COUNT: 50.0,  # Count
            SensorType.AIR_FLOW: 2.0,  # m/s
            SensorType.UV_INTENSITY: 0.5,  # W/m²
            SensorType.SPORE_LEVEL: 100.0,  # ml
        }
        return max_changes.get(sensor_type, float("inf"))

    async def calibrate_sensor(self, sensor_id: str) -> Dict[str, Any]:
        """Calibrate a sensor."""
        if sensor_id not in self.sensors:
            return {"success": False, "error": f"Sensor not found: {sensor_id}"}

        sensor = self.sensors[sensor_id]
        sensor.status = SensorStatus.CALIBRATING

        try:
            # Simulate calibration process
            await asyncio.sleep(2.0)  # Calibration takes time

            # Update calibration data
            self.calibration_data[sensor_id] = {
                "calibration_time": datetime.now().isoformat(),
                "sensor_type": sensor.sensor_type.name,
                "pre_calibration_status": sensor.status.name,
            }

            # Set next calibration due date (30 days from now)
            sensor.calibration_due = datetime.now() + timedelta(days=30)

            # Reset error count and improve status
            sensor.error_count = 0
            sensor.status = SensorStatus.HEALTHY

            # Update metrics
            sensor.metrics["last_calibration"] = datetime.now().isoformat()

            return {
                "success": True,
                "sensor_id": sensor_id,
                "calibration_time": datetime.now().isoformat(),
                "next_calibration_due": sensor.calibration_due.isoformat(),
            }

        except Exception as e:
            sensor.status = SensorStatus.FAULTY
            return {
                "success": False,
                "sensor_id": sensor_id,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def get_sensor_health(self, sensor_id: str) -> Optional[SensorHealth]:
        """Get health information for a specific sensor."""
        return self.sensors.get(sensor_id)

    def get_all_sensor_health(self) -> List[SensorHealth]:
        """Get health information for all sensors."""
        return list(self.sensors.values())

    def get_sensor_readings(
        self, sensor_id: str, limit: int = 50
    ) -> List[SensorReading]:
        """Get recent readings for a sensor."""
        history = self.reading_history.get(sensor_id, [])
        return history[-limit:] if limit > 0 else history

    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        total_sensors = len(self.sensors)
        if total_sensors == 0:
            return {
                "status": "NO_SENSORS",
                "message": "No sensors registered",
                "total_sensors": 0,
            }

        # Count sensors by status
        status_counts = {status.name: 0 for status in SensorStatus}
        for sensor in self.sensors.values():
            status_counts[sensor.status.name] += 1

        # Calculate overall system status
        if status_counts["FAULTY"] > 0:
            overall_status = "FAULTY"
        elif status_counts["DEGRADED"] > 0:
            overall_status = "DEGRADED"
        elif status_counts["HEALTHY"] == total_sensors:
            overall_status = "HEALTHY"
        else:
            overall_status = "UNKNOWN"

        # Calculate average metrics
        total_readings = 0
        total_valid = 0
        total_confidence = 0.0

        for sensor in self.sensors.values():
            metrics = sensor.metrics
            total_readings += metrics["total_readings"]
            total_valid += metrics["valid_readings"]
            total_confidence += metrics["average_confidence"]

        avg_confidence = total_confidence / total_sensors if total_sensors > 0 else 0.0
        validity_rate = total_valid / total_readings if total_readings > 0 else 0.0

        return {
            "overall_status": overall_status,
            "total_sensors": total_sensors,
            "status_counts": status_counts,
            "total_readings": total_readings,
            "valid_readings": total_valid,
            "validity_rate": validity_rate,
            "average_confidence": avg_confidence,
            "system_uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "calibrations_due": sum(
                1
                for s in self.sensors.values()
                if s.calibration_due and s.calibration_due < datetime.now()
            ),
        }

    async def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive sensor diagnostics."""
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.get_system_health_summary(),
            "sensor_details": [],
            "recommendations": [],
        }

        # Collect detailed information for each sensor
        for sensor_id, sensor in self.sensors.items():
            sensor_info = sensor.to_dict()
            sensor_info["recent_readings"] = [
                r.to_dict() for r in self.get_sensor_readings(sensor_id, limit=5)
            ]
            diagnostics["sensor_details"].append(sensor_info)

            # Generate recommendations
            if sensor.status == SensorStatus.FAULTY:
                diagnostics["recommendations"].append(
                    f"Replace or repair faulty sensor: {sensor_id}"
                )
            elif sensor.status == SensorStatus.DEGRADED:
                diagnostics["recommendations"].append(
                    f"Investigate degraded sensor: {sensor_id}"
                )
            elif sensor.calibration_due and sensor.calibration_due < datetime.now():
                diagnostics["recommendations"].append(f"Calibrate sensor: {sensor_id}")

        return diagnostics


# Convenience function for quick sensor diagnostics
async def diagnose_sensors() -> Dict[str, Any]:
    """Quick sensor diagnostics."""
    diagnostics = SensorDiagnostics()
    return await diagnostics.run_diagnostics()

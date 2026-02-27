"""
Crusader Combat Refrigerator - Fly Counter System
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Fly counter system for detecting, tracking, and counting flies.
Uses multiple sensor modalities (optical, thermal, acoustic) for accurate detection.
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

from ..core.constants import EnvironmentalConstants, HardwareConstants, TimeConstants
from ..core.utils.time_utils import TimeUtils


class DetectionMethod(Enum):
    """Fly detection methods."""

    OPTICAL = auto()  # Optical sensor (camera/IR beam)
    THERMAL = auto()  # Thermal imaging
    ACOUSTIC = auto()  # Acoustic (wingbeat detection)
    VIBRATION = auto()  # Vibration sensor
    PRESSURE = auto()  # Air pressure change
    MULTIMODAL = auto()  # Combined methods
    SIMULATED = auto()  # Simulation mode


class DetectionConfidence(Enum):
    """Detection confidence levels."""

    LOW = auto()  # 0-33% confidence
    MEDIUM = auto()  # 34-66% confidence
    HIGH = auto()  # 67-100% confidence
    CONFIRMED = auto()  # > 95% confidence (multiple methods)


class FlySizeCategory(Enum):
    """Fly size categories."""

    SMALL = auto()  # < 2mm (fruit flies)
    MEDIUM = auto()  # 2-4mm (house flies)
    LARGE = auto()  # 4-8mm (blow flies)
    VERY_LARGE = auto()  # > 8mm (horse flies)


class CounterStatus(Enum):
    """Counter system status."""

    READY = auto()  # Ready for operation
    ACTIVE = auto()  # Actively counting
    CALIBRATING = auto()  # Calibrating sensors
    ERROR = auto()  # System error
    MAINTENANCE = auto()  # Under maintenance
    OVERLOADED = auto()  # Too many detections
    LOW_POWER = auto()  # Low power mode


@dataclass
class FlyCounterConfig:
    """Fly counter configuration."""

    # Sensor specifications
    sensor_count: int = 4
    detection_methods: List[DetectionMethod] = None
    detection_range_mm: float = 1000.0
    field_of_view_degrees: float = 90.0
    detection_frequency_hz: float = 10.0

    # Detection parameters
    min_fly_size_mm: float = 1.0
    max_fly_size_mm: float = 10.0
    detection_threshold: float = 0.7  # 0-1 confidence threshold
    confirmation_threshold: int = 2  # Minimum sensors for confirmation

    # Tracking parameters
    max_tracked_flies: int = 50
    tracking_timeout_seconds: float = 5.0
    position_accuracy_mm: float = 10.0

    # Performance parameters
    calibration_interval_hours: float = 24.0
    maintenance_interval_hours: float = 168.0  # Weekly
    data_retention_days: int = 30

    # Energy parameters
    power_consumption_active_w: float = 15.0
    power_consumption_idle_w: float = 2.0
    low_power_threshold_percent: float = 20.0

    # Environmental compensation
    temperature_compensation: bool = True
    humidity_compensation: bool = True
    lighting_compensation: bool = True

    def __post_init__(self):
        if self.detection_methods is None:
            self.detection_methods = [
                DetectionMethod.OPTICAL,
                DetectionMethod.THERMAL,
                DetectionMethod.ACOUSTIC,
            ]


@dataclass
class SensorState:
    """Individual sensor state."""

    sensor_id: int
    detection_method: DetectionMethod
    status: str  # "normal", "calibrating", "error", "maintenance"
    temperature_c: float
    last_calibration: Optional[datetime]
    detection_count: int
    error_count: int
    uptime_hours: float
    sensitivity: float  # 0-1 scale
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DetectionEvent:
    """Individual fly detection event."""

    detection_id: str
    timestamp: datetime
    sensor_id: int
    detection_method: DetectionMethod
    confidence: float
    confidence_level: DetectionConfidence
    position: Tuple[float, float, float]  # x, y, z in mm
    estimated_size_mm: float
    size_category: FlySizeCategory
    velocity_mps: Optional[float] = None
    direction_degrees: Optional[float] = None
    temperature_c: Optional[float] = None
    wingbeat_frequency_hz: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["detection_method"] = self.detection_method.name
        data["confidence_level"] = self.confidence_level.name
        data["size_category"] = self.size_category.name
        return data


@dataclass
class TrackedFly:
    """Tracked fly with multiple detections."""

    track_id: str
    first_detection: datetime
    last_detection: datetime
    detection_count: int
    average_position: Tuple[float, float, float]
    estimated_size_mm: float
    size_category: FlySizeCategory
    average_velocity_mps: float
    confidence: float
    active: bool
    detection_history: List[DetectionEvent]
    metadata: Optional[Dict[str, Any]] = None

    def update(self, detection: DetectionEvent) -> None:
        """Update track with new detection."""
        self.last_detection = detection.timestamp
        self.detection_count += 1

        # Update average position (moving average)
        old_weight = (self.detection_count - 1) / self.detection_count
        new_weight = 1 / self.detection_count

        self.average_position = (
            self.average_position[0] * old_weight + detection.position[0] * new_weight,
            self.average_position[1] * old_weight + detection.position[1] * new_weight,
            self.average_position[2] * old_weight + detection.position[2] * new_weight,
        )

        # Update confidence (weighted average)
        self.confidence = (
            self.confidence * old_weight + detection.confidence * new_weight
        )

        self.detection_history.append(detection)

        # Update velocity if available
        if detection.velocity_mps is not None:
            self.average_velocity_mps = (
                self.average_velocity_mps * old_weight
                + detection.velocity_mps * new_weight
            )

        # Check if track should be considered inactive
        time_since_last = (datetime.now() - self.last_detection).total_seconds()
        if time_since_last > 10.0:  # 10 seconds without detection
            self.active = False


@dataclass
class CountingResult:
    """Result of counting operation."""

    count_id: str
    timestamp: datetime
    status: CounterStatus
    duration_seconds: float
    total_detections: int
    confirmed_flies: int
    size_distribution: Dict[str, int]  # Size category -> count
    detection_rate_per_minute: float
    average_confidence: float
    sensor_utilization: Dict[int, float]  # Sensor ID -> utilization %
    success: bool
    error_message: Optional[str] = None
    tracked_flies: Optional[List[Dict[str, Any]]] = None
    environmental_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["status"] = self.status.name
        return data


@dataclass
class PerformanceReport:
    """Counter performance report."""

    timestamp: datetime
    detection_accuracy_percent: float
    false_positive_rate_percent: float
    false_negative_rate_percent: float
    average_latency_ms: float
    sensor_reliability: Dict[int, float]  # Sensor ID -> reliability %
    environmental_impact: Dict[str, float]  # Factor -> impact score
    recommendations: List[str]
    test_duration_hours: float
    test_conditions: Dict[str, Any]


class FlyCounterSystem:
    """
    Fly counter system for detecting and counting flies.
    Uses multiple sensors and tracking algorithms for accurate counting.
    """

    def __init__(self, config: Optional[FlyCounterConfig] = None):
        """Initialize fly counter system."""
        self.config = config or FlyCounterConfig()
        self.status = CounterStatus.READY

        # Sensor management
        self.sensors: Dict[int, SensorState] = {}
        self._initialize_sensors()

        # Detection tracking
        self.detection_history: List[DetectionEvent] = []
        self.tracked_flies: Dict[str, TrackedFly] = {}
        self.active_tracks: List[str] = []

        # Counting results
        self.counting_results: List[CountingResult] = []
        self.performance_history: List[PerformanceReport] = []

        # Statistics
        self.total_detections: int = 0
        self.confirmed_flies_count: int = 0
        self.false_positives: int = 0
        self.false_negatives: int = 0

        # Adaptive parameters
        self.adaptive_parameters: Dict[str, Any] = {
            "detection_threshold": self.config.detection_threshold,
            "environmental_compensation": 1.0,
            "sensitivity_adjustments": {},
            "learning_rate": 0.1,
            "performance_history": [],
        }

        # Maintenance tracking
        self.last_calibration: Optional[datetime] = None
        self.last_maintenance: Optional[datetime] = None
        self.maintenance_alerts: List[str] = []

        # Hardware interface (simulated for now)
        self.hardware_connected = False
        self.simulation_mode = True

        # Async components
        self._counting_task: Optional[asyncio.Task] = None
        self._tracking_task: Optional[asyncio.Task] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        print(f"FlyCounterSystem initialized with {self.config.sensor_count} sensors")

    def _initialize_sensors(self) -> None:
        """Initialize sensor states."""
        detection_methods = self.config.detection_methods

        for i in range(self.config.sensor_count):
            method = detection_methods[i % len(detection_methods)]

            self.sensors[i] = SensorState(
                sensor_id=i,
                detection_method=method,
                status="normal",
                temperature_c=25.0,
                last_calibration=None,
                detection_count=0,
                error_count=0,
                uptime_hours=0.0,
                sensitivity=0.8,
            )

    async def start_counting(self) -> CountingResult:
        """Start the fly counting system."""
        if self.status in [CounterStatus.ACTIVE, CounterStatus.CALIBRATING]:
            return CountingResult(
                count_id="already_active",
                timestamp=datetime.now(),
                status=self.status,
                duration_seconds=0.0,
                total_detections=0,
                confirmed_flies=0,
                size_distribution={},
                detection_rate_per_minute=0.0,
                average_confidence=0.0,
                sensor_utilization={},
                success=False,
                error_message=f"System already {self.status.name.lower()}",
            )

        print("Starting fly counting system")

        self.status = CounterStatus.ACTIVE
        count_id = self._generate_count_id()
        start_time = datetime.now()

        try:
            # Connect to hardware
            await self._connect_hardware()

            # Start sensor calibration
            await self._calibrate_sensors()

            # Start async tasks
            self._counting_task = asyncio.create_task(self._counting_loop())
            self._tracking_task = asyncio.create_task(self._tracking_loop())
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

            print("Fly counting system active")

            return CountingResult(
                count_id=count_id,
                timestamp=datetime.now(),
                status=CounterStatus.ACTIVE,
                duration_seconds=0.0,
                total_detections=self.total_detections,
                confirmed_flies=self.confirmed_flies_count,
                size_distribution=self._get_size_distribution(),
                detection_rate_per_minute=self._calculate_detection_rate(),
                average_confidence=self._calculate_average_confidence(),
                sensor_utilization=self._calculate_sensor_utilization(),
                success=True,
            )

        except Exception as e:
            self.status = CounterStatus.ERROR
            print(f"Failed to start counting system: {e}")

            return CountingResult(
                count_id=count_id,
                timestamp=datetime.now(),
                status=CounterStatus.ERROR,
                duration_seconds=0.0,
                total_detections=0,
                confirmed_flies=0,
                size_distribution={},
                detection_rate_per_minute=0.0,
                average_confidence=0.0,
                sensor_utilization={},
                success=False,
                error_message=str(e),
            )

    async def stop_counting(self) -> CountingResult:
        """Stop the fly counting system."""
        if self.status in [CounterStatus.READY, CounterStatus.ERROR]:
            return CountingResult(
                count_id="already_stopped",
                timestamp=datetime.now(),
                status=self.status,
                duration_seconds=0.0,
                total_detections=0,
                confirmed_flies=0,
                size_distribution={},
                detection_rate_per_minute=0.0,
                average_confidence=0.0,
                sensor_utilization={},
                success=False,
                error_message=f"System already {self.status.name.lower()}",
            )

        print("Stopping fly counting system")
        self.status = CounterStatus.READY

        try:
            # Signal shutdown
            self._shutdown_event.set()

            # Cancel tasks
            for task in [
                self._counting_task,
                self._tracking_task,
                self._monitoring_task,
            ]:
                if task:
                    task.cancel()

            # Wait for shutdown
            await asyncio.sleep(1.0)

            # Calculate final statistics
            duration = 0.0  # Would be calculated from start time
            detection_rate = self._calculate_detection_rate()
            avg_confidence = self._calculate_average_confidence()
            sensor_utilization = self._calculate_sensor_utilization()
            size_distribution = self._get_size_distribution()

            self._shutdown_event.clear()

            print("Fly counting system stopped")

            result = CountingResult(
                count_id=self._generate_count_id(),
                timestamp=datetime.now(),
                status=CounterStatus.READY,
                duration_seconds=duration,
                total_detections=self.total_detections,
                confirmed_flies=self.confirmed_flies_count,
                size_distribution=size_distribution,
                detection_rate_per_minute=detection_rate,
                average_confidence=avg_confidence,
                sensor_utilization=sensor_utilization,
                success=True,
                tracked_flies=[asdict(track) for track in self.tracked_flies.values()],
            )

            self.counting_results.append(result)
            return result

        except Exception as e:
            self.status = CounterStatus.ERROR
            print(f"Error stopping counting system: {e}")

            return CountingResult(
                count_id="error",
                timestamp=datetime.now(),
                status=CounterStatus.ERROR,
                duration_seconds=0.0,
                total_detections=0,
                confirmed_flies=0,
                size_distribution={},
                detection_rate_per_minute=0.0,
                average_confidence=0.0,
                sensor_utilization={},
                success=False,
                error_message=str(e),
            )

    async def report_detection(
        self,
        sensor_id: int,
        confidence: float,
        position: Tuple[float, float, float],
        size_mm: float,
        velocity_mps: Optional[float] = None,
        direction_degrees: Optional[float] = None,
        temperature_c: Optional[float] = None,
        wingbeat_hz: Optional[float] = None,
    ) -> DetectionEvent:
        """Report a fly detection from a sensor."""
        if sensor_id not in self.sensors:
            raise ValueError(f"Invalid sensor ID: {sensor_id}")

        sensor = self.sensors[sensor_id]

        # Determine confidence level
        if confidence >= 0.95:
            confidence_level = DetectionConfidence.CONFIRMED
        elif confidence >= 0.67:
            confidence_level = DetectionConfidence.HIGH
        elif confidence >= 0.34:
            confidence_level = DetectionConfidence.MEDIUM
        else:
            confidence_level = DetectionConfidence.LOW

        # Determine size category
        if size_mm < 2.0:
            size_category = FlySizeCategory.SMALL
        elif size_mm < 4.0:
            size_category = FlySizeCategory.MEDIUM
        elif size_mm < 8.0:
            size_category = FlySizeCategory.LARGE
        else:
            size_category = FlySizeCategory.VERY_LARGE

        # Apply environmental compensation
        compensated_confidence = (
            confidence * self.adaptive_parameters["environmental_compensation"]
        )
        compensated_confidence = min(1.0, max(0.0, compensated_confidence))

        # Update sensor statistics
        sensor.detection_count += 1
        self.total_detections += 1

        # Check if detection meets threshold
        if compensated_confidence >= self.adaptive_parameters["detection_threshold"]:
            self.confirmed_flies_count += 1

        # Create detection event
        event = DetectionEvent(
            detection_id=self._generate_detection_id(),
            timestamp=datetime.now(),
            sensor_id=sensor_id,
            detection_method=sensor.detection_method,
            confidence=compensated_confidence,
            confidence_level=confidence_level,
            position=position,
            estimated_size_mm=size_mm,
            size_category=size_category,
            velocity_mps=velocity_mps,
            direction_degrees=direction_degrees,
            temperature_c=temperature_c,
            wingbeat_frequency_hz=wingbeat_hz,
            metadata={
                "sensor_sensitivity": sensor.sensitivity,
                "environmental_compensation": self.adaptive_parameters[
                    "environmental_compensation"
                ],
                "compensated_confidence": compensated_confidence,
            },
        )

        # Add to history
        self.detection_history.append(event)

        # Update tracking
        await self._update_tracking(event)

        print(
            f"Detection reported: sensor {sensor_id}, confidence {compensated_confidence:.2f}, size {size_mm:.1f}mm"
        )

        return event

    async def _connect_hardware(self) -> None:
        """Connect to hardware components."""
        if self.simulation_mode:
            print("Simulating hardware connection for fly counter")
            await asyncio.sleep(0.5)
            self.hardware_connected = True
        else:
            # Actual hardware connection would go here
            raise NotImplementedError("Hardware connection not implemented")

    async def _calibrate_sensors(self) -> None:
        """Calibrate all sensors."""
        print("Calibrating fly counter sensors")
        self.status = CounterStatus.CALIBRATING

        for sensor_id, sensor in self.sensors.items():
            if self.simulation_mode:
                print(
                    f"  Calibrating sensor {sensor_id} ({sensor.detection_method.name})..."
                )
                await asyncio.sleep(0.3)

                # Simulate calibration results
                sensor.sensitivity = random.uniform(0.7, 0.95)
                sensor.last_calibration = datetime.now()
                sensor.status = "normal"

        self.status = CounterStatus.ACTIVE
        self.last_calibration = datetime.now()
        print("Sensor calibration complete")

    async def _counting_loop(self) -> None:
        """Main counting loop."""
        print("Starting fly counting loop")

        try:
            while not self._shutdown_event.is_set():
                # Simulate detections in simulation mode
                if self.simulation_mode and random.random() > 0.7:
                    await self._simulate_detection()

                # Update tracking
                await self._cleanup_old_tracks()

                # Update adaptive parameters
                await self._update_adaptive_parameters()

                # Sleep for counting interval
                await asyncio.sleep(1.0 / self.config.detection_frequency_hz)

        except asyncio.CancelledError:
            print("Counting loop cancelled")
        except Exception as e:
            print(f"Error in counting loop: {e}")
            self.status = CounterStatus.ERROR

    async def _tracking_loop(self) -> None:
        """Tracking loop for following fly movements."""
        print("Starting fly tracking loop")

        try:
            while not self._shutdown_event.is_set():
                # Update active tracks
                await self._update_track_positions()

                # Calculate fly trajectories
                await self._calculate_trajectories()

                # Predict future positions
                await self._predict_positions()

                # Sleep for tracking interval
                await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            print("Tracking loop cancelled")
        except Exception as e:
            print(f"Error in tracking loop: {e}")

    async def _monitoring_loop(self) -> None:
        """Monitoring loop for system health."""
        print("Starting fly counter monitoring loop")

        try:
            while not self._shutdown_event.is_set():
                # Monitor sensor health
                await self._monitor_sensor_health()

                # Check for maintenance needs
                await self._check_maintenance()

                # Update performance metrics
                await self._update_performance_metrics()

                # Sleep for monitoring interval
                await asyncio.sleep(2.0)

        except asyncio.CancelledError:
            print("Monitoring loop cancelled")
        except Exception as e:
            print(f"Error in monitoring loop: {e}")

    async def _simulate_detection(self) -> None:
        """Simulate a fly detection (for testing)."""
        if not self.simulation_mode:
            return

        # Random sensor
        sensor_id = random.randint(0, self.config.sensor_count - 1)
        sensor = self.sensors[sensor_id]

        # Random position within detection range
        position = (
            random.uniform(
                -self.config.detection_range_mm / 2, self.config.detection_range_mm / 2
            ),
            random.uniform(
                -self.config.detection_range_mm / 2, self.config.detection_range_mm / 2
            ),
            random.uniform(0, 500.0),  # z: 0-500mm
        )

        # Random size
        size_mm = random.uniform(
            self.config.min_fly_size_mm, self.config.max_fly_size_mm
        )

        # Random confidence (affected by sensor sensitivity)
        base_confidence = random.uniform(0.5, 0.95)
        confidence = base_confidence * sensor.sensitivity

        # Random velocity and direction
        velocity_mps = random.uniform(0.5, 2.0) if random.random() > 0.3 else None
        direction_degrees = random.uniform(0, 360) if velocity_mps else None

        # Random temperature (for thermal sensor)
        temperature_c = (
            random.uniform(20.0, 30.0)
            if sensor.detection_method == DetectionMethod.THERMAL
            else None
        )

        # Random wingbeat (for acoustic sensor)
        wingbeat_hz = (
            random.uniform(150.0, 250.0)
            if sensor.detection_method == DetectionMethod.ACOUSTIC
            else None
        )

        # Report detection
        await self.report_detection(
            sensor_id=sensor_id,
            confidence=confidence,
            position=position,
            size_mm=size_mm,
            velocity_mps=velocity_mps,
            direction_degrees=direction_degrees,
            temperature_c=temperature_c,
            wingbeat_hz=wingbeat_hz,
        )

    async def _update_tracking(self, detection: DetectionEvent) -> None:
        """Update fly tracking with new detection."""
        # Check if this detection matches an existing track
        matched_track_id = None
        max_distance = self.config.position_accuracy_mm * 2.0

        for track_id, track in self.tracked_flies.items():
            if not track.active:
                continue

            # Calculate distance to track average position
            distance = math.sqrt(
                (detection.position[0] - track.average_position[0]) ** 2
                + (detection.position[1] - track.average_position[1]) ** 2
                + (detection.position[2] - track.average_position[2]) ** 2
            )

            # Check if same size category
            same_size = detection.size_category == track.size_category

            if distance < max_distance and same_size:
                matched_track_id = track_id
                break

        if matched_track_id:
            # Update existing track
            track = self.tracked_flies[matched_track_id]
            track.update(detection)
            print(f"Updated track {matched_track_id} with new detection")
        else:
            # Create new track
            track_id = self._generate_track_id()
            track = TrackedFly(
                track_id=track_id,
                first_detection=detection.timestamp,
                last_detection=detection.timestamp,
                detection_count=1,
                average_position=detection.position,
                estimated_size_mm=detection.estimated_size_mm,
                size_category=detection.size_category,
                average_velocity_mps=detection.velocity_mps or 0.0,
                confidence=detection.confidence,
                active=True,
                detection_history=[detection],
            )
            self.tracked_flies[track_id] = track
            self.active_tracks.append(track_id)
            print(f"Created new track {track_id}")

        # Limit number of tracks
        if len(self.tracked_flies) > self.config.max_tracked_flies:
            # Remove oldest inactive track
            oldest_track_id = None
            oldest_time = datetime.now()

            for track_id, track in self.tracked_flies.items():
                if not track.active and track.last_detection < oldest_time:
                    oldest_track_id = track_id
                    oldest_time = track.last_detection

            if oldest_track_id:
                del self.tracked_flies[oldest_track_id]
                if oldest_track_id in self.active_tracks:
                    self.active_tracks.remove(oldest_track_id)

    async def _cleanup_old_tracks(self) -> None:
        """Clean up old inactive tracks."""
        current_time = datetime.now()
        tracks_to_remove = []

        for track_id, track in self.tracked_flies.items():
            if not track.active:
                time_since_last = (current_time - track.last_detection).total_seconds()
                if time_since_last > self.config.tracking_timeout_seconds:
                    tracks_to_remove.append(track_id)

        for track_id in tracks_to_remove:
            del self.tracked_flies[track_id]
            if track_id in self.active_tracks:
                self.active_tracks.remove(track_id)

        if tracks_to_remove:
            print(f"Cleaned up {len(tracks_to_remove)} old tracks")

    async def _update_track_positions(self) -> None:
        """Update track positions based on velocity."""
        current_time = datetime.now()

        for track_id in self.active_tracks:
            if track_id not in self.tracked_flies:
                continue

            track = self.tracked_flies[track_id]
            if not track.active or track.average_velocity_mps <= 0:
                continue

            # Calculate time since last update
            if not track.detection_history:
                continue

            last_detection = track.detection_history[-1]
            time_delta = (current_time - last_detection.timestamp).total_seconds()

            # Update position based on velocity
            if last_detection.direction_degrees is not None:
                # Convert polar to Cartesian
                angle_rad = math.radians(last_detection.direction_degrees)
                distance_m = track.average_velocity_mps * time_delta
                distance_mm = distance_m * 1000.0  # Convert to mm

                dx = distance_mm * math.cos(angle_rad)
                dy = distance_mm * math.sin(angle_rad)

                # Update average position (predicted)
                track.average_position = (
                    track.average_position[0] + dx,
                    track.average_position[1] + dy,
                    track.average_position[2],  # Keep same height
                )

    async def _calculate_trajectories(self) -> None:
        """Calculate fly trajectories from track history."""
        for track_id in self.active_tracks:
            if track_id not in self.tracked_flies:
                continue

            track = self.tracked_flies[track_id]
            if len(track.detection_history) < 2:
                continue

            # Calculate trajectory from last two detections
            last_two = track.detection_history[-2:]
            pos1 = last_two[0].position
            pos2 = last_two[1].position
            time_diff = (last_two[1].timestamp - last_two[0].timestamp).total_seconds()

            if time_diff > 0:
                # Calculate velocity vector
                dx = pos2[0] - pos1[0]
                dy = pos2[1] - pos1[1]
                dz = pos2[2] - pos1[2]

                distance_mm = math.sqrt(dx * dx + dy * dy + dz * dz)
                velocity_mps = (distance_mm / 1000.0) / time_diff

                # Calculate direction
                if dx != 0 or dy != 0:
                    direction_rad = math.atan2(dy, dx)
                    direction_degrees = math.degrees(direction_rad) % 360
                else:
                    direction_degrees = 0.0

                # Update track with calculated values
                track.average_velocity_mps = velocity_mps
                if track.detection_history:
                    track.detection_history[-1].velocity_mps = velocity_mps
                    track.detection_history[-1].direction_degrees = direction_degrees

    async def _predict_positions(self) -> None:
        """Predict future fly positions."""
        # This would implement prediction algorithms
        # For now, just a placeholder
        pass

    async def _monitor_sensor_health(self) -> None:
        """Monitor sensor health and detect issues."""
        for sensor_id, sensor in self.sensors.items():
            # Check temperature
            if sensor.temperature_c > 50.0:
                sensor.status = "overheating"
                self.maintenance_alerts.append(f"Sensor {sensor_id} overheating")

            # Check error rate
            if sensor.detection_count > 0:
                error_rate = sensor.error_count / sensor.detection_count
                if error_rate > 0.1:  # 10% error rate
                    sensor.status = "error"
                    self.maintenance_alerts.append(
                        f"Sensor {sensor_id} high error rate"
                    )

            # Update uptime
            sensor.uptime_hours += 2.0 / 3600.0  # 2 seconds per check

            # Simulate temperature changes
            if self.simulation_mode:
                sensor.temperature_c += random.uniform(-0.1, 0.1)
                sensor.temperature_c = max(20.0, min(40.0, sensor.temperature_c))

    async def _check_maintenance(self) -> None:
        """Check if maintenance is needed."""
        now = datetime.now()

        # Check calibration
        if self.last_calibration:
            hours_since = (now - self.last_calibration).total_seconds() / 3600.0
            if hours_since > self.config.calibration_interval_hours:
                self.maintenance_alerts.append("Sensor calibration needed")

        # Check general maintenance
        if self.last_maintenance:
            hours_since = (now - self.last_maintenance).total_seconds() / 3600.0
            if hours_since > self.config.maintenance_interval_hours:
                self.maintenance_alerts.append("System maintenance needed")

        # Check sensor uptime
        for sensor_id, sensor in self.sensors.items():
            if sensor.uptime_hours > 1000:  # 1000 hours
                self.maintenance_alerts.append(f"Sensor {sensor_id} needs inspection")

    async def _update_performance_metrics(self) -> None:
        """Update performance metrics."""
        # Calculate detection accuracy (simulated)
        if self.total_detections > 0:
            accuracy = 0.85  # Base accuracy
            # Adjust based on sensor conditions
            for sensor in self.sensors.values():
                if sensor.status == "normal":
                    accuracy += 0.02
                elif sensor.status == "error":
                    accuracy -= 0.05

            accuracy = max(0.0, min(1.0, accuracy))
            self.adaptive_parameters["performance_history"].append(accuracy)

            # Keep history manageable
            if len(self.adaptive_parameters["performance_history"]) > 100:
                self.adaptive_parameters["performance_history"] = (
                    self.adaptive_parameters["performance_history"][-100:]
                )

    async def _update_adaptive_parameters(self) -> None:
        """Update adaptive parameters based on performance."""
        # Adjust detection threshold based on performance
        if self.adaptive_parameters["performance_history"]:
            avg_performance = statistics.mean(
                self.adaptive_parameters["performance_history"]
            )
            if avg_performance < 0.7:  # Low performance
                # Lower threshold to catch more flies
                self.adaptive_parameters["detection_threshold"] = max(
                    0.5, self.adaptive_parameters["detection_threshold"] - 0.05
                )
                print(
                    f"Lowered detection threshold to {self.adaptive_parameters['detection_threshold']:.2f}"
                )
            elif avg_performance > 0.9:  # High performance
                # Raise threshold to reduce false positives
                self.adaptive_parameters["detection_threshold"] = min(
                    0.9, self.adaptive_parameters["detection_threshold"] + 0.02
                )
                print(
                    f"Raised detection threshold to {self.adaptive_parameters['detection_threshold']:.2f}"
                )

        # Update environmental compensation (simulated)
        # In real system, this would use actual sensor data
        self.adaptive_parameters["environmental_compensation"] = random.uniform(
            0.9, 1.1
        )

    def _calculate_detection_rate(self) -> float:
        """Calculate current detection rate (flies per minute)."""
        if not self.detection_history:
            return 0.0

        # Look at last 5 minutes
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_detections = [
            event
            for event in self.detection_history
            if event.timestamp > cutoff_time
            and event.confidence >= self.adaptive_parameters["detection_threshold"]
        ]

        return len(recent_detections) / 5.0  # flies per minute

    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence of recent detections."""
        if not self.detection_history:
            return 0.0

        # Look at last 100 detections
        recent = self.detection_history[-100:]
        confidences = [event.confidence for event in recent]
        return statistics.mean(confidences) if confidences else 0.0

    def _calculate_sensor_utilization(self) -> Dict[int, float]:
        """Calculate sensor utilization percentages."""
        utilizations = {}
        total_detections = max(1, self.total_detections)

        for sensor_id, sensor in self.sensors.items():
            utilization = sensor.detection_count / total_detections
            utilizations[sensor_id] = utilization * 100.0  # Convert to percentage

        return utilizations

    def _get_size_distribution(self) -> Dict[str, int]:
        """Get current size distribution of detected flies."""
        distribution = {"SMALL": 0, "MEDIUM": 0, "LARGE": 0, "VERY_LARGE": 0}

        # Count confirmed detections by size category
        for event in self.detection_history:
            if event.confidence >= self.adaptive_parameters["detection_threshold"]:
                distribution[event.size_category.name] += 1

        return distribution

    def _generate_count_id(self) -> str:
        """Generate unique count ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = random.randint(1000, 9999)
        return f"FC_{timestamp}_{random_suffix}"

    def _generate_detection_id(self) -> str:
        """Generate unique detection ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        random_suffix = random.randint(100, 999)
        return f"FD_{timestamp}_{random_suffix}"

    def _generate_track_id(self) -> str:
        """Generate unique track ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = random.randint(1000, 9999)
        return f"FT_{timestamp}_{random_suffix}"

    async def calibrate(self) -> bool:
        """Calibrate the fly counter system."""
        if self.status != CounterStatus.READY:
            print(f"Cannot calibrate when system is {self.status.name}")
            return False

        print("Starting fly counter calibration")
        self.status = CounterStatus.CALIBRATING

        try:
            # Simulate calibration process
            if self.simulation_mode:
                print("Calibrating detection thresholds...")
                await asyncio.sleep(1.5)

                print("Aligning sensor fields of view...")
                await asyncio.sleep(1.0)

                print("Testing detection algorithms...")
                await asyncio.sleep(2.0)

            # Update calibration timestamp
            self.last_calibration = datetime.now()

            # Reset adaptive parameters
            self.adaptive_parameters["detection_threshold"] = (
                self.config.detection_threshold
            )
            self.adaptive_parameters["environmental_compensation"] = 1.0

            # Clear calibration alerts
            self.maintenance_alerts = [
                alert
                for alert in self.maintenance_alerts
                if "calibration" not in alert.lower()
            ]

            self.status = CounterStatus.READY
            print("Calibration complete")
            return True

        except Exception as e:
            self.status = CounterStatus.ERROR
            print(f"Calibration failed: {e}")
            return False

    async def perform_maintenance(self) -> bool:
        """Perform routine maintenance."""
        if self.status != CounterStatus.READY:
            print(f"Cannot perform maintenance when system is {self.status.name}")
            return False

        print("Starting fly counter maintenance")
        self.status = CounterStatus.MAINTENANCE

        try:
            # Simulate maintenance process
            if self.simulation_mode:
                print("Cleaning sensor lenses...")
                await asyncio.sleep(1.5)

                print("Checking sensor alignment...")
                await asyncio.sleep(1.0)

                print("Testing sensor functionality...")
                await asyncio.sleep(2.0)

                print("Resetting error counters...")
                await asyncio.sleep(0.5)

            # Reset sensor states
            for sensor in self.sensors.values():
                sensor.error_count = 0
                sensor.status = "normal"
                sensor.temperature_c = 25.0

            # Update maintenance timestamp
            self.last_maintenance = datetime.now()

            # Clear maintenance alerts
            self.maintenance_alerts = []

            self.status = CounterStatus.READY
            print("Maintenance complete")
            return True

        except Exception as e:
            self.status = CounterStatus.ERROR
            print(f"Maintenance failed: {e}")
            return False

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        active_sensors = [s for s in self.sensors.values() if s.status == "normal"]
        error_sensors = [s for s in self.sensors.values() if s.status == "error"]

        return {
            "system": {
                "status": self.status.name,
                "detection_threshold": self.adaptive_parameters["detection_threshold"],
                "environmental_compensation": self.adaptive_parameters[
                    "environmental_compensation"
                ],
            },
            "sensors": {
                "total": len(self.sensors),
                "active": len(active_sensors),
                "errors": len(error_sensors),
                "average_sensitivity": (
                    sum(s.sensitivity for s in active_sensors) / len(active_sensors)
                    if active_sensors
                    else 0.0
                ),
                "average_temperature": (
                    sum(s.temperature_c for s in self.sensors.values())
                    / len(self.sensors)
                    if self.sensors
                    else 0.0
                ),
            },
            "performance": {
                "total_detections": self.total_detections,
                "confirmed_flies": self.confirmed_flies_count,
                "detection_rate_per_minute": self._calculate_detection_rate(),
                "average_confidence": self._calculate_average_confidence(),
                "size_distribution": self._get_size_distribution(),
                "active_tracks": len(self.active_tracks),
                "total_tracks": len(self.tracked_flies),
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
                "detection_events": len(self.detection_history),
                "counting_results": len(self.counting_results),
                "performance_reports": len(self.performance_history),
                "average_performance": (
                    statistics.mean(self.adaptive_parameters["performance_history"])
                    if self.adaptive_parameters["performance_history"]
                    else 0.0
                ),
            },
        }

    def get_detection_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get detection history."""
        history = self.detection_history[-limit:] if self.detection_history else []
        return [event.to_dict() for event in history]

    def get_tracked_flies(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get tracked flies."""
        tracks = self.tracked_flies.values()
        if active_only:
            tracks = [t for t in tracks if t.active]
        return [asdict(track) for track in tracks]

    def get_counting_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get counting results history."""
        history = self.counting_results[-limit:] if self.counting_results else []
        return [result.to_dict() for result in history]

    def clear_history(self) -> None:
        """Clear performance history."""
        self.detection_history = []
        self.tracked_flies = {}
        self.active_tracks = []
        self.counting_results = []
        self.performance_history = []
        self.adaptive_parameters["performance_history"] = []
        print("Performance history cleared")

    async def emergency_shutdown(self) -> None:
        """Emergency shutdown procedure."""
        print("EMERGENCY SHUTDOWN INITIATED FOR FLY COUNTER SYSTEM")

        # Cancel all tasks
        for task in [self._counting_task, self._tracking_task, self._monitoring_task]:
            if task:
                task.cancel()

        # Set error state
        self.status = CounterStatus.ERROR

        print("Emergency shutdown complete")

    async def measure_performance(self) -> PerformanceReport:
        """Measure current system performance."""
        print("Measuring fly counter performance")

        # Simulate performance measurement
        test_duration = 1.0  # hours
        detection_accuracy = 0.85  # Base accuracy

        # Adjust based on sensor conditions
        for sensor in self.sensors.values():
            if sensor.status == "normal":
                detection_accuracy += 0.02
            elif sensor.status == "error":
                detection_accuracy -= 0.05

        detection_accuracy = max(0.0, min(1.0, detection_accuracy)) * 100.0

        # Calculate false positive/negative rates (simulated)
        false_positive_rate = max(0.0, 10.0 - detection_accuracy / 10.0)
        false_negative_rate = max(0.0, 15.0 - detection_accuracy / 8.0)

        # Calculate average latency (simulated)
        average_latency = 50.0  # milliseconds

        # Calculate sensor reliability
        sensor_reliability = {}
        for sensor_id, sensor in self.sensors.items():
            if sensor.detection_count > 0:
                reliability = 100.0 * (
                    1.0 - sensor.error_count / sensor.detection_count
                )
            else:
                reliability = 95.0  # Default
            sensor_reliability[sensor_id] = max(0.0, min(100.0, reliability))

        # Environmental impact (simulated)
        environmental_impact = {
            "temperature": random.uniform(0.8, 1.2),
            "humidity": random.uniform(0.9, 1.1),
            "lighting": random.uniform(0.7, 1.3),
        }

        # Generate recommendations
        recommendations = []
        if detection_accuracy < 80.0:
            recommendations.append("Calibrate sensors to improve accuracy")
        if false_positive_rate > 5.0:
            recommendations.append(
                "Increase detection threshold to reduce false positives"
            )
        if false_negative_rate > 10.0:
            recommendations.append(
                "Decrease detection threshold to reduce false negatives"
            )

        # Add maintenance alerts
        recommendations.extend(self.maintenance_alerts[:3])

        report = PerformanceReport(
            timestamp=datetime.now(),
            detection_accuracy_percent=detection_accuracy,
            false_positive_rate_percent=false_positive_rate,
            false_negative_rate_percent=false_negative_rate,
            average_latency_ms=average_latency,
            sensor_reliability=sensor_reliability,
            environmental_impact=environmental_impact,
            recommendations=recommendations,
            test_duration_hours=test_duration,
            test_conditions={
                "sensors_active": len(
                    [s for s in self.sensors.values() if s.status == "normal"]
                ),
                "detection_threshold": self.adaptive_parameters["detection_threshold"],
                "simulation_mode": self.simulation_mode,
            },
        )

        self.performance_history.append(report)
        return report

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.status == CounterStatus.ACTIVE:
            await self.stop_counting()


# Example usage and test function
async def test_fly_counter_system():
    """Test the fly counter system."""
    print("\n" + "=" * 60)
    print("TESTING FLY COUNTER SYSTEM")
    print("=" * 60)

    # Create system
    config = FlyCounterConfig(
        sensor_count=2,  # Fewer sensors for testing
        detection_frequency_hz=5.0,
    )

    system = FlyCounterSystem(config)

    try:
        # Test startup
        print("\n1. Testing startup...")
        result = await system.start_counting()
        print(f"   Startup result: {result.success}")
        print(f"   Status: {result.status.name}")
        print(f"   Confirmed flies: {result.confirmed_flies}")

        # Run for a bit
        await asyncio.sleep(2.0)

        # Test manual detection reporting
        print("\n2. Testing manual detection reporting...")
        for i in range(3):
            event = await system.report_detection(
                sensor_id=random.randint(0, config.sensor_count - 1),
                confidence=random.uniform(0.7, 0.95),
                position=(
                    random.uniform(-200.0, 200.0),
                    random.uniform(-200.0, 200.0),
                    random.uniform(0.0, 300.0),
                ),
                size_mm=random.uniform(2.0, 5.0),
                velocity_mps=random.uniform(0.5, 1.5),
                direction_degrees=random.uniform(0, 360),
            )
            print(
                f"   Detection {i + 1}: sensor {event.sensor_id}, confidence {event.confidence:.2f}"
            )
            await asyncio.sleep(0.3)

        # Let simulation run
        await asyncio.sleep(3.0)

        # Test status report
        print("\n3. Testing status report...")
        status = system.get_status_report()
        print(f"   System status: {status['system']['status']}")
        print(f"   Total detections: {status['performance']['total_detections']}")
        print(f"   Active tracks: {status['performance']['active_tracks']}")
        print(
            f"   Detection rate: {status['performance']['detection_rate_per_minute']:.1f}/min"
        )

        # Test performance measurement
        print("\n4. Testing performance measurement...")
        performance = await system.measure_performance()
        print(f"   Detection accuracy: {performance.detection_accuracy_percent:.1f}%")
        print(f"   False positive rate: {performance.false_positive_rate_percent:.1f}%")
        print(f"   Recommendations: {len(performance.recommendations)}")

        # Test shutdown
        print("\n5. Testing shutdown...")
        result = await system.stop_counting()
        print(f"   Shutdown result: {result.success}")
        print(f"   Duration: {result.duration_seconds:.1f}s")
        print(f"   Total confirmed flies: {result.confirmed_flies}")

        # Test calibration
        print("\n6. Testing calibration...")
        calibrated = await system.calibrate()
        print(f"   Calibration result: {calibrated}")

        # Test maintenance
        print("\n7. Testing maintenance...")
        maintained = await system.perform_maintenance()
        print(f"   Maintenance result: {maintained}")

        print("\n" + "=" * 60)
        print("FLY COUNTER SYSTEM TEST COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR during test: {e}")
        await system.emergency_shutdown()


if __name__ == "__main__":
    # Run test
    asyncio.run(test_fly_counter_system())

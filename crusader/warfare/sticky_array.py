"""
Crusader Combat Refrigerator - Sticky Trap System
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Sticky trap system for capturing flies that penetrate other defenses.
Uses adhesive surfaces with attractants to capture and immobilize flies.
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


class StickyTrapType(Enum):
    """Types of sticky traps."""

    STANDARD = auto()  # Standard adhesive surface
    ATTRACTANT = auto()  # With chemical attractants
    UV_REFLECTIVE = auto()  # UV-reflective surface
    THERMAL = auto()  # Thermally activated adhesive
    REPLACEABLE = auto()  # Replaceable cartridge
    MULTI_LAYER = auto()  # Multiple adhesive layers


class TrapStatus(Enum):
    """Sticky trap status."""

    READY = auto()  # Ready for deployment
    ACTIVE = auto()  # Currently active
    DEPLOYING = auto()  # Being deployed
    RETRACTING = auto()  # Being retracted
    SATURATED = auto()  # Full of flies
    DEGRADED = auto()  # Adhesive degraded
    ERROR = auto()  # System error
    MAINTENANCE = auto()  # Under maintenance
    CALIBRATING = auto()  # Calibrating


class DeploymentPattern(Enum):
    """Trap deployment patterns."""

    FULL_COVERAGE = auto()  # Cover entire area
    HOTSPOT = auto()  # Focus on fly hotspots
    PERIMETER = auto()  # Perimeter defense
    GRID = auto()  # Grid pattern
    SPIRAL = auto()  # Spiral pattern
    RANDOM = auto()  # Random distribution
    ADAPTIVE = auto()  # Adaptive based on fly activity


@dataclass
class StickyTrapConfig:
    """Sticky trap configuration."""

    # Trap specifications
    trap_count: int = 8
    trap_width_mm: float = 100.0
    trap_height_mm: float = 150.0
    adhesive_thickness_mm: float = 2.0
    max_capacity_flies: int = 50

    # Deployment parameters
    deployment_time_seconds: float = 5.0
    retraction_time_seconds: float = 3.0
    deployment_interval_hours: float = 168.0  # Weekly

    # Adhesive properties
    adhesive_viscosity: float = 5000.0  # centipoise
    tackiness_score: float = 8.5  # 0-10 scale
    temperature_range_c: Tuple[float, float] = (10.0, 40.0)
    humidity_range_percent: Tuple[float, float] = (20.0, 80.0)

    # Attractant properties (if applicable)
    attractant_type: str = "food_based"
    attractant_strength: float = 7.0  # 0-10 scale
    attractant_duration_hours: float = 336.0  # 2 weeks

    # Maintenance parameters
    replacement_interval_hours: float = 720.0  # 30 days
    cleaning_interval_hours: float = 168.0  # Weekly
    calibration_interval_hours: float = 336.0  # 2 weeks

    # Performance thresholds
    saturation_threshold_percent: float = 80.0
    degradation_threshold_percent: float = 60.0
    effectiveness_threshold_percent: float = 70.0


@dataclass
class TrapState:
    """Individual trap state."""

    trap_id: int
    trap_type: StickyTrapType
    status: TrapStatus
    deployment_position: Tuple[float, float, float]  # x, y, z in mm
    fly_count: int
    capacity_percent: float
    effectiveness_percent: float
    adhesive_quality_percent: float
    temperature_c: float
    last_deployment: Optional[datetime]
    last_cleaning: Optional[datetime]
    total_captures: int
    deployment_count: int
    error_count: int
    metadata: Optional[Dict[str, Any]] = None

    def is_saturated(self) -> bool:
        """Check if trap is saturated."""
        return self.capacity_percent >= 100.0

    def needs_replacement(self) -> bool:
        """Check if trap needs replacement."""
        return self.adhesive_quality_percent <= 40.0

    def needs_cleaning(self) -> bool:
        """Check if trap needs cleaning."""
        if not self.last_cleaning:
            return True
        hours_since_cleaning = (
            datetime.now() - self.last_cleaning
        ).total_seconds() / 3600.0
        return hours_since_cleaning > 168.0  # Weekly


@dataclass
class CaptureEvent:
    """Fly capture event."""

    event_id: str
    timestamp: datetime
    trap_id: int
    fly_size_mm: float
    capture_location: Tuple[float, float]  # x, y on trap surface
    capture_force_n: float
    struggle_duration_seconds: float
    escape_attempts: int
    success: bool
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class DeploymentResult:
    """Result of trap deployment."""

    deployment_id: str
    timestamp: datetime
    pattern: DeploymentPattern
    status: TrapStatus
    duration_seconds: float
    traps_deployed: int
    traps_active: int
    estimated_coverage_percent: float
    success: bool
    error_message: Optional[str] = None
    trap_states: Optional[List[Dict[str, Any]]] = None
    environmental_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["pattern"] = self.pattern.name
        data["status"] = self.status.name
        return data


@dataclass
class EffectivenessReport:
    """Trap effectiveness report."""

    timestamp: datetime
    overall_effectiveness_percent: float
    capture_rate_flies_per_hour: float
    saturation_level_percent: float
    adhesive_quality_average_percent: float
    hotspots_detected: List[Tuple[float, float]]  # x, y coordinates
    recommendations: List[str]
    test_duration_hours: float
    test_conditions: Dict[str, Any]


class StickyTrapSystem:
    """
    Sticky trap system for capturing flies.
    Manages multiple traps, deployment patterns, and effectiveness monitoring.
    """

    def __init__(self, config: Optional[StickyTrapConfig] = None):
        """Initialize sticky trap system."""
        self.config = config or StickyTrapConfig()
        self.status = TrapStatus.READY
        self.active_pattern = DeploymentPattern.FULL_COVERAGE

        # Trap management
        self.traps: Dict[int, TrapState] = {}
        self._initialize_traps()

        # Deployment tracking
        self.current_deployment_id: Optional[str] = None
        self.deployment_start_time: Optional[datetime] = None
        self.total_captures: int = 0
        self.total_deployments: int = 0

        # Performance tracking
        self.capture_history: List[CaptureEvent] = []
        self.deployment_history: List[DeploymentResult] = []
        self.effectiveness_history: List[EffectivenessReport] = []

        # Adaptive control
        self.adaptive_parameters: Dict[str, Any] = {
            "fly_activity_map": {},  # Maps positions to fly activity
            "hotspots": [],
            "last_activity_update": None,
            "pattern_effectiveness": {
                pattern.name: 0.8 for pattern in DeploymentPattern
            },
        }

        # Maintenance tracking
        self.last_calibration: Optional[datetime] = None
        self.last_maintenance: Optional[datetime] = None
        self.maintenance_alerts: List[str] = []

        # Hardware interface (simulated for now)
        self.hardware_connected = False
        self.simulation_mode = True

        # Async components
        self._deployment_task: Optional[asyncio.Task] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        print(f"StickyTrapSystem initialized with {self.config.trap_count} traps")

    def _initialize_traps(self) -> None:
        """Initialize trap states."""
        trap_types = list(StickyTrapType)

        for i in range(self.config.trap_count):
            trap_type = trap_types[i % len(trap_types)]

            # Calculate grid position
            grid_size = int(math.sqrt(self.config.trap_count))
            row = i // grid_size
            col = i % grid_size

            position = (
                col * 200.0,  # x: 200mm spacing
                row * 200.0,  # y: 200mm spacing
                0.0,  # z: surface level
            )

            self.traps[i] = TrapState(
                trap_id=i,
                trap_type=trap_type,
                status=TrapStatus.READY,
                deployment_position=position,
                fly_count=0,
                capacity_percent=0.0,
                effectiveness_percent=85.0,
                adhesive_quality_percent=95.0,
                temperature_c=22.0,
                last_deployment=None,
                last_cleaning=None,
                total_captures=0,
                deployment_count=0,
                error_count=0,
            )

    async def deploy_traps(
        self, pattern: DeploymentPattern = DeploymentPattern.FULL_COVERAGE
    ) -> DeploymentResult:
        """Deploy sticky traps."""
        if self.status in [TrapStatus.ACTIVE, TrapStatus.DEPLOYING]:
            return DeploymentResult(
                deployment_id=self.current_deployment_id or "unknown",
                timestamp=datetime.now(),
                pattern=pattern,
                status=self.status,
                duration_seconds=0.0,
                traps_deployed=0,
                traps_active=0,
                estimated_coverage_percent=0.0,
                success=False,
                error_message=f"System already {self.status.name.lower()}",
            )

        print(f"Deploying sticky traps with {pattern.name} pattern")

        self.status = TrapStatus.DEPLOYING
        self.active_pattern = pattern
        self.current_deployment_id = self._generate_deployment_id()
        self.deployment_start_time = datetime.now()

        try:
            # Connect to hardware (simulated)
            await self._connect_hardware()

            # Deploy traps according to pattern
            deployed_traps = await self._deploy_for_pattern(pattern)

            # Start monitoring
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

            # Wait for deployment to complete
            await asyncio.sleep(self.config.deployment_time_seconds)

            self.status = TrapStatus.ACTIVE
            self.total_deployments += 1

            # Calculate coverage
            coverage = self._calculate_coverage(pattern, deployed_traps)

            print(
                f"Sticky traps deployed: {len(deployed_traps)} traps, {coverage:.1f}% coverage"
            )

            result = DeploymentResult(
                deployment_id=self.current_deployment_id,
                timestamp=datetime.now(),
                pattern=pattern,
                status=TrapStatus.ACTIVE,
                duration_seconds=self.config.deployment_time_seconds,
                traps_deployed=len(deployed_traps),
                traps_active=len(deployed_traps),
                estimated_coverage_percent=coverage,
                success=True,
                trap_states=[asdict(trap) for trap in deployed_traps],
            )

            self.deployment_history.append(result)
            return result

        except Exception as e:
            self.status = TrapStatus.ERROR
            print(f"Failed to deploy traps: {e}")

            return DeploymentResult(
                deployment_id=self.current_deployment_id or "error",
                timestamp=datetime.now(),
                pattern=pattern,
                status=TrapStatus.ERROR,
                duration_seconds=0.0,
                traps_deployed=0,
                traps_active=0,
                estimated_coverage_percent=0.0,
                success=False,
                error_message=str(e),
            )

    async def retract_traps(self) -> DeploymentResult:
        """Retract sticky traps."""
        if self.status in [TrapStatus.READY, TrapStatus.RETRACTING]:
            return DeploymentResult(
                deployment_id=self.current_deployment_id or "unknown",
                timestamp=datetime.now(),
                pattern=self.active_pattern,
                status=self.status,
                duration_seconds=0.0,
                traps_deployed=0,
                traps_active=0,
                estimated_coverage_percent=0.0,
                success=False,
                error_message=f"System already {self.status.name.lower()}",
            )

        print("Retracting sticky traps")
        self.status = TrapStatus.RETRACTING

        try:
            # Signal shutdown
            self._shutdown_event.set()

            # Retract traps
            await self._retract_all_traps()

            # Wait for retraction to complete
            await asyncio.sleep(self.config.retraction_time_seconds)

            # Cancel monitoring task
            if self._monitoring_task:
                self._monitoring_task.cancel()

            # Calculate duration
            duration = 0.0
            if self.deployment_start_time:
                duration = (datetime.now() - self.deployment_start_time).total_seconds()

            # Count active traps before retraction
            active_traps = [
                trap for trap in self.traps.values() if trap.status == TrapStatus.ACTIVE
            ]

            self.status = TrapStatus.READY
            self._shutdown_event.clear()

            print("Sticky traps retracted")

            result = DeploymentResult(
                deployment_id=self.current_deployment_id or "retraction",
                timestamp=datetime.now(),
                pattern=self.active_pattern,
                status=TrapStatus.READY,
                duration_seconds=duration,
                traps_deployed=len(active_traps),
                traps_active=0,
                estimated_coverage_percent=0.0,
                success=True,
            )

            # Reset for next deployment
            self.current_deployment_id = None
            self.deployment_start_time = None

            return result

        except Exception as e:
            self.status = TrapStatus.ERROR
            print(f"Error retracting traps: {e}")

            return DeploymentResult(
                deployment_id=self.current_deployment_id or "error",
                timestamp=datetime.now(),
                pattern=self.active_pattern,
                status=TrapStatus.ERROR,
                duration_seconds=0.0,
                traps_deployed=0,
                traps_active=0,
                estimated_coverage_percent=0.0,
                success=False,
                error_message=str(e),
            )

    async def report_capture(
        self, trap_id: int, fly_size_mm: float = 3.0
    ) -> CaptureEvent:
        """Report a fly capture."""
        if trap_id not in self.traps:
            raise ValueError(f"Invalid trap ID: {trap_id}")

        trap = self.traps[trap_id]

        if trap.status != TrapStatus.ACTIVE:
            print(f"Trap {trap_id} is not active (status: {trap.status.name})")
            # Still create event but mark as unsuccessful
            event = CaptureEvent(
                event_id=self._generate_event_id(),
                timestamp=datetime.now(),
                trap_id=trap_id,
                fly_size_mm=fly_size_mm,
                capture_location=(
                    random.uniform(0, self.config.trap_width_mm),
                    random.uniform(0, self.config.trap_height_mm),
                ),
                capture_force_n=0.0,
                struggle_duration_seconds=0.0,
                escape_attempts=0,
                success=False,
                metadata={"error": "trap_not_active"},
            )
            self.capture_history.append(event)
            return event

        # Simulate capture
        capture_location = (
            random.uniform(0, self.config.trap_width_mm),
            random.uniform(0, self.config.trap_height_mm),
        )

        # Capture force depends on adhesive quality
        base_force = 0.05  # Newtons
        force = base_force * (trap.adhesive_quality_percent / 100.0)

        # Struggle duration depends on fly size and adhesive
        struggle_duration = fly_size_mm * 0.5 * (100.0 / trap.adhesive_quality_percent)

        # Escape attempts (simulated)
        escape_attempts = random.randint(1, 5)

        # Update trap state
        trap.fly_count += 1
        trap.total_captures += 1
        trap.capacity_percent = (
            trap.fly_count / self.config.max_capacity_flies
        ) * 100.0

        # Update adhesive quality (degrades with use)
        quality_loss = random.uniform(0.1, 0.5)
        trap.adhesive_quality_percent = max(
            0.0, trap.adhesive_quality_percent - quality_loss
        )

        # Update effectiveness (decreases with saturation)
        if trap.capacity_percent > self.config.saturation_threshold_percent:
            effectiveness_loss = (
                trap.capacity_percent - self.config.saturation_threshold_percent
            ) / 10.0
            trap.effectiveness_percent = max(
                0.0, trap.effectiveness_percent - effectiveness_loss
            )

        # Update global counters
        self.total_captures += 1

        # Update adaptive parameters
        await self._update_adaptive_parameters(trap_id, capture_location)

        # Create capture event
        event = CaptureEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(),
            trap_id=trap_id,
            fly_size_mm=fly_size_mm,
            capture_location=capture_location,
            capture_force_n=force,
            struggle_duration_seconds=struggle_duration,
            escape_attempts=escape_attempts,
            success=True,
            metadata={
                "adhesive_quality": trap.adhesive_quality_percent,
                "trap_capacity": trap.capacity_percent,
                "effectiveness": trap.effectiveness_percent,
            },
        )

        self.capture_history.append(event)

        print(
            f"Capture reported: trap {trap_id} caught {fly_size_mm:.1f}mm fly (total: {trap.fly_count})"
        )

        return event

    async def measure_effectiveness(self) -> EffectivenessReport:
        """Measure current trap effectiveness."""
        print("Measuring sticky trap effectiveness")

        # Calculate overall metrics
        active_traps = [
            trap for trap in self.traps.values() if trap.status == TrapStatus.ACTIVE
        ]

        if not active_traps:
            return EffectivenessReport(
                timestamp=datetime.now(),
                overall_effectiveness_percent=0.0,
                capture_rate_flies_per_hour=0.0,
                saturation_level_percent=0.0,
                adhesive_quality_average_percent=0.0,
                hotspots_detected=[],
                recommendations=["Deploy traps to start capturing flies"],
                test_duration_hours=24.0,
                test_conditions={"traps_active": 0},
            )

        # Calculate averages
        total_effectiveness = sum(trap.effectiveness_percent for trap in active_traps)
        total_adhesive_quality = sum(
            trap.adhesive_quality_percent for trap in active_traps
        )
        total_saturation = sum(trap.capacity_percent for trap in active_traps)

        avg_effectiveness = total_effectiveness / len(active_traps)
        avg_adhesive_quality = total_adhesive_quality / len(active_traps)
        avg_saturation = total_saturation / len(active_traps)

        # Calculate capture rate (flies per hour)
        # Look at last 24 hours of captures
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_captures = [
            event
            for event in self.capture_history
            if event.timestamp > cutoff_time and event.success
        ]
        capture_rate = len(recent_captures) / 24.0  # flies per hour

        # Detect hotspots from capture locations
        hotspots = self._detect_hotspots()

        # Generate recommendations
        recommendations = self._generate_effectiveness_recommendations(
            avg_effectiveness, avg_adhesive_quality, avg_saturation, hotspots
        )

        report = EffectivenessReport(
            timestamp=datetime.now(),
            overall_effectiveness_percent=avg_effectiveness,
            capture_rate_flies_per_hour=capture_rate,
            saturation_level_percent=avg_saturation,
            adhesive_quality_average_percent=avg_adhesive_quality,
            hotspots_detected=hotspots,
            recommendations=recommendations,
            test_duration_hours=24.0,
            test_conditions={
                "traps_active": len(active_traps),
                "total_captures": self.total_captures,
                "pattern": self.active_pattern.name,
            },
        )

        self.effectiveness_history.append(report)
        return report

    async def _connect_hardware(self) -> None:
        """Connect to hardware components."""
        if self.simulation_mode:
            print("Simulating hardware connection for sticky traps")
            await asyncio.sleep(0.5)
            self.hardware_connected = True
        else:
            # Actual hardware connection would go here
            raise NotImplementedError("Hardware connection not implemented")

    async def _deploy_for_pattern(self, pattern: DeploymentPattern) -> List[TrapState]:
        """Deploy traps according to specified pattern."""
        deployed_traps = []

        print(f"Deploying traps with {pattern.name} pattern")

        for trap_id, trap in self.traps.items():
            # Determine if this trap should be deployed based on pattern
            should_deploy = self._should_deploy_trap(trap_id, pattern)

            if should_deploy:
                trap.status = TrapStatus.ACTIVE
                trap.last_deployment = datetime.now()
                trap.deployment_count += 1
                deployed_traps.append(trap)

                if self.simulation_mode:
                    print(
                        f"  Trap {trap_id} deployed at position {trap.deployment_position}"
                    )
                    await asyncio.sleep(0.1)

        return deployed_traps

    async def _retract_all_traps(self) -> None:
        """Retract all traps."""
        print("Retracting all traps")

        for trap_id, trap in self.traps.items():
            if trap.status == TrapStatus.ACTIVE:
                trap.status = TrapStatus.READY

                if self.simulation_mode:
                    print(f"  Trap {trap_id} retracted")
                    await asyncio.sleep(0.05)

    async def _monitoring_loop(self) -> None:
        """Monitoring loop for trap system."""
        print("Starting sticky trap monitoring loop")

        try:
            while not self._shutdown_event.is_set():
                # Check trap conditions
                await self._check_trap_conditions()

                # Update adaptive parameters
                await self._update_adaptive_patterns()

                # Check for maintenance needs
                await self._check_maintenance()

                # Log status
                await self._log_status()

                # Sleep for monitoring interval
                await asyncio.sleep(5.0)

        except asyncio.CancelledError:
            print("Monitoring loop cancelled")
        except Exception as e:
            print(f"Error in monitoring loop: {e}")

    async def _check_trap_conditions(self) -> None:
        """Check trap conditions and update status."""
        for trap_id, trap in self.traps.items():
            if trap.status != TrapStatus.ACTIVE:
                continue

            # Check saturation
            if trap.capacity_percent >= 100.0:
                trap.status = TrapStatus.SATURATED
                self.maintenance_alerts.append(f"Trap {trap_id} is saturated")

            # Check adhesive degradation
            elif (
                trap.adhesive_quality_percent
                <= self.config.degradation_threshold_percent
            ):
                trap.status = TrapStatus.DEGRADED
                self.maintenance_alerts.append(f"Trap {trap_id} adhesive degraded")

            # Check effectiveness
            elif (
                trap.effectiveness_percent
                <= self.config.effectiveness_threshold_percent
            ):
                self.maintenance_alerts.append(f"Trap {trap_id} effectiveness low")

            # Simulate environmental effects
            await self._simulate_environmental_effects(trap)

    async def _simulate_environmental_effects(self, trap: TrapState) -> None:
        """Simulate environmental effects on trap."""
        if not self.simulation_mode:
            return

        # Temperature effects
        if trap.temperature_c < self.config.temperature_range_c[0]:
            # Too cold - adhesive less effective
            trap.adhesive_quality_percent -= 0.1
        elif trap.temperature_c > self.config.temperature_range_c[1]:
            # Too hot - adhesive degrades faster
            trap.adhesive_quality_percent -= 0.2

        # Natural degradation over time
        trap.adhesive_quality_percent -= 0.01  # 0.01% per check

        # Ensure values stay in bounds
        trap.adhesive_quality_percent = max(0.0, trap.adhesive_quality_percent)
        trap.effectiveness_percent = max(0.0, trap.effectiveness_percent)

    async def _update_adaptive_parameters(
        self, trap_id: int, location: Tuple[float, float]
    ) -> None:
        """Update adaptive parameters based on capture."""
        # Update fly activity map
        position_key = f"{location[0]:.1f},{location[1]:.1f}"
        self.adaptive_parameters["fly_activity_map"][position_key] = (
            self.adaptive_parameters["fly_activity_map"].get(position_key, 0) + 1
        )

        # Update last activity time
        self.adaptive_parameters["last_activity_update"] = datetime.now()

        # Recalculate hotspots
        self._recalculate_hotspots()

    async def _update_adaptive_patterns(self) -> None:
        """Update pattern effectiveness based on performance."""
        if not self.capture_history:
            return

        # Calculate effectiveness for current pattern
        recent_captures = [
            event
            for event in self.capture_history[-100:]  # Last 100 captures
            if event.success
        ]

        if recent_captures:
            # Simple effectiveness metric: captures per trap
            active_traps = [
                t for t in self.traps.values() if t.status == TrapStatus.ACTIVE
            ]
            if active_traps:
                captures_per_trap = len(recent_captures) / len(active_traps)
                self.adaptive_parameters["pattern_effectiveness"][
                    self.active_pattern.name
                ] = min(1.0, captures_per_trap / 10.0)  # Normalize to 0-1

    def _should_deploy_trap(self, trap_id: int, pattern: DeploymentPattern) -> bool:
        """Determine if a trap should be deployed based on pattern."""
        trap = self.traps[trap_id]
        position = trap.deployment_position

        if pattern == DeploymentPattern.FULL_COVERAGE:
            return True
        elif pattern == DeploymentPattern.HOTSPOT:
            # Deploy in hotspots
            return self._is_in_hotspot(position)
        elif pattern == DeploymentPattern.PERIMETER:
            # Deploy on perimeter
            return self._is_on_perimeter(position)
        elif pattern == DeploymentPattern.GRID:
            # Every other trap in grid
            return (trap_id % 2) == 0
        elif pattern == DeploymentPattern.SPIRAL:
            # Spiral pattern from center
            return self._is_in_spiral(trap_id, position)
        elif pattern == DeploymentPattern.RANDOM:
            # Random deployment
            return random.random() > 0.5
        elif pattern == DeploymentPattern.ADAPTIVE:
            # Adaptive based on previous effectiveness
            return self._adaptive_deployment_decision(trap_id)
        else:
            return True

    def _is_in_hotspot(self, position: Tuple[float, float, float]) -> bool:
        """Check if position is in a hotspot."""
        for hotspot in self.adaptive_parameters["hotspots"]:
            distance = math.sqrt(
                (position[0] - hotspot[0]) ** 2 + (position[1] - hotspot[1]) ** 2
            )
            if distance < 100.0:  # Within 100mm of hotspot
                return True
        return False

    def _is_on_perimeter(self, position: Tuple[float, float, float]) -> bool:
        """Check if position is on perimeter."""
        # Assuming deployment area is 1000x1000mm
        return (
            position[0] < 100.0
            or position[0] > 900.0
            or position[1] < 100.0
            or position[1] > 900.0
        )

    def _is_in_spiral(self, trap_id: int, position: Tuple[float, float, float]) -> bool:
        """Check if position is in spiral pattern."""
        # Simple spiral: traps closer to center deployed first
        center_x, center_y = 500.0, 500.0  # Center of deployment area
        distance = math.sqrt(
            (position[0] - center_x) ** 2 + (position[1] - center_y) ** 2
        )
        # Deploy traps within increasing distance based on trap_id
        max_distance = (trap_id + 1) * 100.0
        return distance <= max_distance

    def _adaptive_deployment_decision(self, trap_id: int) -> bool:
        """Make adaptive deployment decision."""
        trap = self.traps[trap_id]

        # Consider trap condition
        if trap.adhesive_quality_percent < 50.0:
            return False  # Don't deploy degraded traps

        # Consider previous effectiveness
        if trap.effectiveness_percent < 50.0:
            return False  # Don't deploy ineffective traps

        # Consider position in hotspots
        if self._is_in_hotspot(trap.deployment_position):
            return True  # Always deploy in hotspots

        # Random chance based on overall effectiveness
        overall_effectiveness = self.adaptive_parameters["pattern_effectiveness"][
            self.active_pattern.name
        ]
        return random.random() < overall_effectiveness

    def _calculate_coverage(
        self, pattern: DeploymentPattern, deployed_traps: List[TrapState]
    ) -> float:
        """Calculate estimated coverage percentage."""
        if not deployed_traps:
            return 0.0

        # Simple coverage calculation based on pattern
        base_coverage_per_trap = 0.15  # Each trap covers ~15% of area

        if pattern == DeploymentPattern.FULL_COVERAGE:
            multiplier = 1.0
        elif pattern == DeploymentPattern.HOTSPOT:
            multiplier = 0.8
        elif pattern == DeploymentPattern.PERIMETER:
            multiplier = 0.6
        elif pattern == DeploymentPattern.GRID:
            multiplier = 0.5
        elif pattern == DeploymentPattern.SPIRAL:
            multiplier = 0.7
        elif pattern == DeploymentPattern.RANDOM:
            multiplier = 0.4
        elif pattern == DeploymentPattern.ADAPTIVE:
            multiplier = 0.9
        else:
            multiplier = 0.5

        coverage = len(deployed_traps) * base_coverage_per_trap * multiplier
        return min(100.0, coverage * 100.0)

    def _detect_hotspots(self) -> List[Tuple[float, float]]:
        """Detect fly activity hotspots."""
        hotspots = []

        if not self.adaptive_parameters["fly_activity_map"]:
            return hotspots

        # Group nearby activity
        activity_threshold = 3  # Minimum captures to be a hotspot

        for position_str, count in self.adaptive_parameters["fly_activity_map"].items():
            if count >= activity_threshold:
                x, y = map(float, position_str.split(","))
                hotspots.append((x, y))

        # Limit number of hotspots
        hotspots.sort(
            key=lambda pos: self.adaptive_parameters["fly_activity_map"][
                f"{pos[0]:.1f},{pos[1]:.1f}"
            ],
            reverse=True,
        )
        return hotspots[:5]  # Top 5 hotspots

    def _recalculate_hotspots(self) -> None:
        """Recalculate hotspots from activity map."""
        self.adaptive_parameters["hotspots"] = self._detect_hotspots()

    def _generate_effectiveness_recommendations(
        self,
        effectiveness: float,
        adhesive_quality: float,
        saturation: float,
        hotspots: List[Tuple[float, float]],
    ) -> List[str]:
        """Generate recommendations based on effectiveness metrics."""
        recommendations = []

        if effectiveness < self.config.effectiveness_threshold_percent:
            recommendations.append("Consider changing deployment pattern")
            recommendations.append("Check adhesive quality on all traps")

        if adhesive_quality < 60.0:
            recommendations.append("Replace degraded adhesive on traps")
            recommendations.append("Consider using different adhesive type")

        if saturation > self.config.saturation_threshold_percent:
            recommendations.append("Clean or replace saturated traps")
            recommendations.append("Increase trap density in high-activity areas")

        if hotspots:
            recommendations.append(
                f"Focus deployment on {len(hotspots)} detected hotspots"
            )

        # Add maintenance alerts
        recommendations.extend(self.maintenance_alerts[:3])  # Limit to 3 most important

        return recommendations

    async def _check_maintenance(self) -> None:
        """Check if maintenance is needed."""
        now = datetime.now()

        # Check calibration
        if self.last_calibration:
            hours_since = (now - self.last_calibration).total_seconds() / 3600.0
            if hours_since > self.config.calibration_interval_hours:
                self.maintenance_alerts.append("System calibration needed")

        # Check general maintenance
        if self.last_maintenance:
            hours_since = (now - self.last_maintenance).total_seconds() / 3600.0
            if hours_since > self.config.maintenance_interval_hours:
                self.maintenance_alerts.append("System maintenance needed")

        # Check individual traps
        for trap_id, trap in self.traps.items():
            if trap.needs_cleaning():
                self.maintenance_alerts.append(f"Trap {trap_id} needs cleaning")
            if trap.needs_replacement():
                self.maintenance_alerts.append(f"Trap {trap_id} needs replacement")

    async def _log_status(self) -> None:
        """Log current system status."""
        if self.status != TrapStatus.ACTIVE:
            return

        active_traps = [t for t in self.traps.values() if t.status == TrapStatus.ACTIVE]
        if not active_traps:
            return

        # Simple status log
        avg_effectiveness = sum(t.effectiveness_percent for t in active_traps) / len(
            active_traps
        )
        avg_capacity = sum(t.capacity_percent for t in active_traps) / len(active_traps)

        print(
            f"Sticky trap status: {len(active_traps)} active, "
            f"effectiveness: {avg_effectiveness:.1f}%, "
            f"capacity: {avg_capacity:.1f}%"
        )

    def _generate_deployment_id(self) -> str:
        """Generate unique deployment ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = random.randint(1000, 9999)
        return f"ST_{timestamp}_{random_suffix}"

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        random_suffix = random.randint(100, 999)
        return f"CE_{timestamp}_{random_suffix}"

    async def calibrate(self) -> bool:
        """Calibrate the sticky trap system."""
        if self.status != TrapStatus.READY:
            print(f"Cannot calibrate when system is {self.status.name}")
            return False

        print("Starting sticky trap calibration")
        self.status = TrapStatus.CALIBRATING

        try:
            # Simulate calibration process
            if self.simulation_mode:
                print("Calibrating deployment mechanisms...")
                await asyncio.sleep(2.0)

                print("Testing trap deployment positions...")
                await asyncio.sleep(1.5)

                print("Verifying adhesive quality sensors...")
                await asyncio.sleep(1.0)

            # Update calibration timestamp
            self.last_calibration = datetime.now()

            # Clear calibration alerts
            self.maintenance_alerts = [
                alert
                for alert in self.maintenance_alerts
                if "calibration" not in alert.lower()
            ]

            self.status = TrapStatus.READY
            print("Calibration complete")
            return True

        except Exception as e:
            self.status = TrapStatus.ERROR
            print(f"Calibration failed: {e}")
            return False

    async def perform_maintenance(self) -> bool:
        """Perform routine maintenance."""
        if self.status != TrapStatus.READY:
            print(f"Cannot perform maintenance when system is {self.status.name}")
            return False

        print("Starting sticky trap maintenance")
        self.status = TrapStatus.MAINTENANCE

        try:
            # Simulate maintenance process
            if self.simulation_mode:
                print("Cleaning trap surfaces...")
                await asyncio.sleep(1.5)

                print("Replacing adhesive on degraded traps...")
                await asyncio.sleep(2.0)

                print("Testing deployment mechanisms...")
                await asyncio.sleep(1.0)

                print("Resetting trap counters...")
                await asyncio.sleep(0.5)

            # Reset trap states
            for trap in self.traps.values():
                if trap.status in [TrapStatus.SATURATED, TrapStatus.DEGRADED]:
                    trap.fly_count = 0
                    trap.capacity_percent = 0.0
                    trap.adhesive_quality_percent = 95.0
                    trap.effectiveness_percent = 85.0
                    trap.status = TrapStatus.READY
                    trap.last_cleaning = datetime.now()

            # Update maintenance timestamp
            self.last_maintenance = datetime.now()

            # Clear maintenance alerts
            self.maintenance_alerts = []

            self.status = TrapStatus.READY
            print("Maintenance complete")
            return True

        except Exception as e:
            self.status = TrapStatus.ERROR
            print(f"Maintenance failed: {e}")
            return False

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        active_traps = [t for t in self.traps.values() if t.status == TrapStatus.ACTIVE]
        saturated_traps = [
            t for t in self.traps.values() if t.status == TrapStatus.SATURATED
        ]
        degraded_traps = [
            t for t in self.traps.values() if t.status == TrapStatus.DEGRADED
        ]

        return {
            "system": {
                "status": self.status.name,
                "active_pattern": self.active_pattern.name,
                "deployment_id": self.current_deployment_id,
                "deployment_duration_seconds": (
                    (datetime.now() - self.deployment_start_time).total_seconds()
                    if self.deployment_start_time
                    else 0.0
                ),
            },
            "traps": {
                "total": len(self.traps),
                "active": len(active_traps),
                "saturated": len(saturated_traps),
                "degraded": len(degraded_traps),
                "ready": len(
                    [t for t in self.traps.values() if t.status == TrapStatus.READY]
                ),
            },
            "performance": {
                "total_captures": self.total_captures,
                "total_deployments": self.total_deployments,
                "average_effectiveness": (
                    sum(t.effectiveness_percent for t in active_traps)
                    / len(active_traps)
                    if active_traps
                    else 0.0
                ),
                "average_capacity": (
                    sum(t.capacity_percent for t in active_traps) / len(active_traps)
                    if active_traps
                    else 0.0
                ),
                "average_adhesive_quality": (
                    sum(t.adhesive_quality_percent for t in active_traps)
                    / len(active_traps)
                    if active_traps
                    else 0.0
                ),
                "hotspots_detected": len(self.adaptive_parameters["hotspots"]),
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
                "capture_events": len(self.capture_history),
                "deployments": len(self.deployment_history),
                "effectiveness_reports": len(self.effectiveness_history),
                "latest_effectiveness": (
                    self.effectiveness_history[-1].overall_effectiveness_percent
                    if self.effectiveness_history
                    else 0.0
                ),
            },
        }

    def get_capture_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get capture history."""
        history = self.capture_history[-limit:] if self.capture_history else []
        return [event.to_dict() for event in history]

    def get_deployment_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get deployment history."""
        history = self.deployment_history[-limit:] if self.deployment_history else []
        return [result.to_dict() for result in history]

    def get_effectiveness_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get effectiveness history."""
        history = (
            self.effectiveness_history[-limit:] if self.effectiveness_history else []
        )
        return [asdict(report) for report in history]

    def clear_history(self) -> None:
        """Clear performance history."""
        self.capture_history = []
        self.deployment_history = []
        self.effectiveness_history = []
        self.adaptive_parameters["fly_activity_map"] = {}
        self.adaptive_parameters["hotspots"] = []
        print("Performance history cleared")

    async def emergency_shutdown(self) -> None:
        """Emergency shutdown procedure."""
        print("EMERGENCY SHUTDOWN INITIATED FOR STICKY TRAP SYSTEM")

        # Immediate retraction
        for trap in self.traps.values():
            if trap.status == TrapStatus.ACTIVE:
                trap.status = TrapStatus.READY

        # Cancel monitoring task
        if self._monitoring_task:
            self._monitoring_task.cancel()

        # Set error state
        self.status = TrapStatus.ERROR

        print("Emergency shutdown complete")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.status in [TrapStatus.ACTIVE, TrapStatus.DEPLOYING]:
            await self.retract_traps()


# Example usage and test function
async def test_sticky_trap_system():
    """Test the sticky trap system."""
    print("\n" + "=" * 60)
    print("TESTING STICKY TRAP SYSTEM")
    print("=" * 60)

    # Create system
    config = StickyTrapConfig(
        trap_count=4,  # Fewer traps for testing
        max_capacity_flies=20,
    )

    system = StickyTrapSystem(config)

    try:
        # Test deployment
        print("\n1. Testing trap deployment...")
        result = await system.deploy_traps(DeploymentPattern.FULL_COVERAGE)
        print(f"   Deployment result: {result.success}")
        print(f"   Traps deployed: {result.traps_deployed}")
        print(f"   Coverage: {result.estimated_coverage_percent:.1f}%")

        # Run for a bit
        await asyncio.sleep(1.0)

        # Test capture reporting
        print("\n2. Testing capture reporting...")
        for i in range(5):
            trap_id = random.randint(0, config.trap_count - 1)
            event = await system.report_capture(
                trap_id, fly_size_mm=random.uniform(2.0, 4.0)
            )
            print(f"   Capture {i + 1}: trap {trap_id}, success: {event.success}")
            await asyncio.sleep(0.2)

        # Test effectiveness measurement
        print("\n3. Testing effectiveness measurement...")
        effectiveness = await system.measure_effectiveness()
        print(
            f"   Overall effectiveness: {effectiveness.overall_effectiveness_percent:.1f}%"
        )
        print(
            f"   Capture rate: {effectiveness.capture_rate_flies_per_hour:.1f} flies/hour"
        )
        print(f"   Recommendations: {len(effectiveness.recommendations)}")

        # Test status report
        print("\n4. Testing status report...")
        status = system.get_status_report()
        print(f"   System status: {status['system']['status']}")
        print(f"   Active traps: {status['traps']['active']}")
        print(f"   Total captures: {status['performance']['total_captures']}")

        # Test retraction
        print("\n5. Testing trap retraction...")
        result = await system.retract_traps()
        print(f"   Retraction result: {result.success}")
        print(f"   Duration: {result.duration_seconds:.1f}s")

        # Test calibration
        print("\n6. Testing calibration...")
        calibrated = await system.calibrate()
        print(f"   Calibration result: {calibrated}")

        # Test maintenance
        print("\n7. Testing maintenance...")
        maintained = await system.perform_maintenance()
        print(f"   Maintenance result: {maintained}")

        print("\n" + "=" * 60)
        print("STICKY TRAP SYSTEM TEST COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR during test: {e}")
        await system.emergency_shutdown()


if __name__ == "__main__":
    # Run test
    asyncio.run(test_sticky_trap_system())

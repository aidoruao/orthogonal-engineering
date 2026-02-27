"""
Crusader Combat Refrigerator - Spore Deployment System
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Spore deployment system for Beauveria bassiana.
Manages spore reservoir, deployment patterns, and biological integration.
"""

import asyncio
import math
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from datetime import time as dt_time
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from ..core.constants import EnvironmentalConstants, PatternConstants, TimeConstants
from ..core.utils.time_utils import TimeUtils


class DeploymentPattern(Enum):
    """Spore deployment patterns."""

    MORNING = auto()
    EVENING = auto()
    ADAPTIVE = auto()
    RANDOM = auto()
    DEFENSE = auto()
    PURGE = auto()


class DeploymentStatus(Enum):
    """Deployment status."""

    READY = auto()
    DEPLOYING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    RESERVOIR_EMPTY = auto()
    SYSTEM_ERROR = auto()


@dataclass
class DeploymentResult:
    """Result of a spore deployment."""

    deployment_id: str
    timestamp: datetime
    pattern: DeploymentPattern
    status: DeploymentStatus
    duration_seconds: float
    volume_ml: float
    concentration_percent: float
    success: bool
    error_message: Optional[str] = None
    sensor_data: Optional[Dict[str, Any]] = None
    fly_count: Optional[int] = None
    humidity_percent: Optional[float] = None
    temperature_celsius: Optional[float] = None
    reservoir_level_ml: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["pattern"] = self.pattern.name
        data["status"] = self.status.name
        return data


@dataclass
class SporeReservoir:
    """Spore reservoir state."""

    capacity_ml: float
    current_level_ml: float
    concentration_percent: float
    last_refill: Optional[datetime]
    refill_count: int
    total_deployed_ml: float
    viability_percent: float
    temperature_celsius: float
    last_mixing: Optional[datetime]
    metadata: Optional[Dict[str, Any]] = None

    def get_percentage_full(self) -> float:
        """Get reservoir fill percentage."""
        if self.capacity_ml <= 0:
            return 0.0
        return (self.current_level_ml / self.capacity_ml) * 100.0

    def is_low(self, threshold_percent: float = 10.0) -> bool:
        """Check if reservoir is low."""
        return self.get_percentage_full() <= threshold_percent

    def is_empty(self) -> bool:
        """Check if reservoir is empty."""
        return self.current_level_ml <= 0.0


class SporeDeploymentSystem:
    """
    Spore deployment system for Beauveria bassiana.
    Manages reservoir, deployment patterns, and biological optimization.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize spore deployment system."""
        self.config = config or self._default_config()

        # Reservoir state
        self.reservoir = SporeReservoir(
            capacity_ml=self.config["reservoir_capacity_ml"],
            current_level_ml=self.config["initial_level_ml"],
            concentration_percent=self.config["spore_concentration"],
            last_refill=None,
            refill_count=0,
            total_deployed_ml=0.0,
            viability_percent=100.0,
            temperature_celsius=EnvironmentalConstants.OPTIMAL_TEMPERATURE,
            last_mixing=None,
        )

        # Deployment state
        self.deployment_history: List[DeploymentResult] = []
        self.current_deployment: Optional[DeploymentResult] = None
        self.deployment_lock = asyncio.Lock()

        # Pattern state
        self.pattern_enabled = {
            DeploymentPattern.MORNING: self.config["patterns"]["morning"]["enabled"],
            DeploymentPattern.EVENING: self.config["patterns"]["evening"]["enabled"],
            DeploymentPattern.ADAPTIVE: self.config["patterns"]["adaptive"]["enabled"],
            DeploymentPattern.RANDOM: self.config["patterns"]["random"]["enabled"],
        }

        # Statistics
        self.statistics = {
            "total_deployments": 0,
            "successful_deployments": 0,
            "failed_deployments": 0,
            "total_volume_ml": 0.0,
            "average_deployment_time": 0.0,
            "deployments_by_pattern": {
                pattern.name: 0 for pattern in DeploymentPattern
            },
            "last_deployment_time": None,
            "consecutive_failures": 0,
        }

        # Biological state
        self.biological_state = {
            "viability_trend": [],
            "environmental_impact": [],
            "efficacy_score": 100.0,
            "last_viability_check": None,
        }

        # Hardware interface (would be GPIO in production)
        self.hardware_initialized = False

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "reservoir_capacity_ml": 1000.0,
            "initial_level_ml": 1000.0,
            "spore_concentration": 0.1,
            "deployment_volume_ml": 5.0,
            "deployment_duration_seconds": 5.0,
            "low_reservoir_threshold_ml": 100.0,
            "min_viability_percent": 80.0,
            "patterns": {
                "morning": {
                    "enabled": True,
                    "start_time": "06:00",
                    "end_time": "08:00",
                    "intensity": "high",
                    "volume_multiplier": 1.5,
                },
                "evening": {
                    "enabled": True,
                    "start_time": "18:00",
                    "end_time": "20:00",
                    "intensity": "medium",
                    "volume_multiplier": 1.0,
                },
                "adaptive": {
                    "enabled": True,
                    "fly_threshold": 5,
                    "humidity_threshold": 60.0,
                    "volume_multiplier": 2.0,
                },
                "random": {
                    "enabled": False,
                    "probability": 0.1,
                    "volume_multiplier": 0.5,
                },
            },
            "bio_integration": {
                "optimal_temperature": EnvironmentalConstants.OPTIMAL_TEMPERATURE,
                "optimal_humidity": EnvironmentalConstants.OPTIMAL_HUMIDITY,
                "temperature_tolerance": 5.0,
                "humidity_tolerance": 10.0,
                "viability_decay_rate": 0.1,  # percent per day
            },
            "hardware": {
                "pump_pin": 17,
                "valve_pin": 27,
                "sensor_pin": 22,
                "flow_rate_ml_per_second": 1.0,
            },
        }

    async def initialize(self) -> bool:
        """Initialize the spore deployment system."""
        print("🔧 Initializing Spore Deployment System...")

        try:
            # Initialize hardware (simulated)
            await self._initialize_hardware()

            # Check reservoir
            if self.reservoir.is_empty():
                print("⚠️ Spore reservoir is empty")
                return False

            # Check viability
            if self.reservoir.viability_percent < self.config["min_viability_percent"]:
                print(f"⚠️ Spore viability low: {self.reservoir.viability_percent:.1f}%")
                return False

            self.hardware_initialized = True
            print(
                f"✅ Spore Deployment System initialized. Reservoir: {self.reservoir.current_level_ml:.1f}ml"
            )
            return True

        except Exception as e:
            print(f"❌ Spore Deployment System initialization failed: {e}")
            return False

    async def _initialize_hardware(self):
        """Initialize hardware components."""
        # In production, this would initialize GPIO pins
        print("  ↪️ Initializing pump and valves...")
        await asyncio.sleep(0.1)  # Simulated hardware initialization
        print("  ✅ Hardware initialized")

    async def should_deploy(
        self, sensor_data: Dict[str, Any], fly_count: int
    ) -> Tuple[bool, Optional[DeploymentPattern]]:
        """
        Determine if spores should be deployed.

        Returns:
            Tuple of (should_deploy, deployment_pattern)
        """
        # Check basic conditions
        if not self.hardware_initialized:
            return False, None

        if self.reservoir.is_empty():
            print("⚠️ Cannot deploy: Reservoir empty")
            return False, None

        if self.reservoir.viability_percent < self.config["min_viability_percent"]:
            print(
                f"⚠️ Cannot deploy: Viability too low ({self.reservoir.viability_percent:.1f}%)"
            )
            return False, None

        # Check for emergency deployment (very high fly count)
        if fly_count > 50:
            print(f"🚨 Emergency deployment triggered: {fly_count} flies detected")
            return True, DeploymentPattern.DEFENSE

        # Check pattern-based deployment
        patterns_to_check = [
            (DeploymentPattern.MORNING, self._check_morning_pattern),
            (DeploymentPattern.EVENING, self._check_evening_pattern),
            (
                DeploymentPattern.ADAPTIVE,
                lambda: self._check_adaptive_pattern(sensor_data, fly_count),
            ),
            (DeploymentPattern.RANDOM, self._check_random_pattern),
        ]

        for pattern, check_func in patterns_to_check:
            if self.pattern_enabled.get(pattern, False):
                should_deploy = await check_func()
                if should_deploy:
                    return True, pattern

        return False, None

    async def _check_morning_pattern(self) -> bool:
        """Check if morning pattern should trigger."""
        current_time = datetime.now().time()
        start_time = dt_time.fromisoformat(
            self.config["patterns"]["morning"]["start_time"]
        )
        end_time = dt_time.fromisoformat(self.config["patterns"]["morning"]["end_time"])

        if start_time <= current_time <= end_time:
            # Check if we haven't deployed recently
            if self._has_deployed_recently(hours=1):
                return False

            print("🌅 Morning pattern deployment check passed")
            return True

        return False

    async def _check_evening_pattern(self) -> bool:
        """Check if evening pattern should trigger."""
        current_time = datetime.now().time()
        start_time = dt_time.fromisoformat(
            self.config["patterns"]["evening"]["start_time"]
        )
        end_time = dt_time.fromisoformat(self.config["patterns"]["evening"]["end_time"])

        if start_time <= current_time <= end_time:
            # Check if we haven't deployed recently
            if self._has_deployed_recently(hours=1):
                return False

            print("🌆 Evening pattern deployment check passed")
            return True

        return False

    async def _check_adaptive_pattern(
        self, sensor_data: Dict[str, Any], fly_count: int
    ) -> bool:
        """Check if adaptive pattern should trigger."""
        fly_threshold = self.config["patterns"]["adaptive"]["fly_threshold"]
        humidity_threshold = self.config["patterns"]["adaptive"]["humidity_threshold"]

        humidity = sensor_data.get("humidity_percent", 0.0)

        if fly_count >= fly_threshold and humidity >= humidity_threshold:
            # Check if we haven't deployed recently
            if self._has_deployed_recently(minutes=30):
                return False

            print(
                f"🎯 Adaptive pattern deployment: {fly_count} flies, {humidity:.1f}% humidity"
            )
            return True

        return False

    async def _check_random_pattern(self) -> bool:
        """Check if random pattern should trigger."""
        probability = self.config["patterns"]["random"]["probability"]

        if random.random() < probability:
            # Check if we haven't deployed recently
            if self._has_deployed_recently(minutes=15):
                return False

            print("🎲 Random pattern deployment triggered")
            return True

        return False

    def _has_deployed_recently(self, minutes: int = 0, hours: int = 0) -> bool:
        """Check if deployment occurred recently."""
        if not self.deployment_history:
            return False

        recent_time = datetime.now().timestamp() - (hours * 3600 + minutes * 60)
        last_deployment = self.deployment_history[-1]

        return last_deployment.timestamp.timestamp() > recent_time

    async def deploy(
        self,
        pattern: DeploymentPattern = DeploymentPattern.ADAPTIVE,
        sensor_data: Optional[Dict[str, Any]] = None,
        fly_count: int = 0,
    ) -> DeploymentResult:
        """
        Deploy spores.

        Returns:
            DeploymentResult with outcome
        """
        import uuid

        async with self.deployment_lock:
            deployment_id = str(uuid.uuid4())
            start_time = datetime.now()

            print(f"🚀 Starting spore deployment {deployment_id} ({pattern.name})")

            # Create deployment result
            deployment = DeploymentResult(
                deployment_id=deployment_id,
                timestamp=start_time,
                pattern=pattern,
                status=DeploymentStatus.DEPLOYING,
                duration_seconds=0.0,
                volume_ml=0.0,
                concentration_percent=self.reservoir.concentration_percent,
                success=False,
                sensor_data=sensor_data,
                fly_count=fly_count,
                humidity_percent=sensor_data.get("humidity_percent")
                if sensor_data
                else None,
                temperature_celsius=sensor_data.get("temperature_celsius")
                if sensor_data
                else None,
                reservoir_level_ml=self.reservoir.current_level_ml,
            )

            self.current_deployment = deployment

            try:
                # Calculate deployment volume
                volume_ml = self._calculate_deployment_volume(pattern, fly_count)

                # Check reservoir
                if volume_ml > self.reservoir.current_level_ml:
                    deployment.status = DeploymentStatus.RESERVOIR_EMPTY
                    deployment.error_message = f"Insufficient reservoir: {self.reservoir.current_level_ml:.1f}ml < {volume_ml:.1f}ml"
                    print(f"❌ {deployment.error_message}")
                    self.current_deployment = None
                    return deployment

                # Update biological viability
                await self._update_viability(sensor_data)

                # Execute deployment
                success = await self._execute_deployment(volume_ml, pattern)

                # Update deployment result
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                deployment.duration_seconds = duration
                deployment.volume_ml = volume_ml if success else 0.0
                deployment.success = success
                deployment.status = (
                    DeploymentStatus.COMPLETED if success else DeploymentStatus.FAILED
                )

                if success:
                    # Update reservoir
                    self.reservoir.current_level_ml -= volume_ml
                    self.reservoir.total_deployed_ml += volume_ml

                    # Update statistics
                    self.statistics["total_deployments"] += 1
                    self.statistics["successful_deployments"] += 1
                    self.statistics["total_volume_ml"] += volume_ml
                    self.statistics["deployments_by_pattern"][pattern.name] += 1
                    self.statistics["last_deployment_time"] = end_time
                    self.statistics["consecutive_failures"] = 0

                    # Calculate average deployment time
                    total_time = self.statistics["average_deployment_time"] * (
                        self.statistics["successful_deployments"] - 1
                    )
                    self.statistics["average_deployment_time"] = (
                        total_time + duration
                    ) / self.statistics["successful_deployments"]

                    print(
                        f"✅ Deployment {deployment_id} completed: {volume_ml:.1f}ml in {duration:.1f}s"
                    )

                else:
                    self.statistics["failed_deployments"] += 1
                    self.statistics["consecutive_failures"] += 1
                    print(f"❌ Deployment {deployment_id} failed")

                # Add to history
                self.deployment_history.append(deployment)

                # Check reservoir level
                if self.reservoir.is_low(10.0):
                    print(
                        f"⚠️ Spore reservoir low: {self.reservoir.current_level_ml:.1f}ml ({self.reservoir.get_percentage_full():.1f}%)"
                    )

                return deployment

            except Exception as e:
                deployment.status = DeploymentStatus.SYSTEM_ERROR
                deployment.error_message = str(e)
                deployment.success = False

                self.statistics["failed_deployments"] += 1
                self.statistics["consecutive_failures"] += 1

                print(f"❌ Deployment {deployment_id} error: {e}")

                # Add to history even if failed
                self.deployment_history.append(deployment)
                return deployment

            finally:
                self.current_deployment = None

    def _calculate_deployment_volume(
        self, pattern: DeploymentPattern, fly_count: int
    ) -> float:
        """Calculate deployment volume based on pattern and conditions."""
        base_volume = self.config["deployment_volume_ml"]

        # Get pattern multiplier
        if pattern == DeploymentPattern.MORNING:
            multiplier = self.config["patterns"]["morning"]["volume_multiplier"]
        elif pattern == DeploymentPattern.EVENING:
            multiplier = self.config["patterns"]["evening"]["volume_multiplier"]
        elif pattern == DeploymentPattern.ADAPTIVE:
            multiplier = self.config["patterns"]["adaptive"]["volume_multiplier"]
            # Increase volume with fly count
            fly_multiplier = min(3.0, 1.0 + (fly_count / 10.0))
            multiplier *= fly_multiplier
        else:
            multiplier = 1.0

        # Apply temperature adjustment
        if self.temperature_c is not None:
            if self.temperature_c > 25.0:
                # Higher temperature = more evaporation, increase volume
                temp_multiplier = 1.0 + (self.temperature_c - 25.0) * 0.02
                multiplier *= min(1.5, temp_multiplier)
            elif self.temperature_c < 15.0:
                # Lower temperature = less evaporation, decrease volume
                temp_multiplier = 1.0 - (15.0 - self.temperature_c) * 0.03
                multiplier *= max(0.5, temp_multiplier)

        # Apply humidity adjustment
        if self.humidity_percent is not None:
            if self.humidity_percent > 70.0:
                # High humidity = less evaporation, decrease volume
                humidity_multiplier = 1.0 - (self.humidity_percent - 70.0) * 0.01
                multiplier *= max(0.7, humidity_multiplier)
            elif self.humidity_percent < 40.0:
                # Low humidity = more evaporation, increase volume
                humidity_multiplier = 1.0 + (40.0 - self.humidity_percent) * 0.015
                multiplier *= min(1.3, humidity_multiplier)

        # Calculate final volume
        volume_ml = base_volume * multiplier

        # Apply safety limits
        min_volume = self.config["min_deployment_volume_ml"]
        max_volume = self.config["max_deployment_volume_ml"]
        volume_ml = max(min_volume, min(max_volume, volume_ml))

        return volume_ml

    def _log_deployment(self, deployment: DeploymentResult) -> None:
        """Log deployment to history and file."""
        # Add to history
        self.deployment_history.append(deployment)

        # Keep history manageable
        if len(self.deployment_history) > self.config["max_history_entries"]:
            self.deployment_history = self.deployment_history[
                -self.config["max_history_entries"] :
            ]

        # Log to file if configured
        if self.config["log_deployments"]:
            try:
                log_entry = {
                    "timestamp": deployment.timestamp.isoformat(),
                    "pattern": deployment.pattern.name,
                    "volume_ml": deployment.volume_ml,
                    "duration_seconds": deployment.duration_seconds,
                    "success": deployment.success,
                    "error": deployment.error,
                    "fly_count": deployment.fly_count,
                    "temperature_c": deployment.temperature_c,
                    "humidity_percent": deployment.humidity_percent,
                }

                log_file = self.config["log_file_path"]
                os.makedirs(os.path.dirname(log_file), exist_ok=True)

                mode = "a" if os.path.exists(log_file) else "w"
                with open(log_file, mode, encoding="utf-8") as f:
                    if mode == "w":
                        # Write header
                        f.write(
                            "timestamp,pattern,volume_ml,duration_seconds,success,error,fly_count,temperature_c,humidity_percent\n"
                        )

                    # Write data
                    f.write(
                        f"{log_entry['timestamp']},{log_entry['pattern']},{log_entry['volume_ml']:.2f},{log_entry['duration_seconds']:.1f},{log_entry['success']},{log_entry['error'] or ''},{log_entry['fly_count']},{log_entry['temperature_c'] or ''},{log_entry['humidity_percent'] or ''}\n"
                    )

            except Exception as e:
                print(f"❌ Failed to log deployment: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        total_deployments = len(self.deployment_history)
        successful_deployments = sum(1 for d in self.deployment_history if d.success)
        failed_deployments = total_deployments - successful_deployments

        if total_deployments > 0:
            success_rate = (successful_deployments / total_deployments) * 100.0
            total_volume = sum(d.volume_ml for d in self.deployment_history)
            avg_volume = total_volume / total_deployments
        else:
            success_rate = 0.0
            total_volume = 0.0
            avg_volume = 0.0

        # Get recent deployments (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_deployments = [
            d for d in self.deployment_history if d.timestamp > cutoff_time
        ]

        # Calculate pattern usage
        pattern_counts = {}
        for pattern in DeploymentPattern:
            pattern_counts[pattern.name] = sum(
                1 for d in self.deployment_history if d.pattern == pattern
            )

        return {
            "system_status": self.status.name,
            "total_deployments": total_deployments,
            "successful_deployments": successful_deployments,
            "failed_deployments": failed_deployments,
            "success_rate_percent": success_rate,
            "total_volume_ml": total_volume,
            "average_volume_ml": avg_volume,
            "recent_deployments_24h": len(recent_deployments),
            "pattern_counts": pattern_counts,
            "current_temperature_c": self.temperature_c,
            "current_humidity_percent": self.humidity_percent,
            "current_fly_count": self.fly_count,
            "last_deployment_time": self.last_deployment_time.isoformat()
            if self.last_deployment_time
            else None,
            "next_scheduled_deployment": self.next_scheduled_deployment.isoformat()
            if self.next_scheduled_deployment
            else None,
        }

    def get_maintenance_alerts(self) -> List[str]:
        """Get maintenance alerts."""
        alerts = []

        # Check deployment frequency
        if (
            len(self.deployment_history)
            >= self.config["maintenance_interval_deployments"]
        ):
            alerts.append(
                f"Maintenance due after {len(self.deployment_history)} deployments"
            )

        # Check time since last maintenance
        if self.last_maintenance:
            days_since = (datetime.now() - self.last_maintenance).days
            if days_since >= self.config["maintenance_interval_days"]:
                alerts.append(
                    f"Maintenance due: {days_since} days since last maintenance"
                )

        # Check for consecutive failures
        recent_failures = 0
        for deployment in reversed(self.deployment_history[-5:]):  # Last 5 deployments
            if not deployment.success:
                recent_failures += 1
            else:
                break

        if recent_failures >= 3:
            alerts.append(f"{recent_failures} consecutive deployment failures")

        # Check spore reservoir level
        if self.spore_reservoir_ml < self.config["min_reservoir_ml"]:
            alerts.append(
                f"Low spore reservoir: {self.spore_reservoir_ml:.1f}ml remaining"
            )

        return alerts

    def perform_maintenance(self) -> Dict[str, Any]:
        """Perform system maintenance."""
        print("Performing spore deployment system maintenance...")

        maintenance_record = {
            "timestamp": datetime.now().isoformat(),
            "deployments_before": len(self.deployment_history),
            "reservoir_before": self.spore_reservoir_ml,
            "actions": [],
            "success": True,
            "errors": [],
        }

        try:
            # Refill reservoir
            refill_amount = (
                self.config["reservoir_capacity_ml"] - self.spore_reservoir_ml
            )
            if refill_amount > 0:
                self.spore_reservoir_ml = self.config["reservoir_capacity_ml"]
                maintenance_record["actions"].append(
                    f"Refilled reservoir with {refill_amount:.1f}ml"
                )
                print(f"  Refilled reservoir: +{refill_amount:.1f}ml")

            # Clear deployment history if too large
            if len(self.deployment_history) > self.config["max_history_entries"] * 2:
                old_count = len(self.deployment_history)
                self.deployment_history = self.deployment_history[
                    -self.config["max_history_entries"] :
                ]
                maintenance_record["actions"].append(
                    f"Cleared deployment history: {old_count} -> {len(self.deployment_history)} entries"
                )
                print(
                    f"  Cleared deployment history: {old_count} -> {len(self.deployment_history)} entries"
                )

            # Update maintenance timestamp
            self.last_maintenance = datetime.now()
            maintenance_record["actions"].append("Updated maintenance timestamp")

            # Reset error counters
            self.consecutive_errors = 0
            maintenance_record["actions"].append("Reset error counters")

            maintenance_record["reservoir_after"] = self.spore_reservoir_ml
            maintenance_record["deployments_after"] = len(self.deployment_history)

            print("✅ Maintenance completed successfully")

        except Exception as e:
            maintenance_record["success"] = False
            maintenance_record["errors"].append(str(e))
            print(f"❌ Maintenance failed: {e}")

        return maintenance_record

    def __del__(self):
        """Cleanup on destruction."""
        try:
            if self.status == SystemStatus.ACTIVE:
                self.stop()
        except:
            pass  # Ignore errors during cleanup

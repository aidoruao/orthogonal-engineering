"""
Crusader Combat Refrigerator - Monitoring Diagnostics System
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Comprehensive diagnostics system for monitoring all Crusader subsystems.
Provides real-time health monitoring, performance analysis, and predictive maintenance.
"""

import asyncio
import hashlib
import json
import random
import statistics
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.constants import EnvironmentalConstants, HardwareConstants, TimeConstants
from ..core.utils.hash_utils import HashEngine
from ..core.utils.time_utils import TimeUtils


class DiagnosticLevel(Enum):
    """Diagnostic severity levels."""

    INFO = auto()  # Informational message
    WARNING = auto()  # Warning condition
    ERROR = auto()  # Error condition
    CRITICAL = auto()  # Critical system failure
    DEBUG = auto()  # Debug information
    PERFORMANCE = auto()  # Performance metrics
    SECURITY = auto()  # Security-related event
    AUDIT = auto()  # Audit trail entry


class DiagnosticCategory(Enum):
    """Diagnostic categories."""

    SYSTEM = auto()  # Core system diagnostics
    WARFARE = auto()  # Warfare subsystem diagnostics
    MONITORING = auto()  # Monitoring subsystem diagnostics
    HARDWARE = auto()  # Hardware diagnostics
    INTERFACE = auto()  # Interface diagnostics
    NETWORK = auto()  # Network diagnostics
    SECURITY = auto()  # Security diagnostics
    PERFORMANCE = auto()  # Performance diagnostics
    ENVIRONMENTAL = auto()  # Environmental diagnostics
    POWER = auto()  # Power management diagnostics
    MEMORY = auto()  # Memory usage diagnostics
    STORAGE = auto()  # Storage diagnostics
    COMMUNICATION = auto()  # Communication diagnostics
    INTEGRITY = auto()  # System integrity diagnostics


class DiagnosticStatus(Enum):
    """Diagnostic check status."""

    PASS = auto()  # Check passed
    FAIL = auto()  # Check failed
    WARNING = auto()  # Check warning
    UNKNOWN = auto()  # Status unknown
    RUNNING = auto()  # Check in progress
    SKIPPED = auto()  # Check skipped
    TIMEOUT = auto()  # Check timed out


@dataclass
class DiagnosticCheck:
    """Individual diagnostic check definition."""

    check_id: str
    name: str
    description: str
    category: DiagnosticCategory
    level: DiagnosticLevel
    timeout_seconds: float
    dependencies: List[str]  # IDs of checks this depends on
    required: bool
    automated: bool
    repair_action: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""

    check_id: str
    timestamp: datetime
    status: DiagnosticStatus
    duration_seconds: float
    message: str
    data: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    error_details: Optional[str] = None
    repair_attempted: bool = False
    repair_successful: Optional[bool] = None
    next_check_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["status"] = self.status.name
        if self.next_check_time:
            data["next_check_time"] = self.next_check_time.isoformat()
        return data


@dataclass
class SystemHealth:
    """Overall system health assessment."""

    timestamp: datetime
    overall_status: DiagnosticStatus
    health_score: float  # 0.0 to 100.0
    passed_checks: int
    failed_checks: int
    warning_checks: int
    total_checks: int
    critical_issues: List[str]
    performance_metrics: Dict[str, float]
    subsystem_status: Dict[str, DiagnosticStatus]
    recommendations: List[str]
    next_full_check: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceMetrics:
    """System performance metrics."""

    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_bandwidth_mbps: float
    response_time_ms: float
    throughput_ops_per_second: float
    error_rate_percent: float
    uptime_seconds: float
    active_connections: int
    queue_depth: int
    cache_hit_rate_percent: float
    subsystem_metrics: Dict[str, Dict[str, float]]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PredictiveAlert:
    """Predictive maintenance alert."""

    alert_id: str
    timestamp: datetime
    component: str
    predicted_failure: str
    confidence_percent: float
    estimated_time_to_failure_hours: float
    severity: DiagnosticLevel
    current_health_percent: float
    degradation_rate_per_hour: float
    recommendations: List[str]
    historical_data: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class SystemDiagnostics:
    """
    Comprehensive diagnostics system for Crusader combat refrigerator.
    Monitors all subsystems, performs health checks, and provides predictive maintenance.
    """

    def __init__(self):
        """Initialize diagnostics system."""
        self.checks: Dict[str, DiagnosticCheck] = {}
        self.results: Dict[str, List[DiagnosticResult]] = {}
        self.health_history: List[SystemHealth] = []
        self.performance_history: List[PerformanceMetrics] = []
        self.predictive_alerts: List[PredictiveAlert] = []

        # Configuration
        self.check_interval_seconds = 60.0  # Default check interval
        self.performance_interval_seconds = 30.0
        self.health_history_limit = 1000
        self.performance_history_limit = 5000

        # State
        self.running = False
        self.last_full_check: Optional[datetime] = None
        self.last_performance_check: Optional[datetime] = None
        self.total_checks_performed = 0
        self.total_errors_detected = 0
        self.total_warnings_detected = 0

        # Async components
        self._check_task: Optional[asyncio.Task] = None
        self._performance_task: Optional[asyncio.Task] = None
        self._alert_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Initialize checks
        self._initialize_checks()

        print("SystemDiagnostics initialized with {} checks".format(len(self.checks)))

    def _initialize_checks(self) -> None:
        """Initialize diagnostic checks."""
        # System checks
        self._add_check(
            DiagnosticCheck(
                check_id="sys_core_operational",
                name="Core System Operational",
                description="Check if core system is operational",
                category=DiagnosticCategory.SYSTEM,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=5.0,
                dependencies=[],
                required=True,
                automated=True,
                repair_action="Restart core system",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="sys_memory_usage",
                name="Memory Usage",
                description="Check system memory usage",
                category=DiagnosticCategory.MEMORY,
                level=DiagnosticLevel.WARNING,
                timeout_seconds=3.0,
                dependencies=[],
                required=True,
                automated=True,
                repair_action="Clear memory cache or restart services",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="sys_disk_space",
                name="Disk Space",
                description="Check available disk space",
                category=DiagnosticCategory.STORAGE,
                level=DiagnosticLevel.WARNING,
                timeout_seconds=2.0,
                dependencies=[],
                required=True,
                automated=True,
                repair_action="Clean up temporary files or expand storage",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="sys_cpu_usage",
                name="CPU Usage",
                description="Check CPU utilization",
                category=DiagnosticCategory.PERFORMANCE,
                level=DiagnosticLevel.WARNING,
                timeout_seconds=2.0,
                dependencies=[],
                required=True,
                automated=True,
                repair_action="Optimize processes or upgrade hardware",
            )
        )

        # Warfare subsystem checks
        self._add_check(
            DiagnosticCheck(
                check_id="warfare_spore_deployment",
                name="Spore Deployment System",
                description="Check spore deployment system health",
                category=DiagnosticCategory.WARFARE,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=10.0,
                dependencies=["sys_core_operational"],
                required=True,
                automated=True,
                repair_action="Calibrate or repair spore deployment system",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="warfare_uv_sterilization",
                name="UV Sterilization System",
                description="Check UV sterilization system health",
                category=DiagnosticCategory.WARFARE,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=8.0,
                dependencies=["sys_core_operational"],
                required=True,
                automated=True,
                repair_action="Clean UV lamps or replace bulbs",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="warfare_air_curtain",
                name="Air Curtain System",
                description="Check air curtain system health",
                category=DiagnosticCategory.WARFARE,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=8.0,
                dependencies=["sys_core_operational"],
                required=True,
                automated=True,
                repair_action="Clean fans or replace motors",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="warfare_sticky_traps",
                name="Sticky Trap System",
                description="Check sticky trap system health",
                category=DiagnosticCategory.WARFARE,
                level=DiagnosticLevel.WARNING,
                timeout_seconds=6.0,
                dependencies=["sys_core_operational"],
                required=True,
                automated=True,
                repair_action="Replace adhesive or clean traps",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="warfare_fly_counter",
                name="Fly Counter System",
                description="Check fly counter system health",
                category=DiagnosticCategory.WARFARE,
                level=DiagnosticLevel.WARNING,
                timeout_seconds=7.0,
                dependencies=["sys_core_operational"],
                required=True,
                automated=True,
                repair_action="Calibrate sensors or clean lenses",
            )
        )

        # Monitoring subsystem checks
        self._add_check(
            DiagnosticCheck(
                check_id="monitoring_sensors",
                name="Sensor System",
                description="Check monitoring sensor health",
                category=DiagnosticCategory.MONITORING,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=5.0,
                dependencies=["sys_core_operational"],
                required=True,
                automated=True,
                repair_action="Calibrate or replace sensors",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="monitoring_witness",
                name="Witness Layer",
                description="Check cryptographic witness layer",
                category=DiagnosticCategory.INTEGRITY,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=3.0,
                dependencies=["sys_core_operational"],
                required=True,
                automated=True,
                repair_action="Rebuild witness data or restore from backup",
            )
        )

        # Hardware checks
        self._add_check(
            DiagnosticCheck(
                check_id="hardware_gpio",
                name="GPIO Interface",
                description="Check GPIO interface functionality",
                category=DiagnosticCategory.HARDWARE,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=4.0,
                dependencies=["sys_core_operational"],
                required=True,
                automated=True,
                repair_action="Reset GPIO or check connections",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="hardware_power",
                name="Power Supply",
                description="Check power supply stability",
                category=DiagnosticCategory.POWER,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=3.0,
                dependencies=[],
                required=True,
                automated=True,
                repair_action="Check power connections or replace supply",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="hardware_temperature",
                name="Temperature Control",
                description="Check temperature control system",
                category=DiagnosticCategory.ENVIRONMENTAL,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=5.0,
                dependencies=["sys_core_operational"],
                required=True,
                automated=True,
                repair_action="Calibrate thermostats or check cooling",
            )
        )

        # Environmental checks
        self._add_check(
            DiagnosticCheck(
                check_id="env_temperature",
                name="Environmental Temperature",
                description="Check environmental temperature",
                category=DiagnosticCategory.ENVIRONMENTAL,
                level=DiagnosticLevel.WARNING,
                timeout_seconds=2.0,
                dependencies=[],
                required=True,
                automated=True,
                repair_action="Adjust temperature settings",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="env_humidity",
                name="Environmental Humidity",
                description="Check environmental humidity",
                category=DiagnosticCategory.ENVIRONMENTAL,
                level=DiagnosticLevel.WARNING,
                timeout_seconds=2.0,
                dependencies=[],
                required=True,
                automated=True,
                repair_action="Adjust humidity control",
            )
        )

        # Security checks
        self._add_check(
            DiagnosticCheck(
                check_id="sec_integrity",
                name="System Integrity",
                description="Check system file integrity",
                category=DiagnosticCategory.SECURITY,
                level=DiagnosticLevel.CRITICAL,
                timeout_seconds=10.0,
                dependencies=[],
                required=True,
                automated=True,
                repair_action="Restore from known good backup",
            )
        )

        self._add_check(
            DiagnosticCheck(
                check_id="sec_access",
                name="Access Control",
                description="Check access control systems",
                category=DiagnosticCategory.SECURITY,
                level=DiagnosticLevel.WARNING,
                timeout_seconds=3.0,
                dependencies=[],
                required=True,
                automated=True,
                repair_action="Review and update access controls",
            )
        )

    def _add_check(self, check: DiagnosticCheck) -> None:
        """Add a diagnostic check."""
        self.checks[check.check_id] = check
        self.results[check.check_id] = []

    async def start(self) -> bool:
        """Start the diagnostics system."""
        if self.running:
            print("Diagnostics system already running")
            return False

        print("Starting diagnostics system")
        self.running = True

        try:
            # Start async tasks
            self._check_task = asyncio.create_task(self._check_loop())
            self._performance_task = asyncio.create_task(self._performance_loop())
            self._alert_task = asyncio.create_task(self._alert_loop())

            # Run initial full check
            await self.run_full_check()

            print("Diagnostics system started successfully")
            return True

        except Exception as e:
            print(f"Failed to start diagnostics system: {e}")
            self.running = False
            return False

    async def stop(self) -> bool:
        """Stop the diagnostics system."""
        if not self.running:
            print("Diagnostics system not running")
            return False

        print("Stopping diagnostics system")
        self.running = False

        try:
            # Signal shutdown
            self._shutdown_event.set()

            # Cancel tasks
            for task in [self._check_task, self._performance_task, self._alert_task]:
                if task:
                    task.cancel()

            # Wait for shutdown
            await asyncio.sleep(1.0)

            self._shutdown_event.clear()
            print("Diagnostics system stopped")
            return True

        except Exception as e:
            print(f"Error stopping diagnostics system: {e}")
            return False

    async def run_full_check(self) -> SystemHealth:
        """Run a full system diagnostic check."""
        print("Running full system diagnostic check")

        start_time = datetime.now()
        results: List[DiagnosticResult] = []

        # Run checks in dependency order
        checks_to_run = list(self.checks.values())
        checks_to_run.sort(key=lambda c: len(c.dependencies))

        for check in checks_to_run:
            # Check dependencies
            dependency_failed = False
            for dep_id in check.dependencies:
                if dep_id in self.results and self.results[dep_id]:
                    latest_result = self.results[dep_id][-1]
                    if latest_result.status == DiagnosticStatus.FAIL:
                        dependency_failed = True
                        break

            if dependency_failed:
                result = DiagnosticResult(
                    check_id=check.check_id,
                    timestamp=datetime.now(),
                    status=DiagnosticStatus.SKIPPED,
                    duration_seconds=0.0,
                    message=f"Skipped due to failed dependency",
                    recommendations=["Fix dependent checks first"],
                )
                results.append(result)
                self.results[check.check_id].append(result)
                continue

            # Run the check
            result = await self._run_check(check)
            results.append(result)
            self.results[check.check_id].append(result)

            # Update statistics
            self.total_checks_performed += 1
            if result.status == DiagnosticStatus.FAIL:
                self.total_errors_detected += 1
            elif result.status == DiagnosticStatus.WARNING:
                self.total_warnings_detected += 1

        # Calculate overall health
        health = self._calculate_system_health(results, start_time)
        self.health_history.append(health)

        # Keep history manageable
        if len(self.health_history) > self.health_history_limit:
            self.health_history = self.health_history[-self.health_history_limit :]

        self.last_full_check = datetime.now()
        print(
            f"Full diagnostic check completed: {health.overall_status.name}, score: {health.health_score:.1f}"
        )

        return health

    async def _run_check(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Run an individual diagnostic check."""
        start_time = time.time()
        status = DiagnosticStatus.RUNNING
        message = ""
        data = None
        error_details = None

        try:
            # Run the check with timeout
            async with asyncio.timeout(check.timeout_seconds):
                if check.check_id.startswith("sys_"):
                    result = await self._run_system_check(check)
                elif check.check_id.startswith("warfare_"):
                    result = await self._run_warfare_check(check)
                elif check.check_id.startswith("monitoring_"):
                    result = await self._run_monitoring_check(check)
                elif check.check_id.startswith("hardware_"):
                    result = await self._run_hardware_check(check)
                elif check.check_id.startswith("env_"):
                    result = await self._run_environmental_check(check)
                elif check.check_id.startswith("sec_"):
                    result = await self._run_security_check(check)
                else:
                    result = DiagnosticResult(
                        check_id=check.check_id,
                        timestamp=datetime.now(),
                        status=DiagnosticStatus.UNKNOWN,
                        duration_seconds=0.0,
                        message=f"Unknown check type: {check.check_id}",
                    )

                return result

        except asyncio.TimeoutError:
            status = DiagnosticStatus.TIMEOUT
            message = f"Check timed out after {check.timeout_seconds} seconds"
        except Exception as e:
            status = DiagnosticStatus.FAIL
            message = f"Check failed with exception: {str(e)}"
            error_details = traceback.format_exc()
        finally:
            duration = time.time() - start_time

        return DiagnosticResult(
            check_id=check.check_id,
            timestamp=datetime.now(),
            status=status,
            duration_seconds=duration,
            message=message,
            data=data,
            error_details=error_details,
        )

    async def _run_system_check(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Run a system-level diagnostic check."""
        if check.check_id == "sys_core_operational":
            # Simulate core system check
            await asyncio.sleep(0.5)
            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=DiagnosticStatus.PASS,
                duration_seconds=0.5,
                message="Core system operational",
                data={"uptime": random.uniform(1000.0, 10000.0)},
            )

        elif check.check_id == "sys_memory_usage":
            # Simulate memory check
            await asyncio.sleep(0.3)
            memory_usage = random.uniform(30.0, 80.0)
            status = DiagnosticStatus.PASS
            message = f"Memory usage: {memory_usage:.1f}%"

            if memory_usage > 70.0:
                status = DiagnosticStatus.WARNING
                message = f"High memory usage: {memory_usage:.1f}%"
            elif memory_usage > 90.0:
                status = DiagnosticStatus.FAIL
                message = f"Critical memory usage: {memory_usage:.1f}%"

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.3,
                message=message,
                data={"memory_usage_percent": memory_usage},
                recommendations=["Clear cache", "Restart services"]
                if memory_usage > 70.0
                else None,
            )

        elif check.check_id == "sys_disk_space":
            # Simulate disk space check
            await asyncio.sleep(0.2)
            disk_usage = random.uniform(20.0, 95.0)
            status = DiagnosticStatus.PASS
            message = f"Disk usage: {disk_usage:.1f}%"

            if disk_usage > 80.0:
                status = DiagnosticStatus.WARNING
                message = f"Low disk space: {100.0 - disk_usage:.1f}% free"
            elif disk_usage > 95.0:
                status = DiagnosticStatus.FAIL
                message = f"Critical disk space: {100.0 - disk_usage:.1f}% free"

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.2,
                message=message,
                data={"disk_usage_percent": disk_usage},
                recommendations=["Clean temporary files", "Expand storage"]
                if disk_usage > 80.0
                else None,
            )

        elif check.check_id == "sys_cpu_usage":
            # Simulate CPU check
            await asyncio.sleep(0.2)
            cpu_usage = random.uniform(10.0, 90.0)
            status = DiagnosticStatus.PASS
            message = f"CPU usage: {cpu_usage:.1f}%"

            if cpu_usage > 70.0:
                status = DiagnosticStatus.WARNING
                message = f"High CPU usage: {cpu_usage:.1f}%"
            elif cpu_usage > 90.0:
                status = DiagnosticStatus.FAIL
                message = f"Critical CPU usage: {cpu_usage:.1f}%"

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.2,
                message=message,
                data={"cpu_usage_percent": cpu_usage},
                recommendations=["Optimize processes", "Upgrade hardware"]
                if cpu_usage > 70.0
                else None,
            )

        else:
            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=DiagnosticStatus.UNKNOWN,
                duration_seconds=0.0,
                message=f"Unknown system check: {check.check_id}",
            )

    async def _run_warfare_check(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Run a warfare subsystem diagnostic check."""
        # Simulate warfare system checks
        await asyncio.sleep(random.uniform(0.5, 1.0))

        # Base result for all warfare checks
        status = random.choice(
            [DiagnosticStatus.PASS, DiagnosticStatus.WARNING, DiagnosticStatus.FAIL]
        )
        if status == DiagnosticStatus.PASS:
            message = f"{check.name} operational"
        elif status == DiagnosticStatus.WARNING:
            message = f"{check.name} needs attention"
        else:
            message = f"{check.name} failed"

        return DiagnosticResult(
            check_id=check.check_id,
            timestamp=datetime.now(),
            status=status,
            duration_seconds=random.uniform(0.5, 1.0),
            message=message,
            data={
                "subsystem": "warfare",
                "check_type": check.check_id.split("_")[1],
                "simulated": True,
            },
            recommendations=[check.repair_action]
            if status != DiagnosticStatus.PASS
            else None,
        )

    async def _run_monitoring_check(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Run a monitoring subsystem diagnostic check."""
        await asyncio.sleep(random.uniform(0.3, 0.7))

        if check.check_id == "monitoring_sensors":
            # Simulate sensor check
            sensor_count = random.randint(4, 8)
            working_sensors = random.randint(3, sensor_count)
            status = (
                DiagnosticStatus.PASS
                if working_sensors >= sensor_count * 0.8
                else DiagnosticStatus.WARNING
            )

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.5,
                message=f"Sensors: {working_sensors}/{sensor_count} operational",
                data={
                    "total_sensors": sensor_count,
                    "working_sensors": working_sensors,
                    "health_percent": (working_sensors / sensor_count) * 100.0,
                },
                recommendations=["Calibrate sensors"]
                if status != DiagnosticStatus.PASS
                else None,
            )

        elif check.check_id == "monitoring_witness":
            # Simulate witness layer check
            await asyncio.sleep(0.3)
            integrity_score = random.uniform(0.7, 1.0)
            status = (
                DiagnosticStatus.PASS
                if integrity_score > 0.9
                else DiagnosticStatus.WARNING
            )

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.3,
                message=f"Witness layer integrity: {integrity_score:.1%}",
                data={"integrity_score": integrity_score},
                recommendations=["Rebuild witness data"]
                if integrity_score < 0.95
                else None,
            )

        else:
            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=DiagnosticStatus.UNKNOWN,
                duration_seconds=0.0,
                message=f"Unknown monitoring check: {check.check_id}",
            )

    async def _run_hardware_check(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Run a hardware diagnostic check."""
        await asyncio.sleep(random.uniform(0.2, 0.5))

        if check.check_id == "hardware_gpio":
            # Simulate GPIO check
            gpio_ports = random.randint(8, 16)
            working_ports = random.randint(gpio_ports - 2, gpio_ports)
            status = (
                DiagnosticStatus.PASS
                if working_ports == gpio_ports
                else DiagnosticStatus.WARNING
            )

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.3,
                message=f"GPIO ports: {working_ports}/{gpio_ports} functional",
                data={
                    "total_ports": gpio_ports,
                    "working_ports": working_ports,
                    "health_percent": (working_ports / gpio_ports) * 100.0,
                },
                recommendations=["Check connections"]
                if status != DiagnosticStatus.PASS
                else None,
            )

        elif check.check_id == "hardware_power":
            # Simulate power check
            voltage = random.uniform(11.5, 12.5)
            status = (
                DiagnosticStatus.PASS
                if 11.8 <= voltage <= 12.2
                else DiagnosticStatus.WARNING
            )

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.2,
                message=f"Power supply: {voltage:.2f}V",
                data={"voltage": voltage},
                recommendations=["Check power connections"]
                if status != DiagnosticStatus.PASS
                else None,
            )

        elif check.check_id == "hardware_temperature":
            # Simulate temperature control check
            temperature = random.uniform(18.0, 25.0)
            target = 22.0
            deviation = abs(temperature - target)
            status = (
                DiagnosticStatus.PASS if deviation < 2.0 else DiagnosticStatus.WARNING
            )

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.4,
                message=f"Temperature: {temperature:.1f}°C (target: {target}°C)",
                data={
                    "temperature": temperature,
                    "target": target,
                    "deviation": deviation,
                },
                recommendations=["Calibrate thermostat"] if deviation > 2.0 else None,
            )

        else:
            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=DiagnosticStatus.UNKNOWN,
                duration_seconds=0.0,
                message=f"Unknown hardware check: {check.check_id}",
            )

    async def _run_environmental_check(
        self, check: DiagnosticCheck
    ) -> DiagnosticResult:
        """Run an environmental diagnostic check."""
        await asyncio.sleep(0.1)

        if check.check_id == "env_temperature":
            temperature = random.uniform(18.0, 28.0)
            status = (
                DiagnosticStatus.PASS
                if 20.0 <= temperature <= 25.0
                else DiagnosticStatus.WARNING
            )

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.1,
                message=f"Environmental temperature: {temperature:.1f}°C",
                data={"temperature": temperature},
                recommendations=["Adjust temperature"]
                if status != DiagnosticStatus.PASS
                else None,
            )

        elif check.check_id == "env_humidity":
            humidity = random.uniform(30.0, 70.0)
            status = (
                DiagnosticStatus.PASS
                if 40.0 <= humidity <= 60.0
                else DiagnosticStatus.WARNING
            )

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.1,
                message=f"Environmental humidity: {humidity:.1f}%",
                data={"humidity": humidity},
                recommendations=["Adjust humidity"]
                if status != DiagnosticStatus.PASS
                else None,
            )

        else:
            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=DiagnosticStatus.UNKNOWN,
                duration_seconds=0.0,
                message=f"Unknown environmental check: {check.check_id}",
            )

    async def _run_security_check(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Run a security diagnostic check."""
        await asyncio.sleep(random.uniform(0.5, 2.0))

        if check.check_id == "sec_integrity":
            # Simulate integrity check
            files_checked = random.randint(100, 500)
            files_valid = random.randint(files_checked - 10, files_checked)
            integrity_score = files_valid / files_checked

            status = (
                DiagnosticStatus.PASS
                if integrity_score > 0.99
                else DiagnosticStatus.FAIL
            )

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=1.0,
                message=f"System integrity: {files_valid}/{files_checked} files valid",
                data={
                    "files_checked": files_checked,
                    "files_valid": files_valid,
                    "integrity_score": integrity_score,
                },
                recommendations=["Restore from backup"]
                if status != DiagnosticStatus.PASS
                else None,
            )

        elif check.check_id == "sec_access":
            # Simulate access control check
            access_violations = random.randint(0, 5)
            status = (
                DiagnosticStatus.PASS
                if access_violations == 0
                else DiagnosticStatus.WARNING
            )

            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=status,
                duration_seconds=0.5,
                message=f"Access control: {access_violations} violations detected",
                data={"access_violations": access_violations},
                recommendations=["Review access logs"]
                if access_violations > 0
                else None,
            )

        else:
            return DiagnosticResult(
                check_id=check.check_id,
                timestamp=datetime.now(),
                status=DiagnosticStatus.UNKNOWN,
                duration_seconds=0.0,
                message=f"Unknown security check: {check.check_id}",
            )

    def _calculate_system_health(
        self, results: List[DiagnosticResult], start_time: datetime
    ) -> SystemHealth:
        """Calculate overall system health from diagnostic results."""
        passed = sum(1 for r in results if r.status == DiagnosticStatus.PASS)
        failed = sum(1 for r in results if r.status == DiagnosticStatus.FAIL)
        warning = sum(1 for r in results if r.status == DiagnosticStatus.WARNING)
        total = len(results)

        # Calculate health score (0-100)
        if total == 0:
            health_score = 0.0
        else:
            health_score = (passed / total) * 100.0
            # Apply penalty for warnings
            health_score -= (warning / total) * 20.0
            health_score = max(0.0, min(100.0, health_score))

        # Determine overall status
        if failed > 0:
            overall_status = DiagnosticStatus.FAIL
        elif warning > 0:
            overall_status = DiagnosticStatus.WARNING
        elif passed == total:
            overall_status = DiagnosticStatus.PASS
        else:
            overall_status = DiagnosticStatus.UNKNOWN

        # Identify critical issues
        critical_issues = []
        for result in results:
            if result.status == DiagnosticStatus.FAIL:
                critical_issues.append(f"{result.check_id}: {result.message}")

        # Calculate performance metrics
        performance_metrics = {
            "check_duration_seconds": (datetime.now() - start_time).total_seconds(),
            "average_check_duration": statistics.mean(
                [r.duration_seconds for r in results]
            )
            if results
            else 0.0,
            "health_score": health_score,
            "check_success_rate": (passed / total) * 100.0 if total > 0 else 0.0,
        }

        # Determine subsystem status
        subsystem_status = {}
        for result in results:
            check = self.checks.get(result.check_id)
            if check:
                subsystem = check.category.name
                if subsystem not in subsystem_status:
                    subsystem_status[subsystem] = result.status
                else:
                    # Use worst status for subsystem
                    status_order = {
                        DiagnosticStatus.FAIL: 4,
                        DiagnosticStatus.WARNING: 3,
                        DiagnosticStatus.UNKNOWN: 2,
                        DiagnosticStatus.PASS: 1,
                    }
                    current_rank = status_order.get(subsystem_status[subsystem], 0)
                    new_rank = status_order.get(result.status, 0)
                    if new_rank > current_rank:
                        subsystem_status[subsystem] = result.status

        # Generate recommendations
        recommendations = []
        for result in results:
            if (
                result.status in [DiagnosticStatus.FAIL, DiagnosticStatus.WARNING]
                and result.recommendations
            ):
                recommendations.extend(result.recommendations)

        # Limit recommendations
        recommendations = list(set(recommendations))[:10]  # Unique, max 10

        # Schedule next full check
        next_full_check = datetime.now() + timedelta(
            seconds=self.check_interval_seconds
        )

        return SystemHealth(
            timestamp=datetime.now(),
            overall_status=overall_status,
            health_score=health_score,
            passed_checks=passed,
            failed_checks=failed,
            warning_checks=warning,
            total_checks=total,
            critical_issues=critical_issues[:5],  # Limit to 5 most critical
            performance_metrics=performance_metrics,
            subsystem_status=subsystem_status,
            recommendations=recommendations,
            next_full_check=next_full_check,
        )

    async def _check_loop(self) -> None:
        """Main diagnostic check loop."""
        print("Starting diagnostic check loop")

        try:
            while not self._shutdown_event.is_set():
                # Run scheduled checks
                await self._run_scheduled_checks()

                # Sleep for check interval
                await asyncio.sleep(self.check_interval_seconds)

        except asyncio.CancelledError:
            print("Check loop cancelled")
        except Exception as e:
            print(f"Error in check loop: {e}")

    async def _performance_loop(self) -> None:
        """Performance monitoring loop."""
        print("Starting performance monitoring loop")

        try:
            while not self._shutdown_event.is_set():
                # Collect performance metrics
                metrics = await self._collect_performance_metrics()
                self.performance_history.append(metrics)

                # Keep history manageable
                if len(self.performance_history) > self.performance_history_limit:
                    self.performance_history = self.performance_history[
                        -self.performance_history_limit :
                    ]

                self.last_performance_check = datetime.now()

                # Sleep for performance interval
                await asyncio.sleep(self.performance_interval_seconds)

        except asyncio.CancelledError:
            print("Performance loop cancelled")
        except Exception as e:
            print(f"Error in performance loop: {e}")

    async def _alert_loop(self) -> None:
        """Predictive alert generation loop."""
        print("Starting predictive alert loop")

        try:
            while not self._shutdown_event.is_set():
                # Generate predictive alerts
                await self._generate_predictive_alerts()

                # Sleep for alert interval (longer interval)
                await asyncio.sleep(self.check_interval_seconds * 5)

        except asyncio.CancelledError:
            print("Alert loop cancelled")
        except Exception as e:
            print(f"Error in alert loop: {e}")

    async def _run_scheduled_checks(self) -> None:
        """Run scheduled diagnostic checks."""
        # For now, just run critical checks
        critical_checks = [
            c for c in self.checks.values() if c.level == DiagnosticLevel.CRITICAL
        ]

        for check in critical_checks:
            # Check if this check needs to run
            if check.check_id in self.results and self.results[check.check_id]:
                last_result = self.results[check.check_id][-1]
                if (
                    last_result.next_check_time
                    and last_result.next_check_time > datetime.now()
                ):
                    continue

            # Run the check
            result = await self._run_check(check)
            self.results[check.check_id].append(result)

            # Update statistics
            self.total_checks_performed += 1
            if result.status == DiagnosticStatus.FAIL:
                self.total_errors_detected += 1
            elif result.status == DiagnosticStatus.WARNING:
                self.total_warnings_detected += 1

    async def _collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics."""
        # Simulate metric collection
        await asyncio.sleep(0.1)

        return PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_usage_percent=random.uniform(10.0, 80.0),
            memory_usage_percent=random.uniform(30.0, 85.0),
            disk_usage_percent=random.uniform(20.0, 90.0),
            network_bandwidth_mbps=random.uniform(10.0, 100.0),
            response_time_ms=random.uniform(5.0, 50.0),
            throughput_ops_per_second=random.uniform(100.0, 1000.0),
            error_rate_percent=random.uniform(0.1, 5.0),
            uptime_seconds=random.uniform(1000.0, 100000.0),
            active_connections=random.randint(5, 50),
            queue_depth=random.randint(0, 20),
            cache_hit_rate_percent=random.uniform(70.0, 99.0),
            subsystem_metrics={
                "warfare": {
                    "spore_deployment_rate": random.uniform(0.5, 5.0),
                    "uv_effectiveness": random.uniform(80.0, 99.0),
                    "air_curtain_velocity": random.uniform(2.0, 4.0),
                },
                "monitoring": {
                    "sensor_accuracy": random.uniform(85.0, 99.0),
                    "detection_latency": random.uniform(10.0, 100.0),
                },
                "hardware": {
                    "temperature_variance": random.uniform(0.5, 3.0),
                    "power_stability": random.uniform(95.0, 100.0),
                },
            },
        )

    async def _generate_predictive_alerts(self) -> None:
        """Generate predictive maintenance alerts."""
        # Simulate predictive analysis
        await asyncio.sleep(0.2)

        # Only generate alerts occasionally
        if random.random() > 0.3:
            return

        components = [
            "Spore Deployment System",
            "UV Sterilization Lamps",
            "Air Curtain Fans",
            "Sticky Trap Adhesive",
            "Fly Counter Sensors",
            "Temperature Sensors",
            "Power Supply",
            "GPIO Interface",
        ]

        component = random.choice(components)
        failure_modes = {
            "Spore Deployment System": [
                "Clogged nozzles",
                "Pump failure",
                "Reservoir empty",
            ],
            "UV Sterilization Lamps": [
                "Bulb degradation",
                "Power supply issue",
                "Dirty lenses",
            ],
            "Air Curtain Fans": [
                "Bearing wear",
                "Motor overheating",
                "Blade imbalance",
            ],
            "Sticky Trap Adhesive": [
                "Adhesive degradation",
                "Surface contamination",
                "Drying out",
            ],
            "Fly Counter Sensors": [
                "Lens fogging",
                "Sensor drift",
                "Calibration needed",
            ],
            "Temperature Sensors": [
                "Calibration drift",
                "Sensor failure",
                "Environmental interference",
            ],
            "Power Supply": ["Voltage instability", "Capacitor aging", "Overheating"],
            "GPIO Interface": [
                "Connection corrosion",
                "Pin damage",
                "Signal interference",
            ],
        }

        predicted_failure = random.choice(
            failure_modes.get(component, ["Unknown failure mode"])
        )
        confidence = random.uniform(60.0, 95.0)
        time_to_failure = random.uniform(24.0, 720.0)  # 1-30 days
        current_health = random.uniform(40.0, 90.0)
        degradation_rate = random.uniform(0.1, 2.0)

        # Determine severity
        if confidence > 85.0 and time_to_failure < 168.0:  # High confidence, < 1 week
            severity = DiagnosticLevel.CRITICAL
        elif confidence > 70.0:
            severity = DiagnosticLevel.WARNING
        else:
            severity = DiagnosticLevel.INFO

        # Generate recommendations
        recommendations = [
            f"Schedule maintenance for {component}",
            f"Monitor {component} performance closely",
            "Consider proactive replacement",
        ]

        if "Sensor" in component:
            recommendations.append("Perform calibration check")
        if "Adhesive" in component or "Lamps" in component:
            recommendations.append("Check expiration date")

        # Historical data
        historical_data = []
        for i in range(5):
            historical_data.append(
                {
                    "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                    "health_percent": max(0.0, current_health + i * degradation_rate),
                    "performance_score": random.uniform(70.0, 100.0),
                }
            )

        alert = PredictiveAlert(
            alert_id=f"PA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            timestamp=datetime.now(),
            component=component,
            predicted_failure=predicted_failure,
            confidence_percent=confidence,
            estimated_time_to_failure_hours=time_to_failure,
            severity=severity,
            current_health_percent=current_health,
            degradation_rate_per_hour=degradation_rate,
            recommendations=recommendations,
            historical_data=historical_data,
        )

        self.predictive_alerts.append(alert)
        print(
            f"Generated predictive alert: {component} - {predicted_failure} ({confidence:.1f}% confidence)"
        )

    def get_health_report(self) -> SystemHealth:
        """Get current system health report."""
        if not self.health_history:
            return SystemHealth(
                timestamp=datetime.now(),
                overall_status=DiagnosticStatus.UNKNOWN,
                health_score=0.0,
                passed_checks=0,
                failed_checks=0,
                warning_checks=0,
                total_checks=0,
                critical_issues=["No diagnostic data available"],
                performance_metrics={},
                subsystem_status={},
                recommendations=["Run full diagnostic check"],
            )

        return self.health_history[-1]

    def get_performance_report(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get performance history."""
        history = self.performance_history[-limit:] if self.performance_history else []
        return [asdict(metrics) for metrics in history]

    def get_diagnostic_results(
        self, check_id: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get diagnostic results."""
        if check_id:
            if check_id in self.results:
                results = self.results[check_id][-limit:]
                return [r.to_dict() for r in results]
            return []

        # Get all results
        all_results = []
        for check_results in self.results.values():
            all_results.extend(check_results[-5:])  # Last 5 results per check

        # Sort by timestamp
        all_results.sort(key=lambda r: r.timestamp, reverse=True)
        return [r.to_dict() for r in all_results[:limit]]

    def get_predictive_alerts(
        self, active_only: bool = True, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get predictive alerts."""
        alerts = self.predictive_alerts
        if active_only:
            # Consider alerts from last 7 days as active
            cutoff = datetime.now() - timedelta(days=7)
            alerts = [a for a in alerts if a.timestamp > cutoff]

        alerts.sort(
            key=lambda a: (a.severity.value, a.confidence_percent), reverse=True
        )
        return [asdict(alert) for alert in alerts[:limit]]

    def clear_history(self) -> None:
        """Clear diagnostic history."""
        self.health_history = []
        self.performance_history = []
        self.predictive_alerts = []
        for check_id in self.results:
            self.results[check_id] = []
        print("Diagnostic history cleared")

    async def emergency_shutdown(self) -> None:
        """Emergency shutdown procedure."""
        print("EMERGENCY SHUTDOWN INITIATED FOR DIAGNOSTICS SYSTEM")

        # Cancel all tasks
        for task in [self._check_task, self._performance_task, self._alert_task]:
            if task:
                task.cancel()

        self.running = False
        print("Emergency shutdown complete")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.running:
            await self.stop()


# Example usage and test function
async def test_diagnostics_system():
    """Test the diagnostics system."""
    print("\n" + "=" * 60)
    print("TESTING DIAGNOSTICS SYSTEM")
    print("=" * 60)

    system = SystemDiagnostics()

    try:
        # Test startup
        print("\n1. Testing startup...")
        started = await system.start()
        print(f"   Startup result: {started}")

        # Run for a bit
        await asyncio.sleep(2.0)

        # Test full check
        print("\n2. Testing full diagnostic check...")
        health = await system.run_full_check()
        print(f"   Overall status: {health.overall_status.name}")
        print(f"   Health score: {health.health_score:.1f}")
        print(f"   Passed checks: {health.passed_checks}/{health.total_checks}")
        print(f"   Critical issues: {len(health.critical_issues)}")

        # Run for a bit more
        await asyncio.sleep(3.0)

        # Test health report
        print("\n3. Testing health report...")
        current_health = system.get_health_report()
        print(f"   Current health: {current_health.overall_status.name}")
        print(f"   Current score: {current_health.health_score:.1f}")

        # Test diagnostic results
        print("\n4. Testing diagnostic results...")
        results = system.get_diagnostic_results(limit=5)
        print(f"   Recent results: {len(results)}")
        for i, result in enumerate(results[:3], 1):
            print(f"   Result {i}: {result['check_id']} - {result['status']}")

        # Test performance report
        print("\n5. Testing performance report...")
        performance = system.get_performance_report(limit=3)
        print(f"   Performance entries: {len(performance)}")
        if performance:
            latest = performance[-1]
            print(f"   Latest CPU: {latest['cpu_usage_percent']:.1f}%")
            print(f"   Latest memory: {latest['memory_usage_percent']:.1f}%")

        # Test predictive alerts
        print("\n6. Testing predictive alerts...")
        alerts = system.get_predictive_alerts(limit=3)
        print(f"   Predictive alerts: {len(alerts)}")
        for i, alert in enumerate(alerts[:2], 1):
            print(f"   Alert {i}: {alert['component']} - {alert['predicted_failure']}")

        # Test shutdown
        print("\n7. Testing shutdown...")
        stopped = await system.stop()
        print(f"   Shutdown result: {stopped}")

        print("\n" + "=" * 60)
        print("DIAGNOSTICS SYSTEM TEST COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR during test: {e}")
        await system.emergency_shutdown()


if __name__ == "__main__":
    # Run test
    asyncio.run(test_diagnostics_system())

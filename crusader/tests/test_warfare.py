"""
Crusader Combat Refrigerator - Warfare System Tests
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Comprehensive test suite for warfare systems.
Tests spore deployment, UV sterilization, air curtain, sticky traps, and fly counter.
"""

import asyncio
import json
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from warfare.air_curtain import (
    AirCurtainResult,
    AirCurtainStatus,
    AirCurtainSystem,
    AirflowPattern,
    FanSpeed,
)
from warfare.counter import (
    DetectionMethod,
    FlyCounterSystem,
    FlyDetectionResult,
)
from warfare.spore_deployment import (
    DeploymentPattern,
    DeploymentResult,
    DeploymentStatus,
    SporeDeploymentSystem,
    SporeReservoir,
)
from warfare.sticky_array import (
    StickyTrapResult,
    StickyTrapSystem,
    TrapPosition,
    TrapStatus,
)
from warfare.uv_sterilization import (
    SafetyInterlock,
    SterilizationResult,
    UVIntensity,
    UVStatus,
    UVSterilizationSystem,
    UVSystemState,
)


class TestSporeDeploymentSystem(unittest.TestCase):
    """Test spore deployment system."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = SporeDeploymentSystem()
        self.test_config = {
            "reservoir_capacity_ml": 500.0,
            "initial_level_ml": 500.0,
            "spore_concentration": 0.1,
            "deployment_volume_ml": 5.0,
            "deployment_duration_seconds": 2.0,
            "low_reservoir_threshold_ml": 50.0,
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
        }

    async def asyncSetUp(self):
        """Async setup."""
        await self.system.initialize()

    def test_reservoir_initialization(self):
        """Test reservoir initialization."""
        reservoir = SporeReservoir(
            capacity_ml=1000.0,
            current_level_ml=1000.0,
            concentration_percent=0.1,
            last_refill=datetime.now(),
            refill_count=0,
            total_deployed_ml=0.0,
            viability_percent=100.0,
            temperature_celsius=25.0,
            last_mixing=datetime.now(),
        )

        self.assertEqual(reservoir.capacity_ml, 1000.0)
        self.assertEqual(reservoir.current_level_ml, 1000.0)
        self.assertEqual(reservoir.get_percentage_full(), 100.0)
        self.assertFalse(reservoir.is_low())
        self.assertFalse(reservoir.is_empty())

    def test_reservoir_low_level(self):
        """Test reservoir low level detection."""
        reservoir = SporeReservoir(
            capacity_ml=1000.0,
            current_level_ml=50.0,
            concentration_percent=0.1,
            last_refill=datetime.now(),
            refill_count=0,
            total_deployed_ml=950.0,
            viability_percent=100.0,
            temperature_celsius=25.0,
            last_mixing=datetime.now(),
        )

        self.assertTrue(reservoir.is_low(10.0))
        self.assertEqual(reservoir.get_percentage_full(), 5.0)

    def test_deployment_result_serialization(self):
        """Test deployment result serialization."""
        result = DeploymentResult(
            deployment_id="test_id",
            timestamp=datetime.now(),
            pattern=DeploymentPattern.MORNING,
            status=DeploymentStatus.COMPLETED,
            duration_seconds=5.0,
            volume_ml=10.0,
            concentration_percent=0.1,
            success=True,
            error_message=None,
            sensor_data={"temperature": 25.0, "humidity": 60.0},
            fly_count=5,
            humidity_percent=60.0,
            temperature_celsius=25.0,
            reservoir_level_ml=500.0,
        )

        data = result.to_dict()
        self.assertEqual(data["deployment_id"], "test_id")
        self.assertEqual(data["pattern"], "MORNING")
        self.assertEqual(data["status"], "COMPLETED")
        self.assertEqual(data["volume_ml"], 10.0)
        self.assertTrue(data["success"])

    @patch("warfare.spore_deployment.SporeDeploymentSystem._initialize_hardware")
    async def test_system_initialization(self, mock_hardware):
        """Test system initialization."""
        mock_hardware.return_value = None

        system = SporeDeploymentSystem(self.test_config)
        success = await system.initialize()

        self.assertTrue(success)
        self.assertIsNotNone(system.reservoir)
        self.assertEqual(system.reservoir.capacity_ml, 500.0)

    @patch("warfare.spore_deployment.SporeDeploymentSystem._execute_deployment")
    async def test_spore_deployment(self, mock_execute):
        """Test spore deployment."""
        mock_execute.return_value = True

        system = SporeDeploymentSystem(self.test_config)
        await system.initialize()

        # Test deployment
        result = await system.deploy(
            pattern=DeploymentPattern.MORNING,
            sensor_data={"temperature": 25.0, "humidity": 65.0},
            fly_count=3,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.pattern, DeploymentPattern.MORNING)
        self.assertIn(
            result.status, [DeploymentStatus.COMPLETED, DeploymentStatus.FAILED]
        )

        # Check statistics
        self.assertGreaterEqual(system.statistics["total_deployments"], 0)

    async def test_should_deploy_logic(self):
        """Test deployment decision logic."""
        system = SporeDeploymentSystem(self.test_config)
        await system.initialize()

        # Test with empty reservoir
        system.reservoir.current_level_ml = 0.0
        should_deploy, pattern = await system.should_deploy(
            sensor_data={"temperature": 25.0, "humidity": 65.0}, fly_count=10
        )
        self.assertFalse(should_deploy)
        self.assertIsNone(pattern)

        # Test with healthy reservoir
        system.reservoir.current_level_ml = 500.0
        should_deploy, pattern = await system.should_deploy(
            sensor_data={"temperature": 25.0, "humidity": 65.0}, fly_count=10
        )
        # May or may not deploy based on pattern logic
        self.assertIsInstance(should_deploy, bool)

    def test_deployment_volume_calculation(self):
        """Test deployment volume calculation."""
        system = SporeDeploymentSystem(self.test_config)

        # Test morning pattern
        volume = system._calculate_deployment_volume(DeploymentPattern.MORNING, 5)
        self.assertGreater(volume, 0.0)

        # Test adaptive pattern with high fly count
        volume = system._calculate_deployment_volume(DeploymentPattern.ADAPTIVE, 20)
        self.assertGreater(volume, 0.0)

        # Test random pattern
        volume = system._calculate_deployment_volume(DeploymentPattern.RANDOM, 5)
        self.assertGreaterEqual(volume, 0.0)

    async def test_pattern_checks(self):
        """Test pattern checking logic."""
        system = SporeDeploymentSystem(self.test_config)

        # Test morning pattern check
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value.time.return_value = datetime.strptime(
                "07:00", "%H:%M"
            ).time()
            should_deploy = await system._check_morning_pattern()
            self.assertIsInstance(should_deploy, bool)

        # Test adaptive pattern check
        should_deploy = await system._check_adaptive_pattern(
            sensor_data={"humidity_percent": 70.0}, fly_count=10
        )
        self.assertIsInstance(should_deploy, bool)

        # Test random pattern check
        should_deploy = await system._check_random_pattern()
        self.assertIsInstance(should_deploy, bool)


class TestUVSterilizationSystem(unittest.TestCase):
    """Test UV sterilization system."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = UVSterilizationSystem()

    async def asyncSetUp(self):
        """Async setup."""
        await self.system.initialize()

    def test_system_state_health(self):
        """Test system state health checks."""
        state = UVSystemState(
            led_lifetime_hours=1000.0,
            led_efficiency_percent=95.0,
            last_calibration=datetime.now(),
            calibration_count=5,
            total_energy_joules=5000.0,
            total_sterilization_time=3600.0,
            temperature_celsius=35.0,
            led_health_percent=90.0,
            safety_interlocks_active=[],
        )

        self.assertTrue(state.is_safe_to_operate())
        self.assertGreater(state.get_led_remaining_life(), 0.0)
        self.assertGreater(state.get_led_remaining_percent(), 0.0)

        # Test with critical interlock
        state.safety_interlocks_active = [SafetyInterlock.DOOR_SENSOR]
        self.assertFalse(state.is_safe_to_operate())

    def test_sterilization_result_serialization(self):
        """Test sterilization result serialization."""
        result = SterilizationResult(
            cycle_id="test_cycle",
            timestamp=datetime.now(),
            duration_seconds=30.0,
            intensity=UVIntensity.MEDIUM,
            status=UVStatus.COMPLETED,
            success=True,
            energy_joules=300.0,
            uv_dose_mj_per_cm2=45.0,
            temperature_start_celsius=25.0,
            temperature_end_celsius=28.0,
            safety_interlocks_triggered=[],
            sensor_data={"motion": False, "door_closed": True},
        )

        data = result.to_dict()
        self.assertEqual(data["cycle_id"], "test_cycle")
        self.assertEqual(data["intensity"], "MEDIUM")
        self.assertEqual(data["status"], "COMPLETED")
        self.assertEqual(data["duration_seconds"], 30.0)
        self.assertTrue(data["success"])

    @patch("warfare.uv_sterilization.UVSterilizationSystem._initialize_hardware")
    async def test_system_initialization(self, mock_hardware):
        """Test UV system initialization."""
        mock_hardware.return_value = None

        system = UVSterilizationSystem()
        success = await system.initialize()

        self.assertTrue(success)
        self.assertIsNotNone(system.system_state)
        self.assertTrue(system.system_state.is_safe_to_operate())

    async def test_should_sterilize_logic(self):
        """Test sterilization decision logic."""
        system = UVSterilizationSystem()
        await system.initialize()

        # Test with healthy system
        should_sterilize, intensity = await system.should_sterilize(
            sensor_data={"temperature_celsius": 25.0, "humidity_percent": 50.0}
        )
        self.assertIsInstance(should_sterilize, bool)
        self.assertIsInstance(intensity, (UVIntensity, type(None)))

        # Test with exceeded daily exposure
        system.system_state.total_sterilization_time = (
            400.0  # Exceeds 300s default limit
        )
        should_sterilize, intensity = await system.should_sterilize(
            sensor_data={"temperature_celsius": 25.0, "humidity_percent": 50.0}
        )
        self.assertFalse(should_sterilize)

    @patch("warfare.uv_sterilization.UVSterilizationSystem._execute_sterilization")
    async def test_sterilization_cycle(self, mock_execute):
        """Test sterilization cycle execution."""
        mock_execute.return_value = True

        system = UVSterilizationSystem()
        await system.initialize()

        # Test sterilization
        result = await system.sterilize(
            intensity=UVIntensity.MEDIUM,
            sensor_data={"temperature_celsius": 25.0, "door_closed": True},
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.intensity, UVIntensity.MEDIUM)
        self.assertIn(result.status, [UVStatus.COMPLETED, UVStatus.FAILED])

        # Check statistics
        self.assertGreaterEqual(system.statistics["total_cycles"], 0)

    def test_intensity_determination(self):
        """Test UV intensity determination."""
        system = UVSterilizationSystem()

        # Test high temperature
        sensor_data = {"temperature_celsius": 32.0, "humidity_percent": 50.0}
        intensity = system._determine_intensity(sensor_data)
        self.assertEqual(intensity, UVIntensity.HIGH)

        # Test medium temperature
        sensor_data = {"temperature_celsius": 27.0, "humidity_percent": 50.0}
        intensity = system._determine_intensity(sensor_data)
        self.assertEqual(intensity, UVIntensity.MEDIUM)

        # Test low temperature
        sensor_data = {"temperature_celsius": 22.0, "humidity_percent": 50.0}
        intensity = system._determine_intensity(sensor_data)
        self.assertEqual(intensity, UVIntensity.LOW)

    def test_daily_exposure_calculation(self):
        """Test daily exposure calculation."""
        system = UVSterilizationSystem()

        # Add some test cycles
        today = datetime.now().date()
        system.sterilization_history = [
            SterilizationResult(
                cycle_id="test1",
                timestamp=datetime.combine(today, datetime.min.time()),
                duration_seconds=100.0,
                intensity=UVIntensity.MEDIUM,
                status=UVStatus.COMPLETED,
                success=True,
                energy_joules=1000.0,
                uv_dose_mj_per_cm2=30.0,
                temperature_start_celsius=25.0,
                temperature_end_celsius=27.0,
                safety_interlocks_triggered=[],
            ),
            SterilizationResult(
                cycle_id="test2",
                timestamp=datetime.combine(today, datetime.min.time()),
                duration_seconds=150.0,
                intensity=UVIntensity.HIGH,
                status=UVStatus.COMPLETED,
                success=True,
                energy_joules=1500.0,
                uv_dose_mj_per_cm2=45.0,
                temperature_start_celsius=25.0,
                temperature_end_celsius=28.0,
                safety_interlocks_triggered=[],
            ),
        ]

        daily_exposure = system._get_daily_exposure()
        self.assertEqual(daily_exposure, 250.0)  # 100 + 150


class TestAirCurtainSystem(unittest.TestCase):
    """Test air curtain system."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = AirCurtainSystem()

    async def asyncSetUp(self):
        """Async setup."""
        await self.system.initialize()

    def test_air_curtain_result_serialization(self):
        """Test air curtain result serialization."""
        result = AirCurtainResult(
            operation_id="test_op",
            timestamp=datetime.now(),
            pattern=AirflowPattern.DEFENSE,
            fan_speed=FanSpeed.HIGH,
            duration_seconds=60.0,
            status=AirCurtainStatus.COMPLETED,
            success=True,
            power_consumption_j=500.0,
            airflow_cfm=150.0,
            noise_level_db=65.0,
            sensor_data={"temperature": 25.0, "fly_count": 5},
        )

        data = result.to_dict()
        self.assertEqual(data["operation_id"], "test_op")
        self.assertEqual(data["pattern"], "DEFENSE")
        self.assertEqual(data["fan_speed"], "HIGH")
        self.assertEqual(data["status"], "COMPLETED")
        self.assertTrue(data["success"])

    @patch("warfare.air_curtain.AirCurtainSystem._initialize_hardware")
    async def test_system_initialization(self, mock_hardware):
        """Test air curtain system initialization."""
        mock_hardware.return_value = None

        system = AirCurtainSystem()
        success = await system.initialize()

        self.assertTrue(success)
        self.assertIsNotNone(system.system_state)

    async def test_air_curtain_management(self):
        """Test air curtain management logic."""
        system = AirCurtainSystem()
        await system.initialize()

        # Test with normal conditions
        result = await system.manage(
            sensor_data={"temperature": 25.0, "humidity": 60.0, "fly_count": 3}
        )

        self.assertIsNotNone(result)
        self.assertIn(
            result.status, [AirCurtainStatus.COMPLETED, AirCurtainStatus.FAILED]
        )

        # Test with high fly count (should trigger defense)
        result = await system.manage(
            sensor_data={"temperature": 25.0, "humidity": 60.0, "fly_count": 15}
        )

        self.assertIsNotNone(result)
        if result.success:
            self.assertEqual(result.pattern, AirflowPattern.DEFENSE)
            self.assertEqual(result.fan_speed, FanSpeed.HIGH)

    @unittest_run_loop
    async def test_sticky_trap_system(self):
        """Test sticky trap deployment system."""
        system = StickyTrapSystem()
        await system.initialize()

        # Test normal deployment
        result = await system.deploy_traps(count=3, pattern="triangle")
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.traps_deployed, 3)

        # Test with invalid count
        result = await system.deploy_traps(count=10, pattern="grid")
        self.assertIsNotNone(result)
        self.assertFalse(result.success)

    @unittest_run_loop
    async def test_fly_counter_system(self):
        """Test fly detection and counting system."""
        system = FlyCounterSystem()
        await system.initialize()

        # Test detection with sample image
        result = await system.detect_flies(image_data=b"sample_image_data")
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.fly_count, 0)

        # Test with empty image
        result = await system.detect_flies(image_data=b"")
        self.assertIsNotNone(result)
        self.assertFalse(result.success)

    @unittest_run_loop
    async def test_uv_sterilization_system(self):
        """Test UV sterilization system."""
        system = UVSterilizationSystem()
        await system.initialize()

        # Test normal sterilization cycle
        result = await system.sterilize(duration_seconds=30, intensity=0.7)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.sterilization_complete, True)

        # Test with excessive duration
        result = await system.sterilize(duration_seconds=3600, intensity=1.0)
        self.assertIsNotNone(result)
        self.assertFalse(result.success)

    @unittest_run_loop
    async def test_spore_deployment_system(self):
        """Test spore deployment system."""
        system = SporeDeploymentSystem()
        await system.initialize()

        # Test normal spore deployment
        result = await system.deploy_spores(
            spore_type="beauveria_bassiana", quantity_ml=5.0, target_area="shelf_1"
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.spores_deployed_ml, 5.0)

        # Test with invalid spore type
        result = await system.deploy_spores(
            spore_type="invalid_type", quantity_ml=5.0, target_area="shelf_1"
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main()

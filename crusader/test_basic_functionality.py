"""
Crusader Combat Refrigerator - Basic Functionality Test
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Basic functionality test to verify the Crusader system can initialize
and perform core operations. This test validates the system architecture
without requiring hardware dependencies.
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Dict, List

# Add crusader directory to sys.path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import Crusader components
from crusader.core.constants import SystemMode
from crusader.core.main import CrusaderSystem
from crusader.core.state_machine.mode import ModeManager
from crusader.core.utils.hash_utils import HashEngine
from crusader.core.utils.io_utils import IOEngine
from crusader.core.utils.time_utils import TimeUtils
from crusader.monitoring.diagnostics import SystemDiagnostics
from crusader.monitoring.sensors import SensorManager
from crusader.warfare.air_curtain import AirCurtainSystem
from crusader.warfare.counter import FlyCounterSystem
from crusader.warfare.spore_deployment import SporeDeploymentSystem
from crusader.warfare.sticky_array import StickyTrapSystem
from crusader.warfare.uv_sterilization import UVSterilizationSystem


class CrusaderBasicTest:
    """Basic functionality test for Crusader Combat Refrigerator."""

    def __init__(self):
        self.test_results = []
        self.start_time = time.time()

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        return success

    async def test_core_utilities(self) -> bool:
        """Test core utility modules."""
        print("\n" + "=" * 60)
        print("TESTING CORE UTILITIES")
        print("=" * 60)

        all_passed = True

        # Test TimeUtils
        try:
            time_utils = TimeUtils()
            current_time = time_utils.get_current_time()
            formatted = time_utils.format_time(current_time)

            success = self.log_test(
                "TimeUtils - Initialization", True, f"Current time: {formatted}"
            )
            all_passed = all_passed and success
        except Exception as e:
            success = self.log_test("TimeUtils - Initialization", False, f"Error: {e}")
            all_passed = False

        # Test HashEngine
        try:
            hash_engine = HashEngine()
            test_data = "Crusader Combat Refrigerator Test"
            hash_result = hash_engine.compute_hash(test_data)

            success = self.log_test(
                "HashEngine - Hash Computation",
                True,
                f"Hash: {hash_result.hash[:16]}...",
            )
            all_passed = all_passed and success
        except Exception as e:
            success = self.log_test(
                "HashEngine - Hash Computation", False, f"Error: {e}"
            )
            all_passed = False

        # Test IOEngine
        try:
            io_engine = IOEngine()
            test_content = "Test content for IO operations"

            # Test file operations in simulation mode
            result = io_engine.write_file("/tmp/test_file.txt", test_content)

            success = self.log_test(
                "IOEngine - File Operations",
                result.success,
                f"Result: {result.message}",
            )
            all_passed = all_passed and success
        except Exception as e:
            success = self.log_test("IOEngine - File Operations", False, f"Error: {e}")
            all_passed = False

        return all_passed

    async def test_monitoring_systems(self) -> bool:
        """Test monitoring systems."""
        print("\n" + "=" * 60)
        print("TESTING MONITORING SYSTEMS")
        print("=" * 60)

        all_passed = True

        # Test SensorManager
        try:
            sensor_manager = SensorManager(simulation_mode=True)
            initialized = await sensor_manager.initialize()

            success = self.log_test(
                "SensorManager - Initialization",
                initialized,
                f"Initialized: {initialized}",
            )
            all_passed = all_passed and success

            if initialized:
                # Test sensor readings
                readings = await sensor_manager.get_sensor_readings()
                success = self.log_test(
                    "SensorManager - Get Readings",
                    len(readings) > 0,
                    f"Got {len(readings)} sensor readings",
                )
                all_passed = all_passed and success

                await sensor_manager.shutdown()
        except Exception as e:
            success = self.log_test(
                "SensorManager - Initialization", False, f"Error: {e}"
            )
            all_passed = False

        # Test SystemDiagnostics
        try:
            diagnostics = SystemDiagnostics(simulation_mode=True)
            initialized = await diagnostics.initialize()

            success = self.log_test(
                "SystemDiagnostics - Initialization",
                initialized,
                f"Initialized: {initialized}",
            )
            all_passed = all_passed and success

            if initialized:
                # Run diagnostics
                diag_result = await diagnostics.run_diagnostics()
                success = self.log_test(
                    "SystemDiagnostics - Run Diagnostics",
                    diag_result.overall_status == "HEALTHY",
                    f"Status: {diag_result.overall_status}",
                )
                all_passed = all_passed and success
        except Exception as e:
            success = self.log_test(
                "SystemDiagnostics - Initialization", False, f"Error: {e}"
            )
            all_passed = False

        return all_passed

    async def test_warfare_systems(self) -> bool:
        """Test warfare systems."""
        print("\n" + "=" * 60)
        print("TESTING WARFARE SYSTEMS")
        print("=" * 60)

        all_passed = True

        # Test SporeDeploymentSystem
        try:
            spore_system = SporeDeploymentSystem(simulation_mode=True)
            initialized = await spore_system.initialize()

            success = self.log_test(
                "SporeDeploymentSystem - Initialization",
                initialized,
                f"Initialized: {initialized}",
            )
            all_passed = all_passed and success

            if initialized:
                # Test deployment
                deployment = await spore_system.deploy_spores(volume_ml=10.0)
                success = self.log_test(
                    "SporeDeploymentSystem - Deploy Spores",
                    deployment.success,
                    f"Deployed: {deployment.volume_ml}ml",
                )
                all_passed = all_passed and success
        except Exception as e:
            success = self.log_test(
                "SporeDeploymentSystem - Initialization", False, f"Error: {e}"
            )
            all_passed = False

        # Test UVSterilizationSystem
        try:
            uv_system = UVSterilizationSystem(simulation_mode=True)
            initialized = await uv_system.initialize()

            success = self.log_test(
                "UVSterilizationSystem - Initialization",
                initialized,
                f"Initialized: {initialized}",
            )
            all_passed = all_passed and success

            if initialized:
                # Test sterilization
                result = await uv_system.sterilize(duration_seconds=5)
                success = self.log_test(
                    "UVSterilizationSystem - Sterilize",
                    result.success,
                    f"Sterilized for {result.duration_seconds} seconds",
                )
                all_passed = all_passed and success
        except Exception as e:
            success = self.log_test(
                "UVSterilizationSystem - Initialization", False, f"Error: {e}"
            )
            all_passed = False

        # Test AirCurtainSystem
        try:
            air_system = AirCurtainSystem(simulation_mode=True)
            initialized = await air_system.initialize()

            success = self.log_test(
                "AirCurtainSystem - Initialization",
                initialized,
                f"Initialized: {initialized}",
            )
            all_passed = all_passed and success

            if initialized:
                # Test activation
                result = await air_system.activate(duration_seconds=3)
                success = self.log_test(
                    "AirCurtainSystem - Activate",
                    result.success,
                    f"Activated for {result.duration_seconds} seconds",
                )
                all_passed = all_passed and success
        except Exception as e:
            success = self.log_test(
                "AirCurtainSystem - Initialization", False, f"Error: {e}"
            )
            all_passed = False

        # Test StickyTrapSystem
        try:
            sticky_system = StickyTrapSystem(simulation_mode=True)
            initialized = await sticky_system.initialize()

            success = self.log_test(
                "StickyTrapSystem - Initialization",
                initialized,
                f"Initialized: {initialized}",
            )
            all_passed = all_passed and success

            if initialized:
                # Test trap check
                result = await sticky_system.check_traps()
                success = self.log_test(
                    "StickyTrapSystem - Check Traps",
                    result.success,
                    f"Checked {result.traps_checked} traps",
                )
                all_passed = all_passed and success
        except Exception as e:
            success = self.log_test(
                "StickyTrapSystem - Initialization", False, f"Error: {e}"
            )
            all_passed = False

        # Test FlyCounterSystem
        try:
            fly_system = FlyCounterSystem(simulation_mode=True)
            initialized = await fly_system.initialize()

            success = self.log_test(
                "FlyCounterSystem - Initialization",
                initialized,
                f"Initialized: {initialized}",
            )
            all_passed = all_passed and success

            if initialized:
                # Test counting
                result = await fly_system.count_flies(duration_seconds=2)
                success = self.log_test(
                    "FlyCounterSystem - Count Flies",
                    result.success,
                    f"Counted {result.fly_count} flies",
                )
                all_passed = all_passed and success
        except Exception as e:
            success = self.log_test(
                "FlyCounterSystem - Initialization", False, f"Error: {e}"
            )
            all_passed = False

        return all_passed

    async def test_mode_manager(self) -> bool:
        """Test mode management system."""
        print("\n" + "=" * 60)
        print("TESTING MODE MANAGER")
        print("=" * 60)

        all_passed = True

        try:
            mode_manager = ModeManager()
            initialized = await mode_manager.initialize()

            success = self.log_test(
                "ModeManager - Initialization",
                initialized,
                f"Initialized: {initialized}",
            )
            all_passed = all_passed and success

            if initialized:
                # Test mode transitions
                current_mode = mode_manager.get_current_mode()
                success = self.log_test(
                    "ModeManager - Get Current Mode",
                    current_mode is not None,
                    f"Current mode: {current_mode}",
                )
                all_passed = all_passed and success

                # Test mode change
                result = await mode_manager.transition_to_mode(
                    SystemMode.STANDBY, reason="Test transition"
                )
                success = self.log_test(
                    "ModeManager - Transition Mode",
                    result.success,
                    f"Transitioned to {result.new_mode}",
                )
                all_passed = all_passed and success
        except Exception as e:
            success = self.log_test(
                "ModeManager - Initialization", False, f"Error: {e}"
            )
            all_passed = False

        return all_passed

    async def test_full_system(self) -> bool:
        """Test full Crusader system initialization."""
        print("\n" + "=" * 60)
        print("TESTING FULL CRUSADER SYSTEM")
        print("=" * 60)

        all_passed = True

        try:
            # Initialize full system in simulation mode
            crusader_system = CrusaderSystem(
                simulation_mode=True,
                config={
                    "system": {
                        "name": "Crusader Test System",
                        "version": "1.0.0",
                        "simulation_mode": True,
                    },
                    "warfare": {
                        "enabled": True,
                        "systems": ["spore", "uv", "air", "sticky", "counter"],
                    },
                    "monitoring": {
                        "enabled": True,
                        "sensors": True,
                        "diagnostics": True,
                    },
                },
            )

            # Initialize system
            initialized = await crusader_system.initialize()

            success = self.log_test(
                "CrusaderSystem - Initialization",
                initialized,
                f"System initialized: {initialized}",
            )
            all_passed = all_passed and success

            if initialized:
                # Get system status
                status = crusader_system.get_status()
                success = self.log_test(
                    "CrusaderSystem - Get Status",
                    status is not None,
                    f"Mode: {status['current_mode']}, Uptime: {status['uptime_seconds']:.1f}s",
                )
                all_passed = all_passed and success

                # Run one cycle
                cycle_result = await crusader_system.run_cycle()
                success = self.log_test(
                    "CrusaderSystem - Run Cycle",
                    cycle_result.success,
                    f"Cycle completed: {cycle_result.message}",
                )
                all_passed = all_passed and success

                # Shutdown system
                shutdown_result = await crusader_system.shutdown()
                success = self.log_test(
                    "CrusaderSystem - Shutdown",
                    shutdown_result,
                    "System shutdown cleanly",
                )
                all_passed = all_passed and success
        except Exception as e:
            success = self.log_test(
                "CrusaderSystem - Initialization", False, f"Error: {e}"
            )
            all_passed = False

        return all_passed

    def generate_report(self) -> Dict:
        """Generate test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        elapsed_time = time.time() - self.start_time

        report = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "elapsed_time_seconds": f"{elapsed_time:.2f}",
            },
            "results": self.test_results,
            "summary": {
                "core_utilities": "✅ PASS"
                if all(
                    r["success"]
                    for r in self.test_results
                    if "TimeUtils" in r["test"]
                    or "HashEngine" in r["test"]
                    or "IOEngine" in r["test"]
                )
                else "❌ FAIL",
                "monitoring_systems": "✅ PASS"
                if all(
                    r["success"]
                    for r in self.test_results
                    if "SensorManager" in r["test"] or "SystemDiagnostics" in r["test"]
                )
                else "❌ FAIL",
                "warfare_systems": "✅ PASS"
                if all(
                    r["success"]
                    for r in self.test_results
                    if "SporeDeploymentSystem" in r["test"]
                    or "UVSterilizationSystem" in r["test"]
                    or "AirCurtainSystem" in r["test"]
                    or "StickyTrapSystem" in r["test"]
                    or "FlyCounterSystem" in r["test"]
                )
                else "❌ FAIL",
                "mode_manager": "✅ PASS"
                if all(
                    r["success"]
                    for r in self.test_results
                    if "ModeManager" in r["test"]
                )
                else "❌ FAIL",
                "full_system": "✅ PASS"
                if all(
                    r["success"]
                    for r in self.test_results
                    if "CrusaderSystem" in r["test"]
                )
                else "❌ FAIL",
            },
        }

        return report

    async def run_all_tests(self) -> bool:
        """Run all tests."""
        print("=" * 80)
        print("CRUSADER COMBAT REFRIGERATOR - BASIC FUNCTIONALITY TEST")
        print("=" * 80)
        print(f"Starting test at: {datetime.now().isoformat()}")
        print(f"Python version: {sys.version}")
        print()

        all_passed = True

        # Run test suites
        all_passed = all_passed and await self.test_core_utilities()
        all_passed = all_passed and await self.test_monitoring_systems()
        all_passed = all_passed and await self.test_warfare_systems()
        all_passed = all_passed and await self.test_mode_manager()
        all_passed = all_passed and await self.test_full_system()

        # Generate report
        report = self.generate_report()

        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total tests: {report['test_run']['total_tests']}")
        print(f"Passed: {report['test_run']['passed_tests']}")
        print(f"Failed: {report['test_run']['failed_tests']}")
        print(f"Success rate: {report['test_run']['success_rate']}")
        print(f"Elapsed time: {report['test_run']['elapsed_time_seconds']} seconds")

        print("\nComponent Status:")
        for component, status in report["summary"].items():
            print(f"  {component.replace('_', ' ').title()}: {status}")

        print("\n" + "=" * 80)
        if all_passed:
            print("✅ ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED")
        print("=" * 80)

        return all_passed


async def main():
    """Main test runner."""
    tester = CrusaderBasicTest()
    success = await tester.run_all_tests()

    if success:
        print("\n🎉 Crusader Combat Refrigerator is functional!")
        print("The system architecture is sound and ready for deployment.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

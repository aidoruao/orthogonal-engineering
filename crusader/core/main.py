#!/usr/bin/env python3
"""
Crusader Combat Refrigerator - Main Control System
Version: 1.0.0
Yeshua Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Main entry point for the Crusader combat refrigerator system.
Implements the core control loop, scheduling, and system orchestration.
"""

import asyncio
import signal
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

from crusader.core.diagnostics.integrity_check import IntegrityVerifier
from crusader.core.diagnostics.memory_check import MemoryMonitor
from crusader.core.diagnostics.sensor_check import SensorDiagnostics
from crusader.core.state_machine.audit import AuditLogger
from crusader.core.state_machine.error_states import ErrorStateManager
from crusader.core.state_machine.mode import ModeManager, SystemMode
from crusader.core.state_machine.transitions import TransitionManager
from crusader.core.utils.hash_utils import HashEngine
from crusader.core.utils.io_utils import FileLogger, SystemIO
from crusader.core.utils.time_utils import Scheduler
from crusader.monitoring.diagnostics import SystemDiagnostics

# Import monitoring subsystems
from crusader.monitoring.sensors import SensorManager
from crusader.monitoring.witness import WitnessLayer
from crusader.warfare.air_curtain import AirCurtainSystem
from crusader.warfare.counter import FlyCounterSystem

# Import warfare subsystems
from crusader.warfare.spore_deployment import SporeDeploymentSystem
from crusader.warfare.sticky_array import StickyTrapSystem
from crusader.warfare.uv_sterilization import UVSterilizationSystem


class CrusaderSystem:
    """
    Main Crusader system controller.
    Orchestrates all subsystems and maintains system state.
    """

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the Crusader system with configuration."""
        self.config_path = config_path
        self.config = self._load_config()

        # Core components
        self.mode_manager = ModeManager()
        self.transition_manager = TransitionManager()
        self.error_manager = ErrorStateManager()
        self.audit_logger = AuditLogger()

        # Utilities
        self.scheduler = Scheduler()
        self.hash_engine = HashEngine()
        self.file_logger = FileLogger()
        self.system_io = SystemIO()

        # Diagnostics
        self.memory_monitor = MemoryMonitor()
        self.sensor_diagnostics = SensorDiagnostics()
        self.integrity_verifier = IntegrityVerifier()

        # Warfare subsystems
        self.spore_system = SporeDeploymentSystem()
        self.uv_system = UVSterilizationSystem()
        self.air_curtain = AirCurtainSystem()
        self.sticky_traps = StickyTrapSystem()
        self.fly_counter = FlyCounterSystem()

        # Monitoring subsystems
        self.sensor_manager = SensorManager()
        self.system_diagnostics = SystemDiagnostics()
        self.witness_layer = WitnessLayer()

        # System state
        self.running = False
        self.start_time = None
        self.cycle_count = 0
        self.last_health_check = None

        # Performance metrics
        self.metrics = {
            "total_cycles": 0,
            "successful_deployments": 0,
            "fly_eliminations": 0,
            "system_errors": 0,
            "uptime_seconds": 0,
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        import yaml

        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {self.config_path} not found. Using defaults.")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "system": {
                "name": "Crusader Combat Refrigerator",
                "version": "1.0.0",
                "mode": "active",
                "debug": False,
            },
            "warfare": {
                "spore_deployment_interval": 3600,  # 1 hour
                "uv_sterilization_interval": 7200,  # 2 hours
                "air_curtain_active": True,
                "sticky_trap_monitoring": True,
            },
            "monitoring": {
                "sensor_poll_interval": 60,  # 1 minute
                "health_check_interval": 300,  # 5 minutes
                "witness_update_interval": 3600,  # 1 hour
            },
            "hardware": {
                "gpio_pins": {"sprayer": 17, "uv_led": 27, "fan": 22, "sensor_power": 5}
            },
        }

    async def initialize(self) -> bool:
        """
        Initialize all subsystems.
        Returns True if all subsystems initialized successfully.
        """
        print("[INIT] Initializing Crusader Combat Refrigerator System...")

        # Initialize core components
        self.mode_manager.initialize()
        self.transition_manager.initialize()
        self.error_manager.initialize()
        self.audit_logger.initialize()

        # Initialize utilities
        self.scheduler.initialize()
        self.hash_engine.initialize()
        self.file_logger.initialize()
        self.system_io.initialize()

        # Initialize diagnostics
        memory_ok = self.memory_monitor.initialize()
        sensor_ok = self.sensor_diagnostics.initialize()
        integrity_ok = self.integrity_verifier.initialize()

        if not all([memory_ok, sensor_ok, integrity_ok]):
            print("❌ Diagnostic initialization failed")
            return False

        # Initialize warfare subsystems
        warfare_success = await asyncio.gather(
            self.spore_system.initialize(),
            self.uv_system.initialize(),
            self.air_curtain.initialize(),
            self.sticky_traps.initialize(),
            self.fly_counter.initialize(),
        )

        if not all(warfare_success):
            print("❌ Warfare subsystem initialization failed")
            return False

        # Initialize monitoring subsystems
        monitoring_success = await asyncio.gather(
            self.sensor_manager.initialize(),
            self.system_diagnostics.initialize(),
            self.witness_layer.initialize(),
        )

        if not all(monitoring_success):
            print("❌ Monitoring subsystem initialization failed")
            return False

        # Record initialization in audit log
        self.audit_logger.log_event(
            event_type="system_initialization",
            message="Crusader system initialized successfully",
            severity="INFO",
        )

        # Generate initial witness hash
        initial_hash = self.witness_layer.generate_system_hash()
        print(f"🔐 Initial system hash: {initial_hash}")

        print("✅ Crusader system initialized successfully")
        return True

    async def run_cycle(self) -> bool:
        """
        Execute one complete system cycle.
        Returns True if cycle completed successfully.
        """
        self.cycle_count += 1
        cycle_start = time.time()

        print(f"\n🔄 Cycle #{self.cycle_count} starting at {datetime.now()}")

        try:
            # 1. Check system health
            health_ok = await self._check_system_health()
            if not health_ok:
                print("⚠️ System health check failed, entering safe mode")
                await self.mode_manager.set_mode(SystemMode.SAFE)
                return False

            # 2. Read sensors
            sensor_data = await self.sensor_manager.read_all_sensors()

            # 3. Update fly counter
            fly_count = await self.fly_counter.update_count(sensor_data)

            # 4. Execute warfare actions based on mode and conditions
            warfare_results = await self._execute_warfare_actions(
                sensor_data, fly_count
            )

            # 5. Update monitoring and witness
            await self._update_monitoring(sensor_data, warfare_results)

            # 6. Perform periodic maintenance
            await self._perform_maintenance()

            # 7. Update metrics
            self._update_metrics(warfare_results)

            cycle_duration = time.time() - cycle_start
            print(f"✅ Cycle #{self.cycle_count} completed in {cycle_duration:.2f}s")

            return True

        except Exception as e:
            print(f"❌ Cycle #{self.cycle_count} failed: {e}")
            self.error_manager.handle_error(e)
            return False

    async def _check_system_health(self) -> bool:
        """Perform comprehensive system health check."""
        checks = [
            self.memory_monitor.check_memory(),
            self.sensor_diagnostics.run_diagnostics(),
            self.integrity_verifier.verify_system_integrity(),
        ]

        results = await asyncio.gather(*checks)
        return all(results)

    async def _execute_warfare_actions(self, sensor_data: Dict, fly_count: int) -> Dict:
        """Execute all warfare actions based on current conditions."""
        results = {}

        # Check if we should deploy spores
        should_deploy = await self.spore_system.should_deploy(sensor_data, fly_count)
        if should_deploy:
            results["spore_deployment"] = await self.spore_system.deploy()

        # Check if we should run UV sterilization
        should_sterilize = await self.uv_system.should_sterilize(sensor_data)
        if should_sterilize:
            results["uv_sterilization"] = await self.uv_system.sterilize()

        # Manage air curtain
        results["air_curtain"] = await self.air_curtain.manage(sensor_data)

        # Check sticky traps
        results["sticky_traps"] = await self.sticky_traps.check_status()

        return results

    async def _update_monitoring(self, sensor_data: Dict, warfare_results: Dict):
        """Update monitoring systems and witness layer."""
        # Log sensor data
        await self.system_diagnostics.log_sensor_data(sensor_data)

        # Log warfare results
        await self.system_diagnostics.log_warfare_results(warfare_results)

        # Update witness if needed
        current_time = time.time()
        if (
            self.last_health_check is None
            or current_time - self.last_health_check
            > self.config["monitoring"]["witness_update_interval"]
        ):
            await self.witness_layer.update()
            self.last_health_check = current_time

    async def _perform_maintenance(self):
        """Perform periodic maintenance tasks."""
        # Check if it's time for maintenance
        if self.cycle_count % 100 == 0:  # Every 100 cycles
            print("🔧 Performing periodic maintenance...")
            await self.system_diagnostics.run_comprehensive_check()

    def _update_metrics(self, warfare_results: Dict):
        """Update system performance metrics."""
        self.metrics["total_cycles"] = self.cycle_count

        if warfare_results.get("spore_deployment", {}).get("success", False):
            self.metrics["successful_deployments"] += 1

        if warfare_results.get("fly_eliminations", 0) > 0:
            self.metrics["fly_eliminations"] += warfare_results.get(
                "fly_eliminations", 0
            )

        if self.start_time:
            self.metrics["uptime_seconds"] = time.time() - self.start_time

    async def run(self):
        """Main system run loop."""
        self.running = True
        self.start_time = time.time()

        print("\n" + "=" * 60)
        print("[OPERATIONAL] CRUSADER COMBAT REFRIGERATOR - OPERATIONAL")
        print("=" * 60)
        print(f"System: {self.config['system']['name']}")
        print(f"Version: {self.config['system']['version']}")
        print(f"Mode: {self.mode_manager.current_mode}")
        print("=" * 60 + "\n")

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            while self.running:
                # Run one cycle
                cycle_success = await self.run_cycle()

                if not cycle_success:
                    print("⚠️ Cycle failed, waiting before retry...")
                    await asyncio.sleep(10)  # Wait before retry
                else:
                    # Wait for next cycle based on configuration
                    await asyncio.sleep(self.config["system"].get("cycle_interval", 60))

        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Fatal error in main loop: {e}")
        finally:
            await self.shutdown()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n📡 Received signal {signum}, initiating shutdown...")
        self.running = False

    async def shutdown(self):
        """Gracefully shutdown all subsystems."""
        print("\n🔴 Shutting down Crusader system...")

        # Stop all subsystems
        shutdown_tasks = [
            self.spore_system.shutdown(),
            self.uv_system.shutdown(),
            self.air_curtain.shutdown(),
            self.sticky_traps.shutdown(),
            self.fly_counter.shutdown(),
            self.sensor_manager.shutdown(),
            self.system_diagnostics.shutdown(),
            self.witness_layer.shutdown(),
        ]

        await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        # Final audit log
        self.audit_logger.log_event(
            event_type="system_shutdown",
            message=f"Crusader system shutdown after {self.cycle_count} cycles",
            severity="INFO",
        )

        # Generate final witness hash
        final_hash = self.witness_layer.generate_system_hash()
        print(f"🔐 Final system hash: {final_hash}")

        # Print summary
        print("\n" + "=" * 60)
        print("📊 CRUSADER SYSTEM SUMMARY")
        print("=" * 60)
        print(f"Total cycles: {self.metrics['total_cycles']}")
        print(f"Successful deployments: {self.metrics['successful_deployments']}")
        print(f"Fly eliminations: {self.metrics['fly_eliminations']}")
        print(f"System errors: {self.metrics['system_errors']}")
        print(f"Uptime: {self.metrics['uptime_seconds']:.0f} seconds")
        print("=" * 60)

        print("✅ Crusader system shutdown complete")


async def main():
    """Main entry point."""
    system = CrusaderSystem()

    # Initialize system
    if not await system.initialize():
        print("❌ System initialization failed. Exiting.")
        return 1

    # Run system
    try:
        await system.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

"""
Crusader Combat Refrigerator - Monitoring Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Monitoring subsystems for the Crusader combat refrigerator.
Provides environmental sensing, witness layer, and system diagnostics.
"""

from . import diagnostics, sensors, witness

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"

# Export monitoring systems
__all__ = [
    "diagnostics",
    "sensors",
    "witness",
]

# Convenience imports
from .diagnostics import SystemDiagnostics
from .sensors import SensorManager
from .witness import WitnessLayer


# Combined monitoring interface
class MonitoringOrchestrator:
    """Orchestrates all monitoring systems."""

    def __init__(self):
        self.systems = {
            "sensors": SensorManager(),
            "witness": WitnessLayer(),
            "diagnostics": SystemDiagnostics(),
        }

    def get_system(self, name: str):
        """Get a specific monitoring system."""
        return self.systems.get(name)

    def get_all_systems(self):
        """Get all monitoring systems."""
        return self.systems

    def get_status(self):
        """Get status of all monitoring systems."""
        return {
            name: system.get_status() if hasattr(system, "get_status") else "unknown"
            for name, system in self.systems.items()
        }

    def get_metrics(self):
        """Get metrics from all monitoring systems."""
        metrics = {}
        for name, system in self.systems.items():
            if hasattr(system, "get_metrics"):
                metrics[name] = system.get_metrics()
            elif hasattr(system, "get_status"):
                metrics[name] = system.get_status()
        return metrics


# Export the orchestrator
MonitoringSystems = MonitoringOrchestrator

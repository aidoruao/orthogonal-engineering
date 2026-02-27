"""
Crusader Combat Refrigerator - Warfare Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Warfare subsystems for the Crusader combat refrigerator.
Implements multi-layered defense against insect infestation.
"""

from . import air_curtain, counter, spore_deployment, sticky_array, uv_sterilization

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"

# Export main warfare systems
__all__ = [
    "air_curtain",
    "counter",
    "spore_deployment",
    "sticky_array",
    "uv_sterilization",
]

# Convenience imports
from .air_curtain import AirCurtainSystem
from .counter import FlyCounterSystem
from .spore_deployment import SporeDeploymentSystem
from .sticky_array import StickyTrapSystem
from .uv_sterilization import UVSterilizationSystem


# Combined warfare interface
class WarfareOrchestrator:
    """Orchestrates all warfare systems."""

    def __init__(self):
        self.systems = {
            "spore_deployment": SporeDeploymentSystem(),
            "uv_sterilization": UVSterilizationSystem(),
            "air_curtain": AirCurtainSystem(),
            "sticky_array": StickyTrapSystem(),
            "counter": FlyCounterSystem(),
        }

    def get_system(self, name: str):
        """Get a specific warfare system."""
        return self.systems.get(name)

    def get_all_systems(self):
        """Get all warfare systems."""
        return self.systems

    def get_status(self):
        """Get status of all warfare systems."""
        return {
            name: system.get_status() if hasattr(system, "get_status") else "unknown"
            for name, system in self.systems.items()
        }


# Export the orchestrator
WarfareSystems = WarfareOrchestrator

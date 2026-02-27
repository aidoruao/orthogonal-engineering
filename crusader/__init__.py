"""
Crusader Combat Refrigerator - Main Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Main package for the Crusader Combat Refrigerator system.
Provides centralized imports and package configuration.
"""

import os
import sys

# Add the parent directory to sys.path to allow absolute imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Package metadata
__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"
__description__ = "Advanced fly warfare system for refrigerators using orthogonal engineering principles"

# Core imports
try:
    from crusader.core.constants import (
        ALL_CONSTANTS,
        CRYPTO_CONSTANTS,
        ENVIRONMENTAL_CONSTANTS,
        FILE_CONSTANTS,
        HARDWARE_CONSTANTS,
        MATH_CONSTANTS,
        PATTERN_CONSTANTS,
        SYSTEM_LIMITS,
        TIME_CONSTANTS,
        CryptographicConstants,
        EnvironmentalConstants,
        FileConstants,
        HardwareConstants,
        MathematicalConstants,
        PatternConstants,
        SystemLimits,
        TimeConstants,
        get_all_constants,
    )
except ImportError as e:
    print(f"Warning: Could not import core constants: {e}")

    # Define fallback constants
    class EnvironmentalConstants:
        OPTIMAL_TEMPERATURE = 25.0
        MIN_TEMPERATURE = 2.0
        MAX_TEMPERATURE = 35.0

    ENVIRONMENTAL_CONSTANTS = {}
    TIME_CONSTANTS = {}
    HARDWARE_CONSTANTS = {}
    SYSTEM_LIMITS = {}
    MATH_CONSTANTS = {}
    PATTERN_CONSTANTS = {}
    CRYPTO_CONSTANTS = {}
    FILE_CONSTANTS = {}
    ALL_CONSTANTS = {}
    get_all_constants = lambda: {}

# Core utilities
try:
    from crusader.core.utils.hash_utils import HashEngine
    from crusader.core.utils.io_utils import IOEngine
    from crusader.core.utils.time_utils import TimeUtils
except ImportError as e:
    print(f"Warning: Could not import core utilities: {e}")
    TimeUtils = None
    HashEngine = None
    IOEngine = None

# Warfare systems
try:
    from crusader.warfare import WarfareSystems
    from crusader.warfare.air_curtain import AirCurtainSystem
    from crusader.warfare.counter import FlyCounterSystem
    from crusader.warfare.spore_deployment import SporeDeploymentSystem
    from crusader.warfare.sticky_array import StickyTrapSystem
    from crusader.warfare.uv_sterilization import UVSterilizationSystem
except ImportError as e:
    print(f"Warning: Could not import warfare systems: {e}")
    AirCurtainSystem = None
    FlyCounterSystem = None
    SporeDeploymentSystem = None
    StickyTrapSystem = None
    UVSterilizationSystem = None
    WarfareSystems = None

# Monitoring systems
try:
    from crusader.monitoring import MonitoringSystems
    from crusader.monitoring.diagnostics import SystemDiagnostics
    from crusader.monitoring.sensors import SensorManager
    from crusader.monitoring.witness import WitnessLayer
except ImportError as e:
    print(f"Warning: Could not import monitoring systems: {e}")
    SystemDiagnostics = None
    SensorManager = None
    WitnessLayer = None
    MonitoringSystems = None

# Hardware interfaces
try:
    from crusader.hardware import GPIO, Hardware
    from crusader.hardware.drivers.sprayer import SprayerDriver
except ImportError as e:
    print(f"Warning: Could not import hardware interfaces: {e}")
    Hardware = None
    GPIO = None
    SprayerDriver = None

# User interfaces
try:
    from crusader.interface import Interface, Templates
    from crusader.interface.display import (
        DisplayInterface,
        DisplayMode,
        DisplayPage,
        DisplayStatus,
        DisplayType,
    )
except ImportError as e:
    print(f"Warning: Could not import interface systems: {e}")
    Interface = None
    Templates = None
    DisplayInterface = None
    DisplayMode = None
    DisplayPage = None
    DisplayStatus = None
    DisplayType = None

# Main entry point
try:
    from crusader.core.main import main
except ImportError as e:
    print(f"Warning: Could not import main module: {e}")
    main = None

# Export all available components
__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__license__",
    "__description__",
    # Core constants
    "EnvironmentalConstants",
    "TimeConstants",
    "HardwareConstants",
    "SystemLimits",
    "MathematicalConstants",
    "PatternConstants",
    "CryptographicConstants",
    "FileConstants",
    "ENVIRONMENTAL_CONSTANTS",
    "TIME_CONSTANTS",
    "HARDWARE_CONSTANTS",
    "SYSTEM_LIMITS",
    "MATH_CONSTANTS",
    "PATTERN_CONSTANTS",
    "CRYPTO_CONSTANTS",
    "FILE_CONSTANTS",
    "ALL_CONSTANTS",
    "get_all_constants",
    # Core utilities
    "TimeUtils",
    "HashEngine",
    "IOEngine",
    # Warfare systems
    "AirCurtainSystem",
    "FlyCounterSystem",
    "SporeDeploymentSystem",
    "StickyTrapSystem",
    "UVSterilizationSystem",
    "WarfareSystems",
    # Monitoring systems
    "SystemDiagnostics",
    "SensorManager",
    "WitnessLayer",
    "MonitoringSystems",
    # Hardware interfaces
    "Hardware",
    "GPIO",
    "SprayerDriver",
    # User interfaces
    "Interface",
    "Templates",
    "DisplayInterface",
    "DisplayMode",
    "DisplayPage",
    "DisplayStatus",
    "DisplayType",
    # Main entry point
    "main",
]


# Package initialization
def initialize(simulation_mode: bool = False):
    """
    Initialize the Crusader system.

    Args:
        simulation_mode: If True, run in simulation mode without hardware.

    Returns:
        dict: Dictionary with initialized components.
    """
    components = {}

    # Initialize hardware
    if Hardware is not None:
        components["hardware"] = Hardware(simulation_mode=simulation_mode)
        components["hardware"].initialize()

    # Initialize interfaces
    if Interface is not None:
        components["interface"] = Interface(simulation_mode=simulation_mode)
        components["interface"].initialize()

    # Initialize warfare systems
    if WarfareSystems is not None:
        components["warfare"] = WarfareSystems()

    # Initialize monitoring systems
    if MonitoringSystems is not None:
        components["monitoring"] = MonitoringSystems()

    return components


def get_version():
    """Get the package version."""
    return __version__


def get_system_info():
    """Get system information."""
    return {
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "description": __description__,
        "components": {
            "core": TimeUtils is not None,
            "warfare": WarfareSystems is not None,
            "monitoring": MonitoringSystems is not None,
            "hardware": Hardware is not None,
            "interface": Interface is not None,
        },
    }


# Test function
def test_imports():
    """Test that all imports are working."""
    print("=" * 60)
    print("CRUSADER COMBAT REFRIGERATOR - IMPORT TEST")
    print("=" * 60)

    components = get_system_info()["components"]

    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print()
    print("Component Status:")
    for component, status in components.items():
        status_symbol = "✅" if status else "❌"
        print(f"  {status_symbol} {component}")

    all_working = all(components.values())
    if all_working:
        print("\n✅ All components imported successfully!")
    else:
        print(
            f"\n⚠️  Some components failed to import: {[c for c, s in components.items() if not s]}"
        )

    return all_working


if __name__ == "__main__":
    # Run import test when module is executed directly
    success = test_imports()
    sys.exit(0 if success else 1)

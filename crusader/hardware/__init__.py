"""
Crusader Combat Refrigerator - Hardware Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Hardware interfaces and drivers for the Crusader combat refrigerator.
Provides abstraction layer for GPIO, sensors, and actuators.
"""

from . import drivers

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"

# Export hardware components
__all__ = [
    "drivers",
]

# Hardware configuration
try:
    from pathlib import Path

    import yaml

    # Load pin configuration
    pins_config_path = Path(__file__).parent / "pins.yaml"
    if pins_config_path.exists():
        with open(pins_config_path, "r") as f:
            PIN_CONFIG = yaml.safe_load(f)
    else:
        PIN_CONFIG = {}
        print(f"Warning: Pin configuration not found at {pins_config_path}")
except ImportError:
    PIN_CONFIG = {}
    print("Warning: PyYAML not installed, using empty pin configuration")


# Hardware abstraction layer
class HardwareManager:
    """Manages all hardware interfaces."""

    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode
        self.drivers = {}
        self.initialized = False

    def initialize(self):
        """Initialize hardware interfaces."""
        if self.simulation_mode:
            print("Hardware running in simulation mode")
            # Initialize simulated drivers
            from .drivers.sprayer import SprayerDriver

            self.drivers["sprayer"] = SprayerDriver(simulation_mode=True)
        else:
            print("Initializing real hardware interfaces")
            # Initialize real hardware drivers
            try:
                from .drivers.sprayer import SprayerDriver

                self.drivers["sprayer"] = SprayerDriver(simulation_mode=False)
            except ImportError as e:
                print(f"Warning: Could not initialize hardware driver: {e}")
                self.drivers["sprayer"] = None

        self.initialized = True
        return True

    def get_driver(self, name: str):
        """Get a hardware driver by name."""
        return self.drivers.get(name)

    def get_all_drivers(self):
        """Get all hardware drivers."""
        return self.drivers

    def get_status(self):
        """Get hardware status."""
        status = {
            "simulation_mode": self.simulation_mode,
            "initialized": self.initialized,
            "drivers": {},
        }

        for name, driver in self.drivers.items():
            if driver is not None and hasattr(driver, "get_status"):
                status["drivers"][name] = driver.get_status()
            else:
                status["drivers"][name] = "not_available"

        return status

    def cleanup(self):
        """Clean up hardware resources."""
        for name, driver in self.drivers.items():
            if driver is not None and hasattr(driver, "cleanup"):
                try:
                    driver.cleanup()
                except Exception as e:
                    print(f"Error cleaning up driver {name}: {e}")

        self.drivers = {}
        self.initialized = False
        print("Hardware resources cleaned up")


# Export hardware manager
Hardware = HardwareManager


# GPIO utilities
class GPIOUtils:
    """GPIO utility functions."""

    @staticmethod
    def get_pin_config(pin_name: str):
        """Get configuration for a specific pin."""
        if not PIN_CONFIG:
            return None

        # Search for pin in configuration
        def find_pin(config, name):
            if isinstance(config, dict):
                for key, value in config.items():
                    if key == name:
                        return value
                    elif isinstance(value, (dict, list)):
                        result = find_pin(value, name)
                        if result is not None:
                            return result
            elif isinstance(config, list):
                for item in config:
                    result = find_pin(item, name)
                    if result is not None:
                        return result
            return None

        return find_pin(PIN_CONFIG, pin_name)

    @staticmethod
    def validate_pin_assignment(pin: int):
        """Validate a pin assignment."""
        if not isinstance(pin, int):
            return False, "Pin must be an integer"

        if pin < 0 or pin > 27:  # Raspberry Pi 4 has 28 GPIO pins (0-27)
            return False, f"Pin {pin} out of range (0-27)"

        # Check for reserved pins
        reserved_pins = [14, 15, 2, 3, 9, 10, 11, 8, 7]  # UART, I2C, SPI
        if pin in reserved_pins:
            return True, f"Pin {pin} is reserved for system use"

        return True, f"Pin {pin} is valid"

    @staticmethod
    def get_pin_physical(pin: int):
        """Get physical pin number for BCM pin."""
        # Raspberry Pi 4 pin mapping (BCM to physical)
        pin_map = {
            0: 27,
            1: 28,
            2: 3,
            3: 5,
            4: 7,
            5: 29,
            6: 31,
            7: 26,
            8: 24,
            9: 21,
            10: 19,
            11: 23,
            12: 32,
            13: 33,
            14: 8,
            15: 10,
            16: 36,
            17: 11,
            18: 12,
            19: 35,
            20: 38,
            21: 40,
            22: 15,
            23: 16,
            24: 18,
            25: 22,
            26: 37,
            27: 13,
        }
        return pin_map.get(pin, "unknown")


# Export GPIO utilities
GPIO = GPIOUtils

"""
Crusader Combat Refrigerator - Interface Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

User interface subsystems for the Crusader combat refrigerator.
Provides display, input, and feedback interfaces.
"""

from . import display

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"

# Export interface components
__all__ = [
    "display",
]

# Convenience imports
from .display import (
    DisplayInterface,
    DisplayMode,
    DisplayPage,
    DisplayStatus,
    DisplayType,
)


# Interface manager
class InterfaceManager:
    """Manages all user interface components."""

    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode
        self.interfaces = {}
        self.initialized = False

    def initialize(self, display_type: DisplayType = DisplayType.LCD_16x2):
        """Initialize interface components."""
        if self.simulation_mode:
            print("Interface running in simulation mode")

            # Initialize display
            from .display import DisplayInterface

            self.interfaces["display"] = DisplayInterface(
                display_type=display_type, simulation_mode=True
            )
        else:
            print("Initializing real hardware interfaces")

            try:
                from .display import DisplayInterface

                self.interfaces["display"] = DisplayInterface(
                    display_type=display_type, simulation_mode=False
                )
            except ImportError as e:
                print(f"Warning: Could not initialize display interface: {e}")
                self.interfaces["display"] = None

        self.initialized = True
        return True

    def get_interface(self, name: str):
        """Get an interface component by name."""
        return self.interfaces.get(name)

    def get_all_interfaces(self):
        """Get all interface components."""
        return self.interfaces

    def get_status(self):
        """Get interface status."""
        status = {
            "simulation_mode": self.simulation_mode,
            "initialized": self.initialized,
            "interfaces": {},
        }

        for name, interface in self.interfaces.items():
            if interface is not None and hasattr(interface, "get_status"):
                status["interfaces"][name] = interface.get_status()
            else:
                status["interfaces"][name] = "not_available"

        return status

    def show_message(self, message: str, duration: float = 5.0):
        """Show a message on the display."""
        display = self.interfaces.get("display")
        if display is not None and hasattr(display, "show_text"):
            return display.show_text([message], duration_seconds=duration)
        else:
            print(f"Display message: {message}")
            return True

    def show_emergency(self, message: str, details: list = None):
        """Show emergency message."""
        display = self.interfaces.get("display")
        if display is not None and hasattr(display, "show_emergency"):
            return display.show_emergency(message, details)
        else:
            print(f"EMERGENCY: {message}")
            if details:
                for detail in details:
                    print(f"  - {detail}")
            return True

    def clear_emergency(self):
        """Clear emergency message."""
        display = self.interfaces.get("display")
        if display is not None and hasattr(display, "clear_emergency"):
            return display.clear_emergency()
        else:
            print("Emergency cleared")
            return True

    def cleanup(self):
        """Clean up interface resources."""
        for name, interface in self.interfaces.items():
            if interface is not None and hasattr(interface, "cleanup"):
                try:
                    interface.cleanup()
                except Exception as e:
                    print(f"Error cleaning up interface {name}: {e}")

        self.interfaces = {}
        self.initialized = False
        print("Interface resources cleaned up")


# Export interface manager
Interface = InterfaceManager


# Display templates for common messages
class DisplayTemplates:
    """Pre-defined display templates."""

    @staticmethod
    def system_boot():
        """System boot sequence template."""
        return {
            "lines": [
                "CRUSADER",
                "Combat Refrigerator",
                "Version 1.0.0",
                "Booting...",
            ],
            "duration": 3.0,
            "priority": 1,
        }

    @staticmethod
    def system_ready():
        """System ready template."""
        return {
            "lines": [
                "System Ready",
                "Status: OPERATIONAL",
                "Mode: NORMAL",
                "Uptime: 00:00:00",
            ],
            "duration": 5.0,
            "priority": 3,
        }

    @staticmethod
    def warfare_active():
        """Warfare systems active template."""
        return {
            "lines": [
                "Warfare Active",
                "Spores: DEPLOYED",
                "UV: STERILIZING",
                "AirCurtain: ON",
            ],
            "duration": 5.0,
            "priority": 5,
        }

    @staticmethod
    def environmental_status(temp: float, humidity: float, flies: int):
        """Environmental status template."""
        return {
            "lines": [
                "Environment",
                f"Temp: {temp:.1f}°C",
                f"Humidity: {humidity:.0f}%",
                f"Flies: {flies}",
            ],
            "duration": 8.0,
            "priority": 4,
        }

    @staticmethod
    def diagnostics(cpu: float, memory: float, disk: float):
        """Diagnostics template."""
        return {
            "lines": [
                "Diagnostics",
                f"CPU: {cpu:.0f}%",
                f"Mem: {memory:.0f}%",
                f"Disk: {disk:.0f}%",
            ],
            "duration": 8.0,
            "priority": 3,
        }

    @staticmethod
    def maintenance_mode():
        """Maintenance mode template."""
        return {
            "lines": [
                "Maintenance Mode",
                "Systems: OFFLINE",
                "Access: RESTRICTED",
                "Check logs",
            ],
            "duration": None,  # Stay until changed
            "priority": 7,
        }

    @staticmethod
    def error_message(error: str):
        """Error message template."""
        return {
            "lines": [
                "! ERROR !",
                error[:16],
                "Check system",
                "logs for details",
            ],
            "duration": 10.0,
            "priority": 8,
            "blink_lines": [0, 1],
        }


# Export display templates
Templates = DisplayTemplates

"""
Crusader Combat Refrigerator - Hardware Drivers Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Hardware drivers package for the Crusader Combat Refrigerator system.
Provides interfaces for hardware components like sprayers, sensors, and displays.
"""

from .sprayer import SprayerDriver, SprayerResult, SprayerStatus

__all__ = [
    # Sprayer driver
    "SprayerDriver",
    "SprayerStatus",
    "SprayerResult",
]

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"

"""
Crusader Combat Refrigerator - Diagnostics Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Diagnostics package for the Crusader Combat Refrigerator system.
Provides memory checking, integrity verification, and sensor diagnostics.
"""

from .integrity_check import IntegrityCheck, IntegrityResult, IntegrityVerifier
from .memory_check import (
    MemoryAlert,
    MemoryAlertLevel,
    MemoryIssueType,
    MemoryMonitor,
    MemorySnapshot,
)
from .sensor_check import SensorDiagnostics, SensorStatus

__all__ = [
    # Memory checking
    "MemoryMonitor",
    "MemoryAlert",
    "MemoryAlertLevel",
    "MemoryIssueType",
    "MemorySnapshot",
    # Integrity verification
    "IntegrityVerifier",
    "IntegrityCheck",
    "IntegrityResult",
    # Sensor diagnostics
    "SensorDiagnostics",
    "SensorStatus",
]

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"

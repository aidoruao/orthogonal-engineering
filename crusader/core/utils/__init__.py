"""
Crusader Combat Refrigerator - Utilities Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Utilities package for the Crusader Combat Refrigerator system.
Provides time utilities, hash functions, and I/O operations.
"""

from .hash_utils import HashAlgorithm, HashEngine, HashResult
from .io_utils import FileLogger, IOEngine, IOOperation, IOResult
from .time_utils import Scheduler, Timer, TimeUtils

__all__ = [
    # Time utilities
    "TimeUtils",
    "Timer",
    "Scheduler",
    # Hash utilities
    "HashAlgorithm",
    "HashEngine",
    "HashResult",
    # I/O utilities
    "IOEngine",
    "IOResult",
    "IOOperation",
    "FileLogger",
]

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"

"""
Crusader Combat Refrigerator - Core Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Core system components for the Crusader combat refrigerator.
"""

from . import constants, diagnostics, state_machine, utils
from .main import main

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"

__all__ = [
    "constants",
    "state_machine",
    "utils",
    "diagnostics",
    "main",
]

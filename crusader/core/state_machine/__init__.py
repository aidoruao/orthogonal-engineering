"""
Crusader Combat Refrigerator - State Machine Package
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

State machine package for the Crusader Combat Refrigerator system.
Provides mode management, transitions, error handling, and audit logging.
"""

from .audit import AuditEvent, AuditEventType, AuditLogger, AuditSeverity
from .error_states import ErrorSeverity, ErrorState, ErrorStateManager
from .mode import ModeManager, SystemMode
from .transitions import TransitionManager, TransitionResult, TransitionStatus

__all__ = [
    # Mode management
    "ModeManager",
    "SystemMode",
    # Transitions
    "TransitionManager",
    "TransitionResult",
    "TransitionStatus",
    # Error handling
    "ErrorStateManager",
    "ErrorState",
    "ErrorSeverity",
    # Audit logging
    "AuditLogger",
    "AuditEntry",
    "AuditLevel",
]

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering Framework"
__license__ = "AGAPE (Free Forever)"

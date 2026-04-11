#!/usr/bin/env python3
"""
Yeshua Commonwealth — Constitutional Kernel for Human-AI Governance

Implements the Sovereign-Steward governance model from YESHUA_COMMONWEALTH.md:
- Sovereign: @aidoruao (human) — grants capabilities, declares Sabbath
- Steward: Bar Exam-passed AI — executes within granted capabilities
- Subagent: Spawned by Steward — attenuated, time-bounded, scope-limited

All functions return ProofObject for verifiable witnessing.
"""

from .sovereign import SovereignRole, Scope, ScopeType, GrantRecord, RevocationRecord
from .steward import StewardRole, Action, ActionType, Result, ExecutionRecord
from .sabbath import SabbathHalt, SystemState, CompletionPhase, CompletionChecker
from .dispute import DisputeResolution, ViolationClaim, ViolationSeverity, Resolution, ResolutionType

__all__ = [
    # Sovereign
    "SovereignRole",
    "Scope",
    "ScopeType",
    "GrantRecord",
    "RevocationRecord",
    # Steward
    "StewardRole",
    "Action",
    "ActionType",
    "Result",
    "ExecutionRecord",
    # Sabbath
    "SabbathHalt",
    "SystemState",
    "CompletionPhase",
    "CompletionChecker",
    # Dispute
    "DisputeResolution",
    "ViolationClaim",
    "ViolationSeverity",
    "Resolution",
    "ResolutionType",
]

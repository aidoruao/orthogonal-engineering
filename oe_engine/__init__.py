"""Orthogonal Engineering AI — Deterministic Invariant-Locked Inference Engine

Not a language model. Not stochastic. Not neural.
A modular, auditable, falsifiable inference engine constrained by domain
invariants, operating under cryptographic audit with outputs verified by
deterministic checks before reaching the speaker layer.

Architecture:
  Speaker ← Router ← Thinker[] ← InvariantBus ← GuardianMonitor
"""

from .manifest import EngineManifest
from .router import DomainRouter, RouteResult
from .thinker import ThinkerModule, ThinkerInput, ThinkerOutput
from .speaker import SpeakerModule, SpeakerOutput
from .engine import OrthogonalEngine, EngineResponse

__all__ = [
    "EngineManifest",
    "DomainRouter",
    "RouteResult",
    "ThinkerModule",
    "ThinkerInput",
    "ThinkerOutput",
    "SpeakerModule",
    "SpeakerOutput",
    "OrthogonalEngine",
    "EngineResponse",
]

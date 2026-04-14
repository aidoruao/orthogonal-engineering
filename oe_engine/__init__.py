"""Orthogonal Engineering AI — Deterministic Invariant-Locked Inference Engine

Not a language model. Not stochastic. Not neural.
A modular, auditable, falsifiable inference engine constrained by domain
invariants, operating under cryptographic audit with outputs verified by
deterministic checks before reaching the speaker layer.

Architecture:
  Speaker ← Router ← Thinker[] ← InvariantBus ← GuardianMonitor
  Generator ← DomainQuery ← Router
  ConversationEngine ← Generator ← Router
"""

from . import _paths

__version__ = "v2.0.0"
from .manifest import EngineManifest
from .router import DomainRouter, RouteResult
from .thinker import ThinkerModule, ThinkerInput, ThinkerOutput
from .speaker import SpeakerModule, SpeakerOutput
from .engine import OrthogonalEngine, EngineResponse
from .synthesizer import (
    ARCSynthesizer,
    SynthesisResult,
    check_synthesis_result_integrity,
)
from .generator import DomainGenerator, DomainQuery, GeneratedResponse
from .conversation import (
    ConversationEngine,
    ConversationState,
    ConversationTurn,
)

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
    "ARCSynthesizer",
    "SynthesisResult",
    "check_synthesis_result_integrity",
    "DomainGenerator",
    "DomainQuery",
    "GeneratedResponse",
    "ConversationEngine",
    "ConversationState",
    "ConversationTurn",
    "_paths",
    "__version__",
]

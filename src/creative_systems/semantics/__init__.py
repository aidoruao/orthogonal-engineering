"""Creative Systems: Semantics, Semiotics, and Etymology.

A framework for analyzing meaning, signs, and word origins across
the Orthogonal Engineering repository.

This module provides:
- Semantic analysis of domain names and documentation
- Semiotic sign-system analysis (signifier/signified)
- Etymological tracing of terminology
- Cross-domain metaphor detection
"""

from .semantic_analyzer import SemanticAnalyzer, SemanticField
from .semiotic_engine import SemioticEngine, Sign, SignSystem
from .etymology_tracer import EtymologyTracer, WordOrigin

__all__ = [
    "SemanticAnalyzer",
    "SemanticField",
    "SemioticEngine",
    "Sign",
    "SignSystem",
    "EtymologyTracer",
    "WordOrigin",
]

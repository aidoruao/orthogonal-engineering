"""Self-Generating Documentation Pipeline.

Auto-generates documentation from code analysis:
- Domain summaries from invariants.py
- Axiom cross-references
- SAL specification updates
- Ontology drift detection
"""

from .domain_summarizer import DomainSummarizer
from .axiom_indexer import AxiomIndexer
from .drift_detector import DriftDetector

__all__ = ["DomainSummarizer", "AxiomIndexer", "DriftDetector"]

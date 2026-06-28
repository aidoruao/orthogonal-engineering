"""Production-grade structural scanners for Orthogonal Engineering.

These scanners use AST parsing, structured extraction, and contextual analysis
instead of naive keyword matching. They surface mathematical formulas, formal
structures, invariant patterns, and infrastructure signatures across the repo.
"""

from __future__ import annotations

from tools.scanners.base import Finding, Scanner, ScannerResult
from tools.scanners.formula_ast_scanner import FormulaAstScanner
from tools.scanners.formal_structure_scanner import FormalStructureScanner
from tools.scanners.invariant_surface_scanner import InvariantSurfaceScanner
from tools.scanners.infrastructure_signature_scanner import InfrastructureSignatureScanner
from tools.scanners.document_notation_scanner import DocumentNotationScanner
from tools.scanners.orchestrator import ScannerOrchestrator, run_scan

__all__ = [
    "Finding",
    "Scanner",
    "ScannerResult",
    "FormulaAstScanner",
    "FormalStructureScanner",
    "InvariantSurfaceScanner",
    "InfrastructureSignatureScanner",
    "DocumentNotationScanner",
    "ScannerOrchestrator",
    "run_scan",
]

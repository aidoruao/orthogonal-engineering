"""Tests for the scanner orchestrator."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.scanners.orchestrator import ScannerOrchestrator

FIXTURES = Path(__file__).resolve().parent / "scanners_fixtures"


def test_orchestrator_runs_all_scanners() -> None:
    orchestrator = ScannerOrchestrator()
    report = orchestrator.run(FIXTURES)
    scanner_names = {r.scanner for r in report.scanners}
    assert scanner_names == {
        "formula_ast",
        "formal_structure",
        "invariant_surface",
        "infrastructure_signature",
        "document_notation",
    }


def test_orchestrator_report_has_merkle_hash() -> None:
    orchestrator = ScannerOrchestrator()
    report = orchestrator.run(FIXTURES)
    h = report.merkle_hash()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_orchestrator_verify_succeeds() -> None:
    orchestrator = ScannerOrchestrator()
    report = orchestrator.run(FIXTURES)
    ok, proof = orchestrator.verify(report)
    assert ok is True
    assert proof.conclusion.startswith("All scanner results")


def test_run_scan_convenience() -> None:
    from tools.scanners.orchestrator import run_scan
    report = run_scan(FIXTURES)
    assert len(report.scanners) == 5

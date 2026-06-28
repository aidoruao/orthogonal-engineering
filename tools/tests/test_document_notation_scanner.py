"""Tests for the document notation scanner."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.scanners.document_notation_scanner import DocumentNotationScanner

FIXTURES = Path(__file__).resolve().parent / "scanners_fixtures"


def test_detects_inline_latex() -> None:
    scanner = DocumentNotationScanner()
    result = scanner.scan(FIXTURES)
    kinds = {f.kind for f in result.findings}
    assert "latex_inline" in kinds


def test_detects_display_latex() -> None:
    scanner = DocumentNotationScanner()
    result = scanner.scan(FIXTURES)
    kinds = {f.kind for f in result.findings}
    assert "latex_display" in kinds


def test_detects_unicode_math() -> None:
    scanner = DocumentNotationScanner()
    result = scanner.scan(FIXTURES)
    kinds = {f.kind for f in result.findings}
    assert "unicode_math" in kinds


def test_ignores_plain_greek() -> None:
    scanner = DocumentNotationScanner()
    result = scanner.scan(FIXTURES)
    snippets = {f.snippet for f in result.findings}
    # The phrase "alpha but no operators" should not produce a finding because
    # it lacks an operator/relation.
    assert not any("alpha but no operators" in s for s in snippets)

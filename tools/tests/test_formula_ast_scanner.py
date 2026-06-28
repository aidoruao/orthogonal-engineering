"""Tests for the AST-based formula scanner."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.scanners.formula_ast_scanner import FormulaAstScanner

FIXTURES = Path(__file__).resolve().parent / "scanners_fixtures"


def test_detects_fraction_construction() -> None:
    scanner = FormulaAstScanner()
    result = scanner.scan(FIXTURES)
    kinds = {f.kind for f in result.findings if f.category == "fraction_construction"}
    assert "exact_literal" in kinds


def test_detects_fraction_comparison() -> None:
    scanner = FormulaAstScanner()
    result = scanner.scan(FIXTURES)
    categories = {f.category for f in result.findings}
    assert "fraction_comparison" in categories


def test_detects_algebraic_expression() -> None:
    scanner = FormulaAstScanner()
    result = scanner.scan(FIXTURES)
    categories = {f.category for f in result.findings}
    assert "algebraic_expression" in categories or "fraction_arithmetic" in categories


def test_metadata_populated() -> None:
    scanner = FormulaAstScanner()
    result = scanner.scan(FIXTURES)
    assert result.metadata["finding_count"] > 0
    assert "fraction_arithmetic" in result.metadata["categories"]

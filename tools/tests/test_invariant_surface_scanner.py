"""Tests for the invariant surface scanner."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.scanners.invariant_surface_scanner import InvariantSurfaceScanner

FIXTURES = Path(__file__).resolve().parent / "scanners_fixtures"


def test_detects_all_check_functions() -> None:
    scanner = InvariantSurfaceScanner()
    result = scanner.scan(FIXTURES)
    names = {f.context["function"] for f in result.findings}
    assert names == {
        "check_sample_positive",
        "check_sample_bounded",
        "check_sample_bad",
    }


def test_falsifies_coverage() -> None:
    scanner = InvariantSurfaceScanner()
    result = scanner.scan(FIXTURES)
    assert result.metadata["total_invariants"] == 3
    assert result.metadata["falsifies_coverage"] == Fraction(2, 3)


def test_typed_coverage() -> None:
    scanner = InvariantSurfaceScanner()
    result = scanner.scan(FIXTURES)
    assert result.metadata["typed_coverage"] == Fraction(2, 3)


def test_bad_invariant_flagged() -> None:
    scanner = InvariantSurfaceScanner()
    result = scanner.scan(FIXTURES)
    bad = next(f for f in result.findings if f.context["function"] == "check_sample_bad")
    assert bad.context["has_falsifies_if"] is False
    assert bad.context["typed_correctly"] is False

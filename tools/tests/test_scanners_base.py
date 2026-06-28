"""Tests for scanner base types and utilities."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.scanners.base import Finding, ScannerResult, _count_fractions


def test_finding_to_dict() -> None:
    finding = Finding(
        scanner="test",
        file=Path("x.py"),
        line=10,
        category="fraction_arithmetic",
        kind="addition",
        snippet="a + b",
        context={"x": 1},
    )
    d = finding.to_dict()
    assert d["file"] == "x.py"
    assert d["line"] == 10
    assert d["snippet"] == "a + b"


def test_scanner_result_merkle_hash() -> None:
    result = ScannerResult(
        scanner="test",
        findings=(
            Finding("test", Path("x.py"), 1, "c", "k", "s", {}),
        ),
    )
    h = result.merkle_hash()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_count_fractions() -> None:
    findings = [
        Finding("test", Path("a.py"), 1, "c", "k", "Fraction(1)", {}),
        Finding("test", Path("a.py"), 2, "c", "k", "x + y", {}),
    ]
    assert _count_fractions(findings) == Fraction(1, 2)

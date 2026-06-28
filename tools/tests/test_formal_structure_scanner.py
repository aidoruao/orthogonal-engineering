"""Tests for the formal structure scanner."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.scanners.formal_structure_scanner import FormalStructureScanner

FIXTURES = Path(__file__).resolve().parent / "scanners_fixtures"


def test_detects_functor() -> None:
    scanner = FormalStructureScanner()
    result = scanner.scan(FIXTURES)
    kinds = {f.kind for f in result.findings}
    assert "functor" in kinds


def test_detects_sheaf() -> None:
    scanner = FormalStructureScanner()
    result = scanner.scan(FIXTURES)
    kinds = {f.kind for f in result.findings}
    assert "sheaf" in kinds


def test_detects_forcing() -> None:
    scanner = FormalStructureScanner()
    result = scanner.scan(FIXTURES)
    kinds = {f.kind for f in result.findings}
    assert "forcing" in kinds


def test_no_keyword_only_matches() -> None:
    scanner = FormalStructureScanner()
    result = scanner.scan(FIXTURES)
    snippets = {f.snippet for f in result.findings}
    # The bare assignment "monad_word = ..." has no corroboration and must not
    # produce a finding.
    assert not any("monad_word" in s for s in snippets)

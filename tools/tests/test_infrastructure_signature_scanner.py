"""Tests for the infrastructure signature scanner."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.scanners.infrastructure_signature_scanner import InfrastructureSignatureScanner

FIXTURES = Path(__file__).resolve().parent / "scanners_fixtures"


def test_detects_hash_calls() -> None:
    scanner = InfrastructureSignatureScanner()
    result = scanner.scan(FIXTURES)
    categories = {f.category for f in result.findings}
    assert "cryptographic_integrity" in categories


def test_detects_consent_calls() -> None:
    scanner = InfrastructureSignatureScanner()
    result = scanner.scan(FIXTURES)
    categories = {f.category for f in result.findings}
    assert "consent_infrastructure" in categories


def test_detects_capability_calls() -> None:
    scanner = InfrastructureSignatureScanner()
    result = scanner.scan(FIXTURES)
    categories = {f.category for f in result.findings}
    assert "capability_gate" in categories


def test_detects_witness_calls() -> None:
    scanner = InfrastructureSignatureScanner()
    result = scanner.scan(FIXTURES)
    categories = {f.category for f in result.findings}
    assert "state_witness" in categories

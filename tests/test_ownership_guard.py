"""
tests/test_ownership_guard.py — Tests for ownership / anti-monetization guard

Author: Orthogonal Engineering
PR: #34
Version: 1.0.0
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from ownership_guard import run_ownership_guard


def test_ownership_guard_passes_clean_repo():
    result = run_ownership_guard()
    assert result["all_passed"] is True, f"Violations: {result['violations']}"


def test_ownership_guard_returns_dict():
    result = run_ownership_guard()
    assert "all_passed" in result
    assert "violation_count" in result
    assert isinstance(result["violations"], list)


def test_ownership_guard_violation_count_matches():
    result = run_ownership_guard()
    assert result["violation_count"] == len(result["violations"])

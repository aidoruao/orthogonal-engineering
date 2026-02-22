"""
tests/test_yeshua_enforcement.py — Tests for Yeshua enforcement layer

Author: Orthogonal Engineering
PR: #34
Version: 1.0.0
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from yeshua.enforcement import EnforcementReport, run_yeshua_enforcement


def test_yeshua_enforcement_returns_report():
    report = run_yeshua_enforcement()
    assert isinstance(report, EnforcementReport)


def test_yeshua_enforcement_core_passes():
    report = run_yeshua_enforcement()
    assert report.all_passed, f"Yeshua violations: {report.violations}"


def test_enforcement_report_to_dict():
    report = run_yeshua_enforcement()
    d = report.to_dict()
    assert "all_passed" in d
    assert "violation_count" in d
    assert isinstance(d["violations"], list)
    assert isinstance(d["passed"], list)


def test_enforcement_report_to_json():
    report = run_yeshua_enforcement()
    j = report.to_json()
    import json
    parsed = json.loads(j)
    assert "all_passed" in parsed

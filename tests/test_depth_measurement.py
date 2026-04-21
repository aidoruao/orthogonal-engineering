"""tests/test_depth_measurement.py — Tests for the depth measurement tooling.

PR: #8a
Standard: Yeshua / Glass-Box / Orthogonal Engineering
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from audit.depth_measurement import (
    _count_non_blank_non_comment_lines,
    _count_fraction_fields,
    measure_domain_depth,
    run_depth_measurement,
)
from fractions import Fraction

REPO_ROOT = Path(__file__).parent.parent


def test_count_non_blank_non_comment_lines():
    """Blank and pure-comment lines are excluded."""
    source = "\n# comment\nprint('hello')\n  \n"
    assert _count_non_blank_non_comment_lines(source) == 1


def test_count_fraction_fields():
    """Fields annotated with Fraction are counted."""
    source = (
        "from dataclasses import dataclass\n"
        "from fractions import Fraction\n"
        "@dataclass\n"
        "class X:\n"
        "    a: Fraction\n"
        "    b: int\n"
        "    c: Fraction\n"
    )
    tree = __import__("ast").parse(source)
    assert _count_fraction_fields(tree) == 2


def test_measure_domain_depth_fraction():
    """depth_score is a Fraction string with denominator 1000."""
    tmp = REPO_ROOT / "src" / "domains" / "d_test_depth"
    tmp.mkdir(exist_ok=True)
    (tmp / "invariants.py").write_text(
        "def run_all_invariants():\n"
        "    return 'FAIL: test'\n"
        "def check_x(data):\n"
        "    success = data.a > 0\n"
    )
    (tmp / "implementation.py").write_text(
        "from dataclasses import dataclass\n"
        "from fractions import Fraction\n"
        "@dataclass\n"
        "class X:\n"
        "    a: Fraction\n"
    )
    data = measure_domain_depth(tmp, {"d_test_depth": 1})
    score_str = data["depth_score"]
    num, den = score_str.split("/")
    assert int(den) == 1000
    assert data["has_run_all"] is True
    assert data["has_failing_test"] is True
    assert data["fraction_field_count"] == 1
    assert data["computational_check_count"] == 1
    # Cleanup
    for f in ["invariants.py", "implementation.py"]:
        (tmp / f).unlink(missing_ok=True)
    tmp.rmdir()


def test_run_depth_measurement_returns_tuple():
    """run_depth_measurement returns (bool, dict)."""
    passed, result = run_depth_measurement()
    assert isinstance(passed, bool)
    assert isinstance(result, dict)
    assert "domains" in result
    assert "summary" in result
    summary = result["summary"]
    assert "mean_depth" in summary
    assert "polymathic_check" in summary


def test_run_depth_measurement_json_written():
    """run_depth_measurement persists JSON report."""
    out = REPO_ROOT / "audit" / "DEPTH_REPORT.json"
    run_depth_measurement(output_path=out)
    assert out.exists()
    import json
    data = json.loads(out.read_text())
    assert "domains" in data
    assert "summary" in data

"""tests/test_tautology_detector.py — Tests for the tautology detector.

PR: #8a
Standard: Yeshua / Glass-Box / Orthogonal Engineering
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from audit.tautology_detector import (
    CheckClassification,
    DomainClassification,
    _classify_function,
    _is_computational_expr,
    run_tautology_audit,
)


def test_check_classification_to_dict():
    """CheckClassification.to_dict() returns expected keys."""
    c = CheckClassification(name="check_x", check_type="computational")
    d = c.to_dict()
    assert d["name"] == "check_x"
    assert d["type"] == "computational"


def test_domain_classification_domain_type():
    """DomainClassification.domain_type aggregates correctly."""
    dc = DomainClassification(domain="d_test")
    assert dc.domain_type == "tautological"  # empty set == tautological
    dc.checks.append(CheckClassification(name="c1", check_type="tautological"))
    assert dc.domain_type == "tautological"
    dc.checks.append(CheckClassification(name="c2", check_type="computational"))
    assert dc.domain_type == "mixed"
    dc2 = DomainClassification(domain="d_test2")
    dc2.checks.append(CheckClassification(name="c1", check_type="computational"))
    assert dc2.domain_type == "computational"


def test_is_computational_expr():
    """_is_computational_expr distinguishes raw data from computation."""
    code = "data.x"
    node = ast.parse(code, mode="eval").body
    assert not _is_computational_expr(node)

    code2 = "data.x + 1"
    node2 = ast.parse(code2, mode="eval").body
    assert _is_computational_expr(node2)


def test_classify_function_tautological():
    """A pure echo is tautological."""
    source = (
        "def check_x(data):\n"
        "    success = data.valid\n"
    )
    tree = ast.parse(source)
    func = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    assert _classify_function(func) == "tautological"


def test_classify_function_computational():
    """Arithmetic makes a check computational."""
    source = (
        "def check_y(data):\n"
        "    success = data.a + data.b > 0\n"
    )
    tree = ast.parse(source)
    func = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    assert _classify_function(func) == "computational"


def test_run_tautology_audit_returns_tuple():
    """run_tautology_audit returns (bool, dict)."""
    ok, result = run_tautology_audit()
    assert isinstance(ok, bool)
    assert isinstance(result, dict)
    assert "total_checks" in result
    assert "tautological_ratio" in result

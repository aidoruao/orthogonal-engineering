"""tests/test_scope_audit.py — Tests for the domain scope audit tooling.

PR: #8a
Standard: Yeshua / Glass-Box / Orthogonal Engineering
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from audit.scope_audit import (
    DomainScopeReport,
    audit_domain,
    run_scope_audit,
)

REPO_ROOT = Path(__file__).parent.parent


def test_domain_scope_report_to_dict():
    """DomainScopeReport.to_dict() returns all expected keys."""
    report = DomainScopeReport(domain="d_test")
    d = report.to_dict()
    assert d["domain"] == "d_test"
    assert d["passed"] is True
    assert "missing_files" in d
    assert "missing_functions" in d
    assert "stub_functions" in d
    assert "float_violations" in d
    assert "notes" in d


def test_audit_domain_missing_files():
    """audit_domain flags missing required files."""
    # Use a non-domain dir to simulate incompleteness
    tmp = REPO_ROOT / "src" / "domains" / "d_test_scope"
    tmp.mkdir(exist_ok=True)
    (tmp / "__init__.py").write_text("")
    # Missing invariants.py and implementation.py
    report = audit_domain(tmp)
    assert not report.passed
    assert "invariants.py" in report.missing_files
    assert "implementation.py" in report.missing_files
    # Cleanup
    (tmp / "__init__.py").unlink(missing_ok=True)
    tmp.rmdir()


def test_audit_domain_no_float():
    """audit_domain detects float() calls."""
    tmp = REPO_ROOT / "src" / "domains" / "d_test_scope"
    tmp.mkdir(exist_ok=True)
    (tmp / "__init__.py").write_text("")
    (tmp / "invariants.py").write_text(
        "def run_all_invariants(): pass\n"
        "def check_x(data):\n    success = float(1.0)\n"
    )
    (tmp / "implementation.py").write_text(
        "from dataclasses import dataclass\n@dataclass\nclass X:\n    pass\n"
    )
    report = audit_domain(tmp)
    assert "invariants.py" in report.float_violations
    # Cleanup
    for f in ["__init__.py", "invariants.py", "implementation.py"]:
        (tmp / f).unlink(missing_ok=True)
    tmp.rmdir()


def test_run_scope_audit_returns_tuple():
    """run_scope_audit returns (bool, ProofObject)."""
    passed, proof = run_scope_audit()
    assert isinstance(passed, bool)
    assert hasattr(proof, "conclusion")
    assert hasattr(proof, "proof_hash")
    assert proof.is_valid()


def test_run_scope_audit_json_written():
    """run_scope_audit persists JSON report."""
    out = REPO_ROOT / "audit" / "SCOPE_AUDIT_REPORT.json"
    run_scope_audit(output_path=out)
    assert out.exists()
    import json
    data = json.loads(out.read_text())
    assert "total_domains" in data
    assert "complete_domains" in data
    assert "incomplete_domains" in data

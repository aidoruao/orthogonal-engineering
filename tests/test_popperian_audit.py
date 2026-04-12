"""
tests/test_popperian_audit.py — Tests for the Popperian audit tooling.

PR: #118
Standard: Yeshua / Glass-Box / Orthogonal Engineering
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from audit.popperian_audit import (
    AuditResult,
    DomainAuditReport,
    run_popperian_audit,
)

REPO_ROOT = Path(__file__).parent.parent
DOMAINS_DIR = REPO_ROOT / "src" / "domains"


def test_audit_result_to_dict():
    """AuditResult.to_dict() returns all expected keys."""
    result = AuditResult(
        domain="d_test",
        function_name="check_something",
        passed=True,
    )
    d = result.to_dict()
    assert d["domain"] == "d_test"
    assert d["function"] == "check_something"
    assert d["passed"] is True
    assert "missing_falsifies_if" in d
    assert "float_violations" in d
    assert "notes" in d


def test_domain_audit_report_to_dict():
    """DomainAuditReport.to_dict() returns all expected keys."""
    report = DomainAuditReport(
        domain="d_test",
        invariants_path="src/domains/d_test/invariants.py",
        passed=True,
    )
    d = report.to_dict()
    assert d["domain"] == "d_test"
    assert d["passed"] is True
    assert "failure_count" in d
    assert "findings" in d


def test_domain_audit_report_failure_count():
    """DomainAuditReport.failure_count counts failing findings."""
    report = DomainAuditReport(
        domain="d_test",
        invariants_path="src/domains/d_test/invariants.py",
        passed=False,
        findings=[
            AuditResult(domain="d_test", function_name="f1", passed=False),
            AuditResult(domain="d_test", function_name="f2", passed=True),
        ],
    )
    assert report.failure_count == 1


def test_run_popperian_audit_returns_list():
    """run_popperian_audit returns a non-empty list of reports."""
    reports = run_popperian_audit()
    assert isinstance(reports, list)
    assert len(reports) > 0


def test_all_domains_pass_popperian_audit():
    """All domain invariants pass the Popperian compliance check."""
    reports = run_popperian_audit()
    failures = [r for r in reports if not r.passed]
    failure_details = [
        f"{r.domain}: {[f.function_name for f in r.findings if not f.passed]}"
        for r in failures
    ]
    assert failures == [], (
        f"Popperian audit failures:\n" + "\n".join(failure_details)
    )


def test_run_popperian_audit_domain_filter():
    """Domain filter narrows audit to a single domain."""
    reports = run_popperian_audit(domain_filter="d_aerospace")
    assert len(reports) == 1
    assert reports[0].domain == "d_aerospace"


def test_run_popperian_audit_nonexistent_domain_filter():
    """Filtering for a nonexistent domain returns empty list."""
    reports = run_popperian_audit(domain_filter="d_does_not_exist")
    assert reports == []

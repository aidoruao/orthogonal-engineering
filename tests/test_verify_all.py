"""tests/test_verify_all.py — Tests for the unified verification wrapper.

PR: #8a
Standard: Yeshua / Glass-Box / Orthogonal Engineering
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.verify_all import (
    CheckResult,
    _run_cmd,
    run_all_checks,
)


def test_check_result_dataclass():
    """CheckResult stores name, status, and details."""
    r = CheckResult(name="X", status="PASS", details="ok")
    assert r.name == "X"
    assert r.status == "PASS"
    assert r.details == "ok"


def test_run_cmd_success():
    """_run_cmd returns 0 for a successful command."""
    rc, out, err = _run_cmd(["python3", "-c", "print('hello')"])
    assert rc == 0
    assert "hello" in out


def test_run_cmd_failure():
    """_run_cmd returns non-zero for a failing command."""
    rc, out, err = _run_cmd(["python3", "-c", "import sys; sys.exit(1)"])
    assert rc == 1


def test_run_all_checks_returns_list():
    """run_all_checks returns a list of CheckResult objects."""
    with patch("tools.verify_all._run_cmd") as mock_run:
        mock_run.return_value = (0, "ok", "")
        results = run_all_checks()
        assert isinstance(results, list)
        assert len(results) == 10
        for r in results:
            assert isinstance(r, CheckResult)
            assert r.status in ("PASS", "FAIL", "STALE", "INFO", "SKIP")


def test_check_names_present():
    """All expected check names are present in results."""
    with patch("tools.verify_all._run_cmd") as mock_run:
        mock_run.return_value = (0, "ok", "")
        results = run_all_checks()
        names = {r.name for r in results}
        expected = {
            "Feed chain",
            "Popperian audit",
            "Standards",
            "Tests",
            "Scope audit",
            "Tautology",
            "Depth measurement",
            "Anti-nominalism",
            "Merkle verify",
            "Scope reduction",
        }
        assert expected.issubset(names)

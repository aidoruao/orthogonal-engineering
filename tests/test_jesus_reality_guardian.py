"""
tests/test_jesus_reality_guardian.py — Tests for JesusRealityTheorem.prove()

Verifies that prove() runs real Yeshua enforcement rather than returning True
unconditionally.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.2
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from JESUS_REALITY_GUARDIAN import JesusRealityTheorem
from yeshua.enforcement import EnforcementReport


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_passing_report() -> EnforcementReport:
    """Return an EnforcementReport with no violations."""
    report = EnforcementReport()
    report.add_pass("no_float_in_core")
    report.add_pass("no_nondeterministic_iteration")
    report.add_pass("dependencies_declared")
    return report


def _make_failing_report() -> EnforcementReport:
    """Return an EnforcementReport with one violation."""
    report = EnforcementReport()
    report.add_violation("no_float_in_core", "some/file.py", "Float at line 1")
    return report


# ---------------------------------------------------------------------------
# Tests: return type and structure
# ---------------------------------------------------------------------------


def test_prove_returns_tuple():
    """prove() must return a 2-tuple (bool, str)."""
    result = JesusRealityTheorem.prove()
    assert isinstance(result, tuple)
    assert len(result) == 2
    success, detail = result
    assert isinstance(success, bool)
    assert isinstance(detail, str)


def test_prove_can_return_false():
    """prove() must be capable of returning False — if not it is not a proof."""
    with patch("JESUS_REALITY_GUARDIAN.JesusRealityTheorem._AXIOMS_PATH",
               new=Path("nonexistent_axioms.json")):
        success, detail = JesusRealityTheorem.prove()
    assert success is False
    data = json.loads(detail)
    assert "error" in data


def test_prove_false_when_enforcement_fails():
    """prove() returns (False, json_details) when enforcement finds violations."""
    with patch("yeshua.enforcement.run_yeshua_enforcement",
               return_value=_make_failing_report()):
        success, detail = JesusRealityTheorem.prove()

    assert success is False
    data = json.loads(detail)
    assert "violations" in data
    assert "proof_hash" in data
    assert len(data["proof_hash"]) == 64  # SHA-256 hex digest


def test_prove_true_when_enforcement_passes():
    """prove() returns (True, YESHUA-ENFORCEMENT-PROOF:<hash>) when all checks pass."""
    with patch("yeshua.enforcement.run_yeshua_enforcement",
               return_value=_make_passing_report()):
        success, detail = JesusRealityTheorem.prove()

    assert success is True
    assert detail.startswith("YESHUA-ENFORCEMENT-PROOF:")
    proof_hash = detail.split(":", 1)[1]
    assert len(proof_hash) == 64
    assert all(c in "0123456789abcdef" for c in proof_hash)


def test_prove_hash_is_sha256_of_report():
    """The proof_hash must be SHA-256 of the serialized enforcement report."""
    import hashlib

    passing_report = _make_passing_report()
    with patch("yeshua.enforcement.run_yeshua_enforcement",
               return_value=passing_report):
        success, detail = JesusRealityTheorem.prove()

    assert success is True
    proof_hash = detail.split(":", 1)[1]

    # Reconstruct what prove() hashes
    axioms_path = JesusRealityTheorem._AXIOMS_PATH
    import json as _json
    with axioms_path.open(encoding="utf-8") as fh:
        axioms_data = _json.load(fh)
    report_dict = passing_report.to_dict()
    report_dict["axioms_verified"] = len(axioms_data["axioms"])
    report_dict["standard"] = axioms_data.get("standard", "Yeshua")
    expected_hash = hashlib.sha256(
        _json.dumps(report_dict, sort_keys=True).encode()
    ).hexdigest()
    assert proof_hash == expected_hash


def test_prove_does_not_unconditionally_return_true():
    """prove() must NOT hardcode True — demonstrated by making enforcement fail."""
    fail_report = _make_failing_report()
    with patch("yeshua.enforcement.run_yeshua_enforcement",
               return_value=fail_report):
        success, _ = JesusRealityTheorem.prove()
    assert success is False, "prove() must return False when enforcement fails"


def test_prove_axioms_file_required():
    """prove() returns False when eight_axioms.json is missing."""
    with patch.object(JesusRealityTheorem, "_AXIOMS_PATH",
                      new=Path("/nonexistent/path/eight_axioms.json")):
        success, detail = JesusRealityTheorem.prove()
    assert success is False
    data = json.loads(detail)
    assert "error" in data


def test_prove_axioms_must_be_eight():
    """prove() returns False if the axioms file does not contain exactly 8 axioms."""
    real_exists = JesusRealityTheorem._AXIOMS_PATH.exists()
    if not real_exists:
        pytest.skip("eight_axioms.json not present; skipping")

    # Use a temp file with fewer axioms
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump({"standard": "Yeshua", "axioms": [{"number": 1}, {"number": 2}]}, tmp)
        tmp_path = tmp.name
    try:
        with patch.object(JesusRealityTheorem, "_AXIOMS_PATH", new=Path(tmp_path)):
            success, detail = JesusRealityTheorem.prove()
        assert success is False
        data = json.loads(detail)
        assert "error" in data
    finally:
        os.unlink(tmp_path)

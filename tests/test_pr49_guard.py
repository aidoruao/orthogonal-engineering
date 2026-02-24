#!/usr/bin/env python3
"""
tests/test_pr49_guard.py — Unit tests for PR #49 Glass-Box Guard

Covers:
  1. Mass-change detection
  2. Forbidden-primitive pattern detection
  3. Logic-bomb pattern detection
  4. Consent log parsing, validation, and scope matching
  5. Deterministic outputs (same input → same output)
  6. Manifest generation

Author: Orthogonal Engineering
PR: #49
Standard: Yeshua / Glass-Box
Version: 49.0.0
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, List
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from automation.pr49_guard import (
    CONSENT_REQUIRED_FIELDS,
    FORBIDDEN_PATTERNS,
    LOGIC_BOMB_PATTERNS,
    _consent_covers,
    _is_executable_path,
    _load_consent_log,
    _scan_patterns,
    check_mass_change,
    generate_manifest,
    sha256_of,
    validate_consent_log,
    _changed_paths_covered_by_consent,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_consent_record(
    authoriser: str = "@aidoruao",
    scope_glob: str = "**/*",
    rule_exceptions: list | None = None,
    justification: str = "test justification",
    extra: dict | None = None,
) -> dict:
    if rule_exceptions is None:
        rule_exceptions = ["mass_change"]
    justification_hash = hashlib.sha256(justification.encode()).hexdigest()
    scope_hash = hashlib.sha256(scope_glob.encode()).hexdigest()
    rec = {
        "authoriser": authoriser,
        "scope_glob": scope_glob,
        "rule_exceptions": rule_exceptions,
        "justification_hash": justification_hash,
        "scope_hash": scope_hash,
    }
    if extra:
        rec.update(extra)
    return rec


def _write_jsonl(path: Path, records: list) -> None:
    lines = []
    for rec in records:
        if isinstance(rec, str):
            lines.append(rec)
        else:
            lines.append(json.dumps(rec))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Mass-change detection
# ---------------------------------------------------------------------------


class TestMassChangeDetection:
    def test_no_violation_below_thresholds(self):
        changed = [f"file{i}.py" for i in range(5)]
        total = 200
        violations: List[Dict] = []
        check_mass_change(changed, total, consent_records=[], violations=violations)
        assert violations == []

    def test_violation_exceeds_file_count(self):
        changed = [f"file{i}.py" for i in range(100)]
        total = 200
        violations: List[Dict] = []
        check_mass_change(changed, total, consent_records=[], violations=violations)
        assert len(violations) == 1
        assert "Mass change detected" in violations[0]["detail"]
        assert violations[0]["gate"] == 1

    def test_violation_exceeds_pct(self):
        changed = [f"file{i}.py" for i in range(35)]
        total = 100
        violations: List[Dict] = []
        check_mass_change(changed, total, consent_records=[], violations=violations)
        assert len(violations) == 1
        assert "Mass change detected" in violations[0]["detail"]

    def test_consent_bypasses_mass_change(self):
        changed = [f"docs/file{i}.md" for i in range(100)]
        total = 200
        rec = _make_consent_record(scope_glob="docs/**", rule_exceptions=["mass_change"])
        violations: List[Dict] = []
        check_mass_change(changed, total, consent_records=[rec], violations=violations)
        assert violations == []

    def test_consent_wrong_rule_does_not_bypass(self):
        changed = [f"file{i}.py" for i in range(100)]
        total = 200
        rec = _make_consent_record(scope_glob="**/*", rule_exceptions=["other_rule"])
        violations: List[Dict] = []
        check_mass_change(changed, total, consent_records=[rec], violations=violations)
        assert len(violations) == 1

    def test_consent_wrong_glob_does_not_bypass(self):
        # Consent only covers docs/, but changes are in src/
        changed = [f"src/file{i}.py" for i in range(100)]
        total = 200
        rec = _make_consent_record(scope_glob="docs/**", rule_exceptions=["mass_change"])
        violations: List[Dict] = []
        check_mass_change(changed, total, consent_records=[rec], violations=violations)
        assert len(violations) == 1

    def test_exactly_at_threshold_no_violation(self):
        """Exactly at threshold (not exceeding) — should pass."""
        from automation.pr49_guard import MASS_CHANGE_FILE_THRESHOLD
        changed = [f"file{i}.py" for i in range(MASS_CHANGE_FILE_THRESHOLD)]
        total = 1000
        violations: List[Dict] = []
        check_mass_change(changed, total, consent_records=[], violations=violations)
        assert violations == []

    def test_deterministic_output(self):
        """Same input must produce same violation detail."""
        changed = [f"file{i}.py" for i in range(100)]
        total = 200
        v1: List[Dict] = []
        v2: List[Dict] = []
        check_mass_change(changed, total, consent_records=[], violations=v1)
        check_mass_change(changed, total, consent_records=[], violations=v2)
        assert v1 == v2


# ---------------------------------------------------------------------------
# 2. Forbidden-primitive detection
# ---------------------------------------------------------------------------


class TestForbiddenPrimitives:
    def _scan(self, content: str, path: str = "automation/evil.py") -> List[Dict]:
        violations: List[Dict] = []
        _scan_patterns(path, content, FORBIDDEN_PATTERNS, gate=2, violations=violations)
        return violations

    def test_rm_rf_root_detected(self):
        v = self._scan("os.system('rm -rf /')", path="automation/x.sh")
        assert len(v) >= 1
        assert any("rm -rf" in viol["detail"] for viol in v)

    def test_shutil_rmtree_root_detected(self):
        v = self._scan("shutil.rmtree('/')", path="automation/x.py")
        assert len(v) >= 1
        assert any("shutil.rmtree" in viol["detail"] for viol in v)

    def test_fork_bomb_detected(self):
        v = self._scan(":(){:|:&};:", path="scripts/x.sh")
        assert len(v) >= 1
        assert any("fork-bomb" in viol["detail"] for viol in v)

    def test_safe_code_no_violation(self):
        safe = "import os\nprint(os.getcwd())\n"
        v = self._scan(safe)
        assert v == []

    def test_find_delete_detected(self):
        v = self._scan("find . -name '*.pyc' -delete", path="scripts/clean.sh")
        assert len(v) >= 1
        assert any("-delete" in viol["detail"] for viol in v)

    def test_subprocess_rm_detected(self):
        v = self._scan(
            "subprocess.run('rm -rf /tmp/data', shell=True)", path="automation/x.py"
        )
        assert len(v) >= 1

    def test_deterministic_scan(self):
        content = "shutil.rmtree('/')"
        v1 = self._scan(content, "automation/x.py")
        v2 = self._scan(content, "automation/x.py")
        assert v1 == v2

    def test_test_file_excluded_from_scan(self):
        """Test files must not trigger guard even if they contain pattern strings."""
        assert not _is_executable_path("tests/test_pr49_guard.py")
        assert not _is_executable_path("tests/test_foo.py")
        assert not _is_executable_path("adversarial_tests/evil.py")

    def test_automation_file_is_executable(self):
        assert _is_executable_path("automation/pr49_guard.py")
        assert _is_executable_path("scripts/deploy.sh")
        assert _is_executable_path(".github/workflows/pr49_guard.yml")


# ---------------------------------------------------------------------------
# 3. Logic-bomb detection
# ---------------------------------------------------------------------------


class TestLogicBombs:
    def _scan(self, content: str, path: str = "automation/bomb.py") -> List[Dict]:
        violations: List[Dict] = []
        import re
        flags = re.MULTILINE | re.DOTALL
        for pattern, label in LOGIC_BOMB_PATTERNS:
            if re.search(pattern, content, flags):
                from automation.pr49_guard import _violation
                violations.append(_violation(3, path, label))
        return violations

    def test_time_gated_rm_detected(self):
        content = "if time.time() > 9999999999:\n    os.system('rm -rf /')\n"
        v = self._scan(content)
        assert len(v) >= 1
        assert any("time" in viol["detail"] for viol in v)

    def test_datetime_gated_rmtree_detected(self):
        content = "if datetime.now() > threshold:\n    shutil.rmtree('/data')\n"
        v = self._scan(content)
        assert len(v) >= 1

    def test_safe_code_no_logic_bomb(self):
        content = "if condition:\n    print('hello')\n"
        v = self._scan(content)
        assert v == []


# ---------------------------------------------------------------------------
# 4. Consent log parsing and validation
# ---------------------------------------------------------------------------


class TestConsentLogParsing:
    def test_empty_log_returns_empty(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            p = Path(f.name)
        p.write_text("", encoding="utf-8")
        records, errors = _load_consent_log(p)
        assert records == []
        assert errors == []

    def test_comment_lines_skipped(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            f.write("# This is a comment\n")
            p = Path(f.name)
        records, errors = _load_consent_log(p)
        assert records == []
        assert errors == []

    def test_valid_record_parsed(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            rec = _make_consent_record()
            f.write(json.dumps(rec) + "\n")
            p = Path(f.name)
        records, errors = _load_consent_log(p)
        assert len(records) == 1
        assert errors == []

    def test_invalid_json_produces_error(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            f.write("{invalid json}\n")
            p = Path(f.name)
        records, errors = _load_consent_log(p)
        assert records == []
        assert len(errors) == 1

    def test_missing_required_fields_produces_violation(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            incomplete = {"authoriser": "@aidoruao"}  # missing fields
            f.write(json.dumps(incomplete) + "\n")
            p = Path(f.name)
        violations: List[Dict] = []
        valid = validate_consent_log(p, changed=[], violations=violations)
        assert len(violations) == 1
        assert "missing required fields" in violations[0]["detail"]
        assert valid == []

    def test_all_required_fields_passes_validation(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            rec = _make_consent_record()
            f.write(json.dumps(rec) + "\n")
            p = Path(f.name)
        violations: List[Dict] = []
        valid = validate_consent_log(p, changed=[], violations=violations)
        assert violations == []
        assert len(valid) == 1

    def test_missing_log_file_returns_empty(self):
        p = Path("/tmp/nonexistent_consent_log_99999.jsonl")
        records, errors = _load_consent_log(p)
        assert records == []
        assert errors == []


# ---------------------------------------------------------------------------
# 5. Scope matching
# ---------------------------------------------------------------------------


class TestScopeMatching:
    def test_glob_matches_file(self):
        rec = _make_consent_record(scope_glob="docs/**")
        assert _consent_covers(rec, "docs/README.md")

    def test_glob_does_not_match_unrelated(self):
        rec = _make_consent_record(scope_glob="docs/**")
        assert not _consent_covers(rec, "src/main.py")

    def test_wildcard_matches_all(self):
        rec = _make_consent_record(scope_glob="**/*")
        assert _consent_covers(rec, "src/main.py")
        assert _consent_covers(rec, "docs/guide.md")

    def test_covered_by_consent(self):
        changed = ["docs/a.md", "docs/b.md"]
        rec = _make_consent_record(scope_glob="docs/**", rule_exceptions=["mass_change"])
        all_covered, uncovered = _changed_paths_covered_by_consent(
            [rec], changed, "mass_change"
        )
        assert all_covered
        assert uncovered == []

    def test_partially_covered(self):
        changed = ["docs/a.md", "src/main.py"]
        rec = _make_consent_record(scope_glob="docs/**", rule_exceptions=["mass_change"])
        all_covered, uncovered = _changed_paths_covered_by_consent(
            [rec], changed, "mass_change"
        )
        assert not all_covered
        assert "src/main.py" in uncovered

    def test_empty_changed_is_always_covered(self):
        rec = _make_consent_record(scope_glob="docs/**", rule_exceptions=["mass_change"])
        all_covered, uncovered = _changed_paths_covered_by_consent(
            [rec], [], "mass_change"
        )
        assert all_covered
        assert uncovered == []


# ---------------------------------------------------------------------------
# 6. Manifest generation (determinism)
# ---------------------------------------------------------------------------


class TestManifestGeneration:
    def test_manifest_has_version(self):
        manifest = generate_manifest()
        assert manifest["version"] == "49.0.0"

    def test_manifest_has_files(self):
        manifest = generate_manifest()
        assert "files" in manifest
        assert isinstance(manifest["files"], dict)

    def test_manifest_deterministic(self):
        m1 = generate_manifest()
        m2 = generate_manifest()
        assert m1 == m2

    def test_sha256_deterministic(self):
        p = Path(__file__)
        h1 = sha256_of(p)
        h2 = sha256_of(p)
        assert h1 == h2
        assert len(h1) == 64  # hex SHA-256

    def test_sha256_correct(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"hello world")
            p = Path(f.name)
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert sha256_of(p) == expected


# ---------------------------------------------------------------------------
# 7. Required fields constant
# ---------------------------------------------------------------------------


class TestRequiredFields:
    def test_all_required_fields_present(self):
        assert CONSENT_REQUIRED_FIELDS == {
            "authoriser",
            "scope_glob",
            "rule_exceptions",
            "justification_hash",
            "scope_hash",
        }

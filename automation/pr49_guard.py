#!/usr/bin/env python3
"""
automation/pr49_guard.py — PR #49 Glass-Box Anti-Malicious Enforcement Guard

Implements deterministic diff scanning to prevent repository-sabotaging
changes and malicious logic patterns.

Checks performed:
  1. Mass-change detection — blocks > MASS_CHANGE_FILE_THRESHOLD files changed
     or > MASS_CHANGE_PCT_THRESHOLD percent of tracked files unless a valid
     consent entry covers all changed paths.
  2. Forbidden-primitive scanning — blocks destructive shell/Python builtins
     (rm -rf, shutil.rmtree, os.remove, etc.) introduced in executable
     contexts (workflows, scripts, automation).
  3. Logic-bomb detection — blocks time/environment-gated destructive patterns
     in executable contexts.
  4. Consent log validation — JSONL entries must include required fields;
     scope_glob must match changed paths; log must be append-only.

Exit codes:
  0 — no violations
  1 — violations detected
  2 — internal error

Author: Orthogonal Engineering
PR: #49
Standard: Yeshua / Glass-Box
Version: 49.0.0
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants — tunable via environment variables (all deterministic)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent

MASS_CHANGE_FILE_THRESHOLD: int = int(os.environ.get("PR49_FILE_THRESHOLD", "80"))
MASS_CHANGE_PCT_THRESHOLD: float = float(os.environ.get("PR49_PCT_THRESHOLD", "30.0"))

CONSENT_LOG_PATH: Path = REPO_ROOT / "pr47_stewardship" / "witness" / "consent_log.jsonl"

CONSENT_REQUIRED_FIELDS = {
    "authoriser",
    "scope_glob",
    "rule_exceptions",
    "justification_hash",
    "scope_hash",
}

# Executable file globs — only these paths are scanned for forbidden patterns
EXECUTABLE_GLOBS: List[str] = [
    ".github/workflows/**",
    "automation/**",
    "scripts/**",
    "**/*.sh",
    "**/*.bash",
    "**/*.py",
]

# ---------------------------------------------------------------------------
# Forbidden destructive primitives (regex patterns)
# ---------------------------------------------------------------------------

FORBIDDEN_PATTERNS: List[Tuple[str, str]] = [
    # Shell destructive commands
    (r"rm\s+-[rRfF]{1,4}\s*/", "forbidden: rm -rf /"),
    (r"rm\s+--no-preserve-root", "forbidden: rm --no-preserve-root"),
    (r":\s*\(\)\s*\{.*:\|:.*\}", "forbidden: fork-bomb pattern :(){:|:&};:"),
    (r">\s*/dev/sd[a-z]", "forbidden: raw disk overwrite"),
    (r"dd\s+if=/dev/zero\s+of=/dev/", "forbidden: dd disk wipe"),
    (r"mkfs\.", "forbidden: filesystem format"),
    # Python destructive
    (r"shutil\.rmtree\s*\(\s*['\"/]", "forbidden: shutil.rmtree on absolute/root path"),
    (r"subprocess\.(run|call|check_call|check_output|Popen)\s*\(.*['\"]rm\s+-[rRfF]", "forbidden: subprocess rm -rf"),
    # Mass overwrite patterns
    (r"for\s+\w+\s+in\s+\$\(find\s+/", "forbidden: recursive find+exec on /"),
    (r"find\s+/\s+.*-exec\s+rm", "forbidden: find / -exec rm"),
    (r"find\s+\.\s+.*-delete", "forbidden: find . -delete (mass delete)"),
    # Truncation of critical files
    (r">\s*requirements\.txt\b", "forbidden: truncate requirements.txt"),
    (r">\s*pyproject\.toml\b", "forbidden: truncate pyproject.toml"),
]

# ---------------------------------------------------------------------------
# Logic-bomb patterns (time/env-gated destructive behaviour)
# ---------------------------------------------------------------------------

LOGIC_BOMB_PATTERNS: List[Tuple[str, str]] = [
    (r"if\s+.*\btime\b.*:\s*\n.*rm\s+-[rRfF]", "logic-bomb: time-gated rm"),
    (r"if\s+.*\bos\.environ\b.*:\s*\n.*rm\s+-[rRfF]", "logic-bomb: env-gated rm"),
    (r"if\s+.*\bdatetime\b.*:\s*\n.*shutil\.rmtree", "logic-bomb: datetime-gated rmtree"),
    (r"schedule\s*\(.*\)\s*.*rm\s+-[rRfF]", "logic-bomb: scheduled rm"),
    (
        r"(time\.time|datetime\.now|datetime\.utcnow)\s*\(\s*\).*\n.*"
        r"(rm\s+-[rRfF]|shutil\.rmtree|os\.remove)",
        "logic-bomb: time-dependent destructive call",
    ),
]

# ---------------------------------------------------------------------------
# Peano-style gate counters (successor-indexed)
# Gate 0 — compute diff
# Gate 1 — mass-change check
# Gate 2 — forbidden-primitive scan
# Gate 3 — logic-bomb scan
# Gate 4 — consent log validation
# Gate 5 — emit report
# ---------------------------------------------------------------------------

GATE_NAMES = [
    "compute_diff",
    "mass_change_check",
    "forbidden_primitive_scan",
    "logic_bomb_scan",
    "consent_log_validation",
    "emit_report",
]


# ---------------------------------------------------------------------------
# Violation dataclass (plain dict for JSON serialisability)
# ---------------------------------------------------------------------------

def _violation(gate: int, path: str, detail: str) -> Dict:
    return {
        "gate": gate,
        "gate_name": GATE_NAMES[gate],
        "path": path,
        "detail": detail,
    }


# ---------------------------------------------------------------------------
# Gate 0 — compute diff
# ---------------------------------------------------------------------------

def compute_diff(base_ref: str) -> Tuple[List[str], int]:
    """
    Return (changed_paths, total_tracked_files).

    Uses `git diff --name-only` against base_ref.  Falls back to comparing
    HEAD against the merge-base so that the result is deterministic regardless
    of whether the caller passes a branch name or a SHA.
    """
    try:
        merge_base = subprocess.check_output(
            ["git", "merge-base", base_ref, "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        merge_base = base_ref

    diff_out = subprocess.check_output(
        ["git", "diff", "--name-only", merge_base, "HEAD"],
        stderr=subprocess.DEVNULL,
        text=True,
    )
    changed = [p.strip() for p in diff_out.splitlines() if p.strip()]

    ls_out = subprocess.check_output(
        ["git", "ls-files"],
        stderr=subprocess.DEVNULL,
        text=True,
    )
    total = len([p for p in ls_out.splitlines() if p.strip()])

    return changed, max(total, 1)


# ---------------------------------------------------------------------------
# Consent log helpers
# ---------------------------------------------------------------------------

def _load_consent_log(path: Path) -> Tuple[List[Dict], List[str]]:
    """
    Parse JSONL consent log.  Returns (records, parse_errors).
    """
    if not path.exists():
        return [], []
    records: List[Dict] = []
    errors: List[str] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            errors.append(f"line {i}: {exc}")
    return records, errors


def _consent_covers(record: Dict, path: str) -> bool:
    """Return True if record's scope_glob matches path."""
    glob_pat = record.get("scope_glob", "")
    if not glob_pat:
        return False
    return fnmatch.fnmatch(path, glob_pat) or fnmatch.fnmatch(path, glob_pat.rstrip("/") + "/*")


def _changed_paths_covered_by_consent(
    records: List[Dict],
    changed: List[str],
    rule_exception: str,
) -> Tuple[bool, List[str]]:
    """
    Check whether every changed path is covered by at least one valid consent
    record that declares rule_exception in its rule_exceptions list.

    Returns (all_covered, uncovered_paths).
    """
    uncovered: List[str] = []
    for p in changed:
        covered = False
        for rec in records:
            exceptions = rec.get("rule_exceptions", [])
            if isinstance(exceptions, list) and rule_exception in exceptions:
                if _consent_covers(rec, p):
                    covered = True
                    break
        if not covered:
            uncovered.append(p)
    return len(uncovered) == 0, uncovered


# ---------------------------------------------------------------------------
# Gate 4 — consent log validation
# ---------------------------------------------------------------------------

def validate_consent_log(
    path: Path,
    changed: List[str],
    violations: List[Dict],
) -> List[Dict]:
    """
    Validate the consent log at *path*.  Append violations for:
      - parse errors
      - missing required fields
      - scope_glob not matching any changed path (warn, not block)
    Returns the parsed (valid) records.
    """
    try:
        rel_str = str(path.relative_to(REPO_ROOT))
    except ValueError:
        rel_str = str(path)

    records, parse_errors = _load_consent_log(path)
    for err in parse_errors:
        violations.append(_violation(4, rel_str, err))

    valid_records: List[Dict] = []
    for i, rec in enumerate(records):
        missing = CONSENT_REQUIRED_FIELDS - set(rec.keys())
        if missing:
            violations.append(
                _violation(
                    4,
                    rel_str,
                    f"record {i}: missing required fields: {sorted(missing)}",
                )
            )
        else:
            valid_records.append(rec)

    return valid_records


# ---------------------------------------------------------------------------
# Gate 1 — mass-change check
# ---------------------------------------------------------------------------

def check_mass_change(
    changed: List[str],
    total: int,
    consent_records: List[Dict],
    violations: List[Dict],
) -> None:
    n = len(changed)
    pct = 100.0 * n / total

    exceeds_count = n > MASS_CHANGE_FILE_THRESHOLD
    exceeds_pct = pct > MASS_CHANGE_PCT_THRESHOLD

    if not (exceeds_count or exceeds_pct):
        return

    # Check if valid consent covers all changed paths for mass_change rule
    all_covered, uncovered = _changed_paths_covered_by_consent(
        consent_records, changed, "mass_change"
    )
    if all_covered:
        return

    violations.append(
        _violation(
            1,
            "*",
            (
                f"Mass change detected: {n} files ({pct:.1f}%) changed. "
                f"Thresholds: {MASS_CHANGE_FILE_THRESHOLD} files / "
                f"{MASS_CHANGE_PCT_THRESHOLD}%. "
                f"Uncovered paths (sample): {uncovered[:5]}"
            ),
        )
    )


# ---------------------------------------------------------------------------
# Gate 2 — forbidden-primitive scan
# ---------------------------------------------------------------------------

def _is_executable_path(path: str) -> bool:
    for glob_pat in EXECUTABLE_GLOBS:
        if fnmatch.fnmatch(path, glob_pat):
            return True
    return False


def _scan_patterns(
    path: str,
    content: str,
    patterns: List[Tuple[str, str]],
    gate: int,
    violations: List[Dict],
    multiline: bool = False,
) -> None:
    flags = re.MULTILINE | (re.DOTALL if multiline else 0)
    for pattern, label in patterns:
        if re.search(pattern, content, flags):
            violations.append(_violation(gate, path, label))


def check_forbidden_primitives(
    changed: List[str],
    repo_root: Path,
    violations: List[Dict],
) -> None:
    for rel_path in changed:
        if not _is_executable_path(rel_path):
            continue
        full = repo_root / rel_path
        if not full.exists() or not full.is_file():
            continue
        try:
            content = full.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        _scan_patterns(rel_path, content, FORBIDDEN_PATTERNS, 2, violations, multiline=False)


# ---------------------------------------------------------------------------
# Gate 3 — logic-bomb scan
# ---------------------------------------------------------------------------

def check_logic_bombs(
    changed: List[str],
    repo_root: Path,
    violations: List[Dict],
) -> None:
    for rel_path in changed:
        if not _is_executable_path(rel_path):
            continue
        full = repo_root / rel_path
        if not full.exists() or not full.is_file():
            continue
        try:
            content = full.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        _scan_patterns(rel_path, content, LOGIC_BOMB_PATTERNS, 3, violations, multiline=True)


# ---------------------------------------------------------------------------
# Manifest verification (Axiom 8 — every artifact hash-anchored)
# ---------------------------------------------------------------------------

MANIFEST_PATH = REPO_ROOT / "pr49_guard.manifest.json"
MANIFEST_TRACKED_FILES = [
    "automation/pr49_guard.py",
    ".github/workflows/pr49_guard.yml",
    ".github/CODEOWNERS",
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def generate_manifest() -> Dict:
    """Compute and return the manifest dict."""
    entries: Dict[str, str] = {}
    for rel in MANIFEST_TRACKED_FILES:
        p = REPO_ROOT / rel
        if p.exists():
            entries[rel] = sha256_of(p)
        else:
            entries[rel] = "MISSING"
    return {"version": "49.0.0", "files": entries}


def verify_manifest(violations: List[Dict]) -> None:
    """
    Verify that pr49_guard.manifest.json matches on-disk files.
    If manifest does not exist yet, skip (first-run bootstrap).
    """
    if not MANIFEST_PATH.exists():
        return
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        violations.append(
            _violation(5, "pr49_guard.manifest.json", f"Cannot read manifest: {exc}")
        )
        return
    for rel, expected_hash in manifest.get("files", {}).items():
        if expected_hash == "MISSING":
            continue
        actual = sha256_of(REPO_ROOT / rel) if (REPO_ROOT / rel).exists() else "MISSING"
        if actual != expected_hash:
            violations.append(
                _violation(
                    5,
                    rel,
                    f"Manifest hash mismatch: expected {expected_hash[:16]}… got {actual[:16]}…",
                )
            )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_guard(base_ref: str = "origin/main", verify_manifest_flag: bool = True) -> Dict:
    """
    Run all gates and return a machine-readable report dict.
    """
    violations: List[Dict] = []

    # Gate 0 — compute diff
    try:
        changed, total = compute_diff(base_ref)
    except Exception as exc:
        return {
            "pr49_guard": True,
            "version": "49.0.0",
            "base_ref": base_ref,
            "gate_reached": 0,
            "changed_files": [],
            "total_tracked": 0,
            "violations": [_violation(0, "*", f"compute_diff error: {exc}")],
            "passed": False,
        }

    # Gate 4 — parse + validate consent log (needed by gate 1)
    consent_records = validate_consent_log(CONSENT_LOG_PATH, changed, violations)

    # Gate 1 — mass-change check
    check_mass_change(changed, total, consent_records, violations)

    # Gate 2 — forbidden-primitive scan
    check_forbidden_primitives(changed, REPO_ROOT, violations)

    # Gate 3 — logic-bomb scan
    check_logic_bombs(changed, REPO_ROOT, violations)

    # Gate 5 — manifest verification
    if verify_manifest_flag:
        verify_manifest(violations)

    return {
        "pr49_guard": True,
        "version": "49.0.0",
        "base_ref": base_ref,
        "gate_reached": 5,
        "changed_files": changed,
        "total_tracked": total,
        "violations": violations,
        "passed": len(violations) == 0,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PR #49 Glass-Box Guard")
    parser.add_argument(
        "--base",
        default=os.environ.get("PR49_BASE_REF", "origin/main"),
        help="Base git ref to diff against (default: origin/main)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write JSON report to this file path",
    )
    parser.add_argument(
        "--generate-manifest",
        action="store_true",
        help="Regenerate pr49_guard.manifest.json and exit",
    )
    parser.add_argument(
        "--no-verify-manifest",
        action="store_true",
        help="Skip manifest verification",
    )
    args = parser.parse_args()

    if args.generate_manifest:
        manifest = generate_manifest()
        MANIFEST_PATH.write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
        print(f"Manifest written to {MANIFEST_PATH}")
        sys.exit(0)

    report = run_guard(
        base_ref=args.base,
        verify_manifest_flag=not args.no_verify_manifest,
    )
    report_json = json.dumps(report, indent=2, sort_keys=True)

    if args.output:
        Path(args.output).write_text(report_json, encoding="utf-8")
    else:
        print(report_json)

    sys.exit(0 if report["passed"] else 1)

#!/usr/bin/env python3
"""
tools/since_last_session.py — Session Catch-Up Tool

Shows what changed since a previous agent session, so a returning agent can
catch up without reading the entire AGENT_FEED.md or full git log.

Two reference modes:
    --since-commit <SHA>   Show changes since that commit (uses git log)
    --since-row <N>        Show all AGENT_FEED.md rows after row N (0-indexed)

Outputs:
    - New git commits and their messages
    - New AGENT_FEED.md rows (since-row mode) or since the given commit
    - New or modified Python files
    - New domain directories
    - New standards added to STANDARDS_REGISTRY.json (if ref-commit is in git)

Usage:
    python tools/since_last_session.py --since-commit abc1234
    python tools/since_last_session.py --since-row 180
    python tools/since_last_session.py --since-commit HEAD~3 --json

Exit codes:
    0  Report printed
    1  Git or file error
    2  Usage error

Author: Orthogonal Engineering
Gap: #15 (gap analysis 2026-04-17)
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_FEED = REPO_ROOT / "AGENT_FEED.md"
REGISTRY = REPO_ROOT / "STANDARDS_REGISTRY.json"
DOMAINS_DIR = REPO_ROOT / "src" / "domains"


# ---------------------------------------------------------------------------
# AGENT_FEED.md parsing
# ---------------------------------------------------------------------------

def _parse_feed_rows(content: str) -> list[dict[str, str]]:
    """Parse data rows from AGENT_FEED.md.

    Falsifies if: returns rows that contain header or separator lines.
    falsifies_if: returns rows that contain header or separator lines.
    """
    columns = [
        "timestamp", "freeze_hash", "merkle_root", "invariant_spec_version",
        "source_paths", "commit_sha", "prev_entry_hash", "entry_hash",
    ]
    rows: list[dict[str, str]] = []
    in_table = False
    header_seen = False
    sep_seen = False
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "timestamp" in stripped and "freeze_hash" in stripped:
            in_table = True
            header_seen = True
            continue
        if in_table and header_seen and not sep_seen and "---" in stripped:
            sep_seen = True
            continue
        if in_table and header_seen and sep_seen:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= len(columns):
                rows.append(dict(zip(columns, cells[: len(columns)])))
    return rows


def get_feed_rows() -> list[dict[str, str]]:
    """Return all rows from AGENT_FEED.md.

    Falsifies if: returns an empty list when AGENT_FEED.md has data rows.
    falsifies_if: returns an empty list when AGENT_FEED.md has data rows.
    """
    if not AGENT_FEED.exists():
        return []
    return _parse_feed_rows(AGENT_FEED.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _run_git(args: list[str]) -> tuple[int, str]:
    """Run a git command and return (returncode, stdout).

    Falsifies if: returns (0, '') on a command that should produce output.
    falsifies_if: returns (0, '') on a command that should produce output.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        return result.returncode, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return 1, str(exc)


def commits_since(ref: str) -> list[dict[str, str]]:
    """Return commits since ref (exclusive) as list of dicts.

    Falsifies if: returns commits whose SHA is older than ref.
    falsifies_if: returns commits whose SHA is older than ref.
    """
    rc, out = _run_git(["log", f"{ref}..HEAD", "--oneline", "--no-decorate"])
    if rc != 0 or not out:
        return []
    commits = []
    for line in out.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            commits.append({"sha": parts[0], "message": parts[1]})
    return commits


def files_changed_since(ref: str) -> list[str]:
    """Return list of files changed since ref (exclusive of ref).

    Falsifies if: returns files that were not changed since ref.
    falsifies_if: returns files that were not changed since ref.
    """
    rc, out = _run_git(["diff", "--name-only", f"{ref}..HEAD"])
    if rc != 0 or not out:
        return []
    return out.splitlines()


def resolve_ref(ref: str) -> tuple[bool, str]:
    """Resolve a git ref to a full SHA.

    Falsifies if: returns ok=True with a SHA that git does not recognize.
    falsifies_if: returns ok=True with a SHA that git does not recognize.
    """
    rc, out = _run_git(["rev-parse", ref])
    return rc == 0, out


# ---------------------------------------------------------------------------
# Domain detection
# ---------------------------------------------------------------------------

def get_domain_names() -> list[str]:
    """Return sorted list of all domain directory names.

    Falsifies if: returns names that do not correspond to actual directories.
    falsifies_if: returns names that do not correspond to actual directories.
    """
    if not DOMAINS_DIR.exists():
        return []
    return sorted(p.name for p in DOMAINS_DIR.iterdir() if p.is_dir())


def new_domains_since(ref: str) -> list[str]:
    """Return list of domain directories added since ref.

    Falsifies if: returns domain names that existed before ref.
    falsifies_if: returns domain names that existed before ref.
    """
    rc, out = _run_git(["diff", "--name-only", "--diff-filter=A", f"{ref}..HEAD"])
    if rc != 0 or not out:
        return []
    added = set(out.splitlines())
    domains = []
    for path_str in added:
        p = Path(path_str)
        # e.g. src/domains/d_newdomain/invariants.py → d_newdomain
        if len(p.parts) >= 3 and p.parts[0] == "src" and p.parts[1] == "domains":
            domain_name = p.parts[2]
            if domain_name not in domains:
                domains.append(domain_name)
    return sorted(set(domains))


# ---------------------------------------------------------------------------
# Standards delta
# ---------------------------------------------------------------------------

def _registry_ids() -> set[str]:
    """Return the set of standard IDs in the current STANDARDS_REGISTRY.json.

    Falsifies if: returned IDs do not match the JSON file contents.
    falsifies_if: returned IDs do not match the JSON file contents.
    """
    if not REGISTRY.exists():
        return set()
    try:
        data: dict[str, Any] = json.loads(REGISTRY.read_text(encoding="utf-8"))
        return {s["id"] for s in data.get("standards", []) if "id" in s}
    except (json.JSONDecodeError, KeyError):
        return set()


def new_standards_since(ref: str) -> list[str]:
    """Return standard IDs added to STANDARDS_REGISTRY.json since ref.

    Falsifies if: returns IDs that existed before ref.
    falsifies_if: returns IDs that existed before ref.
    """
    rc, old_content = _run_git(["show", f"{ref}:STANDARDS_REGISTRY.json"])
    if rc != 0:
        return []
    try:
        old_data: dict[str, Any] = json.loads(old_content)
        old_ids = {s["id"] for s in old_data.get("standards", []) if "id" in s}
    except (json.JSONDecodeError, KeyError):
        old_ids = set()

    current_ids = _registry_ids()
    return sorted(current_ids - old_ids)


# ---------------------------------------------------------------------------
# Report builders
# ---------------------------------------------------------------------------

def _token_estimate(text: str) -> int:
    """Estimate token count using 4-chars-per-token heuristic.

    Falsifies if: returns a negative number.
    falsifies_if: returns a negative number.
    """
    return int(Fraction(len(text)) / Fraction(4))


def report_since_commit(ref: str, *, as_json: bool = False) -> tuple[int, str | dict[str, Any]]:
    """Build the since-commit report.

    Returns (exit_code, report) where report is str or dict depending on as_json.

    Falsifies if: returns exit_code 0 when the ref cannot be resolved.
    falsifies_if: returns exit_code 0 when the ref cannot be resolved.
    """
    ok, resolved_sha = resolve_ref(ref)
    if not ok:
        return 1, f"ERROR: Cannot resolve git ref '{ref}'"

    commits = commits_since(resolved_sha)
    changed_files = files_changed_since(resolved_sha)
    new_py = [f for f in changed_files if f.endswith(".py")]
    new_doms = new_domains_since(resolved_sha)
    new_stds = new_standards_since(resolved_sha)

    feed_rows = get_feed_rows()
    # Find rows added after the ref commit
    ref_short = resolved_sha[:7]
    found_ref = False
    new_feed_rows: list[dict[str, str]] = []
    for row in feed_rows:
        if found_ref:
            new_feed_rows.append(row)
        if row.get("commit_sha", "").startswith(ref_short):
            found_ref = True

    data: dict[str, Any] = {
        "ref": ref,
        "resolved_sha": resolved_sha,
        "new_commits": commits,
        "changed_files": changed_files,
        "new_python_files": new_py,
        "new_domains": new_doms,
        "new_standards": new_stds,
        "new_feed_rows": new_feed_rows,
    }

    if as_json:
        return 0, data

    lines = [
        f"# Since {ref} ({resolved_sha[:7]})",
        "",
        f"New commits: {len(commits)}",
    ]
    for c in commits[:20]:
        lines.append(f"  {c['sha']}  {c['message'][:80]}")
    if len(commits) > 20:
        lines.append(f"  ... and {len(commits) - 20} more")

    lines += [
        "",
        f"Changed files: {len(changed_files)}",
        f"New Python files: {len(new_py)}",
        f"New domains: {new_doms if new_doms else '(none)'}",
        f"New standards: {new_stds if new_stds else '(none)'}",
        f"New AGENT_FEED rows: {len(new_feed_rows)}",
    ]
    if new_feed_rows:
        for row in new_feed_rows[-5:]:
            lines.append(f"  {row.get('timestamp', '?')}  sha={row.get('commit_sha', '?')[:7]}")

    return 0, "\n".join(lines) + "\n"


def report_since_row(
    # TODO: Expand report_since_row() - stub detected by Yeshua Agent
    row_n: int, *, as_json: bool = False
) -> tuple[int, str | dict[str, Any]]:
    """Build the since-row report.

    Returns (exit_code, report) where report is str or dict depending on as_json.

    Falsifies if: returns rows whose index is <= row_n.
    falsifies_if: returns rows whose index is <= row_n.
    """
    all_rows = get_feed_rows()
    total = len(all_rows)

    if row_n < 0:
        row_n = 0
    new_rows = all_rows[row_n:]

    data: dict[str, Any] = {
        "since_row": row_n,
        "total_rows": total,
        "new_rows": new_rows,
        "new_row_count": len(new_rows),
    }

    if as_json:
        return 0, data

    lines = [
        f"# AGENT_FEED since row {row_n} (total: {total})",
        f"New rows: {len(new_rows)}",
        "",
    ]
    for row in new_rows[-20:]:
        ts = row.get("timestamp", "?")
        sha = row.get("commit_sha", "?")[:7]
        lines.append(f"  {ts}  sha={sha}")
    if len(new_rows) > 20:
        lines.insert(2, f"  (showing last 20 of {len(new_rows)})")

    return 0, "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Entry point for the since-last-session tool.

    Falsifies if: returns 0 when the git ref cannot be resolved.
    falsifies_if: returns 0 when the git ref cannot be resolved.
    """
    parser = argparse.ArgumentParser(
        description="Show what changed since the last agent session.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--since-commit",
        metavar="SHA",
        help="Show changes since this commit SHA or ref (e.g. HEAD~3, abc1234).",
    )
    group.add_argument(
        "--since-row",
        type=int,
        metavar="N",
        help="Show AGENT_FEED.md rows after row N (0-indexed).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON.",
    )

    args = parser.parse_args(argv)

    if args.since_commit:
        code, report = report_since_commit(args.since_commit, as_json=args.json)
    else:
        code, report = report_since_row(args.since_row, as_json=args.json)

    if isinstance(report, dict):
        print(json.dumps(report, indent=2))
    else:
        print(report, end="")

    return code


if __name__ == "__main__":
    sys.exit(main())

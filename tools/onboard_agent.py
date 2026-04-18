#!/usr/bin/env python3
"""
tools/onboard_agent.py — Unified Agent Onboarding Script

Detects the agent type, loads applicable standards from STANDARDS_REGISTRY.json
(filtered by --scope), runs basic environment checks, and outputs a single
context block to stdout that a new agent session can paste into its context.

Usage:
    python tools/onboard_agent.py --agent copilot
    python tools/onboard_agent.py --agent claude --scope src/domains/**
    python tools/onboard_agent.py --agent devin --scope .github/workflows/**

Supported agent types:
    copilot | claude | devin | kimi | aider | cursor | windsurf | cline | continue

Exit codes:
    0   Onboarding context printed successfully
    1   Environment checks failed (see stderr)
    2   Usage error

Author: Orthogonal Engineering
Gap: #13 (gap analysis 2026-04-17)
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "STANDARDS_REGISTRY.json"
CONSENT_LOG = REPO_ROOT / "pr47_stewardship" / "witness" / "consent_log.jsonl"
AGENT_FEED = REPO_ROOT / "AGENT_FEED.md"

SUPPORTED_AGENTS = frozenset({
    "copilot", "claude", "devin", "kimi",
    "aider", "cursor", "windsurf", "cline", "continue",
})

# Context window sizes in tokens (approximate upper bounds)
CONTEXT_WINDOWS: dict[str, int] = {
    "copilot":  128_000,
    "claude":   200_000,
    "devin":    200_000,
    "kimi":     220_000,
    "aider":    128_000,
    "cursor":   128_000,
    "windsurf": 128_000,
    "cline":    128_000,
    "continue": 128_000,
}

# Required files that must exist for a healthy repo
REQUIRED_FILES = [
    "SOP_AI_HANDSHAKE.md",
    "STANDARDS_REGISTRY.json",
    "AGENT_FEED.md",
    "pr47_stewardship/witness/consent_log.jsonl",
    ".github/copilot-instructions.md",
]


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def load_registry() -> list[dict[str, Any]]:
    """Load standards from STANDARDS_REGISTRY.json.

    Falsifies if: STANDARDS_REGISTRY.json is absent or malformed.
    falsifies_if: STANDARDS_REGISTRY.json is absent or malformed.
    """
    if not REGISTRY_PATH.exists():
        return []
    data: dict[str, Any] = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return list(data.get("standards", []))


def filter_by_scope(
    standards: list[dict[str, Any]], scope: str | None
) -> list[dict[str, Any]]:
    """Return standards relevant to the given scope glob.

    Falsifies if: non-None scope produces results whose scope patterns do not overlap.
    falsifies_if: non-None scope produces results whose scope patterns do not overlap.
    """
    if not scope:
        return standards

    import fnmatch

    result: list[dict[str, Any]] = []
    for s in standards:
        raw_scope: str = s.get("scope", "**")
        patterns = [p.strip() for p in raw_scope.split(",") if p.strip()]
        for pat in patterns:
            if (
                fnmatch.fnmatch(scope, pat)
                or fnmatch.fnmatch(pat, scope)
                or pat.startswith(scope.rstrip("/*"))
                or scope.rstrip("/*").startswith(pat.rstrip("/*"))
                or pat == "**"
            ):
                result.append(s)
                break
    return result


# ---------------------------------------------------------------------------
# Environment checks
# ---------------------------------------------------------------------------

def check_python_version() -> tuple[bool, str]:
    """Verify Python >= 3.10.

    Falsifies if: sys.version_info < (3, 10).
    falsifies_if: sys.version_info < (3, 10).
    """
    vi = sys.version_info
    ok = (vi.major, vi.minor) >= (3, 10)
    msg = f"Python {vi.major}.{vi.minor}.{vi.micro}"
    return ok, msg


def check_required_files() -> tuple[bool, list[str]]:
    """Verify all required repository files exist.

    Falsifies if: any file in REQUIRED_FILES is absent.
    falsifies_if: any file in REQUIRED_FILES is absent.
    """
    missing = [f for f in REQUIRED_FILES if not (REPO_ROOT / f).exists()]
    return len(missing) == 0, missing


def check_consent_log() -> tuple[bool, int]:
    """Verify consent log exists and has at least one entry.

    Falsifies if: consent_log.jsonl is absent or has no JSONL entries.
    falsifies_if: consent_log.jsonl is absent or has no JSONL entries.
    """
    if not CONSENT_LOG.exists():
        return False, 0
    all_lines = CONSENT_LOG.read_text(encoding="utf-8").splitlines()
    lines = [ln for ln in all_lines if ln.strip() and not ln.strip().startswith("#")]
    return len(lines) > 0, len(lines)


def check_feed_integrity() -> tuple[bool, str]:
    """Delegate feed chain integrity check to generate_feed_entry.py --verify.

    Falsifies if: generate_feed_entry.py --verify exits non-zero.
    falsifies_if: generate_feed_entry.py --verify exits non-zero.
    """
    script = REPO_ROOT / "tools" / "state_witness" / "generate_feed_entry.py"
    if not script.exists():
        return False, "generate_feed_entry.py not found"
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--verify"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def run_env_checks() -> tuple[bool, list[dict[str, Any]]]:
    """Run all environment checks and return (all_pass, results).

    Falsifies if: all_pass is True but any individual check returned False.
    falsifies_if: all_pass is True but any individual check returned False.
    """
    results: list[dict[str, Any]] = []

    py_ok, py_msg = check_python_version()
    results.append({"check": "python_version", "pass": py_ok, "detail": py_msg})

    files_ok, missing = check_required_files()
    results.append({
        "check": "required_files",
        "pass": files_ok,
        "detail": f"missing: {missing}" if missing else "all present",
    })

    log_ok, log_count = check_consent_log()
    results.append({
        "check": "consent_log",
        "pass": log_ok,
        "detail": f"{log_count} entries",
    })

    feed_ok, feed_msg = check_feed_integrity()
    results.append({"check": "feed_integrity", "pass": feed_ok, "detail": feed_msg})

    all_pass = all(r["pass"] for r in results)
    return all_pass, results


# ---------------------------------------------------------------------------
# Context generation
# ---------------------------------------------------------------------------

def _feed_row_count() -> int:
    """Return the number of data rows in AGENT_FEED.md.

    Falsifies if: returns a count that does not match the actual data rows.
    falsifies_if: returns a count that does not match the actual data rows.
    """
    if not AGENT_FEED.exists():
        return 0
    return sum(
        1
        for line in AGENT_FEED.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("| ")
        and "timestamp" not in line
        and "---" not in line
    )


def _last_consent_entry() -> str:
    """Return the timestamp of the most recent consent log entry.

    Falsifies if: returns a timestamp that does not match the last JSONL line.
    falsifies_if: returns a timestamp that does not match the last JSONL line.
    """
    if not CONSENT_LOG.exists():
        return "none"
    lines = [ln for ln in CONSENT_LOG.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return "none"
    try:
        entry = json.loads(lines[-1])
        return str(entry.get("timestamp", "unknown"))
    except json.JSONDecodeError:
        return "parse-error"


def _estimate_tokens(text: str) -> int:
    """Estimate token count using 4-chars-per-token heuristic.

    Falsifies if: returns a count less than 0.
    falsifies_if: returns a count less than 0.
    """
    chars = Fraction(len(text))
    tokens = chars / Fraction(4)
    return int(tokens)


def _git_head_sha() -> str:
    """Return the current HEAD commit SHA.

    Falsifies if: returns a non-hex string of length != 40 when git is available.
    falsifies_if: returns a non-hex string of length != 40 when git is available.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:  # noqa: BLE001
        pass
    return "unknown"


def build_context_block(
    agent: str,
    scope: str | None,
    standards: list[dict[str, Any]],
    env_results: list[dict[str, Any]],
) -> str:
    """Build the onboarding context block for the agent.

    Falsifies if: the context block does not contain the agent name or standard IDs.
    falsifies_if: the context block does not contain the agent name or standard IDs.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    head_sha = _git_head_sha()
    feed_rows = _feed_row_count()
    last_consent = _last_consent_entry()
    ctx_window = CONTEXT_WINDOWS.get(agent, 128_000)

    # Environment summary
    env_lines = [
        f"  {'✓' if r['pass'] else '✗'}  {r['check']:25s}  {r['detail']}"
        for r in env_results
    ]

    # Standards summary
    std_lines = []
    for s in standards:
        sev = s.get("severity", "?")[0].upper()
        std_lines.append(f"  [{sev}] {s['id']:10s}  {s['rule'][:70]}")

    # Build block
    lines = [
        f"# ONBOARDING CONTEXT — {agent.upper()} — {ts}",
        f"# HEAD: {head_sha}",
        f"# Context window: ~{ctx_window:,} tokens",
        f"# AGENT_FEED.md rows: {feed_rows}",
        f"# Last consent entry: {last_consent}",
        "",
        "## Environment",
        *env_lines,
        "",
        f"## Applicable Standards{' (scope: ' + scope + ')' if scope else ''}",
        f"# {len(standards)} standard(s) loaded",
        *std_lines,
        "",
        "## Required Consent Step",
        "  python tools/append_consent.py \\",
        f"    --candidate-id \"{agent}-<YYYYMMDD>-<session-id>\" \\",
        "    --authoriser \"@aidoruao\" \\",
        "    --action \"<action-slug>\" \\",
        "    --scope-glob \"<glob>\" \\",
        "    --justification \"<reason>\"",
        "",
        "## Quick Verify",
        "  python tools/state_witness/generate_feed_entry.py --verify",
        "  python audit/popperian_audit.py 2>&1 | tail -3",
        f"  python tools/standards_check.py --verify{' --scope ' + scope if scope else ''}",
        "  pytest tests/ -q",
        "",
        "## Read Before Coding",
        "  1. SOP_AI_HANDSHAKE.md",
        "  2. .github/copilot-instructions.md",
        "  3. STANDARDS_REGISTRY.json",
        "  4. AGENT_ONBOARDING.md",
        "  5. MEMORY.md",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Entry point for the onboarding tool.

    Falsifies if: --agent is valid but the function returns non-zero on a healthy repo.
    falsifies_if: --agent is valid but the function returns non-zero on a healthy repo.
    """
    parser = argparse.ArgumentParser(
        description="Orthogonal Engineering unified agent onboarding.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--agent",
        default=os.environ.get("OE_AGENT", ""),
        choices=sorted(SUPPORTED_AGENTS),
        required=False,
        help="Agent type (or set OE_AGENT env var).",
    )
    parser.add_argument(
        "--scope",
        default=None,
        help="Glob scope for filtering applicable standards (e.g. src/domains/**).",
    )
    parser.add_argument(
        "--skip-env-check",
        action="store_true",
        help="Skip environment checks (faster, for CI contexts where env is known good).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable context block.",
    )

    args = parser.parse_args(argv)

    agent = args.agent or "copilot"
    if agent not in SUPPORTED_AGENTS:
        print(
            f"ERROR: Unknown agent '{agent}'. Supported: {sorted(SUPPORTED_AGENTS)}",
            file=sys.stderr,
        )
        return 2

    # Load and filter standards
    all_standards = load_registry()
    standards = filter_by_scope(all_standards, args.scope)

    # Run environment checks
    if args.skip_env_check:
        env_ok = True
        env_results: list[dict[str, Any]] = []
    else:
        env_ok, env_results = run_env_checks()

    if args.json:
        output = {
            "agent": agent,
            "scope": args.scope,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "environment_ok": env_ok,
            "environment_checks": env_results,
            "standards_count": len(standards),
            "standards": standards,
            "head_sha": _git_head_sha(),
            "feed_rows": _feed_row_count(),
            "context_window_tokens": CONTEXT_WINDOWS.get(agent, 128_000),
        }
        print(json.dumps(output, indent=2))
    else:
        block = build_context_block(agent, args.scope, standards, env_results)
        print(block)

    if not env_ok and not args.skip_env_check:
        print("\nWARNING: Environment checks failed. Fix issues before coding.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

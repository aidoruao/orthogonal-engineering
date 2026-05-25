#!/usr/bin/env python3
"""
tools/standards_check.py — Standards Registry Query and Verification Tool

Reads STANDARDS_REGISTRY.json and provides:
  --list               Print all standards (filtered by --scope or --category)
  --verify             Run enforcement_command for every applicable standard
  --id <ID>            Show a single standard entry
  --scope <glob>       Filter standards whose scope matches the given path prefix
  --category <cat>     Filter by category (yeshua_axiom, code_standard, etc.)

Usage:
    python tools/standards_check.py --list
    python tools/standards_check.py --list --category code_standard
    python tools/standards_check.py --list --scope src/domains/**
    python tools/standards_check.py --verify
    python tools/standards_check.py --verify --category workflow_constraint
    python tools/standards_check.py --id CS-001

Exit codes:
    0  All verifiable standards passed (or --list / --id only)
    1  One or more standards failed verification

Author: Orthogonal Engineering
PR: Stream C (gap analysis 2026-04-17)
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "STANDARDS_REGISTRY.json"

# Severity ordering for sorting
_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_registry() -> dict[str, Any]:
    """Load and return the parsed STANDARDS_REGISTRY.json.

    Falsifies if: STANDARDS_REGISTRY.json does not exist or is not valid JSON.
    falsifies_if: STANDARDS_REGISTRY.json does not exist or is not valid JSON.
    """
    if not REGISTRY_PATH.exists():
        print(
            f"ERROR: {REGISTRY_PATH} not found. "
            "Run from repo root or check file path.",
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: STANDARDS_REGISTRY.json is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(2)


def get_standards(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the list of standard entries sorted by severity then id.

    Falsifies if: registry has no 'standards' key or it is not a list.
    falsifies_if: registry has no 'standards' key or it is not a list.
    """
    standards: list[dict[str, Any]] = list(registry.get("standards", {}).values())
    return sorted(
        standards,
        key=lambda s: (_SEVERITY_ORDER.get(s.get("severity", "low"), 4), s.get("id", "")),
    )


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def _scope_matches(standard: dict[str, Any], scope_filter: str) -> bool:
    """Return True if any scope pattern in the standard overlaps scope_filter.

    Falsifies if: scope_filter is non-empty and no standard scope pattern matches it.
    falsifies_if: scope_filter is non-empty and no standard scope pattern matches it.
    """
    raw_scope: str = standard.get("scope", "**")
    patterns = [p.strip() for p in raw_scope.split(",") if p.strip()]
    for pat in patterns:
        if fnmatch.fnmatch(scope_filter, pat) or fnmatch.fnmatch(pat, scope_filter):
            return True
        # Also match if scope_filter is a prefix of the pattern
        if pat.startswith(scope_filter.rstrip("/*")):
            return True
    return False


def filter_standards(
    standards: list[dict[str, Any]],
    *,
    scope_filter: str | None = None,
    category_filter: str | None = None,
    id_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Apply optional filters and return matching standards.

    Falsifies if: a non-None filter produces results that don't match the filter criterion.
    falsifies_if: a non-None filter produces results that don't match the filter criterion.
    """
    result = standards
    if id_filter:
        result = [s for s in result if s.get("id", "").upper() == id_filter.upper()]
    if category_filter:
        result = [s for s in result if s.get("category", "") == category_filter]
    if scope_filter:
        result = [s for s in result if _scope_matches(s, scope_filter)]
    return result


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def _severity_badge(severity: str) -> str:
    badges = {
        "critical": "[CRITICAL]",
        "high":     "[HIGH    ]",
        "medium":   "[MEDIUM  ]",
        "low":      "[LOW     ]",
    }
    return badges.get(severity, "[UNKNOWN ]")


def print_standard(s: dict[str, Any], *, verbose: bool = False) -> None:
    """Print a single standard entry to stdout.

    Falsifies if: output does not include the standard's id and rule.
    falsifies_if: output does not include the standard's id and rule.
    """
    sev = _severity_badge(s.get("severity", "low"))
    print(f"{sev} {s.get('id', '?'):10s}  {s.get('rule', '')}")
    if verbose:
        print(f"            Category   : {s.get('category', '')}")
        print(f"            Description: {s.get('description', '')}")
        print(f"            Scope      : {s.get('scope', '')}")
        print(f"            Falsifies if: {s.get('falsifies_if', '')}")
        cmd = s.get("enforcement_command")
        if cmd:
            print(f"            Enforcement: {cmd}")
        print()


def cmd_list(
    standards: list[dict[str, Any]],
    *,
    scope_filter: str | None = None,
    category_filter: str | None = None,
    id_filter: str | None = None,
    verbose: bool = False,
) -> int:
    """List standards to stdout. Returns exit code 0.

    Falsifies if: standards are listed but the count line is wrong.
    falsifies_if: standards are listed but the count line is wrong.
    """
    filtered = filter_standards(
        standards,
        scope_filter=scope_filter,
        category_filter=category_filter,
        id_filter=id_filter,
    )
    if not filtered:
        print("No standards match the given filters.")
        return 0
    for s in filtered:
        print_standard(s, verbose=verbose)
    print(f"\n{len(filtered)} standard(s) listed.")
    return 0


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def run_enforcement(
    standard: dict[str, Any],
) -> tuple[bool, str]:
    """Run the enforcement_command for a standard and return (passed, output).

    Standards without an enforcement_command are considered SKIP (pass=True).

    The semantics are controlled by the optional ``enforcement_passes_on`` field:
    - ``"no_output"``  — PASS when the command produces no stdout (absence check).
                         Typically used with ``grep`` that should find nothing.
    - ``"has_output"`` — PASS when the command produces stdout (presence check).
                         Typically used with ``grep`` that must find something.
    - ``"exit_zero"``  — PASS when the command exits with code 0 (default).

    Falsifies if: a standard with enforcement_passes_on='exit_zero' returns 0
    even though the enforcement_command exits non-zero.
    falsifies_if: a standard with enforcement_passes_on='exit_zero' returns 0
    even though the enforcement_command exits non-zero.
    """
    cmd = standard.get("enforcement_command")
    if not cmd:
        return True, "(no enforcement command — manual check required)"

    passes_on: str = standard.get("enforcement_passes_on", "exit_zero")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=60,
        )
        combined = (result.stdout.strip() + "\n" + result.stderr.strip()).strip()

        if passes_on == "no_output":
            # Absence check: grep that finds nothing (rc=1) or finds nothing (rc=0, empty stdout)
            passed = result.returncode == 1 or (
                result.returncode == 0 and not result.stdout.strip()
            )
        elif passes_on == "has_output":
            # Presence check: grep that finds something (rc=0, non-empty stdout)
            passed = result.returncode == 0 and bool(result.stdout.strip())
        else:
            # Default: exit_zero
            passed = result.returncode == 0

        return passed, combined if combined else "(no output)"
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: enforcement command exceeded 60s"
    except Exception as exc:  # noqa: BLE001
        return False, f"ERROR running enforcement command: {exc}"


def cmd_verify(
    standards: list[dict[str, Any]],
    *,
    scope_filter: str | None = None,
    category_filter: str | None = None,
    id_filter: str | None = None,
) -> int:
    """Run all enforcement commands and report PASS/FAIL. Returns exit code.

    Falsifies if: any standard with a non-null enforcement_command exits non-zero
    and this function returns 0.
    falsifies_if: any standard with a non-null enforcement_command exits non-zero
    and this function returns 0.
    """
    filtered = filter_standards(
        standards,
        scope_filter=scope_filter,
        category_filter=category_filter,
        id_filter=id_filter,
    )
    if not filtered:
        print("No standards match the given filters — nothing to verify.")
        return 0

    passed_ids: list[str] = []
    failed_ids: list[str] = []
    skipped_ids: list[str] = []

    for s in filtered:
        sid = s.get("id", "?")
        rule = s.get("rule", "")
        cmd = s.get("enforcement_command")

        if not cmd:
            print(f"  SKIP  {sid:10s}  {rule[:70]}")
            skipped_ids.append(sid)
            continue

        ok, output = run_enforcement(s)
        status = "PASS" if ok else "FAIL"
        print(f"  {status}  {sid:10s}  {rule[:70]}")
        if not ok:
            for line in output.splitlines()[:5]:
                print(f"              {line}")
            failed_ids.append(sid)
        else:
            passed_ids.append(sid)

    total = len(filtered)
    print()
    print(f"Results: {len(passed_ids)} passed, {len(failed_ids)} failed, "
          f"{len(skipped_ids)} skipped / {total} total")

    if failed_ids:
        print(f"FAILED standards: {', '.join(failed_ids)}", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Entry point for the standards check tool.

    Falsifies if: --verify returns 0 when a critical standard's enforcement command fails.
    falsifies_if: --verify returns 0 when a critical standard's enforcement command fails.
    """
    parser = argparse.ArgumentParser(
        description="Query and verify the Orthogonal Engineering STANDARDS_REGISTRY.json.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print all matching standards.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run enforcement commands for all matching standards.",
    )
    parser.add_argument(
        "--id",
        metavar="ID",
        help="Show or verify a single standard by ID (e.g. CS-001).",
    )
    parser.add_argument(
        "--scope",
        metavar="GLOB",
        help="Filter standards whose scope pattern overlaps this path/glob.",
    )
    parser.add_argument(
        "--category",
        metavar="CAT",
        help=(
            "Filter by category: yeshua_axiom, code_standard, behavioral_constraint, "
            "documentation_register, quality_gate, workflow_constraint, integrity"
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show full details for each standard (with --list).",
    )

    args = parser.parse_args(argv)

    registry = load_registry()
    standards = get_standards(registry)
    meta = registry.get("_meta", {})

    if not args.list and not args.verify and not args.id:
        # Default: print registry summary
        print(f"STANDARDS_REGISTRY.json — schema v{meta.get('schema_version', '?')}")
        print(f"  Total standards : {meta.get('total_standards', len(standards))}")
        print(f"  Last updated    : {meta.get('last_updated', '?')}")
        print(f"  Authority       : {meta.get('authority', '?')}")
        print()
        print("Use --list to browse, --verify to run enforcement, --id <ID> for detail.")
        return 0

    if args.id and not args.verify:
        return cmd_list(
            standards,
            id_filter=args.id,
            verbose=True,
        )

    if args.list:
        return cmd_list(
            standards,
            scope_filter=args.scope,
            category_filter=args.category,
            id_filter=args.id,
            verbose=args.verbose,
        )

    if args.verify:
        return cmd_verify(
            standards,
            scope_filter=args.scope,
            category_filter=args.category,
            id_filter=args.id,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
continuity_check.py — Continuity Artifact Validator

Verifies that all onboarding and continuity artifacts exist and contain the required headings.
Also validates that bootstrap_context.py runs without error.

Usage:
    python continuity_check.py [--repo-root <path>]

Exit codes:
    0  — all checks pass
    1  — one or more artifacts missing or malformed
    2  — bootstrap_context.py fails to run

Can be run manually or in CI.
Standard library only — no pip install required.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Required artifacts and their mandatory headings
# ---------------------------------------------------------------------------

REQUIRED_DOCS = {
    "COPILOT_ONBOARDING.md": [
        "## 1. Purpose",
        "## 2. Boot Sequence",
        "## 3. Continuity Artifacts",
    ],
    "MEMORY.md": [
        "## Architectural Decisions",
        "## Constraints",
        "## Open Questions",
    ],
    "STATE.md": [
        "## ",  # at least one h2 heading
    ],
    "HANDOFF_TEMPLATE.md": [
        "## What Was Done This Session",
        "## What Is In Progress",
        "## Decisions Made",
    ],
}

REQUIRED_SCRIPTS = [
    "bootstrap_context.py",
    "continuity_check.py",
]

# ---------------------------------------------------------------------------
# Check helpers
# ---------------------------------------------------------------------------

PASS = "✅"
FAIL = "❌"


def _check_file_exists(path: Path) -> tuple[bool, str]:
    if path.exists() and path.is_file():
        return True, f"{PASS}  Exists: {path.name}"
    return False, f"{FAIL}  MISSING: {path.name}"


def _check_headings(path: Path, required_headings: list[str]) -> list[tuple[bool, str]]:
    """Return one result per required heading."""
    results = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [(False, f"{FAIL}  Cannot read {path.name}: {exc}")]
    for heading in required_headings:
        if heading in content:
            results.append((True, f"  {PASS}  Heading found: {heading.strip()!r}"))
        else:
            results.append((False, f"  {FAIL}  Missing heading: {heading.strip()!r}"))
    return results


def _run_bootstrap(repo_root: Path) -> tuple[bool, str]:
    """Run bootstrap_context.py and return (ok, message)."""
    script = repo_root / "bootstrap_context.py"
    if not script.exists():
        return False, f"{FAIL}  bootstrap_context.py not found — cannot run"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(repo_root),
        )
        if result.returncode in (0, 1):
            # Exit code 1 means missing artifacts (already reported by doc checks).
            # We care here only that the script itself doesn't crash.
            return True, f"{PASS}  bootstrap_context.py ran (exit code {result.returncode})"
        return False, (
            f"{FAIL}  bootstrap_context.py exited with code {result.returncode}\n"
            f"  stderr: {result.stderr.strip()[:300]}"
        )
    except subprocess.TimeoutExpired:
        return False, f"{FAIL}  bootstrap_context.py timed out (>30s)"
    except Exception as exc:
        return False, f"{FAIL}  bootstrap_context.py raised an exception: {exc}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_checks(repo_root: Path) -> int:
    """Run all checks. Returns exit code (0=pass, 1=failures, 2=bootstrap error)."""
    all_ok = True
    bootstrap_ok = True

    print("=" * 65)
    print("ORTHOGONAL ENGINEERING — CONTINUITY CHECK")
    print("=" * 65)
    print(f"Repo root: {repo_root}\n")

    # 1. Onboarding / continuity documents
    print("── Required Documents ──────────────────────────────────────")
    for doc_name, headings in REQUIRED_DOCS.items():
        doc_path = repo_root / doc_name
        ok, msg = _check_file_exists(doc_path)
        print(msg)
        if not ok:
            all_ok = False
            continue
        heading_results = _check_headings(doc_path, headings)
        for h_ok, h_msg in heading_results:
            print(h_msg)
            if not h_ok:
                all_ok = False

    print()

    # 2. Required scripts
    print("── Required Scripts ─────────────────────────────────────────")
    for script_name in REQUIRED_SCRIPTS:
        ok, msg = _check_file_exists(repo_root / script_name)
        print(msg)
        if not ok:
            all_ok = False

    print()

    # 3. Bootstrap smoke-test
    print("── Bootstrap Smoke Test ─────────────────────────────────────")
    b_ok, b_msg = _run_bootstrap(repo_root)
    print(b_msg)
    if not b_ok:
        bootstrap_ok = False

    print()
    print("=" * 65)

    if not all_ok and not bootstrap_ok:
        print("❌  CONTINUITY CHECK FAILED (documents + bootstrap)")
        return 2
    elif not bootstrap_ok:
        print("❌  CONTINUITY CHECK FAILED (bootstrap error)")
        return 2
    elif not all_ok:
        print("❌  CONTINUITY CHECK FAILED (missing documents or headings)")
        return 1
    else:
        print("✅  CONTINUITY CHECK PASSED")
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate continuity artifacts and bootstrap script."
    )
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parent),
        help="Repository root directory (default: directory containing this script)",
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root)
    sys.exit(run_checks(repo_root))


if __name__ == "__main__":
    main()

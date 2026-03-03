"""
ci_preflight.py — Local CI workflow manifest preflight

Usage:
    python scripts/ci_preflight.py [--json]

What it does:
    - Enumerates every workflow definition tracked in this repository
      (GitHub Actions and auxiliary workflows under workflows/).
    - Outputs count, relative paths, and SHA-256 hashes so you can compare
      against expected workflow sets before opening or updating a PR.

Exit codes:
    0 on success.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, TypedDict

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from enforcement_matrix_generator import REPO_ROOT as MATRIX_ROOT, _ci_workflows


class WorkflowRecord(TypedDict):
    path: str
    hash: str


def main() -> int:
    parser = argparse.ArgumentParser(description="List all CI workflow files with hashes.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable output",
    )
    args = parser.parse_args()

    workflows: List[WorkflowRecord] = _ci_workflows()
    total = len(workflows)

    if args.json:
        print(json.dumps({"count": total, "workflows": workflows}, indent=2))
        return 0

    print(f"[ci-preflight] Found {total} workflow file(s) under {MATRIX_ROOT}")
    for wf in workflows:
        print(f"  - {wf['path']}  {wf['hash']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

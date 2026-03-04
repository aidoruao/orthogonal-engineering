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
import os
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

REQUIRED_ENV = {
    "PYTHONHASHSEED": "0",
    "PYTHONUTF8": "1",
    "LC_ALL": "C",
    "TZ": "UTC",
}

try:
    from enforcement_matrix_generator import ci_workflows
except ImportError as exc:
    raise SystemExit(
        "ci_preflight.py must be run from within the repository root; "
        "failed to import enforcement_matrix_generator."
    ) from exc


def _enforce_deterministic_env() -> None:
    """Fail fast if deterministic env guards are not set."""
    missing = {
        key: val for key, val in REQUIRED_ENV.items() if os.environ.get(key) != val
    }
    if missing:
        needed = " ".join(f"{k}={v}" for k, v in missing.items())
        raise SystemExit(
            "[ci-preflight] deterministic environment required; "
            f"set: {needed} (note: PYTHONHASHSEED must be set before interpreter start)"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="List all CI workflow files with hashes.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable output",
    )
    args = parser.parse_args()

    _enforce_deterministic_env()

    workflows: List[Dict[str, str]] = ci_workflows()
    total = len(workflows)

    if args.json:
        print(json.dumps({"count": total, "workflows": workflows}, indent=2))
        return 0

    print(f"[ci-preflight] Found {total} workflow file(s) under {REPO_ROOT}")
    for wf in workflows:
        print(f"  - {wf['path']}  {wf['hash']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

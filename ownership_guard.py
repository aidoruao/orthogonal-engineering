"""
ownership_guard.py — Free Forever / Anti-Monetization Guard

CI check:
  - Reject addition of payment processors
  - Reject license changes to non-open licenses
  - Reject proprietary headers

Run as: python ownership_guard.py [--strict]

Exits 0 if clean, 1 if violations found.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).parent

# ---------------------------------------------------------------------------
# Monetization / proprietary keyword patterns
# ---------------------------------------------------------------------------

MONETIZATION_KEYWORDS = [
    "stripe.com",
    "paypal.com",
    "braintreepayments",
    "chargebee",
    "recurly",
    "paddle.com",
    "gumroad.com",
    "import stripe",
    "from stripe",
    "import paypalrestsdk",
    "payment_intent",
    "subscription_price",
]

PROPRIETARY_LICENSE_KEYWORDS = [
    "all rights reserved",
    "not for redistribution",
    "commercial use prohibited",
    "no modification allowed",
    "proprietary license",
    "proprietary software",
]

OPEN_LICENSE_IDENTIFIERS = {
    "cc0",
    "mit",
    "apache",
    "gpl",
    "lgpl",
    "mpl",
    "bsd",
    "unlicense",
    "public domain",
    "creative commons",
}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
SKIP_FILES = {"ownership_guard.py"}  # Do not self-scan the guard
SCAN_EXTS = {".py", ".js", ".ts", ".md", ".txt", ".yaml", ".yml", ".json"}


def _walk_repo() -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname in SKIP_FILES:
                continue
            p = Path(dirpath) / fname
            if p.suffix in SCAN_EXTS:
                files.append(p)
    return files


def check_monetization(files: List[Path]) -> List[Dict]:
    """Scan all files for monetization-related keywords."""
    violations: List[Dict] = []
    for fpath in files:
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        for kw in MONETIZATION_KEYWORDS:
            if kw.lower() in content:
                violations.append({
                    "type": "monetization_keyword",
                    "file": str(fpath.relative_to(REPO_ROOT)),
                    "keyword": kw,
                })
    return violations


def check_license_integrity() -> List[Dict]:
    """Verify that LICENSE file exists and contains an open license identifier."""
    violations: List[Dict] = []
    license_path = REPO_ROOT / "LICENSE"
    if not license_path.exists():
        violations.append({
            "type": "missing_license",
            "file": "LICENSE",
            "detail": "LICENSE file is missing — free forever guarantee broken",
        })
        return violations

    content = license_path.read_text(encoding="utf-8", errors="replace").lower()
    if not any(oid in content for oid in OPEN_LICENSE_IDENTIFIERS):
        violations.append({
            "type": "non_open_license",
            "file": "LICENSE",
            "detail": "LICENSE does not contain a recognised open license identifier",
        })

    for pkw in PROPRIETARY_LICENSE_KEYWORDS:
        if pkw in content:
            violations.append({
                "type": "proprietary_license_keyword",
                "file": "LICENSE",
                "keyword": pkw,
            })

    return violations


def run_ownership_guard(strict: bool = False) -> Dict:
    """
    Run all ownership / monetization checks.

    Returns a structured result dict.
    If strict=True, raises RuntimeError on violations.
    """
    files = _walk_repo()
    violations: List[Dict] = []
    violations.extend(check_monetization(files))
    violations.extend(check_license_integrity())

    result = {
        "all_passed": len(violations) == 0,
        "violation_count": len(violations),
        "violations": violations,
    }

    if strict and violations:
        raise RuntimeError(
            f"Ownership guard failed with {len(violations)} violations:\n"
            + json.dumps(violations, indent=2)
        )

    return result


if __name__ == "__main__":
    strict = "--strict" in sys.argv
    result = run_ownership_guard(strict=strict)
    print(json.dumps(result, indent=2, sort_keys=True))
    sys.exit(0 if result["all_passed"] else 1)

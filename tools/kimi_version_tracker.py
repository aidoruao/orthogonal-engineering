"""tools/kimi_version_tracker.py -- Version tracking before/after stress tests.

Part 7B of Forensic Offensive Campaign.

Logs kimi --version before and after each stress test session.
"""

from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject

LOG_PATH = REPO_ROOT / "audit" / "KIMI_VERSION_LOG.json"


def get_kimi_version() -> str:
    """Run kimi --version and return the version string.

    falsifies_if: returns empty string when kimi is installed.
    """
    try:
        result = subprocess.run(
            ["kimi", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() or "unknown"
    except (subprocess.SubprocessError, FileNotFoundError):
        return "not_installed"


def log_version(session_id: str, phase: str) -> Tuple[bool, ProofObject]:
    """Log Kimi CLI version for a given session phase.

    Standard: TEL-VERSION-001 version tracking.
    Falsifies if: version cannot be determined and phase is 'after'.
    falsifies_if: version cannot be determined and phase is 'after'.
    """
    version = get_kimi_version()
    entry = {
        "session_id": session_id,
        "phase": phase,
        "version": version,
    }

    try:
        if LOG_PATH.exists():
            log_data = json.loads(LOG_PATH.read_text(encoding="utf-8"))
        else:
            log_data = []
        log_data.append(entry)
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.write_text(json.dumps(log_data, indent=2), encoding="utf-8")
    except OSError as exc:
        return False, ProofObject(
            rule="kimi_version_tracker",
            premises=[f"session_id={session_id}", f"phase={phase}"],
            conclusion=f"FAIL: Could not write version log: {exc}",
        )

    success = version != "not_installed"
    proof = ProofObject(
        rule="kimi_version_tracker",
        premises=[f"session_id={session_id}", f"phase={phase}", f"version={version}"],
        conclusion=(
            f"PASS: Version {version} logged for {phase} phase"
            if success else f"WARN: kimi not installed, logged '{version}'"
        ),
    )
    return success, proof


def main() -> int:
    """CLI entry point. Log version before or after a session.

    falsifies_if: exit code 0 when version is not_installed.
    """
    if len(sys.argv) < 3:
        print("Usage: python tools/kimi_version_tracker.py <session_id> <before|after>")
        return 1
    session_id = sys.argv[1]
    phase = sys.argv[2]
    ok, proof = log_version(session_id, phase)
    print(proof.conclusion)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

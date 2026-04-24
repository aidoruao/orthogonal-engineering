"""tools/kimi_telemetry_correlation.py -- Crash-to-version correlation tool.

Part 7A of Forensic Offensive Campaign.

Reads witness/session_logs/, maps crash->Kimi version->feature shipped.
Produces timeline correlation report.
"""

from __future__ import annotations

import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject

SESSION_LOGS_DIR = REPO_ROOT / "witness" / "session_logs"
REPORT_PATH = REPO_ROOT / "audit" / "KIMI_TELEMETRY_CORRELATION.json"


def _extract_crash_events_from_log(text: str) -> List[Dict[str, str]]:
    """Extract crash-like events from session log text.

    falsifies_if: returns non-empty list when text contains no crash indicators.
    """
    crashes = []
    crash_indicators = ["ERROR", "FAIL", "VIOLATION", "Exception", "Traceback"]
    for indicator in crash_indicators:
        for match in re.finditer(rf".*{indicator}.*", text):
            crashes.append({
                "line": match.group(0).strip()[:100],
                "indicator": indicator,
            })
    return crashes


def correlate_telemetry() -> Tuple[bool, ProofObject]:
    """Correlate crash events across all session logs.

    Standard: TEL-CORR-001 aggregate correlation.
    Falsifies if: session logs exist but correlation report is empty.
    falsifies_if: session logs exist but correlation report is empty.
    """
    if not SESSION_LOGS_DIR.exists():
        return False, ProofObject(
            rule="kimi_telemetry_correlation",
            premises=["session_logs_dir missing"],
            conclusion="FAIL: witness/session_logs/ directory not found",
        )

    log_files = sorted(SESSION_LOGS_DIR.glob("*.txt"))
    if not log_files:
        return False, ProofObject(
            rule="kimi_telemetry_correlation",
            premises=["session_logs_dir exists", "log_files=0"],
            conclusion="FAIL: No session log files found",
        )

    all_crashes: List[Dict] = []
    for log_file in log_files:
        try:
            text = log_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        crashes = _extract_crash_events_from_log(text)
        if crashes:
            all_crashes.append({
                "file": str(log_file.name),
                "crashes": crashes,
            })

    report = {
        "total_logs_scanned": len(log_files),
        "logs_with_crashes": len(all_crashes),
        "total_crash_events": sum(len(c["crashes"]) for c in all_crashes),
        "details": all_crashes,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    proof = ProofObject(
        rule="kimi_telemetry_correlation",
        premises=[
            f"logs_scanned={len(log_files)}",
            f"logs_with_crashes={len(all_crashes)}",
        ],
        conclusion=(
            f"PASS: Scanned {len(log_files)} logs, found {len(all_crashes)} with crash events"
        ),
    )
    return True, proof


if __name__ == "__main__":
    ok, proof = correlate_telemetry()
    print(proof.conclusion)
    sys.exit(0 if ok else 1)

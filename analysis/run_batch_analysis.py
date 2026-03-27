#!/usr/bin/env python3
"""
BATCH ANALYSIS: Cross-Session Non-Compliance Correlation
Schema ID: BATCH-ANALYSIS-1.0
Version: 1.0
Generated: 2026-03-27

Purpose:
    Scan all existing analysis JSON reports and produce a cross-session
    aggregate showing total violations by type, severity distribution,
    most frequent patterns, and SYSTEMIC patterns (same type in 3+ sessions).

Output: analysis/aggregate_noncompliance_report.json

Glass-Box: fully observable, deterministic, hash-verified output.
"""

import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
REPORTS_DIR = REPO_ROOT / "forgiveness_all_exports_output" / "reports"
OUTPUT_FILE = REPO_ROOT / "analysis" / "aggregate_noncompliance_report.json"

SYSTEMIC_THRESHOLD = 3  # Same violation type in 3+ sessions → SYSTEMIC

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _load_report(path: Path) -> Dict[str, Any]:
    """Load a single analysis JSON report."""
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return json.load(fh)


def _extract_violations_from_report(report: Dict[str, Any], filename: str) -> List[Dict]:
    """
    Extract violation records from a single analysis report.
    Handles both the standard analyze_chat_exports format and the
    fix_forgiveness_system format.
    """
    violations = []

    # --- Format 1: detailed_analysis → violations list ---
    detailed = report.get("detailed_analysis", {})
    raw_violations = detailed.get("violations", [])
    if isinstance(raw_violations, list):
        for v in raw_violations:
            if isinstance(v, dict):
                violations.append({
                    "session": filename,
                    "violation_type": v.get("violation_type", "unknown"),
                    "severity": v.get("severity", "unknown"),
                    "line": v.get("chat_line", ""),
                    "line_number": v.get("line_number", 0),
                    "pattern": v.get("pattern", ""),
                })

    # --- Format 2: violations_by_type summary (from summary key) ---
    summary = report.get("summary", {})
    by_type = summary.get("violations_by_type", {})
    if by_type and not raw_violations:
        # Reconstruct lightweight records from summary counts
        for vtype, count in by_type.items():
            for _ in range(count):
                violations.append({
                    "session": filename,
                    "violation_type": vtype,
                    "severity": "unknown",
                    "line": "",
                    "line_number": 0,
                    "pattern": "",
                })

    return violations


# ---------------------------------------------------------------------------
# MAIN AGGREGATION
# ---------------------------------------------------------------------------


def run_batch_analysis() -> Dict[str, Any]:
    """
    Run cross-session aggregation over all existing analysis reports.

    Returns the aggregate report dict (also written to OUTPUT_FILE).
    """
    if not REPORTS_DIR.exists():
        print(f"ERROR: Reports directory not found: {REPORTS_DIR}", file=sys.stderr)
        sys.exit(1)

    report_files = sorted(REPORTS_DIR.glob("*.json"))
    if not report_files:
        print(f"ERROR: No JSON reports found in {REPORTS_DIR}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(report_files)} analysis reports in {REPORTS_DIR}")

    all_violations: List[Dict] = []
    session_summaries: Dict[str, Dict] = {}
    load_errors: List[str] = []

    # ── Load all reports ────────────────────────────────────────────────────
    for rfile in report_files:
        fname = rfile.name
        try:
            report = _load_report(rfile)
            violations = _extract_violations_from_report(report, fname)
            all_violations.extend(violations)

            session_summaries[fname] = {
                "violations_extracted": len(violations),
                "violation_types": list({v["violation_type"] for v in violations}),
                "path": str(rfile),
            }
            print(f"  ✔  {fname}: {len(violations)} violations")
        except Exception as exc:
            load_errors.append(f"{fname}: {exc}")
            print(f"  ✗  {fname}: {exc}", file=sys.stderr)

    # ── Aggregate counters ──────────────────────────────────────────────────
    violations_by_type: Counter = Counter(
        v["violation_type"] for v in all_violations
    )
    violations_by_severity: Counter = Counter(
        v["severity"] for v in all_violations
    )

    # Sessions per violation type (for SYSTEMIC detection)
    sessions_per_type: Dict[str, set] = defaultdict(set)
    for v in all_violations:
        sessions_per_type[v["violation_type"]].add(v["session"])

    systemic_patterns = {
        vtype: sorted(sessions)
        for vtype, sessions in sessions_per_type.items()
        if len(sessions) >= SYSTEMIC_THRESHOLD
    }

    # Violation density per session (violations / 1 session unit)
    density_per_session = {
        fname: data["violations_extracted"]
        for fname, data in session_summaries.items()
    }
    top_sessions_by_density = sorted(
        density_per_session.items(), key=lambda kv: kv[1], reverse=True
    )[:10]

    # Most frequent violation patterns
    most_frequent = violations_by_type.most_common(10)

    # ── Build output ────────────────────────────────────────────────────────
    aggregate = {
        "metadata": {
            "schema": "batch-analysis/1.0",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "total_sessions_analyzed": len(report_files),
            "sessions_with_load_errors": len(load_errors),
            "total_violations_extracted": len(all_violations),
            "systemic_threshold": SYSTEMIC_THRESHOLD,
        },
        "violations_by_type": dict(violations_by_type.most_common()),
        "violations_by_severity": dict(violations_by_severity.most_common()),
        "most_frequent_patterns": [
            {"violation_type": vt, "count": ct} for vt, ct in most_frequent
        ],
        "top_sessions_by_violation_density": [
            {"session": s, "violations": n} for s, n in top_sessions_by_density
        ],
        "systemic_patterns": {
            vtype: {
                "session_count": len(sessions),
                "sessions": sessions,
                "classification": "SYSTEMIC",
            }
            for vtype, sessions in systemic_patterns.items()
        },
        "session_summaries": session_summaries,
        "load_errors": load_errors,
    }

    # SHA-256 proof of aggregate content (excluding the hash field itself)
    proof_input = json.dumps(aggregate, sort_keys=True)
    aggregate["aggregate_sha256"] = _sha256(proof_input)

    # ── Write output ────────────────────────────────────────────────────────
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(aggregate, fh, indent=2, ensure_ascii=False)

    print(f"\n✔ Aggregate report written to: {OUTPUT_FILE}")
    print(f"  Total violations : {len(all_violations)}")
    print(f"  Systemic patterns: {len(systemic_patterns)}")
    print(f"  Unique types     : {len(violations_by_type)}")
    print(f"  SHA-256          : {aggregate['aggregate_sha256'][:16]}…")

    return aggregate


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_batch_analysis()

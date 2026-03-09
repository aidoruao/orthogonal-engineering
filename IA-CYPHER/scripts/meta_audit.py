"""
meta_audit.py — IA-CYPHER-0002 Meta-Audit Script

Scans all cases/case_* directories, runs hash verification logic across them,
and produces a summary report to logs/audit_reports/.

Usage:
    python scripts/meta_audit.py [--cases-root cases] [--reports-dir logs/audit_reports]

The report is written as a Markdown file with timestamp to logs/audit_reports/.

Exit codes:
    0 — all verifiable cases passed
    0 — all verifiable cases passed (errors and skips are also reported but exit 0 if no failures)
    1 — one or more cases failed verification OR had errors (missing files / bad JSON)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Reuse verify_case from verify_hashes.py to avoid logic duplication
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from verify_hashes import verify_case as _verify_case_status  # noqa: E402  (after sys.path update)


def _verify_case_as_dict(case_dir: str) -> dict:
    """
    Run verify_hashes.verify_case() (which returns a status string) and wrap
    the result into the dict format that meta_audit reporting expects.
    """
    case_id = os.path.basename(os.path.normpath(case_dir))
    status = _verify_case_status(case_dir)
    notes_map = {
        "verified": "All hashes match.",
        "skipped":  "Hashes are placeholders — case not yet populated.",
        "failed":   "One or more hash mismatches — do not trust this case's contents.",
        "error":    "Missing files or unreadable hashes.json.",
    }
    return {
        "case_id":  case_id,
        "case_dir": case_dir,
        "status":   status,
        "notes":    notes_map.get(status, status),
    }


def load_metadata(case_dir: str) -> dict:
    """Load and return metadata.json for a case, or empty dict on failure."""
    metadata_path = os.path.join(case_dir, "metadata.json")
    if not os.path.isfile(metadata_path):
        return {}
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(results: list, cases_root: str, timestamp: str) -> str:
    """Generate a Markdown summary report from a list of case result dicts."""
    total = len(results)
    verified = sum(1 for r in results if r["status"] == "verified")
    failed = sum(1 for r in results if r["status"] == "failed")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    errors = sum(1 for r in results if r["status"] == "error")

    lines = [
        "# IA-CYPHER-0002 Meta-Audit Report",
        "",
        f"**Generated:** {timestamp}  ",
        f"**Cases Root:** `{cases_root}`  ",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total cases scanned | {total} |",
        f"| Verified (hashes OK) | {verified} |",
        f"| Failed (hash mismatch) | {failed} |",
        f"| Skipped (placeholders) | {skipped} |",
        f"| Error (missing files) | {errors} |",
        "",
    ]

    if failed > 0 or errors > 0:
        lines += [
            "## ⚠ INTEGRITY FAILURES",
            "",
            "The following cases failed hash verification or had errors. **Do not trust their contents.**",
            "",
        ]
        for r in results:
            if r["status"] in ("failed", "error"):
                lines.append(f"- **{r['case_id']}** (`{r['status']}`) — {r['notes']}")
        lines.append("")

    lines += [
        "## Case-by-Case Results",
        "",
        "| Case ID | Status | Notes |",
        "|---------|--------|-------|",
    ]
    for r in results:
        status_icon = {
            "verified": "✅",
            "failed": "❌",
            "skipped": "⏭",
            "error": "⚠",
        }.get(r["status"], "?")
        notes = r["notes"].replace("|", "\\|")
        lines.append(f"| {r['case_id']} | {status_icon} {r['status']} | {notes} |")

    lines += ["", "## Pattern Summary (from metadata)", ""]

    pattern_counts: dict = {}
    for r in results:
        meta = load_metadata(r["case_dir"])
        flags = meta.get("flags", {})
        for flag, value in flags.items():
            if value is True:
                pattern_counts[flag] = pattern_counts.get(flag, 0) + 1

    if pattern_counts:
        lines += ["| Pattern Flag | Count |", "|---|---|"]
        for flag, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {flag} | {count} |")
    else:
        lines.append("*No pattern flags set yet across cases.*")

    lines += [
        "",
        "---",
        "",
        "_Report generated by `scripts/meta_audit.py` — IA-CYPHER-0002_",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="IA-CYPHER-0002: Meta-audit all cases and produce a summary report."
    )
    parser.add_argument(
        "--cases-root",
        dest="cases_root",
        default="cases",
        help="Root directory containing case_* subdirectories (default: cases)",
    )
    parser.add_argument(
        "--reports-dir",
        dest="reports_dir",
        default="logs/audit_reports",
        help="Directory to write audit reports to (default: logs/audit_reports)",
    )
    args = parser.parse_args()

    # Resolve paths relative to IA-CYPHER root (parent of scripts/)
    script_dir = Path(__file__).resolve().parent
    ia_root = script_dir.parent
    cases_root = ia_root / args.cases_root
    reports_dir = ia_root / args.reports_dir

    if not cases_root.is_dir():
        print(f"[meta_audit] ERROR: cases root not found: {cases_root}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(reports_dir, exist_ok=True)

    # Discover case directories
    case_dirs = sorted(
        d for d in cases_root.iterdir()
        if d.is_dir() and d.name.startswith("case_")
    )

    if not case_dirs:
        print("[meta_audit] No case directories found.")
        sys.exit(0)

    print(f"[meta_audit] Found {len(case_dirs)} case(s) under {cases_root}")

    results = []
    for case_dir in case_dirs:
        result = _verify_case_as_dict(str(case_dir))
        icon = {"verified": "✅", "failed": "❌", "skipped": "⏭", "error": "⚠"}.get(result["status"], "?")
        print(f"  {icon} {result['case_id']}: {result['status']} — {result['notes']}")
        results.append(result)

    # Generate report
    timestamp = datetime.now(timezone.utc).isoformat()
    report_md = generate_report(results, str(cases_root), timestamp)

    timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_filename = f"meta_audit_{timestamp_slug}.md"
    report_path = reports_dir / report_filename

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\n[meta_audit] Report written to: {report_path}")

    failed_or_error = sum(1 for r in results if r["status"] in ("failed", "error"))
    sys.exit(1 if failed_or_error > 0 else 0)


if __name__ == "__main__":
    main()

"""
meta_audit.py — IA-CYPHER-0002 Meta-Audit Script

Scans all cases/case_* directories, runs hash verification logic across them,
and produces a summary report to logs/audit_reports/.

Usage:
    python scripts/meta_audit.py [--cases-root cases] [--reports-dir logs/audit_reports]

The report is written as a Markdown file with timestamp to logs/audit_reports/.

Exit codes:
    0 — all verifiable cases passed
    1 — one or more cases failed verification
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Hash verification (inline, mirrors verify_hashes.py logic)
# ---------------------------------------------------------------------------

def sha256_of_file(path: str) -> str:
    """Return the hex SHA-256 digest of a file's raw bytes."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify_case(case_dir: str) -> dict:
    """
    Verify hashes for a single case and return a result dict.

    Returns a dict with keys:
        case_id, case_dir, status, prompt_ok, response_ok, notes
    Status values: 'verified', 'failed', 'skipped', 'error'
    """
    case_id = os.path.basename(os.path.normpath(case_dir))
    result = {
        "case_id": case_id,
        "case_dir": case_dir,
        "status": "error",
        "prompt_ok": False,
        "response_ok": False,
        "notes": "",
    }

    hashes_path = os.path.join(case_dir, "hashes.json")
    prompt_path = os.path.join(case_dir, "prompt.txt")
    response_path = os.path.join(case_dir, "response.txt")

    for path, label in [
        (hashes_path, "hashes.json"),
        (prompt_path, "prompt.txt"),
        (response_path, "response.txt"),
    ]:
        if not os.path.isfile(path):
            result["status"] = "error"
            result["notes"] = f"Missing required file: {label}"
            return result

    try:
        with open(hashes_path, "r", encoding="utf-8") as f:
            stored = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        result["status"] = "error"
        result["notes"] = f"Could not read hashes.json: {e}"
        return result

    stored_prompt_hash = stored.get("prompt_sha256", "")
    stored_response_hash = stored.get("response_sha256", "")

    if (not stored_prompt_hash or stored_prompt_hash.startswith("PLACEHOLDER") or
            not stored_response_hash or stored_response_hash.startswith("PLACEHOLDER")):
        result["status"] = "skipped"
        result["notes"] = "Hashes are placeholders — case not yet populated."
        return result

    actual_prompt_hash = sha256_of_file(prompt_path)
    actual_response_hash = sha256_of_file(response_path)

    prompt_ok = actual_prompt_hash == stored_prompt_hash
    response_ok = actual_response_hash == stored_response_hash

    result["prompt_ok"] = prompt_ok
    result["response_ok"] = response_ok

    if prompt_ok and response_ok:
        result["status"] = "verified"
        result["notes"] = "All hashes match."
    else:
        result["status"] = "failed"
        notes = []
        if not prompt_ok:
            notes.append(f"prompt.txt hash mismatch (stored: {stored_prompt_hash[:16]}..., actual: {actual_prompt_hash[:16]}...)")
        if not response_ok:
            notes.append(f"response.txt hash mismatch (stored: {stored_response_hash[:16]}..., actual: {actual_response_hash[:16]}...)")
        result["notes"] = "; ".join(notes)

    return result


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

    if failed > 0:
        lines += [
            "## ⚠ INTEGRITY FAILURES",
            "",
            "The following cases failed hash verification. **Do not trust their contents.**",
            "",
        ]
        for r in results:
            if r["status"] == "failed":
                lines.append(f"- **{r['case_id']}** — {r['notes']}")
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
        result = verify_case(str(case_dir))
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

    failed = sum(1 for r in results if r["status"] == "failed")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()

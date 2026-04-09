#!/usr/bin/env python3
"""CLI Session Usage Tracker — Glass-Box Audit Trail.

Logs Kimi CLI session metadata for sovereign audit trail.
All values are Fraction-based (no floats). Output is JSONL.

Usage:
    python3 tools/session_tracking/cli_usage_tracker.py \
        --session-id c223de88 \
        --context-used 169600 \
        --context-total 262100 \
        --domains-processed 10 \
        --commits 4
"""

import json
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path
from fractions import Fraction


def get_current_commit_hash() -> str:
    """Get HEAD commit hash."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()[:12]
    except Exception:
        return "unknown"


def log_session(
    session_id: str,
    context_used: int,
    context_total: int,
    domains_processed: int,
    commits: int,
    notes: str = "",
) -> dict:
    """Log a CLI session entry."""
    pct_num = context_used * 1000 // context_total
    pct = f"{pct_num // 10}.{pct_num % 10}%"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "context_used": context_used,
        "context_total": context_total,
        "percentage": pct,
        "domains_processed": domains_processed,
        "commits": commits,
        "commit_hash": get_current_commit_hash(),
        "notes": notes,
        "entry_hash": "",
    }

    entry["entry_hash"] = hashlib.sha256(
        json.dumps(entry, sort_keys=True).encode()
    ).hexdigest()[:16]

    log_path = Path("logs/cli_usage.jsonl")
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Logged: {session_id} ({pct} context, {domains_processed} domains, {commits} commits)")
    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log CLI session usage")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--context-used", type=int, required=True)
    parser.add_argument("--context-total", type=int, default=262100)
    parser.add_argument("--domains-processed", type=int, default=0)
    parser.add_argument("--commits", type=int, default=0)
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    log_session(
        args.session_id, args.context_used, args.context_total,
        args.domains_processed, args.commits, args.notes
    )

#!/usr/bin/env python3
"""
tools/state_witness/alert_on_failure.py — State Witness Failure Alerting (P3)

Takes the exit code and output from generate_feed_entry.py --verify.
If the exit code is non-zero, creates a structured alert JSON with:
  - timestamp
  - failure_type
  - stderr content
  - last known good row number
  - recommended action

Outputs to stdout (for CI capture) and optionally appends to
state_witness_alerts.jsonl (append-only).

Usage (CI):
    python tools/state_witness/generate_feed_entry.py --verify \
        2>verify_stderr.txt; \
    python tools/state_witness/alert_on_failure.py \
        --exit-code $? \
        --stderr-file verify_stderr.txt \
        --alerts-file state_witness_alerts.jsonl

Usage (from Python):
    from tools.state_witness.alert_on_failure import build_alert, maybe_alert

Standard: Yeshua Standard — OBS-1, OBS-2 (state witness observability)
Falsifies if: A non-zero exit code produces no alert JSON on stdout.
falsifies_if: non_zero_exit_produces_no_alert_json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Optional

from axioms.logic import ProofObject


def _classify_failure(stderr_content: str) -> str:
    """
    Classify a feed integrity failure from stderr text.

    Standard: INT-001 (feed chain integrity)
    Falsifies if: unknown failure type returned for recognisable error patterns.
    falsifies_if: unknown_type_for_recognised_error

    Returns a short failure_type string for the alert record.
    """
    content_lower = stderr_content.lower()
    if "chain" in content_lower or "prev_entry_hash" in content_lower:
        return "chain_break"
    if "row count" in content_lower or "monotonic" in content_lower:
        return "monotonic_violation"
    if "duplicate" in content_lower:
        return "duplicate_entry"
    if "genesis" in content_lower:
        return "genesis_row_error"
    if "permission" in content_lower or "cannot write" in content_lower:
        return "write_permission_error"
    if "not found" in content_lower or "no such file" in content_lower:
        return "feed_file_missing"
    return "unknown_integrity_failure"


def _last_good_row(alerts_file: Optional[Path]) -> int:
    """
    Read the most recent alert file to find the last known good row number.

    Standard: OBS-1 (observability)
    Falsifies if: returns -1 when a valid alerts file exists with row data.
    falsifies_if: returns_negative_one_when_valid_alerts_exist
    """
    if alerts_file is None or not alerts_file.exists():
        return -1
    try:
        last_row = -1
        with alerts_file.open() as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    entry = json.loads(line)
                    row = entry.get("last_known_good_row", -1)
                    if isinstance(row, int) and row >= 0:
                        last_row = row
                except json.JSONDecodeError:
                    continue
        return last_row
    except OSError:
        return -1


def build_alert(
    exit_code: int,
    stderr_content: str,
    last_known_good_row: int = -1,
) -> dict[str, object]:
    """
    Build a structured alert dict from verify failure data.

    Standard: OBS-1, OBS-2 (state witness observability)
    Falsifies if: alert dict missing required keys (timestamp, failure_type,
        exit_code, stderr_excerpt, recommended_action).
    falsifies_if: alert_dict_missing_required_keys

    Returns:
        dict with keys: timestamp, failure_type, exit_code, stderr_excerpt,
        last_known_good_row, recommended_action
    """
    ts = datetime.now(tz=timezone.utc).isoformat()
    failure_type = _classify_failure(stderr_content)

    recommended_actions: dict[str, str] = {
        "chain_break": (
            "Chain integrity violated. Do NOT append new rows. "
            "Inspect AGENT_FEED.md manually. Run generate_feed_entry.py --verify "
            "to locate the broken link."
        ),
        "monotonic_violation": (
            "Row count did not increase after write-back. "
            "Check for concurrent writers or non-fast-forward push failures."
        ),
        "duplicate_entry": (
            "Duplicate commit SHA detected. CI may be re-running on the same commit. "
            "Check concurrency group in pr40-canonical-presence.yml."
        ),
        "genesis_row_error": (
            "Genesis row (S(0)) appears malformed. "
            "The first row must have prev_entry_hash='' (empty string)."
        ),
        "write_permission_error": (
            "Cannot write to AGENT_FEED.md. "
            "Check repository permissions and GITHUB_TOKEN scope."
        ),
        "feed_file_missing": (
            "AGENT_FEED.md not found. "
            "Ensure the file exists and the workflow checks out the repo correctly."
        ),
        "unknown_integrity_failure": (
            "Unknown integrity failure. Inspect full stderr for details. "
            "Run generate_feed_entry.py --verify locally with verbose output."
        ),
    }

    # Use Fraction for row arithmetic (no floats)
    row_fraction = Fraction(last_known_good_row) if last_known_good_row >= 0 else Fraction(-1)

    return {
        "timestamp": ts,
        "failure_type": failure_type,
        "exit_code": exit_code,
        "stderr_excerpt": stderr_content[:500],
        "last_known_good_row": int(row_fraction),
        "recommended_action": recommended_actions.get(
            failure_type,
            recommended_actions["unknown_integrity_failure"],
        ),
    }


def maybe_alert(
    exit_code: int,
    stderr_content: str,
    alerts_file: Optional[Path] = None,
) -> tuple[bool, ProofObject]:
    """
    Emit an alert if exit_code is non-zero. Append to alerts_file if provided.

    Standard: OBS-1, OBS-2 (state witness observability)
    Falsifies if: returns True (alert emitted) when exit_code is 0.
    falsifies_if: alert_emitted_for_zero_exit_code

    Returns:
        Tuple of (alert_emitted: bool, ProofObject)
    """
    if exit_code == 0:
        proof = ProofObject(
            rule="NoAlertRule",
            premises=["exit_code == 0"],
            conclusion="No alert required — feed integrity verified.",
        )
        return False, proof

    last_row = _last_good_row(alerts_file)
    alert = build_alert(exit_code, stderr_content, last_row)

    # Emit to stdout for CI capture
    print(json.dumps(alert))

    # Append to alerts file if provided
    if alerts_file is not None:
        try:
            with alerts_file.open("a") as fh:
                fh.write(json.dumps(alert) + "\n")
        except OSError as exc:
            sys.stderr.write(f"WARNING: could not write to {alerts_file}: {exc}\n")

    proof = ProofObject(
        rule="AlertEmittedRule",
        premises=[
            f"exit_code = {exit_code}",
            f"failure_type = {alert['failure_type']}",
            f"last_known_good_row = {alert['last_known_good_row']}",
        ],
        conclusion=(
            f"Alert emitted: {alert['failure_type']}. "
            f"Action: {alert['recommended_action'][:80]}..."
        ),
    )
    return True, proof


def main() -> int:
    """
    CLI entry point.

    Standard: OBS-1, OBS-2 (state witness observability)
    Falsifies if: exits 0 when alert was emitted (alert=failure).
    falsifies_if: exits_zero_when_alert_emitted

    Returns exit code: 0 = no alert (healthy), 1 = alert emitted (failure).
    """
    parser = argparse.ArgumentParser(
        description="Emit structured alert when feed integrity check fails."
    )
    parser.add_argument(
        "--exit-code",
        type=int,
        required=True,
        help="Exit code from generate_feed_entry.py --verify",
    )
    parser.add_argument(
        "--stderr-file",
        type=Path,
        default=None,
        help="File containing stderr output from the verify command",
    )
    parser.add_argument(
        "--stderr-text",
        type=str,
        default="",
        help="Inline stderr text (alternative to --stderr-file)",
    )
    parser.add_argument(
        "--alerts-file",
        type=Path,
        default=None,
        help="Append-only JSONL file to record alerts (e.g. state_witness_alerts.jsonl)",
    )

    args = parser.parse_args()

    stderr_content = args.stderr_text
    if args.stderr_file is not None and args.stderr_file.exists():
        try:
            stderr_content = args.stderr_file.read_text()
        except OSError as exc:
            sys.stderr.write(f"WARNING: could not read {args.stderr_file}: {exc}\n")

    alert_emitted, _proof = maybe_alert(
        exit_code=args.exit_code,
        stderr_content=stderr_content,
        alerts_file=args.alerts_file,
    )

    return 1 if alert_emitted else 0


if __name__ == "__main__":
    sys.exit(main())

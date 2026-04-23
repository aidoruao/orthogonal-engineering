"""tools/append_consent.py — Consent log appender for SOP-AI-HANDSHAKE-1.0.

Appends a SHA-256-hashed JSONL consent entry to
``pr47_stewardship/witness/consent_log.jsonl``.

Usage:
    python tools/append_consent.py \\
        --candidate-id <id> \\
        --authoriser <authoriser> \\
        --action <action> \\
        --scope-glob <glob> \\
        --justification <text> \\
        [--rule-exceptions <exc1,exc2>] \\
        [--timestamp <iso8601>]

Standard: Yeshua / Glass-Box / Orthogonal Engineering

falsifies_if: appended entry lacks SHA-256 hash or timestamp is not ISO-8601.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONSENT_LOG = REPO_ROOT / "pr47_stewardship" / "witness" / "consent_log.jsonl"


def _sha256(text: str) -> str:
    """Return the hex SHA-256 digest of the UTF-8 encoded text.

    Falsifies if: the returned string is not 64 lowercase hex characters.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_consent_entry(
    candidate_id: str,
    authoriser: str,
    action: str,
    scope_glob: str,
    justification: str,
    rule_exceptions: list[str] | None = None,
    timestamp: str | None = None,
) -> dict:
    """Construct a SOP-AI-HANDSHAKE-1.0 consent record.

    Hashes ``justification`` and ``scope_glob`` before storing. Appends
    a ``consent_hash`` over the full (pre-hash) record for tamper evidence.

    Args:
        candidate_id: Identifier for the agent being authorised.
        authoriser: GitHub handle of the authorising human (e.g. ``"@aidoruao"``).
        action: Short label for the approved action.
        scope_glob: Glob pattern covering files in scope.
        justification: Human-readable justification for the consent.
        rule_exceptions: Optional list of rule names that are excepted.
        timestamp: ISO-8601 timestamp; defaults to current UTC time.

    Returns:
        Dict suitable for JSONL serialisation.

    Falsifies if: the returned dict is missing ``consent_hash``.
    """
    ts = timestamp or datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    exceptions: list[str] = rule_exceptions or []

    justification_hash = _sha256(justification)
    scope_hash = _sha256(scope_glob)

    record: dict = {
        "schema": "SOP-AI-HANDSHAKE-1.0",
        "candidate_id": candidate_id,
        "authoriser": authoriser,
        "action": action,
        "scope_glob": scope_glob,
        "rule_exceptions": exceptions,
        "justification": justification,
        "justification_hash": justification_hash,
        "scope_hash": scope_hash,
        "timestamp": ts,
    }

    # Consent hash covers all fields in sorted-key order (excluding itself).
    consent_hash = _sha256(json.dumps(record, sort_keys=True, ensure_ascii=True))
    record["consent_hash"] = consent_hash
    return record


def append_consent(entry: dict, log_path: Path = CONSENT_LOG) -> None:
    """Append a consent entry to the JSONL consent log.

    The log file is created if it does not exist.

    Falsifies if: the entry is not present in the log after this call.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True, ensure_ascii=True) + "\n")


def _main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Append a SOP-AI-HANDSHAKE-1.0 consent entry to the log."
    )
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--authoriser", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--scope-glob", required=True)
    parser.add_argument("--justification", required=True)
    parser.add_argument(
        "--rule-exceptions",
        default="",
        help="Comma-separated list of rule exceptions.",
    )
    parser.add_argument("--timestamp", default=None)
    args = parser.parse_args()

    exceptions = [e.strip() for e in args.rule_exceptions.split(",") if e.strip()]
    entry = build_consent_entry(
        candidate_id=args.candidate_id,
        authoriser=args.authoriser,
        action=args.action,
        scope_glob=args.scope_glob,
        justification=args.justification,
        rule_exceptions=exceptions,
        timestamp=args.timestamp,
    )
    append_consent(entry)
    print(json.dumps(entry, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(_main())

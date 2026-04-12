"""Append a consent entry to the repository consent log.

Consent entries are appended to:
    pr47_stewardship/witness/consent_log.jsonl

The log is append-only — existing entries are never modified.

Usage
-----
    python tools/append_consent.py \\
        --candidate-id codex-copilot-pr118 \\
        --action multi_agent_onboarding_suite \\
        --scope-glob "AGENT_ONBOARDING.md,agents/**,tools/session_id.py" \\
        --justification "PR #118: Multi-agent onboarding suite"

Optional flags::

    --authoriser @aidoruao          (default)
    --rule-exceptions mass_change   (comma-separated; default: mass_change)

The tool computes three SHA-256 hashes:
    justification_hash  — SHA-256(justification)
    scope_hash          — SHA-256(scope_glob)
    consent_hash        — SHA-256(JSON-serialised entry without consent_hash)

The completed entry is printed to stdout and appended to the log.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


CONSENT_LOG: Path = Path(__file__).parent.parent / "pr47_stewardship" / "witness" / "consent_log.jsonl"
SCHEMA: str = "SOP-AI-HANDSHAKE-1.0"


def sha256(text: str) -> str:
    """Return the lowercase hex SHA-256 digest of *text* (UTF-8 encoded)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_entry(
    *,
    candidate_id: str,
    authoriser: str,
    action: str,
    scope_glob: str,
    justification: str,
    rule_exceptions: list[str],
) -> dict[str, object]:
    """Construct a fully hashed consent log entry.

    Parameters
    ----------
    candidate_id:
        Identifier for the consenting agent (e.g. ``codex-copilot-pr118``).
    authoriser:
        GitHub handle of the authorising human (e.g. ``@aidoruao``).
    action:
        Short action slug (e.g. ``multi_agent_onboarding_suite``).
    scope_glob:
        Comma-separated glob patterns describing the scope of changes.
    justification:
        Human-readable justification for the change.
    rule_exceptions:
        List of rule-exception tags (e.g. ``["mass_change"]``).

    Returns
    -------
    dict
        Complete consent entry including ``justification_hash``,
        ``scope_hash``, ``timestamp``, and ``consent_hash``.
    """
    timestamp: str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry: dict[str, object] = {
        "schema": SCHEMA,
        "candidate_id": candidate_id,
        "authoriser": authoriser,
        "action": action,
        "scope_glob": scope_glob,
        "rule_exceptions": rule_exceptions,
        "justification": justification,
        "justification_hash": sha256(justification),
        "scope_hash": sha256(scope_glob),
        "timestamp": timestamp,
    }
    # consent_hash covers the full entry (without itself)
    entry["consent_hash"] = sha256(json.dumps(entry, sort_keys=True))
    return entry


def append_entry(entry: dict[str, object]) -> None:
    """Append *entry* as a single JSONL line to the consent log.

    Parameters
    ----------
    entry:
        Fully constructed consent entry dict.
    """
    CONSENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    line: str = json.dumps(entry)
    with CONSENT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def main() -> None:
    """Parse CLI arguments, build the entry, append it, and print it."""
    parser = argparse.ArgumentParser(
        description="Append a consent entry to the repository consent log.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--authoriser",
        default="@aidoruao",
        help="GitHub handle of the authorising human (default: @aidoruao)",
    )
    parser.add_argument(
        "--candidate-id",
        required=True,
        dest="candidate_id",
        help="Identifier for the consenting agent (e.g. codex-copilot-pr118)",
    )
    parser.add_argument(
        "--action",
        required=True,
        help="Short action slug (e.g. multi_agent_onboarding_suite)",
    )
    parser.add_argument(
        "--scope-glob",
        required=True,
        dest="scope_glob",
        help="Comma-separated glob patterns for the scope of changes",
    )
    parser.add_argument(
        "--justification",
        required=True,
        help="Human-readable justification for the change",
    )
    parser.add_argument(
        "--rule-exceptions",
        default="mass_change",
        dest="rule_exceptions",
        help="Comma-separated rule-exception tags (default: mass_change)",
    )

    args = parser.parse_args()
    exceptions: list[str] = [e.strip() for e in args.rule_exceptions.split(",") if e.strip()]

    entry = build_entry(
        candidate_id=args.candidate_id,
        authoriser=args.authoriser,
        action=args.action,
        scope_glob=args.scope_glob,
        justification=args.justification,
        rule_exceptions=exceptions,
    )
    append_entry(entry)
    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()

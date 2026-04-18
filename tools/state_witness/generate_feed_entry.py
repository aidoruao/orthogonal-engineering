#!/usr/bin/env python3
"""
tools/state_witness/generate_feed_entry.py — PR #40 State Witness Layer

Computes a canonical, cryptographically anchored feed entry from the frozen
invariant spec (resilience/invariant_spec_v2.freeze) and appends it to the
append-only ledger file AGENT_FEED.md at the repository root.

Usage:
    python tools/state_witness/generate_feed_entry.py [--verify] [--dry-run]

Modes:
    (default)   Append a new feed entry (idempotent: skips if commit already recorded)
    --verify    Verify feed chain integrity (entry_hash linkage)
    --dry-run   Print the entry that would be appended without writing

Environment:
    GITHUB_SHA   Commit SHA to embed in the entry (optional; falls back to git)
    GITHUB_REF   Git ref (e.g. refs/heads/main)
    PYTHONHASHSEED must be set to a fixed value for determinism in CI

Author: Orthogonal Engineering
PR: #40
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FREEZE_PATH = REPO_ROOT / "resilience" / "invariant_spec_v2.freeze"
AGENT_FEED_PATH = REPO_ROOT / "AGENT_FEED.md"
INVARIANT_SPEC_VERSION = "v2"
PR = 40

FEED_HEADER = (
    "<!-- AGENT_FEED.md — append-only state witness ledger (PR #40) -->\n"
    "<!-- Do not edit existing rows. Append new rows only. -->\n"
    "\n"
    "# AGENT_FEED — State Witness Ledger\n"
    "\n"
    "| timestamp | freeze_hash | merkle_root | invariant_spec_version"
    " | source_paths | commit_sha | prev_entry_hash | entry_hash |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_normalized(path: Path) -> bytes:
    """Read file bytes with CRLF normalised to LF for cross-platform parity."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def _get_commit_sha() -> str:
    """Return commit SHA from GITHUB_SHA env var or from git HEAD."""
    sha = os.environ.get("GITHUB_SHA", "")
    if sha:
        return sha.strip()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return "unknown"


def _get_git_ref() -> str:
    """Return git ref from GITHUB_REF env var or from git symbolic-ref."""
    ref = os.environ.get("GITHUB_REF", "")
    if ref:
        return ref.strip()
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return "unknown"


def compute_freeze_hash() -> str:
    """Compute SHA-256 of the freeze file (CRLF-normalised)."""
    return _sha256(_read_normalized(FREEZE_PATH))


def load_freeze() -> dict:
    """Load and return the parsed freeze file."""
    return json.loads(FREEZE_PATH.read_text(encoding="utf-8"))


def build_feed_entry(
    *,
    timestamp: str | None = None,
    commit_sha: str | None = None,
    git_ref: str | None = None,
    prev_entry_hash: str = "",
) -> dict:
    """Build a deterministic feed entry dict.

    All fields except *timestamp* are fully deterministic given the same repo
    state.  *timestamp* is provided externally so callers can pin it in tests.

    *git_ref* is accepted for caller convenience but is **not** included in the
    returned dict because it is not written to the AGENT_FEED.md ledger row.
    The ledger schema has exactly eight columns; git_ref is not one of them.
    Omitting it from the dict prevents silent information loss and makes the
    producer/consumer contract unambiguous.

    Returns a dict with keys:
        timestamp, freeze_hash, merkle_root, invariant_spec_version,
        source_paths, commit_sha, prev_entry_hash, entry_hash
    """
    freeze = load_freeze()
    freeze_hash = compute_freeze_hash()
    merkle_root = freeze.get("merkle_root", "")
    source_paths = ",".join(
        sorted(e["path"] for e in freeze.get("spec_files", []))
    )

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if commit_sha is None:
        commit_sha = _get_commit_sha()
    # git_ref is resolved but intentionally excluded from the returned dict.
    # The ledger schema has exactly 8 columns; git_ref is not one of them.
    # Resolving it here keeps fallback logic in one place for callers that need it.
    _resolved_git_ref = git_ref if git_ref is not None else _get_git_ref()
    _ = _resolved_git_ref  # not stored in entry to avoid ghost-field confusion

    # entry_hash covers all fields including timestamp; timestamp is intentionally
    # included so that re-runs at different times produce distinct entry hashes,
    # preventing accidental hash collisions across runs on the same commit.
    entry_payload = "|".join([
        timestamp,
        freeze_hash,
        merkle_root,
        INVARIANT_SPEC_VERSION,
        source_paths,
        commit_sha,
        prev_entry_hash,
    ])
    entry_hash = _sha256(entry_payload.encode("utf-8"))

    return {
        "timestamp": timestamp,
        "freeze_hash": freeze_hash,
        "merkle_root": merkle_root,
        "invariant_spec_version": INVARIANT_SPEC_VERSION,
        "source_paths": source_paths,
        "commit_sha": commit_sha,
        "prev_entry_hash": prev_entry_hash,
        "entry_hash": entry_hash,
    }


# ---------------------------------------------------------------------------
# AGENT_FEED.md I/O
# ---------------------------------------------------------------------------

def _parse_feed_rows(content: str) -> list[dict]:
    """Parse existing data rows from the markdown table, skipping header lines."""
    rows: list[dict] = []
    columns = [
        "timestamp", "freeze_hash", "merkle_root", "invariant_spec_version",
        "source_paths", "commit_sha", "prev_entry_hash", "entry_hash",
    ]
    in_table = False
    header_seen = False
    separator_seen = False
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "timestamp" in stripped and "freeze_hash" in stripped:
            in_table = True
            header_seen = True
            continue
        if in_table and header_seen and not separator_seen and "---" in stripped:
            separator_seen = True
            continue
        if in_table and header_seen and separator_seen:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= len(columns):
                rows.append(dict(zip(columns, cells[: len(columns)])))
    return rows


def read_feed() -> list[dict]:
    """Return all existing rows from AGENT_FEED.md."""
    if not AGENT_FEED_PATH.exists():
        return []
    return _parse_feed_rows(AGENT_FEED_PATH.read_text(encoding="utf-8"))


def _entry_to_row(entry: dict) -> str:
    """Format a feed entry as a markdown table row."""
    cells = [
        entry["timestamp"],
        entry["freeze_hash"],
        entry["merkle_root"],
        entry["invariant_spec_version"],
        entry["source_paths"],
        entry["commit_sha"],
        entry["prev_entry_hash"],
        entry["entry_hash"],
    ]
    return "| " + " | ".join(cells) + " |"


def is_duplicate(entry: dict, existing_rows: list[dict]) -> bool:
    """Return True if this commit_sha is already recorded in the feed."""
    commit_sha = entry["commit_sha"]
    if commit_sha in ("unknown", ""):
        # Without a commit SHA we cannot guarantee idempotency; always append
        return False
    return any(row.get("commit_sha") == commit_sha for row in existing_rows)


def append_to_feed(entry: dict, *, dry_run: bool = False) -> bool:
    """Append *entry* to AGENT_FEED.md.

    Returns True if the entry was written, False if it was skipped (duplicate).
    Raises if AGENT_FEED.md cannot be initialised or written.
    """
    existing_rows = read_feed()

    if is_duplicate(entry, existing_rows):
        return False

    row_line = _entry_to_row(entry) + "\n"

    if dry_run:
        print(row_line, end="")
        return True

    if not AGENT_FEED_PATH.exists():
        AGENT_FEED_PATH.write_text(FEED_HEADER, encoding="utf-8")

    with AGENT_FEED_PATH.open("a", encoding="utf-8") as fh:
        fh.write(row_line)

    return True


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_feed_integrity() -> tuple[bool, list[str]]:
    """Verify the prev_entry_hash chain in AGENT_FEED.md.

    Returns (ok, errors).  ok is True only when there are no errors.
    """
    rows = read_feed()
    errors: list[str] = []

    if not rows:
        print("AGENT_FEED.md has no data rows — nothing to verify.")
        return True, []

    prev_hash = ""
    for i, row in enumerate(rows):
        recorded_prev = row.get("prev_entry_hash", "")
        if recorded_prev != prev_hash:
            errors.append(
                f"Row {i}: prev_entry_hash mismatch — "
                f"expected {prev_hash!r}, got {recorded_prev!r}"
            )
        # Recompute entry_hash for this row
        entry_payload = "|".join([
            row.get("timestamp", ""),
            row.get("freeze_hash", ""),
            row.get("merkle_root", ""),
            row.get("invariant_spec_version", ""),
            row.get("source_paths", ""),
            row.get("commit_sha", ""),
            recorded_prev,
        ])
        computed_hash = _sha256(entry_payload.encode("utf-8"))
        recorded_hash = row.get("entry_hash", "")
        if computed_hash != recorded_hash:
            errors.append(
                f"Row {i}: entry_hash mismatch — "
                f"computed {computed_hash!r}, recorded {recorded_hash!r}"
            )
        prev_hash = recorded_hash

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PR #40 State Witness: generate or verify AGENT_FEED.md entries."
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify feed chain integrity instead of appending a new entry.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print entry that would be appended without modifying AGENT_FEED.md.",
    )
    args = parser.parse_args(argv)

    if args.verify:
        ok, errors = verify_feed_integrity()
        if ok:
            rows = read_feed()
            print(f"Feed integrity OK — {len(rows)} row(s) verified.")
            return 0
        else:
            for err in errors:
                print(f"ERROR: {err}", file=sys.stderr)
            return 1

    # Build entry
    existing_rows = read_feed()
    prev_entry_hash = existing_rows[-1]["entry_hash"] if existing_rows else ""
    entry = build_feed_entry(prev_entry_hash=prev_entry_hash)

    if args.dry_run:
        print(json.dumps(entry, indent=2))
        append_to_feed(entry, dry_run=True)
        return 0

    written = append_to_feed(entry)
    if written:
        print(f"Appended entry to AGENT_FEED.md: entry_hash={entry['entry_hash']}")
    else:
        print(
            f"Entry skipped (idempotent): commit_sha={entry['commit_sha']} "
            f"already recorded in AGENT_FEED.md."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

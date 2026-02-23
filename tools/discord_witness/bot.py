#!/usr/bin/env python3
"""
tools/discord_witness/bot.py — PR #40 Discord Derivative Witness Bot

A stateless, read-only bot that mirrors the city's self-witness onto Discord.
The bot has no state, no memory, and no platform loyalty.  It fetches
AGENT_FEED.md from GitHub, verifies the hash chain, and posts the latest
verified entry to a Discord webhook.

The bot is NOT an agent.  It is a speaking mirror: deterministic,
ephemeral, and disposable.  Discord is a temporary viewport into a
self-verifying structure.

Usage:
    # Dry-run: compute speech and print, do not post
    python tools/discord_witness/bot.py --dry-run

    # Post latest verified entry to Discord
    DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/... \\
        python tools/discord_witness/bot.py

    # Use a local feed file instead of fetching from GitHub
    python tools/discord_witness/bot.py --feed-path /path/to/AGENT_FEED.md --dry-run

Environment variables:
    DISCORD_WEBHOOK_URL   Discord webhook URL (required unless --dry-run)
    CITY_FEED_URL         Override the GitHub raw URL for AGENT_FEED.md
    CITY_FREEZE_URL       Override the GitHub raw URL for invariant_spec_v2.freeze

No third-party dependencies: uses only Python standard library.

Author: Orthogonal Engineering
PR: #40 extension (Discord Derivative Witness Layer)
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CITY_FEED_URL = (
    os.environ.get("CITY_FEED_URL")
    or "https://raw.githubusercontent.com/aidoruao/orthogonal-engineering/main/AGENT_FEED.md"
)
CITY_FREEZE_URL = (
    os.environ.get("CITY_FREEZE_URL")
    or "https://raw.githubusercontent.com/aidoruao/orthogonal-engineering/main/resilience/invariant_spec_v2.freeze"
)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

# HTTP timeout in seconds for all remote fetches
_HTTP_TIMEOUT = 15

# Columns in the AGENT_FEED.md markdown table (must match generate_feed_entry.py)
_FEED_COLUMNS = [
    "timestamp",
    "freeze_hash",
    "merkle_root",
    "invariant_spec_version",
    "source_paths",
    "commit_sha",
    "prev_entry_hash",
    "entry_hash",
]


# ---------------------------------------------------------------------------
# Feed fetching
# ---------------------------------------------------------------------------

def fetch_text(url: str) -> str:
    """Fetch plain text from *url* using stdlib urllib.  Raises on error."""
    req = urllib.request.Request(url, headers={"User-Agent": "orthogonal-engineering-witness/1.0"})
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
        return resp.read().decode("utf-8")


def load_feed_text(*, feed_path: Optional[Path] = None, url: str = CITY_FEED_URL) -> str:
    """Return the raw text of AGENT_FEED.md from local path or remote URL."""
    if feed_path is not None:
        return feed_path.read_text(encoding="utf-8")
    return fetch_text(url)


# ---------------------------------------------------------------------------
# Feed parsing
# ---------------------------------------------------------------------------

def parse_feed_rows(content: str) -> list[dict]:
    """Parse data rows from the AGENT_FEED.md markdown table."""
    rows: list[dict] = []
    header_seen = False
    separator_seen = False
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "timestamp" in stripped and "freeze_hash" in stripped:
            header_seen = True
            continue
        if header_seen and not separator_seen and "---" in stripped:
            separator_seen = True
            continue
        if header_seen and separator_seen:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= len(_FEED_COLUMNS):
                rows.append(dict(zip(_FEED_COLUMNS, cells[: len(_FEED_COLUMNS)])))
    return rows


# ---------------------------------------------------------------------------
# Hash chain verification
# ---------------------------------------------------------------------------

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_entry_hash(entry: dict) -> bool:
    """Recompute entry_hash from the row payload and compare to the recorded value."""
    payload = "|".join([
        entry.get("timestamp", ""),
        entry.get("freeze_hash", ""),
        entry.get("merkle_root", ""),
        entry.get("invariant_spec_version", ""),
        entry.get("source_paths", ""),
        entry.get("commit_sha", ""),
        entry.get("prev_entry_hash", ""),
    ])
    computed = _sha256(payload.encode("utf-8"))
    return computed == entry.get("entry_hash", "")


def verify_chain(rows: list[dict]) -> tuple[bool, list[str]]:
    """Verify the full prev_entry_hash chain.  Returns (ok, errors)."""
    errors: list[str] = []
    prev_hash = ""
    for i, row in enumerate(rows):
        recorded_prev = row.get("prev_entry_hash", "")
        if recorded_prev != prev_hash:
            errors.append(
                f"Row {i}: prev_entry_hash mismatch — "
                f"expected {prev_hash!r}, got {recorded_prev!r}"
            )
        if not verify_entry_hash(row):
            errors.append(f"Row {i}: entry_hash verification failed")
        prev_hash = row.get("entry_hash", "")
    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Deterministic speech computation
# ---------------------------------------------------------------------------

def compute_speech(entry: dict) -> str:
    """
    Deterministic speech: the bot says only what the city has witnessed.
    No creativity.  No engagement optimisation.  Pure derivative witness.
    """
    short_freeze = (entry.get("freeze_hash") or "")[:16]
    short_merkle = (entry.get("merkle_root") or "")[:16]
    short_entry = (entry.get("entry_hash") or "")[:16]
    short_commit = (entry.get("commit_sha") or "unknown")[:8]
    timestamp = entry.get("timestamp") or "unknown"
    spec_version = entry.get("invariant_spec_version") or "v2"

    return (
        f"**City Witness** ✅\n"
        f"```\n"
        f"timestamp : {timestamp}\n"
        f"commit    : {short_commit}\n"
        f"freeze    : {short_freeze}...\n"
        f"merkle    : {short_merkle}...\n"
        f"entry     : {short_entry}...\n"
        f"spec      : {spec_version}\n"
        f"```\n"
        f"Verify: <https://github.com/aidoruao/orthogonal-engineering/blob/main/AGENT_FEED.md>"
    )


# ---------------------------------------------------------------------------
# Discord webhook posting
# ---------------------------------------------------------------------------

def post_to_discord(webhook_url: str, content: str) -> None:
    """Post *content* to a Discord webhook using stdlib urllib only."""
    payload = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "orthogonal-engineering-witness/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
        status = resp.status
    if status not in (200, 204):
        raise RuntimeError(f"Discord webhook returned HTTP {status}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "PR #40 Discord Derivative Witness Bot — "
            "posts the latest verified AGENT_FEED.md entry to Discord."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print speech without posting to Discord.",
    )
    parser.add_argument(
        "--feed-path",
        type=Path,
        default=None,
        help="Path to a local AGENT_FEED.md (overrides remote fetch).",
    )
    parser.add_argument(
        "--feed-url",
        default=CITY_FEED_URL,
        help="Remote URL to fetch AGENT_FEED.md from.",
    )
    args = parser.parse_args(argv)

    # 1. Fetch feed
    try:
        feed_text = load_feed_text(feed_path=args.feed_path, url=args.feed_url)
    except (urllib.error.URLError, OSError) as exc:
        print(f"ERROR: could not load feed: {exc}", file=sys.stderr)
        return 1

    # 2. Parse rows
    rows = parse_feed_rows(feed_text)
    if not rows:
        print("Feed has no entries — city has not yet witnessed. Silent exit.", file=sys.stderr)
        return 0

    # 3. Verify chain
    ok, errors = verify_chain(rows)
    if not ok:
        for err in errors:
            print(f"CHAIN ERROR: {err}", file=sys.stderr)
        print(
            "Hash chain verification failed — bot is silent. "
            "The city's integrity must be restored before speaking.",
            file=sys.stderr,
        )
        return 1  # silent failure: bot does not speak unverified content

    # 4. Compute speech from latest entry
    latest = rows[-1]
    speech = compute_speech(latest)

    if args.dry_run:
        print(speech)
        return 0

    # 5. Post to Discord
    webhook_url = DISCORD_WEBHOOK_URL
    if not webhook_url:
        print(
            "ERROR: DISCORD_WEBHOOK_URL is not set. "
            "Use --dry-run to print speech without posting.",
            file=sys.stderr,
        )
        return 1

    try:
        post_to_discord(webhook_url, speech)
        print(f"Posted witness to Discord: entry_hash={latest.get('entry_hash', '')[:16]}...")
    except (urllib.error.URLError, RuntimeError) as exc:
        print(f"ERROR: Discord post failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
tools/discord_witness/verify_chain.py — Standalone Hash Chain Verifier

Verifies the entry_hash chain in AGENT_FEED.md without any side effects.
Can operate on a local file or fetch from GitHub.

This is deliberately kept separate from bot.py so that it can be used
independently by auditors, CI, or any downstream consumer.

Usage:
    # Verify local feed
    python tools/discord_witness/verify_chain.py

    # Verify local feed at a custom path
    python tools/discord_witness/verify_chain.py --feed-path /path/to/AGENT_FEED.md

    # Fetch and verify the live GitHub feed
    python tools/discord_witness/verify_chain.py --remote

Exit codes:
    0 — chain is intact
    1 — chain has errors or feed is unreachable

No third-party dependencies.

Author: Orthogonal Engineering
PR: #40 extension (Discord Derivative Witness Layer)
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from any directory by resolving sibling imports
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.discord_witness.bot import (
    CITY_FEED_URL,
    load_feed_text,
    parse_feed_rows,
    verify_chain,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify the hash chain integrity of AGENT_FEED.md."
    )
    parser.add_argument(
        "--feed-path",
        type=Path,
        default=_REPO_ROOT / "AGENT_FEED.md",
        help="Path to a local AGENT_FEED.md (default: repo root).",
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Fetch AGENT_FEED.md from GitHub instead of reading locally.",
    )
    parser.add_argument(
        "--feed-url",
        default=CITY_FEED_URL,
        help="Remote URL (only used with --remote).",
    )
    args = parser.parse_args(argv)

    try:
        if args.remote:
            feed_text = load_feed_text(url=args.feed_url)
        else:
            feed_text = load_feed_text(feed_path=args.feed_path)
    except (OSError, Exception) as exc:
        print(f"ERROR: could not load feed: {exc}", file=sys.stderr)
        return 1

    rows = parse_feed_rows(feed_text)
    if not rows:
        print("Feed has no data rows — nothing to verify.")
        return 0

    ok, errors = verify_chain(rows)
    if ok:
        print(f"Chain integrity OK — {len(rows)} row(s) verified.")
        return 0

    for err in errors:
        print(f"ERROR: {err}", file=sys.stderr)
    print(f"Chain integrity FAILED — {len(errors)} error(s).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

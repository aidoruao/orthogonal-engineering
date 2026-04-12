"""Generate a session ID for an AI agent working in this repository.

Usage
-----
    python tools/session_id.py --agent codex
    # Output: codex-20260412-3f7a8b2c

    SESSION=$(python tools/session_id.py --agent claude)
    git commit -m "feat: add invariant [Session: $SESSION]"

The session ID format is:
    <agent>-<YYYYMMDD>-<8-char-uuid4-prefix>

Supported agents: codex, claude, kimi, devin, gemini
"""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime, timezone


AGENTS: list[str] = ["codex", "claude", "kimi", "devin", "gemini"]


def generate_session_id(agent: str) -> str:
    """Generate a reproducible-format session ID for the given agent.

    Parameters
    ----------
    agent:
        One of the supported agent names (codex, claude, kimi, devin, gemini).

    Returns
    -------
    str
        Session ID in the format ``<agent>-<YYYYMMDD>-<8-char-uuid4-prefix>``.
        Example: ``codex-20260412-3f7a8b2c``
    """
    date_str: str = datetime.now(tz=timezone.utc).strftime("%Y%m%d")
    uid_prefix: str = uuid.uuid4().hex[:8]
    return f"{agent}-{date_str}-{uid_prefix}"


def main() -> None:
    """Parse CLI arguments and print the session ID to stdout."""
    parser = argparse.ArgumentParser(
        description="Generate a session ID for an AI agent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--agent",
        required=True,
        choices=AGENTS,
        help="Agent name (codex, claude, kimi, devin, gemini)",
    )
    args = parser.parse_args()
    print(generate_session_id(args.agent))


if __name__ == "__main__":
    main()

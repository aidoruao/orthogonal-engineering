"""tools/session_id.py — Agent session ID generator.

Generates a unique, human-readable session identifier in the format:
    <agent>-<YYYYMMDD>-<8-char-uuid4>

Usage:
    python tools/session_id.py [agent_name]

Standard: Yeshua / Glass-Box / Orthogonal Engineering

falsifies_if: generated session ID does not match <agent>-<YYYYMMDD>-<8-char-uuid4> format.
"""

from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone


def generate_session_id(agent: str = "agent") -> str:
    """Generate a session ID for the given agent name.

    Format: ``<agent>-<YYYYMMDD>-<8-char-uuid4>``

    Args:
        agent: Short identifier for the agent (e.g. ``"codex-copilot"``).

    Returns:
        A string such as ``"codex-copilot-20260412-a1b2c3d4"``.

    Falsifies if: the returned string does not match the expected format.
    """
    date_str = datetime.now(tz=timezone.utc).strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:8]
    return f"{agent}-{date_str}-{uid}"


if __name__ == "__main__":
    agent_name = sys.argv[1] if len(sys.argv) > 1 else "agent"
    print(generate_session_id(agent_name))

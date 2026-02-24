# pr47_stewardship/invariants/never_draw_attention.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# NeverDrawAttention invariant: commit messages must not contain trigger
# patterns that would draw attention to sensitive content categories.
#
# Commit messages should be neutral (e.g. "pr47: boundary adjustments").

from __future__ import annotations

import re
from typing import Iterable


# Patterns that would draw unwanted attention in commit messages.
# This list uses opaque structural descriptions, not content terms.
TRIGGER_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)sanitized"),
    re.compile(r"(?i)cleaned[_ -]?up"),
    re.compile(r"(?i)removed[_ -]?personal"),
    re.compile(r"(?i)\bpurged?\b"),
    re.compile(r"(?i)\bdeleted?\b.*\bsensitive\b"),
    re.compile(r"(?i)\bwipe[d]?\b"),
]


class NeverDrawAttentionViolation(Exception):
    """Raised when a commit message matches a trigger pattern."""


def check_commit_message(message: str) -> bool:
    """
    Assert that a single commit message does not match any trigger pattern.

    Returns True if the message is clean.
    Raises NeverDrawAttentionViolation on the first matching trigger.
    """
    for pattern in TRIGGER_PATTERNS:
        if pattern.search(message):
            raise NeverDrawAttentionViolation(
                f"NeverDrawAttention: commit message matches trigger "
                f"{pattern.pattern!r}: {message!r}"
            )
    return True


def check_commit_messages(messages: Iterable[str]) -> bool:
    """
    Assert that every message in messages passes check_commit_message.

    Returns True if all messages are clean.
    Raises NeverDrawAttentionViolation on the first offending message.
    """
    for msg in messages:
        check_commit_message(msg)
    return True

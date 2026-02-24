#!/usr/bin/env python3
"""
revocation/effects.py — Effect matrix for revocation.

On revocation:
  - REMOVE: write, merge, execute_with_consent, write_with_consent
  - KEEP: read, comment, suggest
  - Existing merges stand (past actions are not undone)
"""
from __future__ import annotations
from typing import List


CAPABILITIES_REMOVED_ON_REVOCATION = [
    "write",
    "merge",
    "execute_with_consent",
    "write_with_consent",
]

CAPABILITIES_KEPT_ON_REVOCATION = [
    "read",
    "comment",
    "suggest",
]

PAST_ACTIONS_STAND = True  # Existing merges and actions are not retroactively undone


def apply_revocation_effects(capabilities: List[str]) -> List[str]:
    """Return capability list after applying revocation effects."""
    return [c for c in capabilities if c in CAPABILITIES_KEPT_ON_REVOCATION]


def apply_restoration_effects(capabilities: List[str]) -> List[str]:
    """Return capability list after restoration (full capabilities restored)."""
    from pr50_bar_exam.ordination.certificate import CAPABILITIES_ON_PASS
    return list(CAPABILITIES_ON_PASS)

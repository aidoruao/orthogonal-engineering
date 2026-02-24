# pr46_agape_witness/invariants/always_recoverable.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# AlwaysRecoverable invariant: every failure state has a deterministic
# recovery path. The recovery path is represented by the existence of
# a grace period or a forgiveness record.

from __future__ import annotations

from typing import Any, Dict, Optional

from pr46_agape_witness.util.hashing import sha256_hash


def check_always_recoverable(
    agent_id: str,
    failure_state: Dict[str, Any],
    has_grace_period: bool,
    has_forgiveness_record: bool,
) -> bool:
    """
    AlwaysRecoverable invariant: for any failure state, at least one
    recovery path must exist (grace period or forgiveness record).

    Raises ValueError if no recovery path is available.
    Returns True if the invariant holds.
    """
    if not has_grace_period and not has_forgiveness_record:
        state_hash = sha256_hash(failure_state)
        raise ValueError(
            f"AlwaysRecoverable invariant violated for agent {agent_id!r}: "
            f"failure state (hash={state_hash!r}) has no recovery path"
        )
    return True


def recovery_path_hash(
    agent_id: str,
    failure_state_hash: str,
    recovery_type: str,
) -> str:
    """Return a deterministic hash identifying this recovery path."""
    return sha256_hash({
        "agent_id": agent_id,
        "failure_state_hash": failure_state_hash,
        "recovery_type": recovery_type,
    })

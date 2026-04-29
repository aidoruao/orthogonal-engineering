"""Verification Baseline - pr46_agape_witness/law/verification_baseline.py"""
# pr46_agape_witness/law/verification_baseline.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Re-exports and documents the PR #45 UVDTL verification baseline.
# PR #46 grace/forgiveness mechanisms never weaken these guarantees;
# they extend them with auditable accommodation paths.

from __future__ import annotations

from typing import Any, Dict

from pr46_agape_witness.util.hashing import sha256_hash


# ---------------------------------------------------------------------------
# Baseline verification
# ---------------------------------------------------------------------------

def verify_state_hash(state: Dict[str, Any], expected_hash: str) -> bool:
    """
    Verify that the SHA-256 hash of the canonical state equals expected_hash.
    PR #45 invariant: equal input → equal hash.
    Raises ValueError on mismatch.
    """
    computed = sha256_hash(state)
    if computed != expected_hash:
        raise ValueError(
            f"State hash mismatch: computed={computed!r} expected={expected_hash!r}"
        )
    return True


def compute_state_hash(state: Dict[str, Any]) -> str:
    """Return the canonical SHA-256 hash of state."""
    # TODO: Expand compute_state_hash() - stub detected by Yeshua Agent
    return sha256_hash(state)


# ---------------------------------------------------------------------------
# Baseline invariant: no silent mutation
# ---------------------------------------------------------------------------

def assert_no_silent_mutation(
    state_before: Dict[str, Any],
    state_after: Dict[str, Any],
    operation_id: str,
) -> bool:
    """
    Assert that if state_before != state_after, operation_id is non-empty.
    Mirrors PR #45 Invariant 4: no mutation without trace.
    Raises ValueError on violation.
    """
    hash_before = sha256_hash(state_before)
    hash_after = sha256_hash(state_after)
    if hash_before != hash_after and not operation_id:
        raise ValueError(
            f"Silent mutation detected: state changed without an operation_id"
        )
    return True

"""State Mediation - pr46_agape_witness/reconciliation/state_mediation.py"""
# pr46_agape_witness/reconciliation/state_mediation.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# State mediation: produce a deterministic mediated state from two fork states,
# using a field-by-field union strategy that preserves both histories.

from __future__ import annotations

from typing import Any, Dict

from pr46_agape_witness.util.hashing import sha256_hash


def mediate_states(
    state_a: Dict[str, Any],
    state_b: Dict[str, Any],
    fork_a_id: str,
    fork_b_id: str,
) -> Dict[str, Any]:
    """
    Produce a deterministic mediated state from two fork states.

    Strategy:
      - Keys present in both forks: value from the lexicographically earlier fork_id
        is used (deterministic tie-breaking).
      - Keys exclusive to one fork: included as-is.
      - A provenance field records both fork contributions.

    Returns a plain dict suitable for hashing and witnessing.
    """
    primary_id = sorted([fork_a_id, fork_b_id])[0]
    primary_state = state_a if primary_id == fork_a_id else state_b
    secondary_state = state_b if primary_id == fork_a_id else state_a

    merged: Dict[str, Any] = {}
    all_keys = sorted(set(list(state_a.keys()) + list(state_b.keys())))
    for key in all_keys:
        if key in primary_state:
            merged[key] = primary_state[key]
        else:
            merged[key] = secondary_state[key]

    merged["_mediation_provenance"] = {
        "fork_a_id": fork_a_id,
        "fork_b_id": fork_b_id,
        "primary_id": primary_id,
    }
    return merged

# pr46_agape_witness/invariants/agape_completeness.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# AgapeCompleteness invariant: grace extends law without contradiction.
# PR #46 mechanisms must never disable or bypass PR #45 transparency invariants.

from __future__ import annotations

from typing import Any, Dict

from pr46_agape_witness.util.hashing import sha256_hash


def check_agape_completeness(
    pr45_invariants_still_hold: bool,
    pr46_grace_applied: bool,
) -> bool:
    """
    AgapeCompleteness invariant: if grace was applied (pr46_grace_applied),
    the PR #45 invariants must still hold (pr45_invariants_still_hold).

    Grace extends law; it does not contradict it.
    Raises ValueError on violation.
    Returns True if the invariant holds.
    """
    if pr46_grace_applied and not pr45_invariants_still_hold:
        raise ValueError(
            "AgapeCompleteness violated: PR #46 grace was applied but "
            "PR #45 transparency invariants no longer hold. "
            "Grace must extend law without contradiction."
        )
    return True


def verify_no_bypass(
    operation_id: str,
    witness_entry_count_before: int,
    witness_entry_count_after: int,
) -> bool:
    """
    Verify that a grace/forgiveness operation added at least one witness entry
    (i.e., it did not silently bypass the witness chain).
    Raises ValueError on violation.
    """
    if witness_entry_count_after <= witness_entry_count_before:
        raise ValueError(
            f"AgapeCompleteness: operation {operation_id!r} produced no witness entry. "
            "Grace operations must be witnessed."
        )
    return True

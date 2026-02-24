# pr47_stewardship/invariants/no_silent_transition.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# NoSilentTransition invariant: every artifact that leaves the public boundary
# must have a corresponding entry in the RemovalWitness ledger.

from __future__ import annotations

from pr47_stewardship.witness.removal_witness import RemovalWitness


class NoSilentTransitionViolation(Exception):
    """Raised when an artifact has no witness entry."""


def check_no_silent_transition(
    removed_hashes: set[str],
    witness: RemovalWitness,
) -> bool:
    """
    Assert that every removed artifact is recorded in the witness ledger.

    Parameters:
      removed_hashes — set of content_hash values for artifacts that are no
                       longer present in the public boundary.
      witness        — the RemovalWitness that should have an entry for each.

    Returns True if the invariant holds.
    Raises NoSilentTransitionViolation on first missing entry.
    """
    for h in sorted(removed_hashes):
        if not witness.has_entry_for_hash(h):
            raise NoSilentTransitionViolation(
                f"NoSilentTransition violated: no witness entry for "
                f"content_hash={h!r}"
            )
    return True

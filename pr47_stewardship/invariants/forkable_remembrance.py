# pr47_stewardship/invariants/forkable_remembrance.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# ForkableRemembrance invariant: the witness ledger plus consent records
# contain sufficient information to reconstruct the boundary state.
#
# "Anyone with consent + local keys can reconstruct."

from __future__ import annotations

from pr47_stewardship.witness.removal_witness import RemovalWitness
from pr47_stewardship.witness.consent_log import ConsentLog


class ForkableRemembranceViolation(Exception):
    """Raised when the ledger cannot support a full reconstruction."""


def check_forkable_remembrance(
    witness: RemovalWitness,
    consent_log: ConsentLog,
) -> bool:
    """
    Assert that every witness entry has a corresponding consent record.

    A ledger entry without consent means the transition was unauthorised and
    cannot be legitimately reconstructed, violating forkability.

    Parameters:
      witness     — the RemovalWitness ledger.
      consent_log — the ConsentLog holding human authorisations.

    Returns True if the invariant holds.
    Raises ForkableRemembranceViolation on first unconsented entry.
    """
    for entry in witness.entries():
        if not consent_log.has_consent_for(entry.content_hash):
            raise ForkableRemembranceViolation(
                f"ForkableRemembrance violated: witness entry for "
                f"content_hash={entry.content_hash!r} has no consent record"
            )
    return True

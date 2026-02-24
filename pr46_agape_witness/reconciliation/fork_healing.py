# pr46_agape_witness/reconciliation/fork_healing.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Fork healing / reconciliation.
# Healing requires explicit mutual consent from both forks.
# The healed state is witnessed (append-only, deterministic).

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from pr46_agape_witness.util.hashing import sha256_hash, AGAPE_GENESIS_HASH


@dataclass(frozen=True)
class ConsentRecord:
    """A consent declaration from one fork party."""
    fork_id: str
    consents_to_heal: bool
    timestamp: str      # ISO-8601, injected
    consent_hash: str

    @classmethod
    def create(
        cls,
        fork_id: str,
        consents_to_heal: bool,
        timestamp: str,
    ) -> "ConsentRecord":
        doc = {
            "consents_to_heal": consents_to_heal,
            "fork_id": fork_id,
            "timestamp": timestamp,
        }
        return cls(
            fork_id=fork_id,
            consents_to_heal=consents_to_heal,
            timestamp=timestamp,
            consent_hash=sha256_hash(doc),
        )


@dataclass(frozen=True)
class HealedState:
    """Witnessed result of a successful fork healing."""
    fork_a_id: str
    fork_b_id: str
    consent_a_hash: str
    consent_b_hash: str
    merged_state: Dict[str, Any]
    healed_state_hash: str
    healing_witness_hash: str


def heal_forks(
    fork_a_id: str,
    fork_b_id: str,
    consent_a: ConsentRecord,
    consent_b: ConsentRecord,
    merged_state: Dict[str, Any],
) -> HealedState:
    """
    Attempt to heal two forks into a merged_state.

    Requirements:
      - consent_a.fork_id must equal fork_a_id and consent_a.consents_to_heal == True.
      - consent_b.fork_id must equal fork_b_id and consent_b.consents_to_heal == True.
      - Both consents must be present; healing without mutual consent raises ValueError.

    Returns a HealedState with a deterministic healing_witness_hash.
    Raises ValueError if consent is missing or mismatched.
    """
    if consent_a.fork_id != fork_a_id:
        raise ValueError(
            f"Consent A fork_id mismatch: {consent_a.fork_id!r} != {fork_a_id!r}"
        )
    if consent_b.fork_id != fork_b_id:
        raise ValueError(
            f"Consent B fork_id mismatch: {consent_b.fork_id!r} != {fork_b_id!r}"
        )
    if not consent_a.consents_to_heal:
        raise ValueError(f"Fork {fork_a_id!r} has not consented to healing")
    if not consent_b.consents_to_heal:
        raise ValueError(f"Fork {fork_b_id!r} has not consented to healing")

    healed_state_hash = sha256_hash(merged_state)

    healing_doc = {
        "consent_a_hash": consent_a.consent_hash,
        "consent_b_hash": consent_b.consent_hash,
        "fork_a_id": fork_a_id,
        "fork_b_id": fork_b_id,
        "healed_state_hash": healed_state_hash,
    }
    healing_witness_hash = sha256_hash(healing_doc)

    return HealedState(
        fork_a_id=fork_a_id,
        fork_b_id=fork_b_id,
        consent_a_hash=consent_a.consent_hash,
        consent_b_hash=consent_b.consent_hash,
        merged_state=merged_state,
        healed_state_hash=healed_state_hash,
        healing_witness_hash=healing_witness_hash,
    )

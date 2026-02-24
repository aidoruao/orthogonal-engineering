# pr46_agape_witness/forgiveness/provenance_preservation.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Provenance preservation: forgiveness never deletes history.
# A ForgivenessRecord references the prior state hash and the reason,
# keeping the full audit trail intact.

from __future__ import annotations

from dataclasses import dataclass

from pr46_agape_witness.util.hashing import sha256_hash


@dataclass(frozen=True)
class ForgivenessRecord:
    """
    Append-only forgiveness record.
    References prior_state_hash to preserve provenance (audit trail never broken).
    """
    agent_id: str
    prior_state_hash: str   # hash of the state BEFORE forgiveness
    reason: str
    timestamp: str          # ISO-8601, injected
    record_hash: str        # deterministic hash of this record

    @classmethod
    def create(
        cls,
        agent_id: str,
        prior_state_hash: str,
        reason: str,
        timestamp: str,
    ) -> "ForgivenessRecord":
        doc = {
            "agent_id": agent_id,
            "prior_state_hash": prior_state_hash,
            "reason": reason,
            "timestamp": timestamp,
        }
        return cls(
            agent_id=agent_id,
            prior_state_hash=prior_state_hash,
            reason=reason,
            timestamp=timestamp,
            record_hash=sha256_hash(doc),
        )

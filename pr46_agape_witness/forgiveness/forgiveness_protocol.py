# pr46_agape_witness/forgiveness/forgiveness_protocol.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Forgiveness protocol: provenance-safe append-only "reset".
# History is retained; the ForgivenessRecord references the prior state.
# ForgivenessAuditable invariant: every forgiveness leaves verifiable evidence.

from __future__ import annotations

from typing import Any, Dict

from pr46_agape_witness.forgiveness.justification_witness import JustificationWitnessChain
from pr46_agape_witness.forgiveness.provenance_preservation import ForgivenessRecord
from pr46_agape_witness.util.hashing import sha256_hash


class ForgivenessProtocol:
    """
    Manages forgiveness operations with provenance preservation.

    Usage:
      protocol = ForgivenessProtocol()
      record = protocol.forgive(agent_id, current_state, reason, timestamp)
      # record.prior_state_hash references the pre-forgiveness hash.
      protocol.witness_chain.verify_integrity()  # auditable at any time
    """

    def __init__(self) -> None:
        self.witness_chain = JustificationWitnessChain()

    def forgive(
        self,
        agent_id: str,
        current_state: Dict[str, Any],
        reason: str,
        timestamp: str,
    ) -> ForgivenessRecord:
        """
        Record a forgiveness event.

        - Computes prior_state_hash from current_state (provenance preserved).
        - Creates a ForgivenessRecord referencing the prior state hash.
        - Appends the record to the justification witness chain (append-only).

        Returns the ForgivenessRecord for the caller to store or extend.
        Raises ValueError if reason is empty (justification required).
        """
        if not reason:
            raise ValueError("Forgiveness requires a non-empty reason (justification)")
        prior_state_hash = sha256_hash(current_state)
        record = ForgivenessRecord.create(
            agent_id=agent_id,
            prior_state_hash=prior_state_hash,
            reason=reason,
            timestamp=timestamp,
        )
        self.witness_chain.append(record)
        return record

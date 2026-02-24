# pr46_agape_witness/forgiveness/justification_witness.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Justification witness: an append-only chain of witnessed justifications
# for forgiveness operations. ForgivenessAuditable invariant: every
# forgiveness operation leaves verifiable append-only witness evidence.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from pr46_agape_witness.forgiveness.provenance_preservation import ForgivenessRecord
from pr46_agape_witness.util.hashing import sha256_hash, AGAPE_GENESIS_HASH


@dataclass(frozen=True)
class JustificationEntry:
    """One entry in the justification witness chain."""
    previous_chain_hash: str
    forgiveness_record_hash: str
    entry_hash: str

    @classmethod
    def create(
        cls,
        previous_chain_hash: str,
        forgiveness_record: ForgivenessRecord,
    ) -> "JustificationEntry":
        entry_hash = sha256_hash({
            "forgiveness_record_hash": forgiveness_record.record_hash,
            "previous_chain_hash": previous_chain_hash,
        })
        return cls(
            previous_chain_hash=previous_chain_hash,
            forgiveness_record_hash=forgiveness_record.record_hash,
            entry_hash=entry_hash,
        )


class JustificationWitnessChain:
    """
    Append-only chain of forgiveness justifications.
    ForgivenessAuditable: every forgiveness operation is witnessed here.
    """

    def __init__(self) -> None:
        self._entries: List[JustificationEntry] = []
        self._chain_hash: str = AGAPE_GENESIS_HASH

    def append(self, forgiveness_record: ForgivenessRecord) -> JustificationEntry:
        """Append a forgiveness record to the witness chain."""
        entry = JustificationEntry.create(self._chain_hash, forgiveness_record)
        self._entries.append(entry)
        self._chain_hash = entry.entry_hash
        return entry

    @property
    def chain_hash(self) -> str:
        return self._chain_hash

    @property
    def length(self) -> int:
        return len(self._entries)

    def entries(self) -> List[JustificationEntry]:
        return list(self._entries)

    def verify_integrity(self) -> bool:
        """
        Recompute the chain hash from genesis.
        Raises ValueError if any entry has been tampered with.
        """
        h = AGAPE_GENESIS_HASH
        for entry in self._entries:
            expected = sha256_hash({
                "forgiveness_record_hash": entry.forgiveness_record_hash,
                "previous_chain_hash": h,
            })
            if expected != entry.entry_hash:
                raise ValueError(
                    f"JustificationWitnessChain integrity violation at entry: "
                    f"expected={expected!r} stored={entry.entry_hash!r}"
                )
            h = entry.entry_hash
        if h != self._chain_hash:
            raise ValueError(
                f"JustificationWitnessChain final hash mismatch: "
                f"recomputed={h!r} stored={self._chain_hash!r}"
            )
        return True

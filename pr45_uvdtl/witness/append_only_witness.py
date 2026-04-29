"""Append Only Witness - pr45_uvdtl/witness/append_only_witness.py"""
# pr45_uvdtl/witness/append_only_witness.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section VI.1 — Append-Only Witness
#
# Each canonical state transition appends:
#   {
#     previous_hash,
#     new_hash,
#     operation_id,
#     trace_hash,
#     build_hash
#   }
#
# Witness must be:
#   - Append-only
#   - Deterministically serialized
#   - Publicly recomputable

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import List


# ---------------------------------------------------------------------------
# Witness Entry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WitnessEntry:
    """One entry in the append-only witness chain."""
    previous_hash: str
    new_hash: str
    operation_id: str
    trace_hash: str
    build_hash: str

    def canonical_bytes(self) -> bytes:
        """Deterministic serialisation of this entry (sorted keys, UTF-8)."""
        doc = {
            "build_hash": self.build_hash,
            "new_hash": self.new_hash,
            "operation_id": self.operation_id,
            "previous_hash": self.previous_hash,
            "trace_hash": self.trace_hash,
        }
        return json.dumps(doc, sort_keys=True, ensure_ascii=True).encode("utf-8")

    def entry_hash(self) -> str:
        """SHA-256 of the canonical entry bytes."""
        # TODO: Expand entry_hash() - stub detected by Yeshua Agent
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Witness Chain
# ---------------------------------------------------------------------------

# Genesis constant: the hash of the empty state
GENESIS_HASH: str = hashlib.sha256(b"genesis").hexdigest()


class WitnessChain:
    """
    Append-only witness chain.
    Each append records one canonical state transition.
    The chain is publicly recomputable from genesis.
    """

    def __init__(self) -> None:
        self._entries: List[WitnessEntry] = []
        self._chain_hash: str = GENESIS_HASH

    def append(
        self,
        new_hash: str,
        operation_id: str,
        trace_hash: str,
        build_hash: str,
    ) -> WitnessEntry:
        """
        Append one state transition to the chain.
        previous_hash is always the last chain_hash (append-only).
        """
        entry = WitnessEntry(
            previous_hash=self._chain_hash,
            new_hash=new_hash,
            operation_id=operation_id,
            trace_hash=trace_hash,
            build_hash=build_hash,
        )
        self._entries.append(entry)
        self._chain_hash = entry.entry_hash()
        return entry

    @property
    def chain_hash(self) -> str:
        """Current chain hash after all appended entries."""
        return self._chain_hash

    @property
    def length(self) -> int:
        return len(self._entries)

    def entries(self) -> List[WitnessEntry]:
        """Return a copy of all entries in append order."""
        return list(self._entries)

    def recompute_chain_hash(self) -> str:
        """
        Recompute the chain hash from genesis by replaying entries.
        Must equal self.chain_hash for the chain to be valid.
        """
        h = GENESIS_HASH
        for entry in self._entries:
            verified_entry = WitnessEntry(
                previous_hash=h,
                new_hash=entry.new_hash,
                operation_id=entry.operation_id,
                trace_hash=entry.trace_hash,
                build_hash=entry.build_hash,
            )
            h = verified_entry.entry_hash()
        return h

    def verify_integrity(self) -> bool:
        """
        Assert chain is consistent: recomputed hash matches stored hash.
        Raises ValueError on tampering.
        """
        recomputed = self.recompute_chain_hash()
        if recomputed != self._chain_hash:
            raise ValueError(
                f"Witness chain integrity violation: "
                f"recomputed={recomputed!r} stored={self._chain_hash!r}"
            )
        return True


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "Mutable audit log": "Entries can be modified or deleted; non-recomputable",
    "PR #45 WitnessChain": (
        "Append-only; each entry links previous_hash → new_hash; "
        "chain hash recomputable from genesis; any tampering detected by verify_integrity()"
    ),
}

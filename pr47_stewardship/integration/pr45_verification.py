# pr47_stewardship/integration/pr45_verification.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# Bridge to PR #45 UVDTL verification baseline.
# Appends PR #47 boundary transition events to the PR #45 WitnessChain so
# the full audit trail remains in one coherent, recomputable chain.
#
# PR #45 guarantee preserved:
#   - WitnessChain is append-only; no entries are mutated.
#   - Every boundary event is recorded with operation_id, trace_hash, and
#     build_hash so the chain remains recomputable from genesis.

from __future__ import annotations

import hashlib
import json

from pr45_uvdtl.witness.append_only_witness import WitnessChain, WitnessEntry
from pr47_stewardship.witness.removal_witness import RemovalEntry


def _sha256(doc: dict) -> str:
    raw = json.dumps(doc, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# Stable build hash for PR #47 (deterministic across builds).
PR47_BUILD_HASH: str = _sha256({"pr": 47, "layer": "stewardship"})


def witness_boundary_transition(
    chain: WitnessChain,
    entry: RemovalEntry,
    trace_hash: str = "boundary_transition_trace",
) -> WitnessEntry:
    """
    Append one PR #47 boundary transition to the PR #45 WitnessChain.

    Parameters:
      chain      — the active PR #45 WitnessChain.
      entry      — the RemovalEntry produced by RemovalWitness.
      trace_hash — injected trace identifier (defaults to a stable sentinel).

    Returns the new WitnessEntry appended to the chain.
    """
    return chain.append(
        new_hash=entry.entry_hash(),
        operation_id=f"boundary_transition:{entry.content_hash}",
        trace_hash=trace_hash,
        build_hash=PR47_BUILD_HASH,
    )


def verify_all_transitions(
    chain: WitnessChain,
    entries: list[RemovalEntry],
    trace_hash: str = "boundary_transition_trace",
) -> list[WitnessEntry]:
    """
    Append all RemovalEntries to the WitnessChain and verify integrity.

    Returns the list of newly appended WitnessEntries.
    Raises ValueError (from WitnessChain.verify_integrity) on tampering.
    """
    witness_entries = []
    for entry in entries:
        we = witness_boundary_transition(chain, entry, trace_hash)
        witness_entries.append(we)
    chain.verify_integrity()
    return witness_entries

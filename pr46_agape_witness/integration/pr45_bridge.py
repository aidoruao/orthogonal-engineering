# pr46_agape_witness/integration/pr45_bridge.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Bridge to PR #45 UVDTL verification baseline.
# PR #46 grace/forgiveness operations feed into the PR #45 WitnessChain
# so that the full audit trail remains in one coherent chain.
#
# PR #45 guarantee preserved:
#   - WitnessChain is append-only; no entries are mutated.
#   - Every grace/forgiveness event is recorded with operation_id, trace_hash,
#     and build_hash so the chain remains recomputable from genesis.

from __future__ import annotations

from typing import Any, Dict

from pr45_uvdtl.witness.append_only_witness import WitnessChain, WitnessEntry
from pr46_agape_witness.forgiveness.provenance_preservation import ForgivenessRecord
from pr46_agape_witness.grace.grace_period import GracePeriod
from pr46_agape_witness.reconciliation.fork_healing import HealedState
from pr46_agape_witness.util.hashing import sha256_hash


# Sentinel build hash for PR #46 (stable across builds for determinism)
PR46_BUILD_HASH: str = sha256_hash({"pr": 46, "layer": "agape_witness"})


def witness_grace_period(
    chain: WitnessChain,
    grace_period: GracePeriod,
    trace_hash: str = "grace_period_trace",
) -> WitnessEntry:
    """
    Append a grace period activation event to the PR #45 WitnessChain.
    The new_hash is the grace period's witness_hash.
    """
    return chain.append(
        new_hash=grace_period.witness_hash,
        operation_id=f"grace_period:{grace_period.agent_id}",
        trace_hash=trace_hash,
        build_hash=PR46_BUILD_HASH,
    )


def witness_forgiveness(
    chain: WitnessChain,
    record: ForgivenessRecord,
    trace_hash: str = "forgiveness_trace",
) -> WitnessEntry:
    """
    Append a forgiveness event to the PR #45 WitnessChain.
    The new_hash is the forgiveness record's hash.
    """
    return chain.append(
        new_hash=record.record_hash,
        operation_id=f"forgiveness:{record.agent_id}",
        trace_hash=trace_hash,
        build_hash=PR46_BUILD_HASH,
    )


def witness_healed_state(
    chain: WitnessChain,
    healed: HealedState,
    trace_hash: str = "fork_healing_trace",
) -> WitnessEntry:
    """
    Append a fork healing event to the PR #45 WitnessChain.
    The new_hash is the healing_witness_hash.
    """
    return chain.append(
        new_hash=healed.healing_witness_hash,
        operation_id=f"fork_healing:{healed.fork_a_id}+{healed.fork_b_id}",
        trace_hash=trace_hash,
        build_hash=PR46_BUILD_HASH,
    )

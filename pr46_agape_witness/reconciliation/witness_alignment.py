# pr46_agape_witness/reconciliation/witness_alignment.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Witness alignment: align two independent witness chains
# after fork healing, producing a merged chain hash.

from __future__ import annotations

from pr46_agape_witness.util.hashing import sha256_hash


def align_witness_hashes(chain_hash_a: str, chain_hash_b: str) -> str:
    """
    Produce a deterministic merged witness hash from two fork chain hashes.
    Sorted lexicographically so align(a, b) == align(b, a).
    """
    ordered = sorted([chain_hash_a, chain_hash_b])
    return sha256_hash({"chain_hash_a": ordered[0], "chain_hash_b": ordered[1]})

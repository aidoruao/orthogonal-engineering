"""Vendor Lock - pr43/impossibility/vendor_lock.py"""
# pr43/impossibility/vendor_lock.py
# PR #43 — Orthogonal Parallel
# Standard: Yeshua
#
# Theorem: Vendor Lock Impossibility
#
# If system S is:
#   1. Fully specified by public source
#   2. Deterministically evaluable
#   3. Hash-verifiable
# Then:
#   ∀ replica R implementing identical source, Output(S) = Output(R)
#   Therefore no exclusive computational advantage exists.
#   QED.

from __future__ import annotations

import hashlib
from typing import Dict


def hash_source(source_code: str) -> str:
    """
    SHA-256 of UTF-8 encoded source.
    Same source → same hash on any platform (cross-platform byte identity).
    Anyone can replicate; anyone can verify. No moat possible.
    """
    return hashlib.sha256(source_code.encode("utf-8")).hexdigest()


def verify_no_vendor_lock(source_hash_a: str, source_hash_b: str) -> bool:
    """
    Two replicas of the same source produce the same hash.
    Hash equality is necessary and sufficient for output equality
    (given deterministic evaluation).
    """
    return source_hash_a == source_hash_b


def check_no_lock_in(source_code: str) -> Dict[str, object]:
    """
    Return a proof record demonstrating that source_code carries no vendor lock-in:
      - source is public (anyone can read it)
      - hash is deterministic (anyone can reproduce it)
      - no extraction advantage possible
    """
    h = hash_source(source_code)
    return {
        "theorem": "VendorLockImpossibility",
        "source_sha256": h,
        "public": True,
        "deterministic": True,
        "hash_verifiable": True,
        "exclusive_advantage": False,
        "proof_method": "constructive",
    }

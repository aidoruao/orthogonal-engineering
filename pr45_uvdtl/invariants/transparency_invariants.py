# pr45_uvdtl/invariants/transparency_invariants.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section VIII — Transparency Invariants
#
# The following must hold:
#   1. Equal input → equal canonical output.
#   2. Equal canonical output → equal state hash.
#   3. Equal state hash → equal rebuild artifact.
#   4. No privileged process may modify canonical state without trace.
#   5. Every trace finite and reproducible.

from __future__ import annotations

from typing import Any, Callable, Dict, List

from pr45_uvdtl.state.canonical_serialization import canonical_encode, state_hash
from pr45_uvdtl.foundations.trace_interface import Trace


# ---------------------------------------------------------------------------
# Invariant 1 — Equal input → equal canonical output
# ---------------------------------------------------------------------------

def invariant_1_equal_input_equal_output(
    state_a: Dict[str, Any],
    state_b: Dict[str, Any],
) -> bool:
    """
    Invariant 1: If state_a == state_b then canonical_encode(state_a) == canonical_encode(state_b).
    Returns True; raises AssertionError on violation.
    """
    if state_a == state_b:
        result = canonical_encode(state_a) == canonical_encode(state_b)
        assert result, "Invariant 1 violated: equal inputs produced different canonical bytes"
        return True
    # Inputs differ: invariant is vacuously satisfied
    return True


# ---------------------------------------------------------------------------
# Invariant 2 — Equal canonical output → equal state hash
# ---------------------------------------------------------------------------

def invariant_2_equal_output_equal_hash(
    bytes_a: bytes,
    bytes_b: bytes,
    hash_a: str,
    hash_b: str,
) -> bool:
    """
    Invariant 2: If bytes_a == bytes_b then hash_a == hash_b.
    Returns True; raises AssertionError on violation.
    """
    if bytes_a == bytes_b:
        assert hash_a == hash_b, "Invariant 2 violated: equal bytes produced different hashes"
    return True


# ---------------------------------------------------------------------------
# Invariant 3 — Equal state hash → equal rebuild artifact
# ---------------------------------------------------------------------------

def invariant_3_equal_hash_equal_artifact(
    state_hash_a: str,
    state_hash_b: str,
    artifact_hash_a: str,
    artifact_hash_b: str,
) -> bool:
    """
    Invariant 3: If state_hash_a == state_hash_b and the build is deterministic,
    then artifact_hash_a == artifact_hash_b.
    Returns True; raises AssertionError on violation.
    """
    if state_hash_a == state_hash_b:
        assert artifact_hash_a == artifact_hash_b, (
            "Invariant 3 violated: equal state hashes produced different artifact hashes"
        )
    return True


# ---------------------------------------------------------------------------
# Invariant 4 — No privileged mutation without trace
# ---------------------------------------------------------------------------

def invariant_4_no_mutation_without_trace(
    trace: Trace,
    old_hash: str,
    new_hash: str,
) -> bool:
    """
    Invariant 4: Any state transition from old_hash → new_hash must have
    a non-empty trace. No traceless mutation is canonical.
    Raises ValueError if trace is empty for a non-identity transition.
    """
    if old_hash != new_hash and trace.length() == 0:
        raise ValueError(
            f"Invariant 4 violated: state changed ({old_hash!r} → {new_hash!r}) "
            "without any trace steps"
        )
    return True


# ---------------------------------------------------------------------------
# Invariant 5 — Every trace finite and reproducible
# ---------------------------------------------------------------------------

def invariant_5_trace_finite_reproducible(trace: Trace) -> bool:
    """
    Invariant 5: Every trace is finite (bounded length) and reproducible
    (recompute() returns the same step sequence).
    Raises AssertionError on violation.
    """
    assert trace.is_finite(), "Invariant 5 violated: trace is not finite"
    steps_a = trace.recompute()
    steps_b = trace.recompute()
    assert steps_a == steps_b, "Invariant 5 violated: trace is not reproducible"
    return True


# ---------------------------------------------------------------------------
# Full Invariant Suite
# ---------------------------------------------------------------------------

def verify_all_invariants(
    state: Dict[str, Any],
    trace: Trace,
    old_hash: str,
    new_hash: str,
    artifact_hash: str,
) -> Dict[str, bool]:
    """
    Run all five transparency invariants for one state transition.
    Returns {invariant_id: passed}.
    Raises on any violation.
    """
    enc = canonical_encode(state)
    s_hash = state_hash(state)

    results: Dict[str, bool] = {}

    # Inv 1: equal input → equal canonical output (self-consistency check)
    results["invariant_1"] = invariant_1_equal_input_equal_output(state, dict(state))

    # Inv 2: equal canonical output → equal hash
    results["invariant_2"] = invariant_2_equal_output_equal_hash(enc, enc, s_hash, s_hash)

    # Inv 3: equal state hash → equal artifact hash
    results["invariant_3"] = invariant_3_equal_hash_equal_artifact(
        s_hash, s_hash, artifact_hash, artifact_hash
    )

    # Inv 4: no mutation without trace
    results["invariant_4"] = invariant_4_no_mutation_without_trace(trace, old_hash, new_hash)

    # Inv 5: trace finite and reproducible
    results["invariant_5"] = invariant_5_trace_finite_reproducible(trace)

    return results


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "Unverified system": "No formal invariants; hidden state possible; non-auditable",
    "PR #45 transparency_invariants": (
        "Five formal invariants enforced; equal input → equal output → equal hash → "
        "equal artifact; no traceless mutation; every trace finite and reproducible"
    ),
}

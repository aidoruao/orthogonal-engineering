# pr45_uvdtl/totality/resource_bounds.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section III.2 — Resource Bound Transparency
#
# Each canonical operation must expose:
#   cost(operation) → ℕ
#
# Cost must be:
#   - Deterministic
#   - Recomputable
#   - Independent of machine architecture

from __future__ import annotations

from typing import Any, Dict


# ---------------------------------------------------------------------------
# Cost function definitions
# ---------------------------------------------------------------------------

def cost_zero_test(**_kwargs: int) -> int:
    """cost(zero_test) = 1 (single comparison)."""
    return 1


def cost_successor(**_kwargs: int) -> int:
    """cost(successor) = 1 (single allocation)."""
    return 1


def cost_add(b: int) -> int:
    """cost(add(a, b)) = b (b applications of successor)."""
    return b


def cost_mul(a: int, b: int) -> int:
    """cost(mul(a, b)) = a * b (nested successor applications)."""
    return a * b


def cost_canonical_encode(depth: int, n_keys: int) -> int:
    """
    cost(canonical_encode) = depth * n_keys.
    Depth measures nesting; n_keys counts leaf annotations.
    """
    return depth * n_keys


def cost_sha256(byte_length: int) -> int:
    """
    cost(sha256) measured in 512-bit (64-byte) blocks processed.
    cost = ceil(byte_length / 64)
    """
    return (byte_length + 63) // 64


def cost_derive_seed(**_kwargs: int) -> int:
    """cost(derive_seed) = 2 (one string concatenation + one SHA-256 block)."""
    return 2


def cost_prng(**_kwargs: int) -> int:
    """cost(prng) = 1 (one SHA-256 block + one struct.unpack)."""
    return 1


# ---------------------------------------------------------------------------
# Generic cost dispatcher
# ---------------------------------------------------------------------------

_COST_TABLE: Dict[str, Any] = {
    "zero_test": cost_zero_test,
    "successor": cost_successor,
    "add": cost_add,
    "mul": cost_mul,
    "derive_seed": cost_derive_seed,
    "prng": cost_prng,
    "sha256": cost_sha256,
    "canonical_encode": cost_canonical_encode,
}


def cost(operation: str, **kwargs: int) -> int:
    """
    cost(operation, **kwargs) → ℕ

    Deterministic cost function for each canonical operation.
    Recomputable from operation name and parameters alone.
    Independent of machine architecture.
    """
    if operation not in _COST_TABLE:
        raise ValueError(f"Unknown operation: {operation!r}")
    fn = _COST_TABLE[operation]
    return fn(**kwargs)


def list_operations() -> list:
    """Return sorted list of all costed operations."""
    return sorted(_COST_TABLE.keys())


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "Profiling-only cost": "Machine-dependent; non-recomputable",
    "PR #45 cost()": (
        "Algebraic cost in ℕ; deterministic formula per operation; "
        "recomputable without running the operation; architecture-independent"
    ),
}

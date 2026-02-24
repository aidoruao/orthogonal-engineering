# pr45_uvdtl/parallel/deterministic_reduction.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section V — Parallel Determinism
#
# Parallel computation must obey:
#   - No shared mutable state
#   - Immutable input partitions
#   - Deterministic ordering of reduction
#
# Final state defined as:
#   fold(sorted(outputs))
#
# Sorting key explicitly defined and deterministic.

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Dict, List, Sequence, TypeVar

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Immutable Partition
# ---------------------------------------------------------------------------

def partition(items: Sequence[T], n_partitions: int) -> List[tuple]:
    """
    Divide items into n_partitions contiguous, immutable sub-sequences.
    Deterministic: same items + same n_partitions → same partitioning.
    Returns a list of tuples (each partition is immutable).
    """
    if n_partitions <= 0:
        raise ValueError("n_partitions must be positive")
    size = len(items)
    base, remainder = divmod(size, n_partitions)
    result: List[tuple] = []
    start = 0
    for i in range(n_partitions):
        end = start + base + (1 if i < remainder else 0)
        result.append(tuple(items[start:end]))
        start = end
    return result


# ---------------------------------------------------------------------------
# Deterministic Map + Sorted Reduce
# ---------------------------------------------------------------------------

def map_reduce(
    items: Sequence[T],
    mapper: Callable[[T], Any],
    reducer: Callable[[Any, Any], Any],
    sort_key: Callable[[Any], Any],
    initial: Any,
) -> Any:
    """
    Deterministic map-reduce:
      1. Apply mapper to each item independently (no shared mutable state).
      2. Sort outputs by sort_key (deterministic ordering).
      3. Fold sorted outputs with reducer from initial.

    Final state := fold(sorted(outputs)).
    """
    mapped = [mapper(item) for item in items]
    sorted_mapped = sorted(mapped, key=sort_key)
    result = initial
    for value in sorted_mapped:
        result = reducer(result, value)
    return result


# ---------------------------------------------------------------------------
# Canonical Sorted Fold
# ---------------------------------------------------------------------------

def sorted_fold(outputs: Sequence[Any], sort_key: Callable[[Any], Any]) -> List[Any]:
    """
    Return the sorted sequence. This is the canonical reduction order.
    sort_key must be deterministic and explicitly declared.
    """
    return sorted(outputs, key=sort_key)


# ---------------------------------------------------------------------------
# Hash-based sorting key
# ---------------------------------------------------------------------------

def hash_sort_key(value: Any) -> str:
    """
    Deterministic sort key: SHA-256 of the JSON serialisation.
    Works for any JSON-serialisable value.
    """
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Parallel determinism verifier
# ---------------------------------------------------------------------------

def verify_no_shared_state(results_a: List[Any], results_b: List[Any]) -> bool:
    """
    Verify that two independent parallel executions produce the same sorted outputs.
    Raises ValueError on mismatch.
    """
    sorted_a = sorted(results_a, key=hash_sort_key)
    sorted_b = sorted(results_b, key=hash_sort_key)
    if sorted_a != sorted_b:
        raise ValueError("Parallel executions produced different sorted outputs")
    return True


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "Unordered parallel reduce": "Non-deterministic output depending on scheduling",
    "PR #45 deterministic_reduction": (
        "fold(sorted(outputs)); sort key explicitly defined via hash_sort_key; "
        "no shared mutable state; immutable input partitions"
    ),
}

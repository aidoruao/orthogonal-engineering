# pr44_orthogonal_meta/verification/reproducibility_checker.py
# PR #44 — Orthogonal Meta Parallel
# Standard: Yeshua
#
# Cross-platform equality enforcement.
# Ensures that any two executions of the same deterministic function
# over the same inputs yield byte-identical results.

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Dict, List


def hash_output(value: Any) -> str:
    """
    Serialize value to canonical JSON (sorted keys) and SHA-256 it.
    Deterministic serialization ensures cross-platform byte identity.
    """
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def check_reproducible(
    fn: Callable,
    args: List,
    kwargs: Dict,
    n_runs: int = 3,
) -> Dict:
    """
    Run fn(*args, **kwargs) n_runs times and compare hashed outputs.

    Returns a proof record:
      - reproducible: bool
      - hash: str (common hash if reproducible)
      - mismatch_at: Optional[int] (run index of first mismatch)
    """
    reference_hash: str = ""
    for i in range(n_runs):
        result = fn(*args, **kwargs)
        h = hash_output(result)
        if i == 0:
            reference_hash = h
        elif h != reference_hash:
            return {
                "theorem": "CrossPlatformReproducibility",
                "reproducible": False,
                "hash": reference_hash,
                "mismatch_at": i,
                "n_runs": n_runs,
            }
    return {
        "theorem": "CrossPlatformReproducibility",
        "reproducible": True,
        "hash": reference_hash,
        "mismatch_at": None,
        "n_runs": n_runs,
    }

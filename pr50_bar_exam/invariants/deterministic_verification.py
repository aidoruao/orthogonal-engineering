#!/usr/bin/env python3
"""
invariants/deterministic_verification.py — Ensures transcript->score is stable.
"""
from __future__ import annotations
import json
from typing import Any, Callable, Dict, Tuple


def verify_determinism(
    score_fn: Callable[[Dict[str, Any]], Any],
    transcript: Dict[str, Any],
    iterations: int = 3,
) -> Tuple[bool, str]:
    """Run score_fn on transcript multiple times and assert identical results.

    Returns (deterministic, message).
    """
    results = [score_fn(transcript) for _ in range(iterations)]
    canonical_results = [
        json.dumps(r[0], sort_keys=True, separators=(",", ":")) for r in results
    ]
    if len(set(canonical_results)) == 1:
        return True, "scoring is deterministic"
    return False, f"scoring produced different results across {iterations} runs"

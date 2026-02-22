"""
falsification/counterexample_engine.py — Counterexample Search Engine

Attempts to falsify every registered hypothesis.
If any counterexample is found, raises CounterexampleFound.

Usage:
    from falsification.counterexample_engine import run_falsification
    run_falsification()   # raises on first counterexample

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import json
from typing import List

from falsification.hypothesis import (
    FalsificationResult,
    Hypothesis,
    HYPOTHESIS_REGISTRY,
)

__all__ = ["CounterexampleFound", "run_falsification", "run_all_hypotheses"]


class CounterexampleFound(Exception):
    """Raised when a counterexample is found for a registered hypothesis."""

    def __init__(self, result: FalsificationResult) -> None:
        self.result = result
        super().__init__(
            f"COUNTEREXAMPLE FOUND for {result.hypothesis_id}: {result.detail}"
        )


def run_all_hypotheses(
    hypotheses: List[Hypothesis],
) -> List[FalsificationResult]:
    """
    Run falsification on a list of hypotheses.

    Returns all results (survived=True and survived=False).
    Does NOT raise; callers decide what to do with failures.
    """
    return [h.attempt_falsification() for h in hypotheses]


def run_falsification(
    hypotheses: List[Hypothesis] | None = None,
    raise_on_counterexample: bool = True,
) -> List[FalsificationResult]:
    """
    Run falsification on all registered hypotheses (or the provided list).

    If raise_on_counterexample=True (default), raises CounterexampleFound
    on the first hypothesis that fails.

    Returns list of all results.
    """
    targets = hypotheses if hypotheses is not None else HYPOTHESIS_REGISTRY
    results = run_all_hypotheses(targets)

    if raise_on_counterexample:
        for r in results:
            if not r.survived:
                raise CounterexampleFound(r)

    return results

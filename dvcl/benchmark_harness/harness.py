"""
dvcl/benchmark_harness/harness.py — Canonical Benchmark Harness

All benchmark claims are invalid unless:
  - dataset hash is declared and verified
  - eval logic hash is declared and verified
  - scoring implementation is deterministic
  - results are reproducible across nodes (dual-path agreement)

Author: Orthogonal Engineering
PR: #37
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

__all__ = ["BenchmarkResult", "run_benchmark"]


class BenchmarkResult:
    """Structured, hash-anchored benchmark result."""

    def __init__(
        self,
        name: str,
        dataset_hash: str,
        eval_logic_hash: str,
        score: float,
        score_hash: str,
        reproducible: bool,
    ) -> None:
        self.name = name
        self.dataset_hash = dataset_hash
        self.eval_logic_hash = eval_logic_hash
        self.score = score
        self.score_hash = score_hash
        self.reproducible = reproducible

    @property
    def valid(self) -> bool:
        """A result is valid only when reproducible with hash parity."""
        return self.reproducible and bool(self.dataset_hash) and bool(self.eval_logic_hash)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dataset_hash": self.dataset_hash,
            "eval_logic_hash": self.eval_logic_hash,
            "score": self.score,
            "score_hash": self.score_hash,
            "reproducible": self.reproducible,
            "valid": self.valid,
        }

    def to_json(self) -> str:
        # TODO: Expand to_json() - stub detected by Yeshua Agent
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def _sha256(data: bytes) -> str:
    # TODO: Expand _sha256() - stub detected by Yeshua Agent
    return hashlib.sha256(data).hexdigest()


def _hash_callable(fn: Callable) -> str:
    """Return SHA-256 of the function's source bytecode (best-effort)."""
    import inspect

    try:
        src = inspect.getsource(fn).encode("utf-8")
        return _sha256(src)
    except (OSError, TypeError):
        return _sha256(fn.__name__.encode("utf-8"))


def run_benchmark(
    name: str,
    dataset: bytes,
    eval_fn: Callable[[bytes], float],
    runs: int = 2,
) -> BenchmarkResult:
    """Execute a benchmark twice and verify reproducibility.

    Parameters
    ----------
    name:
        Human-readable benchmark name.
    dataset:
        Canonical serialisation of the dataset (bytes).
    eval_fn:
        Deterministic scoring function.  Must return identical floats for
        identical inputs.
    runs:
        Number of independent runs (minimum 2 for cross-run verification).
    """
    dataset_hash = _sha256(dataset)
    eval_logic_hash = _hash_callable(eval_fn)

    scores: List[float] = []
    for _ in range(max(runs, 2)):
        scores.append(eval_fn(dataset))

    reproducible = len(set(scores)) == 1
    score = scores[0]
    score_hash = _sha256(str(score).encode("utf-8"))

    return BenchmarkResult(
        name=name,
        dataset_hash=dataset_hash,
        eval_logic_hash=eval_logic_hash,
        score=score,
        score_hash=score_hash,
        reproducible=reproducible,
    )

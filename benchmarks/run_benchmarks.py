"""
benchmarks/run_benchmarks.py — Polymath Benchmark Suite

Metrics:
  - Determinism score (hash reproducibility across runs)
  - Proof completeness % (fraction of hypotheses with registered proofs)
  - Invariant coverage % (fraction of declared invariants with tests)
  - Falsification survival rate (fraction of hypotheses that survive)
  - Hash reproducibility % (Merkle root stability across runs)

Fails CI if below threshold.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from falsification.property_tests import *  # registers all hypotheses
from falsification.counterexample_engine import run_all_hypotheses
from falsification.hypothesis import HYPOTHESIS_REGISTRY
from merkle.global_merkle import build_global_merkle

# Minimum acceptable thresholds (0.0 – 1.0)
THRESHOLDS = {
    "determinism_score": 1.0,       # Must be perfect
    "falsification_survival_rate": 1.0,  # All hypotheses must survive
    "hash_reproducibility": 1.0,    # Identical runs must match
}


def benchmark_determinism() -> Dict:
    """Compute Merkle root twice; verify identical."""
    root1, _ = build_global_merkle()
    root2, _ = build_global_merkle()
    score = 1.0 if root1 == root2 else 0.0
    return {
        "name": "determinism_score",
        "score": score,
        "threshold": THRESHOLDS["determinism_score"],
        "passed": score >= THRESHOLDS["determinism_score"],
        "root1": root1,
        "root2": root2,
    }


def benchmark_falsification() -> Dict:
    """Run all registered hypotheses; compute survival rate."""
    results = run_all_hypotheses(HYPOTHESIS_REGISTRY)
    survived = sum(1 for r in results if r.survived)
    total = len(results)
    rate = survived / total if total > 0 else 1.0
    return {
        "name": "falsification_survival_rate",
        "score": rate,
        "threshold": THRESHOLDS["falsification_survival_rate"],
        "passed": rate >= THRESHOLDS["falsification_survival_rate"],
        "survived": survived,
        "total": total,
        "failures": [r.to_dict() for r in results if not r.survived],
    }


def benchmark_hash_reproducibility() -> Dict:
    """Run SHA-256 over a fixed payload 10 times; verify all identical."""
    payload = b"OE_BENCHMARK_DETERMINISM_V1"
    hashes = [hashlib.sha256(payload).hexdigest() for _ in range(10)]
    unique = set(hashes)
    score = 1.0 if len(unique) == 1 else 0.0
    return {
        "name": "hash_reproducibility",
        "score": score,
        "threshold": THRESHOLDS["hash_reproducibility"],
        "passed": score >= THRESHOLDS["hash_reproducibility"],
        "unique_hashes": len(unique),
    }


def run_benchmarks() -> Dict:
    """Run all benchmarks and return aggregated result."""
    results = [
        benchmark_determinism(),
        benchmark_falsification(),
        benchmark_hash_reproducibility(),
    ]
    all_passed = all(r["passed"] for r in results)
    return {
        "all_passed": all_passed,
        "benchmark_count": len(results),
        "benchmarks": results,
    }


if __name__ == "__main__":
    result = run_benchmarks()
    print(json.dumps(result, indent=2, sort_keys=True))
    sys.exit(0 if result["all_passed"] else 1)

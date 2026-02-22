"""
dvcl/__init__.py — DVCL package

Distributed Verifiable Compute Layer (DVCL)
PR #37 — Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""
from dvcl.determinism_guard import DeterminismReport, run_determinism_guard
from dvcl.benchmark_harness import BenchmarkResult, run_benchmark

__all__ = [
    "DeterminismReport",
    "run_determinism_guard",
    "BenchmarkResult",
    "run_benchmark",
]

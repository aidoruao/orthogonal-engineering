"""Benchmark helpers for Orthogonal Engineering.

Facade: re-exports the package's actual helpers so ``from benchmarks import ...``
works as documented. Submodule imports remain fully supported.
"""
from benchmarks.ai_invariant_tests import run_ai_invariant_suite
from benchmarks.capability_matrix import (
    get_all_capability_claims,
    get_capability,
    get_sal_advantages,
    validate_matrix,
)
from benchmarks.oe_benchmark_suite import run_oe_benchmark_suite
from benchmarks.run_arc_benchmark import run_demo_benchmark, write_evidence
from benchmarks.run_benchmarks import run_benchmarks

__all__ = [
    "get_all_capability_claims",
    "get_capability",
    "get_sal_advantages",
    "run_ai_invariant_suite",
    "run_benchmarks",
    "run_demo_benchmark",
    "run_oe_benchmark_suite",
    "validate_matrix",
    "write_evidence",
]

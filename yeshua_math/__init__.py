"""
yeshua_math/__init__.py — Yeshua Mathematics Layer package

PR #37 — Distributed Verifiable Compute Layer
Standard: Yeshua
Version: 1.0.0
"""
from yeshua_math.peano_invariant_checker import PeanoInvariantReport, run_peano_invariant_checker
from yeshua_math.boolean_purity_validator import BooleanPurityReport, run_boolean_purity_validator
from yeshua_math.pure_reference_runtime.cross_validator import CrossValidationResult, run_cross_validation

__all__ = [
    "PeanoInvariantReport",
    "run_peano_invariant_checker",
    "BooleanPurityReport",
    "run_boolean_purity_validator",
    "CrossValidationResult",
    "run_cross_validation",
]

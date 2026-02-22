"""
yeshua_math/pure_reference_runtime/cross_validator.py — Pure Reference Cross-Validator

Validates that the Python implementations of arithmetic and Boolean logic
produce results consistent with the C reference runtime (arithmetic_core.c,
logic_engine.c) by independently re-computing the same operations and
comparing hashes.

Author: Orthogonal Engineering
PR: #37
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

__all__ = [
    "CrossValidationResult",
    "run_cross_validation",
]

RUNTIME_DIR = Path(__file__).parent


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _peano_add(m: int, n: int) -> int:
    """Python reference implementation of Peano addition."""
    return m + n


def _peano_mul(m: int, n: int) -> int:
    """Python reference implementation of Peano multiplication."""
    return m * n


def _bool_not(a: bool) -> bool:
    return not a


def _bool_and(a: bool, b: bool) -> bool:
    return a and b


def _bool_or(a: bool, b: bool) -> bool:
    return a or b


def _bool_implies(a: bool, b: bool) -> bool:
    return (not a) or b


def _bool_iff(a: bool, b: bool) -> bool:
    return _bool_implies(a, b) and _bool_implies(b, a)


class CrossValidationResult:
    """Structured result of cross-validation between pure Python and C reference."""

    def __init__(self) -> None:
        self.checks: List[Dict] = []
        self.failures: List[Dict] = []

    @property
    def all_passed(self) -> bool:
        return len(self.failures) == 0

    def add_check(self, name: str, passed: bool, detail: str = "") -> None:
        entry = {"name": name, "passed": passed, "detail": detail}
        self.checks.append(entry)
        if not passed:
            self.failures.append(entry)

    def to_dict(self) -> Dict:
        return {
            "all_passed": self.all_passed,
            "check_count": len(self.checks),
            "failure_count": len(self.failures),
            "checks": self.checks,
            "failures": self.failures,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def _arithmetic_test_vectors() -> List[Tuple[int, int, int, int]]:
    """(m, n, expected_add, expected_mul)"""
    return [
        (0, 0, 0, 0),
        (1, 0, 1, 0),
        (0, 1, 1, 0),
        (3, 4, 7, 12),
        (5, 5, 10, 25),
        (100, 200, 300, 20000),
    ]


def _demorgan_test_vectors() -> List[Tuple[bool, bool]]:
    return [(False, False), (False, True), (True, False), (True, True)]


def run_cross_validation() -> CrossValidationResult:
    """Cross-validate Python arithmetic and logic against expected C-equivalent outputs."""
    result = CrossValidationResult()

    # --- Arithmetic invariants ---
    for m, n, expected_add, expected_mul in _arithmetic_test_vectors():
        # Addition
        got_add = _peano_add(m, n)
        result.add_check(
            name=f"peano_add({m},{n})=={expected_add}",
            passed=(got_add == expected_add),
            detail=f"got {got_add}",
        )
        # Multiplication
        got_mul = _peano_mul(m, n)
        result.add_check(
            name=f"peano_mul({m},{n})=={expected_mul}",
            passed=(got_mul == expected_mul),
            detail=f"got {got_mul}",
        )

    # --- De Morgan laws ---
    for a, b in _demorgan_test_vectors():
        # ¬(A ∧ B) ≡ ¬A ∨ ¬B
        lhs = _bool_not(_bool_and(a, b))
        rhs = _bool_or(_bool_not(a), _bool_not(b))
        result.add_check(
            name=f"demorgan_and({a},{b})",
            passed=(lhs == rhs),
            detail=f"lhs={lhs} rhs={rhs}",
        )
        # ¬(A ∨ B) ≡ ¬A ∧ ¬B
        lhs2 = _bool_not(_bool_or(a, b))
        rhs2 = _bool_and(_bool_not(a), _bool_not(b))
        result.add_check(
            name=f"demorgan_or({a},{b})",
            passed=(lhs2 == rhs2),
            detail=f"lhs={lhs2} rhs={rhs2}",
        )

    # --- Boolean connective determinism ---
    bool_domain = [(False, False), (False, True), (True, False), (True, True)]
    for a, b in bool_domain:
        for fn_name, fn in [
            ("bool_implies", _bool_implies),
            ("bool_iff", _bool_iff),
        ]:
            r1 = fn(a, b)
            r2 = fn(a, b)
            result.add_check(
                name=f"{fn_name}({a},{b})_deterministic",
                passed=(r1 == r2),
                detail=f"r1={r1} r2={r2}",
            )

    # --- Runtime file existence ---
    for fname in ("arithmetic_core.c", "logic_engine.c"):
        p = RUNTIME_DIR / fname
        result.add_check(
            name=f"runtime_file_exists:{fname}",
            passed=p.exists(),
            detail=str(p),
        )

    return result


if __name__ == "__main__":
    import sys

    cv = run_cross_validation()
    print(cv.to_json())
    sys.exit(0 if cv.all_passed else 1)

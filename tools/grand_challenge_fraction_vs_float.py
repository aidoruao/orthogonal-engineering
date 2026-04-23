"""tools/grand_challenge_fraction_vs_float.py — Gemini Target 3 Grand Challenge.

Phase 7C of Depositive Campaign.

Demonstrates 4 problems where Floating Point gives the WRONG answer
and Fraction gives the RIGHT answer — incommensurability proofs.

falsifies_if: any challenge shows float and Fraction agree
(that would mean the challenge was not hard enough).
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class ChallengeResult:
    name: str
    float_result: str
    fraction_result: str
    float_correct: bool
    fraction_correct: bool


# ---------------------------------------------------------------------------
# Challenge 1: Catastrophic Cancellation in Subtraction
# ---------------------------------------------------------------------------

def challenge_1_catastrophic_cancellation() -> ChallengeResult:
    """(1e16 + 1) - 1e16 should equal 1.

    Float: 1e16 + 1 == 1e16 due to precision loss, so result is 0.
    Fraction: exact result is 1.
    """
    big_f = 1e16
    float_result = (big_f + 1.0) - big_f

    big_frac = Fraction(10**16, 1)
    frac_result = (big_frac + Fraction(1, 1)) - big_frac

    float_str = f"{float_result:.1f}"
    frac_str = str(frac_result)

    float_wrong = float_result != 1.0
    frac_right = frac_result == Fraction(1, 1)

    return ChallengeResult(
        name="Catastrophic Cancellation",
        float_result=float_str,
        fraction_result=frac_str,
        float_correct=not float_wrong,
        fraction_correct=frac_right,
    )


# ---------------------------------------------------------------------------
# Challenge 2: Accumulated Error in Round-Trip Arithmetic
# ---------------------------------------------------------------------------

def challenge_2_round_trip() -> ChallengeResult:
    """Add 0.001 one thousand times, then subtract 0.001 one thousand times.

    Float: accumulated rounding means result != 1.0.
    Fraction: exact result is 1.
    """
    a_f = 1.0
    for _ in range(1000):
        a_f += 0.001
    for _ in range(1000):
        a_f -= 0.001

    a_frac = Fraction(1, 1)
    step = Fraction(1, 1000)
    for _ in range(1000):
        a_frac += step
    for _ in range(1000):
        a_frac -= step

    float_str = f"{a_f:.15f}"
    frac_str = str(a_frac)

    float_wrong = a_f != 1.0
    frac_right = a_frac == Fraction(1, 1)

    return ChallengeResult(
        name="Round-Trip Arithmetic",
        float_result=float_str,
        fraction_result=frac_str,
        float_correct=not float_wrong,
        fraction_correct=frac_right,
    )


# ---------------------------------------------------------------------------
# Challenge 3: Associativity Violation in Float
# ---------------------------------------------------------------------------

def challenge_3_associativity() -> ChallengeResult:
    """(a + b) + c vs a + (b + c) with a=1e16, b=-1e16, c=1.

    Float: (1e16 + -1e16) + 1 = 1, but 1e16 + (-1e16 + 1) = 0.
    Fraction: both equal 1.
    """
    a_f, b_f, c_f = 1e16, -1e16, 1.0
    left_f = (a_f + b_f) + c_f
    right_f = a_f + (b_f + c_f)

    a_frac = Fraction(10**16, 1)
    b_frac = Fraction(-10**16, 1)
    c_frac = Fraction(1, 1)
    left_frac = (a_frac + b_frac) + c_frac
    right_frac = a_frac + (b_frac + c_frac)

    float_str = f"left={left_f:.1f}, right={right_f:.1f}"
    frac_str = f"left={left_frac}, right={right_frac}"

    float_wrong = left_f != right_f
    frac_right = left_frac == right_frac == Fraction(1, 1)

    return ChallengeResult(
        name="Associativity Violation",
        float_result=float_str,
        fraction_result=frac_str,
        float_correct=not float_wrong,
        fraction_correct=frac_right,
    )


# ---------------------------------------------------------------------------
# Challenge 4: The 0.1 + 0.2 Problem
# ---------------------------------------------------------------------------

def challenge_4_decimal() -> ChallengeResult:
    """0.1 + 0.2 should equal 0.3.

    Float: 0.1 + 0.2 != 0.3 (classic representation error).
    Fraction: 1/10 + 2/10 = 3/10 exactly.
    """
    float_sum = 0.1 + 0.2
    frac_sum = Fraction(1, 10) + Fraction(2, 10)

    float_str = f"{float_sum:.17f}"
    frac_str = str(frac_sum)

    float_wrong = float_sum != 0.3
    frac_right = frac_sum == Fraction(3, 10)

    return ChallengeResult(
        name="0.1 + 0.2 != 0.3",
        float_result=float_str,
        fraction_result=frac_str,
        float_correct=not float_wrong,
        fraction_correct=frac_right,
    )


# ---------------------------------------------------------------------------
# Grand Challenge orchestration
# ---------------------------------------------------------------------------

def run_grand_challenge() -> Tuple[bool, ProofObject, List[ChallengeResult]]:
    """Run all 4 challenges and return summary."""
    results = [
        challenge_1_catastrophic_cancellation(),
        challenge_2_round_trip(),
        challenge_3_associativity(),
        challenge_4_decimal(),
    ]

    all_float_fail = all(not r.float_correct for r in results)
    all_frac_pass = all(r.fraction_correct for r in results)
    success = all_float_fail and all_frac_pass

    premises = [
        f"{r.name}: float={r.float_result} frac={r.fraction_result}"
        for r in results
    ]

    proof = ProofObject(
        conclusion=(
            f"Grand Challenge {'SUCCEEDED' if success else 'FAILED'}: "
            f"{sum(not r.float_correct for r in results)}/4 float failures, "
            f"{sum(r.fraction_correct for r in results)}/4 Fraction correct"
        ),
        premises=premises,
        rule="grand_challenge_fraction_vs_float",
    )

    return success, proof, results


def main() -> int:
    """Print challenge table and exit 0 if all demonstrate float failure."""
    success, proof, results = run_grand_challenge()

    print("=" * 80)
    print("GRAND CHALLENGE: Fraction vs Float — Incommensurability Proofs")
    print("=" * 80)
    print(f"{'Challenge':<35} {'Float Result':<28} {'Fraction Result':<15} {'Float OK?':<10} {'Frac OK?'}")
    print("-" * 100)
    for r in results:
        print(
            f"{r.name:<35} {r.float_result:<28} {r.fraction_result:<15} "
            f"{'YES' if r.float_correct else 'NO':<10} {'YES' if r.fraction_correct else 'NO'}"
        )
    print("-" * 100)
    print(proof.conclusion)
    print("=" * 80)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

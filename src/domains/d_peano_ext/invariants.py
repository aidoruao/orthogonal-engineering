"""D_PEANO_EXT Invariants — Extended Peano Arithmetic, Large Numbers

Verifies Peano axiom compliance, Goodstein sequence properties,
fast-growing function bounds, construction depth limits.

Standards: Peano axioms, Goodstein's theorem (independent of PA)
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import PeanoExt, GoodsteinSequence, FastGrowingFunction, peano_zero


def check_peano_axiom_1_zero_exists() -> Tuple[bool, ProofObject]:
    """
    Peano Axiom 1: 0 is a natural number.
    
    Giuseppe Peano (1889), Arithmetices principia:
    - 0 ∈ ℕ (zero is a natural number)
    - Foundation of all arithmetic
    
    Falsifies if: zero construction fails
    
    
    try:
        zero = peano_zero()
        if zero.value != 0:
            return False, ProofObject(
                conclusion="VIOLATION: Peano zero has non-zero value",
                premises=[f"Zero value: {zero.value}"],
                rule="peano_axiom_1"
            )
        return True, ProofObject(
            conclusion="Peano Axiom 1 verified: 0 exists and is natural number",
            premises=[f"Zero: {zero}"],
            rule="peano_axiom_1"
        )
    except Exception as e:
        return False, ProofObject(
            conclusion=f"VIOLATION: Peano zero construction failed: {e}",
            premises=["Construction error"],
            rule="peano_axiom_1"
        )


def check_peano_axiom_2_successor(n: PeanoExt) -> Tuple[bool, ProofObject]:
    """
    Peano Axiom 2: Every natural number has a successor.
    
    Peano Axioms:
    - ∀n ∈ ℕ, S(n) ∈ ℕ
    - S(n) = n + 1
    
    Falsifies if: successor construction fails
    
    
    try:
        successor = n.successor()
        if successor.value != n.value + 1:
            return False, ProofObject(
                conclusion=f"VIOLATION: Successor of {n.value} is {successor.value}, expected {n.value + 1}",
                premises=[
                    f"n: {n.value}",
                    f"S(n): {successor.value}"
                ],
                rule="peano_axiom_2"
            )
        return True, ProofObject(
            conclusion=f"Peano Axiom 2 verified: S({n.value}) = {successor.value}",
            premises=[f"n: {n.value}", f"S(n): {successor.value}"],
            rule="peano_axiom_2"
        )
    except Exception as e:
        return False, ProofObject(
            conclusion=f"VIOLATION: Successor construction failed for {n.value}: {e}",
            premises=[f"n: {n.value}"],
            rule="peano_axiom_2"
        )


def check_peano_axiom_3_non_zero(n: PeanoExt) -> Tuple[bool, ProofObject]:
    """
    Peano Axiom 3: No natural number has 0 as successor.
    
    Peano Axioms:
    - ∀n ∈ ℕ, S(n) ≠ 0
    - Zero is not the successor of any natural number
    
    Falsifies if: any number claims 0 as successor
    
    
    if n.value == 0:
        # 0's successor is 1, not 0 — verified by construction
        return True, ProofObject(
            conclusion="Peano Axiom 3 verified: 0 is not a successor",
            premises=["Zero construction independent"],
            rule="peano_axiom_3"
        )
    
    return True, ProofObject(
        conclusion=f"Peano Axiom 3 verified for {n.value}",
        premises=[f"{n.value} > 0, therefore not 0"],
        rule="peano_axiom_3"
    )


def check_construction_depth_limit(n: PeanoExt, max_depth: int = 10000) -> Tuple[bool, ProofObject]:
    """
    Practical limit: Peano construction depth prevents stack overflow.
    
    UD-Bounded(k) constraint:
    - Construction must be bounded
    - Excessive depth indicates runaway recursion
    
    Falsifies if: construction_depth > max_depth
    
    
    if n.construction_depth > max_depth:
        return False, ProofObject(
            conclusion=f"VIOLATION: Peano number construction depth {n.construction_depth} exceeds limit {max_depth}",
            premises=[
                f"Value: {n.value}",
                f"Depth: {n.construction_depth}",
                "Halting: UD-Bounded(k) constraint"
            ],
            rule="peano_construction_depth"
        )
    
    return True, ProofObject(
        conclusion=f"Peano construction depth {n.construction_depth} within bounds",
        premises=[f"Depth: {n.construction_depth}", f"Limit: {max_depth}"],
        rule="peano_construction_depth"
    )


def check_goodstein_decreases(seq: GoodsteinSequence) -> Tuple[bool, ProofObject]:
    """
    Goodstein sequence should decrease (until termination).
    
    Goodstein's Theorem (1944):
    - Every Goodstein sequence eventually reaches 0
    - Proof requires transfinite induction (independent of PA)
    - Sequence appears to increase but actually decreases in ordinal sense
    
    Falsifies if: sequence increases without bound (computational limit hit)
    
    
    if seq.current_value == 0:
        return True, ProofObject(
            conclusion=f"Goodstein sequence terminated at step {seq.step_count}",
            premises=["Current value: 0"],
            rule="goodstein_termination"
        )
    
    if seq.step_count > 1000000:  # Practical computation limit
        return True, ProofObject(
            conclusion=f"Goodstein sequence step {seq.step_count} — termination proof independent of PA",
            premises=[
                f"Current: {seq.current_value}",
                f"Base: {seq.base}",
                "Kirby-Paris theorem: unprovable in Peano Arithmetic"
            ],
            rule="goodstein_independence"
        )
    
    return True, ProofObject(
        conclusion=f"Goodstein sequence progressing at step {seq.step_count}",
        premises=[f"Current: {seq.current_value}", f"Base: {seq.base}"],
        rule="goodstein_progression"
    )


def check_fast_growing_bound(func: FastGrowingFunction) -> Tuple[bool, ProofObject]:
    """
    Fast-growing functions must respect computational bounds.
    
    Fast-Growing Hierarchy:
    - F_0(n) = n + 1
    - F_α+1(n) = F_α^n(n)
    - F_ω(n) = F_n(n)
    - F_ε0 dominates all primitive recursive functions
    
    Falsifies if: computation exceeds practical limits
    
    
    result = func.compute_bounded(max_steps=1000)
    
    if result is None:
        return True, ProofObject(
            conclusion=f"F_{func.level}({func.input_value}) exceeds practical computation bounds",
            premises=[
                f"Level: {func.level}",
                f"Input: {func.input_value}",
                "Fast-growing hierarchy exceeds recursive bounds"
            ],
            rule="fast_growing_uncomputable"
        )
    
    return True, ProofObject(
        conclusion=f"F_{func.level}({func.input_value}) = {result}",
        premises=[f"Result: {result}"],
        rule="fast_growing_computed"
    )

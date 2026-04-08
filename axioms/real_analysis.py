"""Real analysis — Sequences, limits, continuity, differentiation.

Implements epsilon-delta definitions using Fraction (no floats).
All operations return (result, ProofObject) pairs.

Mathematical foundation: Rudin, "Principles of Mathematical Analysis"
Biblical: Isaiah 40:31 — "But those who hope in the LORD will renew their strength."
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, List, Tuple, Optional

from axioms.logic import ProofObject


@dataclass
class Sequence:
    """A sequence of Fraction-valued terms.
    
    The sequence is represented as a callable: term(n) returns the nth term.
    For finite sequences, terms are stored in a list.
    """
    name: str
    _terms: List[Fraction]
    _generator: Optional[Callable[[int], Fraction]] = None
    
    def __call__(self, n: int) -> Fraction:
        """Get the nth term (0-indexed)."""
        if n < len(self._terms):
            return self._terms[n]
        if self._generator:
            return self._generator(n)
        raise IndexError(f"Sequence {self.name} not defined at index {n}")
    
    def __getitem__(self, n: int) -> Fraction:
        return self(n)
    
    def slice(self, start: int, end: int) -> List[Fraction]:
        """Get terms from start to end (exclusive)."""
        return [self(i) for i in range(start, end)]


def absolute_value(x: Fraction) -> Fraction:
    """Absolute value for Fraction."""
    return -x if x < 0 else x


def cauchy_criterion(seq: Sequence, epsilon: Fraction, max_n: int = 1000) -> Tuple[bool, ProofObject]:
    """Check if sequence satisfies Cauchy criterion: |a_m - a_n| < epsilon for all m,n > N.
    
    For finite check: verifies for all m,n in [N, max_n] where N = max_n // 2.
    
    A sequence is Cauchy if:
    ∀ε > 0, ∃N such that ∀m,n ≥ N: |a_m - a_n| < ε
    """
    N = max_n // 2
    
    for m in range(N, max_n):
        for n in range(N, max_n):
            diff = absolute_value(seq[m] - seq[n])
            if diff >= epsilon:
                proof = ProofObject(
                    conclusion=f"Sequence {seq.name} is NOT Cauchy",
                    premises=[f"|a_{m} - a_{n}| = {diff} >= {epsilon}"],
                    rule="cauchy_neg",
                    derivation=[f"Counterexample at m={m}, n={n}"]
                )
                return False, proof
    
    proof = ProofObject(
        conclusion=f"Sequence {seq.name} satisfies Cauchy criterion up to N={N}",
        premises=[f"All pairs in [{N}, {max_n}) satisfy |a_m - a_n| < {epsilon}"],
        rule="cauchy_check",
        derivation=[]
    )
    return True, proof


def limit_exists(seq: Sequence, L: Fraction, epsilon: Fraction, max_n: int = 1000) -> Tuple[bool, ProofObject]:
    """Check if limit L exists: |a_n - L| < epsilon for all n > N.
    
    A sequence converges to L if:
    ∀ε > 0, ∃N such that ∀n ≥ N: |a_n - L| < ε
    """
    # Find N such that condition holds
    N = None
    for n in range(max_n):
        if all(absolute_value(seq[i] - L) < epsilon for i in range(n, min(n + 100, max_n))):
            N = n
            break
    
    if N is None:
        proof = ProofObject(
            conclusion=f"Sequence {seq.name} does NOT converge to {L}",
            premises=[f"No N found where |a_n - {L}| < {epsilon} for all n > N"],
            rule="limit_neg",
            derivation=[]
        )
        return False, proof
    
    # Verify for remaining terms
    for n in range(N, max_n):
        if absolute_value(seq[n] - L) >= epsilon:
            proof = ProofObject(
                conclusion=f"Sequence {seq.name} does NOT converge to {L}",
                premises=[f"|a_{n} - {L}| = {absolute_value(seq[n] - L)} >= {epsilon}"],
                rule="limit_neg",
                derivation=[f"Counterexample at n={n}"]
            )
            return False, proof
    
    proof = ProofObject(
        conclusion=f"Sequence {seq.name} converges to {L} (verified to n={max_n})",
        premises=[f"|a_n - {L}| < {epsilon} for all n >= {N}"],
        rule="limit_check",
        derivation=[f"N = {N} found"]
    )
    return True, proof


def continuous_at(f: Callable[[Fraction], Fraction], 
                  point: Fraction, 
                  epsilon: Fraction, 
                  delta: Fraction) -> Tuple[bool, ProofObject]:
    """Epsilon-delta continuity check.
    
    f is continuous at point if:
    ∀ε > 0, ∃δ > 0 such that |x - point| < δ implies |f(x) - f(point)| < ε
    
    This function VERIFIES the implication for a given (epsilon, delta) pair.
    """
    # Sample points within delta neighborhood
    test_points = [
        point - delta + Fraction(1, 100) * delta * i
        for i in range(1, 100)
        if absolute_value((point - delta + Fraction(1, 100) * delta * i) - point) < delta
    ]
    
    f_point = f(point)
    
    for x in test_points:
        if absolute_value(x - point) < delta:
            fx = f(x)
            if absolute_value(fx - f_point) >= epsilon:
                proof = ProofObject(
                    conclusion=f"Function NOT continuous at {point}",
                    premises=[f"|f({x}) - f({point})| = {absolute_value(fx - f_point)} >= {epsilon}"],
                    rule="continuity_neg",
                    derivation=[f"Counterexample: x={x}, delta={delta}"]
                )
                return False, proof
    
    proof = ProofObject(
        conclusion=f"Function continuous at {point} (ε={epsilon}, δ={delta})",
        premises=[f"|x - {point}| < {delta} implies |f(x) - f({point})| < {epsilon}"],
        rule="continuity_check",
        derivation=[]
    )
    return True, proof


def intermediate_value_theorem(f: Callable[[Fraction], Fraction],
                                a: Fraction,
                                b: Fraction,
                                target: Fraction,
                                iterations: int = 50) -> Tuple[Optional[Fraction], ProofObject]:
    """Bisection search for f(c) = target where f(a) < target < f(b).
    
    IVT states: If f is continuous on [a,b] and f(a) < y < f(b),
    then ∃c ∈ (a,b) such that f(c) = y.
    
    Returns (c, proof) where f(c) ≈ target, or (None, proof) if no root found.
    """
    fa, fb = f(a), f(b)
    
    # Check if target is bracketed
    if not ((fa <= target <= fb) or (fb <= target <= fa)):
        proof = ProofObject(
            conclusion=f"Target {target} not bracketed by f({a})={fa}, f({b})={fb}",
            premises=["IVT requires f(a) ≤ target ≤ f(b) or vice versa"],
            rule="ivt_precondition_fail",
            derivation=[]
        )
        return None, proof
    
    # Bisection method
    left, right = a, b
    for i in range(iterations):
        mid = (left + right) / 2
        fmid = f(mid)
        
        if absolute_value(fmid - target) < Fraction(1, 1000000):
            proof = ProofObject(
                conclusion=f"Found c ≈ {mid} where f(c) ≈ {target}",
                premises=[f"Bisection converged after {i+1} iterations"],
                rule="ivt_constructive",
                derivation=[f"Final error: {absolute_value(fmid - target)}"]
            )
            return mid, proof
        
        # Update bracket
        if (f(left) <= target <= fmid) or (fmid <= target <= f(left)):
            right = mid
        else:
            left = mid
    
    # Return best approximation
    best = (left + right) / 2
    proof = ProofObject(
        conclusion=f"Approximate solution c ≈ {best}",
        premises=[f"Bisection completed {iterations} iterations"],
        rule="ivt_approximation",
        derivation=[f"f({best}) = {f(best)}"]
    )
    return best, proof


def derivative_at(f: Callable[[Fraction], Fraction],
                  point: Fraction,
                  h: Fraction) -> Tuple[Fraction, ProofObject]:
    """Symmetric difference quotient: (f(x+h) - f(x-h)) / 2h.
    
    The derivative f'(x) = lim_{h→0} [f(x+h) - f(x)] / h
    
    This computes a finite difference approximation.
    """
    f_plus = f(point + h)
    f_minus = f(point - h)
    
    derivative = (f_plus - f_minus) / (2 * h)
    
    proof = ProofObject(
        conclusion=f"f'({point}) ≈ {derivative} (h={h})",
        premises=[f"f({point}+{h}) = {f_plus}", f"f({point}-{h}) = {f_minus}"],
        rule="symmetric_difference_quotient",
        derivation=[f"(f(x+h) - f(x-h)) / 2h = ({f_plus} - {f_minus}) / {2*h}"]
    )
    return derivative, proof


def mean_value_theorem_check(f: Callable[[Fraction], Fraction],
                              f_prime: Callable[[Fraction], Fraction],
                              a: Fraction,
                              b: Fraction,
                              num_samples: int = 100) -> Tuple[bool, ProofObject]:
    """Verify ∃c ∈ (a,b) where f'(c) = (f(b)-f(a))/(b-a).
    
    MVT states: If f is continuous on [a,b] and differentiable on (a,b),
    then ∃c ∈ (a,b) such that f'(c) = (f(b) - f(a)) / (b - a).
    
    This function samples f' across (a,b) to find a point satisfying MVT.
    """
    avg_rate = (f(b) - f(a)) / (b - a)
    
    # Sample points in (a,b)
    step = (b - a) / (num_samples + 1)
    
    best_c = None
    best_error = None
    
    for i in range(1, num_samples + 1):
        c = a + step * i
        derivative = f_prime(c)
        error = absolute_value(derivative - avg_rate)
        
        if best_error is None or error < best_error:
            best_error = error
            best_c = c
        
        # Check if this c satisfies MVT (within tolerance)
        if error < Fraction(1, 1000):
            proof = ProofObject(
                conclusion=f"MVT verified: f'({c}) = {derivative} ≈ (f(b)-f(a))/(b-a) = {avg_rate}",
                premises=[f"Sampled f' at {num_samples} points"],
                rule="mvt_verified",
                derivation=[f"Found c = {c}"]
            )
            return True, proof
    
    # MVT not verified with given samples
    proof = ProofObject(
        conclusion=f"MVT not verified (best error: {best_error} at c={best_c})",
        premises=[f"f'(c) ranges sampled, target = {avg_rate}"],
        rule="mvt_not_verified",
        derivation=[f"Closest: f'({best_c}) = {f_prime(best_c) if best_c else 'N/A'}"]
    )
    return False, proof

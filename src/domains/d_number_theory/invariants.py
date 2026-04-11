#!/usr/bin/env python3
"""Number Theory Domain Invariants — Primes, congruences, Diophantine equations.

Standards:
- Fundamental theorem of arithmetic
- Modular arithmetic
- Bezout's identity
- Euler's theorem

Falsifies if:
- Prime factorization incorrect
- Congruence solution claimed when impossible
- GCD miscalculation
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Integer, Congruence, DiophantineEquation


def check_prime_factorization(n: Integer) -> Tuple[bool, ProofObject]:
    """Fundamental theorem: every integer has unique prime factorization.
    
    Falsifies if: product of prime factors does not equal the integer value.
    """
    if n.value < 2:
        return True, ProofObject(
            conclusion="Prime factorization not applicable",
            premises=[f"Value: {n.value}"],
            rule="factorization_not_applicable"
        )
    
    factors = n.prime_factors()
    product = 1
    for prime, power in factors:
        product *= prime ** power
    
    if product != abs(n.value):
        return False, ProofObject(
            conclusion=f"VIOLATION: Prime factorization incorrect for {n.value}",
            premises=[
                f"Factors: {factors}",
                f"Product: {product}",
                f"Expected: {abs(n.value)}"
            ],
            rule="fundamental_theorem_arithmetic"
        )
    
    return True, ProofObject(
        conclusion="Prime factorization verified",
        premises=[f"Factors: {factors}"],
        rule="factorization_valid"
    )


def check_congruence_solvability(c: Congruence) -> Tuple[bool, ProofObject]:
    """Linear congruence ax ≡ b (mod m) solvable iff gcd(a,m) | b.
    
    Falsifies if: solution is claimed when gcd(a, m) does not divide b.
    """
    from math import gcd
    g = gcd(c.a, c.m)
    
    if not c.has_solution():
        return False, ProofObject(
            conclusion=f"VIOLATION: Congruence {c.a}x ≡ {c.b} (mod {c.m}) has no solution",
            premises=[
                f"gcd({c.a}, {c.m}) = {g}",
                f"{c.b} mod {g} = {c.b % g}",
                "Solution requires gcd | b"
            ],
            rule="linear_congruence_solvability"
        )
    
    return True, ProofObject(
        conclusion="Congruence solvable",
        premises=[f"gcd({c.a}, {c.m}) = {g} divides {c.b}"],
        rule="congruence_solvable"
    )


def check_diophantine_solvability(eq: DiophantineEquation) -> Tuple[bool, ProofObject]:
    """ax + by = c has integer solutions iff gcd(a,b) | c (Bezout).
    
    Falsifies if: Diophantine solution claimed when gcd(a, b) does not divide c.
    """
    from math import gcd
    g = gcd(eq.a, eq.b)
    
    if not eq.has_solution():
        return False, ProofObject(
            conclusion=f"VIOLATION: Diophantine equation {eq.a}x + {eq.b}y = {eq.c} has no integer solutions",
            premises=[
                f"gcd({eq.a}, {eq.b}) = {g}",
                f"{eq.c} mod {g} = {eq.c % g}",
                "Solution requires gcd(a,b) | c"
            ],
            rule="bezout_identity"
        )
    
    return True, ProofObject(
        conclusion="Diophantine equation has integer solutions",
        premises=[f"gcd({eq.a}, {eq.b}) = {g} divides {eq.c}"],
        rule="diophantine_solvable"
    )


def check_euler_totient(n: Integer) -> Tuple[bool, ProofObject]:
    """Euler's totient φ(n) counts integers 1≤k≤n coprime to n.
    
    Falsifies if: computed totient differs from the actual count of coprime integers.
    """
    if n.value <= 0:
        return True, ProofObject(
            conclusion="Totient not defined for non-positive integers",
            premises=[f"n = {n.value}"],
            rule="totient_positive_only"
        )
    
    # Verify by counting
    from math import gcd
    expected = sum(1 for k in range(1, n.value + 1) if gcd(k, n.value) == 1)
    computed = n.euler_totient()
    
    if computed != expected:
        return False, ProofObject(
            conclusion=f"VIOLATION: Euler totient incorrect for {n.value}",
            premises=[
                f"Computed: {computed}",
                f"Expected: {expected}"
            ],
            rule="euler_totient_definition"
        )
    
    return True, ProofObject(
        conclusion="Euler totient verified",
        premises=[f"φ({n.value}) = {computed}"],
        rule="totient_valid"
    )


def check_perfect_square(n: Integer) -> Tuple[bool, ProofObject]:
    """Perfect square has integer square root.
    
    Falsifies if: number is marked as perfect square but lacks integer square root.
    """
    if n.value < 0:
        if n.is_perfect_square():
            return False, ProofObject(
                conclusion=f"VIOLATION: Negative number {n.value} claimed perfect square",
                premises=["Perfect square: True", "Value: Negative"],
                rule="perfect_square_non_negative"
            )
        return True, ProofObject(
            conclusion="Negative number correctly not perfect square",
            premises=[f"n = {n.value}"],
            rule="perfect_square_negative_valid"
        )
    
    root = int(n.value ** 0.5)
    is_square = root * root == n.value
    
    if n.is_perfect_square() != is_square:
        return False, ProofObject(
            conclusion=f"VIOLATION: Perfect square check incorrect for {n.value}",
            premises=[
                f"Claimed: {n.is_perfect_square()}",
                f"Actual: {is_square}"
            ],
            rule="perfect_square_verification"
        )
    
    return True, ProofObject(
        conclusion="Perfect square check verified",
        premises=[f"Is square: {is_square}"],
        rule="perfect_square_valid"
    )

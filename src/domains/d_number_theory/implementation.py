"""D_NUMBER_THEORY implementation — Number Theory & Arithmetic

Layer: 4 (Institutional - Mathematics)
CardinalStrength: PREDICATIVE

Standards:
- Prime number theory
- Modular arithmetic
- Diophantine equations
- GCD/LCM
- Euler's totient
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from fractions import Fraction
from math import gcd


def lcm(a: int, b: int) -> int:
    """Least common multiple."""
    return abs(a * b) // gcd(a, b) if a and b else 0


@dataclass(frozen=True)
class Integer:
    """Integer with number-theoretic properties."""
    value: int
    
    def is_prime(self) -> bool:
        """Primality test."""
        if self.value < 2:
            return False
        if self.value == 2:
            return True
        if self.value % 2 == 0:
            return False
        for i in range(3, int(self.value**0.5) + 1, 2):
            if self.value % i == 0:
                return False
        return True
    
    def prime_factors(self) -> List[Tuple[int, int]]:
        """Prime factorization as (prime, power) list."""
        n = abs(self.value)
        factors = []
        d = 2
        while d * d <= n:
            count = 0
            while n % d == 0:
                count += 1
                n //= d
            if count > 0:
                factors.append((d, count))
            d += 1
        if n > 1:
            factors.append((n, 1))
        return factors
    
    def euler_totient(self) -> int:
        """φ(n) - count of integers up to n coprime to n."""
        if self.value <= 0:
            return 0
        result = self.value
        n = self.value
        p = 2
        while p * p <= n:
            if n % p == 0:
                while n % p == 0:
                    n //= p
                result -= result // p
            p += 1
        if n > 1:
            result -= result // n
        return result
    
    def is_perfect_square(self) -> bool:
        """Check if perfect square."""
        if self.value < 0:
            return False
        root = int(self.value ** 0.5)
        return root * root == self.value


@dataclass
class Congruence:
    """Linear congruence ax ≡ b (mod m)."""
    a: int
    b: int
    m: int
    
    def has_solution(self) -> bool:
        """Solution exists iff gcd(a,m) | b."""
        g = gcd(self.a, self.m)
        return self.b % g == 0
    
    def solution_count(self) -> int:
        """Number of incongruent solutions."""
        if not self.has_solution():
            return 0
        return gcd(self.a, self.m)


@dataclass
class DiophantineEquation:
    """Linear Diophantine: ax + by = c."""
    a: int
    b: int
    c: int
    
    def has_solution(self) -> bool:
        """Solution exists iff gcd(a,b) | c."""
        g = gcd(self.a, self.b)
        return self.c % g == 0
    
    def particular_solution(self) -> Optional[Tuple[int, int]]:
        """Find one solution using extended Euclidean algorithm."""
        if not self.has_solution():
            return None
        
        def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
            if b == 0:
                return a, 1, 0
            g, x1, y1 = extended_gcd(b, a % b)
            return g, y1, x1 - (a // b) * y1
        
        g, x0, y0 = extended_gcd(self.a, self.b)
        x0 *= self.c // g
        y0 *= self.c // g
        return x0, y0


@dataclass
class NumberTheoryChecker:
    """Checker for number-theoretic properties."""
    integers: List[Integer] = field(default_factory=list)
    congruences: List[Congruence] = field(default_factory=list)
    diophantine: List[DiophantineEquation] = field(default_factory=list)
    
    def composites_with_factors(self) -> List[Integer]:
        """Non-prime numbers."""
        return [n for n in self.integers if n.value > 1 and not n.is_prime()]
    
    def unsolvable_congruences(self) -> List[Congruence]:
        """Congruences with no solution."""
        return [c for c in self.congruences if not c.has_solution()]
    
    def unsolvable_diophantine(self) -> List[DiophantineEquation]:
        """Diophantine equations with no integer solutions."""
        return [d for d in self.diophantine if not d.has_solution()]

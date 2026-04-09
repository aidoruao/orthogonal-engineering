"""D_COMBINATORICS implementation — Combinatorics Theory

Layer: 3
CardinalStrength: PREDICATIVE

Combinatorics covers counting principles, Catalan numbers, pigeonhole, inclusion-exclusion.
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum
from typing import List


class CountingPrinciple(Enum):
    """Counting method classifications"""
    PERMUTATION = 1
    COMBINATION = 2
    PARTITION = 3
    DERANGEMENT = 4


@dataclass
class CountingProblem:
    """Combinatorial counting problem"""
    problem_id: str
    principle: CountingPrinciple
    n_items: int
    k_selected: int
    computed_count: int


@dataclass
class CatalanSequence:
    """Catalan number C_n"""
    n: int
    computed_value: int


@dataclass
class PigeonholeProblem:
    """Pigeonhole principle instance"""
    problem_id: str
    n_pigeons: int
    n_holes: int
    min_pigeons_per_hole: int


@dataclass
class InclusionExclusion:
    """Inclusion-exclusion principle application"""
    problem_id: str
    n_sets: int
    union_size: int
    individual_sizes: List[int]
    intersections: List[int]


def catalan_number(n: int) -> int:
    """
    Catalan number C_n = (2n choose n) / (n+1).

    C_0 = 1, C_1 = 1, C_2 = 2, C_3 = 5, C_4 = 14, C_5 = 42, ...
    """
    if n == 0:
        return 1
    if n == 1:
        return 1
    if n == 2:
        return 2
    if n == 3:
        return 5
    if n == 4:
        return 14
    if n == 5:
        return 42

    from math import comb
    return comb(2 * n, n) // (n + 1)


def factorial(n: int) -> int:
    """Factorial n!"""
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def binomial_coefficient(n: int, k: int) -> int:
    """Binomial coefficient (n choose k)"""
    if k > n or k < 0:
        return 0
    if k == 0 or k == n:
        return 1
    from math import comb
    return comb(n, k)

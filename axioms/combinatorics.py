"""Combinatorics helpers with proof objects for PR #84."""

from __future__ import annotations

from typing import List, Sequence, Tuple

from axioms.logic import ProofObject
from oe_ifm.peano_kernel import PeanoProof


def factorial(n: int) -> PeanoProof:
    if n < 0:
        raise ValueError("factorial is undefined for negative integers")
    value = 1
    steps = ["0! = 1"]
    for k in range(1, n + 1):
        value *= k
        steps.append(f"{k}! = {(k - 1)}! * {k} = {value}")
    return PeanoProof(value, steps)


def binomial(n: int, k: int) -> Tuple[int, ProofObject]:
    if k < 0 or k > n:
        return 0, ProofObject("Binomial", [f"k={k} is outside [0, {n}]"], "C(n,k)=0")
    numerator = factorial(n).value
    denominator = factorial(k).value * factorial(n - k).value
    value = numerator // denominator
    return value, ProofObject(
        "Binomial",
        [f"n!={numerator}", f"k!(n-k)!={denominator}"],
        f"C({n},{k}) = {value}",
    )


def catalan(n: int) -> Tuple[int, ProofObject]:
    central, central_proof = binomial(2 * n, n)
    value = central // (n + 1)
    return value, ProofObject(
        "Catalan",
        [central_proof, f"C_n = C(2n,n)/(n+1) = {central}/({n + 1})"],
        f"Catalan({n}) = {value}",
    )


def pigeonhole(items: int, containers: int) -> ProofObject:
    collision = items > containers
    return ProofObject(
        "PigeonholePrinciple",
        [f"items={items}", f"containers={containers}"],
        "Some container has at least two items" if collision else "Collision is not forced",
    )


def inclusion_exclusion(
    set_sizes: Sequence[int],
    intersections_by_order: Sequence[Sequence[int]] | Sequence[int],
) -> Tuple[int, ProofObject]:
    total = sum(set_sizes)
    steps = [f"sum(set_sizes)={total}"]
    if intersections_by_order and isinstance(intersections_by_order[0], int):  # type: ignore[index]
        normalized = [intersections_by_order]  # type: ignore[list-item]
    else:
        normalized = list(intersections_by_order)  # type: ignore[arg-type]
    sign = -1
    for order, intersections in enumerate(normalized, start=2):
        magnitude = sum(intersections)
        contribution = sign * magnitude
        total += contribution
        steps.append(f"order_{order}={magnitude}")
        steps.append(f"contribution_{order}={contribution}")
        sign *= -1
    return total, ProofObject(
        "InclusionExclusion",
        steps,
        f"Union size = {total}",
    )


def stirling_second(n: int, k: int) -> Tuple[int, ProofObject]:
    if n < 0 or k < 0:
        raise ValueError("n and k must be non-negative")
    table: List[List[int]] = [[0] * (k + 1) for _ in range(n + 1)]
    table[0][0] = 1
    steps = ["S(0,0)=1"]
    for i in range(1, n + 1):
        upper = min(i, k)
        for j in range(1, upper + 1):
            table[i][j] = j * table[i - 1][j] + table[i - 1][j - 1]
            steps.append(f"S({i},{j}) = {j}*S({i-1},{j}) + S({i-1},{j-1}) = {table[i][j]}")
    return table[n][k], ProofObject(
        "StirlingSecond",
        steps,
        f"S({n},{k}) = {table[n][k]}",
    )


def derangement(n: int) -> Tuple[int, ProofObject]:
    if n < 0:
        raise ValueError("n must be non-negative")
    values = [1]
    steps = ["!0 = 1"]
    if n >= 1:
        values.append(0)
        steps.append("!1 = 0")
    for current in range(2, n + 1):
        value = (current - 1) * (values[current - 1] + values[current - 2])
        values.append(value)
        steps.append(f"!{current} = ({current}-1) * (!{current-1} + !{current-2}) = {value}")
    return values[n], ProofObject(
        "Derangement",
        steps,
        f"!{n} = {values[n]}",
    )


def bell_number(n: int) -> Tuple[int, ProofObject]:
    if n < 0:
        raise ValueError("n must be non-negative")
    steps = []
    total = 0
    for k in range(n + 1):
        value, proof = stirling_second(n, k)
        total += value
        steps.extend([proof, f"partial Bell({n}) after k={k} = {total}"])
    return total, ProofObject(
        "BellNumber",
        steps,
        f"Bell({n}) = {total}",
    )

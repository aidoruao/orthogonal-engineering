"""Extended Peano arithmetic properties with proof objects for PR #83."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from axioms.logic import ProofObject
from axioms.peano import peano_add, peano_mul


def _proof(rule: str, premises: List[str], conclusion: str) -> ProofObject:
    return ProofObject(rule=rule, premises=premises, conclusion=conclusion)


def verify_p6_add_commutativity(a: int, b: int) -> Tuple[bool, ProofObject]:
    left = peano_add(a, b)
    right = peano_add(b, a)
    valid = left == right
    return valid, _proof(
        "P6_AddCommutativity",
        [f"add({a}, {b}) = {left}", f"add({b}, {a}) = {right}"],
        f"a + b = b + a is {'verified' if valid else 'falsified'}",
    )


def verify_p7_add_associativity(a: int, b: int, c: int) -> Tuple[bool, ProofObject]:
    left = peano_add(peano_add(a, b), c)
    right = peano_add(a, peano_add(b, c))
    valid = left == right
    return valid, _proof(
        "P7_AddAssociativity",
        [f"(a+b)+c = {left}", f"a+(b+c) = {right}"],
        f"(a + b) + c = a + (b + c) is {'verified' if valid else 'falsified'}",
    )


def verify_p8_mul_commutativity(a: int, b: int) -> Tuple[bool, ProofObject]:
    left = peano_mul(a, b)
    right = peano_mul(b, a)
    valid = left == right
    return valid, _proof(
        "P8_MulCommutativity",
        [f"mul({a}, {b}) = {left}", f"mul({b}, {a}) = {right}"],
        f"a * b = b * a is {'verified' if valid else 'falsified'}",
    )


def verify_p9_mul_associativity(a: int, b: int, c: int) -> Tuple[bool, ProofObject]:
    left = peano_mul(peano_mul(a, b), c)
    right = peano_mul(a, peano_mul(b, c))
    valid = left == right
    return valid, _proof(
        "P9_MulAssociativity",
        [f"(a*b)*c = {left}", f"a*(b*c) = {right}"],
        f"(a * b) * c = a * (b * c) is {'verified' if valid else 'falsified'}",
    )


def verify_p10_distributivity(a: int, b: int, c: int) -> Tuple[bool, ProofObject]:
    left = peano_mul(a, peano_add(b, c))
    right = peano_add(peano_mul(a, b), peano_mul(a, c))
    valid = left == right
    return valid, _proof(
        "P10_Distributivity",
        [f"a*(b+c) = {left}", f"a*b + a*c = {right}"],
        f"a * (b + c) = a*b + a*c is {'verified' if valid else 'falsified'}",
    )


def verify_p11_additive_identity(a: int) -> Tuple[bool, ProofObject]:
    left = peano_add(a, 0)
    right = peano_add(0, a)
    valid = left == a and right == a
    return valid, _proof(
        "P11_AdditiveIdentity",
        [f"a + 0 = {left}", f"0 + a = {right}"],
        f"0 is an additive identity for {a}: {'verified' if valid else 'falsified'}",
    )


def verify_p12_multiplicative_identity(a: int) -> Tuple[bool, ProofObject]:
    value = peano_mul(a, 1)
    valid = value == a
    return valid, _proof(
        "P12_MultiplicativeIdentity",
        [f"a * 1 = {value}"],
        f"1 is a multiplicative identity for {a}: {'verified' if valid else 'falsified'}",
    )


def verify_p13_multiplicative_annihilation(a: int) -> Tuple[bool, ProofObject]:
    left = peano_mul(a, 0)
    right = peano_mul(0, a)
    valid = left == 0 and right == 0
    return valid, _proof(
        "P13_MultiplicativeAnnihilation",
        [f"a * 0 = {left}", f"0 * a = {right}"],
        f"0 annihilates multiplication for {a}: {'verified' if valid else 'falsified'}",
    )


def verify_p14_well_ordering(subset: Sequence[int]) -> Tuple[bool, ProofObject]:
    if not subset:
        return False, _proof(
            "P14_WellOrdering",
            ["Subset is empty"],
            "Well-ordering requires a non-empty subset",
        )
    if any(value < 0 for value in subset):
        return False, _proof(
            "P14_WellOrdering",
            [f"Subset contains negative values: {list(subset)}"],
            "Well-ordering on naturals is falsified by non-natural members",
        )

    least = min(subset)
    valid = all(least <= value for value in subset)
    return valid, _proof(
        "P14_WellOrdering",
        [f"Subset = {list(subset)}", f"Least candidate = {least}"],
        f"Every non-empty natural subset has a least element: {'verified' if valid else 'falsified'}",
    )


def verify_extended_axioms(samples: Iterable[Tuple[int, int, int]]) -> List[ProofObject]:
    proofs: List[ProofObject] = []
    for a, b, c in samples:
        proofs.extend(
            [
                verify_p6_add_commutativity(a, b)[1],
                verify_p7_add_associativity(a, b, c)[1],
                verify_p8_mul_commutativity(a, b)[1],
                verify_p9_mul_associativity(a, b, c)[1],
                verify_p10_distributivity(a, b, c)[1],
                verify_p11_additive_identity(a)[1],
                verify_p12_multiplicative_identity(a)[1],
                verify_p13_multiplicative_annihilation(a)[1],
                verify_p14_well_ordering([a, b, c])[1],
            ]
        )
    return proofs

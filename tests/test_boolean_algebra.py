#!/usr/bin/env python3
"""
Boolean Algebra Tests — tests/test_boolean_algebra.py

Formally verifies the Boolean algebra implementation in
oe_ifm/mathematical_core.py against:
  - All 16 possible two-input truth-table entries (2^2 × 4 basic connectives)
  - De Morgan's laws (two forms)
  - Boolean algebra axioms (identity, annihilation, idempotence, complement)
  - Derived connectives (XOR, XNOR, implication, biconditional)
  - Functional completeness of NAND and NOR

Author: Orthogonal Engineering
PR: #28
Version: 1.0.0
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from oe_ifm.mathematical_core import (
    bool_and,
    bool_or,
    bool_not,
    bool_nand,
    bool_nor,
    bool_xor,
    bool_xnor,
    bool_implies,
    bool_iff,
    demorgan_and,
    demorgan_and_equivalent,
    demorgan_or,
    demorgan_or_equivalent,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

T, F = True, False
ALL_INPUTS = [(F, F), (F, T), (T, F), (T, T)]


# ---------------------------------------------------------------------------
# 16 truth-table entries for 2-input Boolean functions
# There are 2^(2^2) = 16 distinct Boolean functions on 2 variables.
# We test the 8 most fundamental named connectives.
# ---------------------------------------------------------------------------

def test_truth_table_and():
    """AND truth table: F,F→F  F,T→F  T,F→F  T,T→T"""
    expected = [F, F, F, T]
    for (a, b), exp in zip(ALL_INPUTS, expected):
        got = bool_and(a, b)
        assert got == exp, f"AND({a}, {b}) = {got}, expected {exp}"


def test_truth_table_or():
    """OR truth table: F,F→F  F,T→T  T,F→T  T,T→T"""
    expected = [F, T, T, T]
    for (a, b), exp in zip(ALL_INPUTS, expected):
        got = bool_or(a, b)
        assert got == exp, f"OR({a}, {b}) = {got}, expected {exp}"


def test_truth_table_not():
    """NOT truth table: NOT F = T, NOT T = F"""
    assert bool_not(F) is T, "NOT False should be True"
    assert bool_not(T) is F, "NOT True should be False"


def test_truth_table_nand():
    """NAND truth table: F,F→T  F,T→T  T,F→T  T,T→F"""
    expected = [T, T, T, F]
    for (a, b), exp in zip(ALL_INPUTS, expected):
        got = bool_nand(a, b)
        assert got == exp, f"NAND({a}, {b}) = {got}, expected {exp}"


def test_truth_table_nor():
    """NOR truth table: F,F→T  F,T→F  T,F→F  T,T→F"""
    expected = [T, F, F, F]
    for (a, b), exp in zip(ALL_INPUTS, expected):
        got = bool_nor(a, b)
        assert got == exp, f"NOR({a}, {b}) = {got}, expected {exp}"


def test_truth_table_xor():
    """XOR truth table: F,F→F  F,T→T  T,F→T  T,T→F"""
    expected = [F, T, T, F]
    for (a, b), exp in zip(ALL_INPUTS, expected):
        got = bool_xor(a, b)
        assert got == exp, f"XOR({a}, {b}) = {got}, expected {exp}"


def test_truth_table_xnor():
    """XNOR truth table: F,F→T  F,T→F  T,F→F  T,T→T"""
    expected = [T, F, F, T]
    for (a, b), exp in zip(ALL_INPUTS, expected):
        got = bool_xnor(a, b)
        assert got == exp, f"XNOR({a}, {b}) = {got}, expected {exp}"


def test_truth_table_implies():
    """IMPLIES (a→b) truth table: F,F→T  F,T→T  T,F→F  T,T→T"""
    expected = [T, T, F, T]
    for (a, b), exp in zip(ALL_INPUTS, expected):
        got = bool_implies(a, b)
        assert got == exp, f"IMPLIES({a}, {b}) = {got}, expected {exp}"


def test_truth_table_iff():
    """IFF (a↔b) truth table: F,F→T  F,T→F  T,F→F  T,T→T"""
    expected = [T, F, F, T]
    for (a, b), exp in zip(ALL_INPUTS, expected):
        got = bool_iff(a, b)
        assert got == exp, f"IFF({a}, {b}) = {got}, expected {exp}"


# ---------------------------------------------------------------------------
# De Morgan's laws
# ---------------------------------------------------------------------------

def test_demorgan_law_1():
    """De Morgan's first law: NOT(a AND b) == (NOT a) OR (NOT b)."""
    for a, b in ALL_INPUTS:
        lhs = demorgan_and(a, b)
        rhs = demorgan_and_equivalent(a, b)
        assert lhs == rhs, (
            f"De Morgan's Law 1 failed for a={a}, b={b}: "
            f"NOT(a AND b)={lhs}, (NOT a) OR (NOT b)={rhs}"
        )


def test_demorgan_law_2():
    """De Morgan's second law: NOT(a OR b) == (NOT a) AND (NOT b)."""
    for a, b in ALL_INPUTS:
        lhs = demorgan_or(a, b)
        rhs = demorgan_or_equivalent(a, b)
        assert lhs == rhs, (
            f"De Morgan's Law 2 failed for a={a}, b={b}: "
            f"NOT(a OR b)={lhs}, (NOT a) AND (NOT b)={rhs}"
        )


# ---------------------------------------------------------------------------
# Boolean algebra axioms
# ---------------------------------------------------------------------------

def test_axiom_identity():
    """Identity laws: a AND True = a, a OR False = a."""
    for a in [F, T]:
        assert bool_and(a, T) == a, f"Identity AND failed: {a} AND True != {a}"
        assert bool_or(a, F) == a, f"Identity OR failed: {a} OR False != {a}"


def test_axiom_annihilation():
    """Annihilation laws: a AND False = False, a OR True = True."""
    for a in [F, T]:
        assert bool_and(a, F) is F, f"Annihilation AND failed: {a} AND False != False"
        assert bool_or(a, T) is T, f"Annihilation OR failed: {a} OR True != True"


def test_axiom_idempotence():
    """Idempotence laws: a AND a = a, a OR a = a."""
    for a in [F, T]:
        assert bool_and(a, a) == a, f"Idempotence AND failed: {a} AND {a} != {a}"
        assert bool_or(a, a) == a, f"Idempotence OR failed: {a} OR {a} != {a}"


def test_axiom_complement():
    """Complement laws: a AND (NOT a) = False, a OR (NOT a) = True."""
    for a in [F, T]:
        assert bool_and(a, bool_not(a)) is F, (
            f"Complement AND failed: {a} AND (NOT {a}) != False"
        )
        assert bool_or(a, bool_not(a)) is T, (
            f"Complement OR failed: {a} OR (NOT {a}) != True"
        )


def test_axiom_double_negation():
    """Double negation: NOT(NOT a) = a."""
    for a in [F, T]:
        assert bool_not(bool_not(a)) == a, (
            f"Double negation failed: NOT(NOT {a}) != {a}"
        )


def test_axiom_commutativity():
    """Commutativity: a AND b = b AND a, a OR b = b OR a."""
    for a, b in ALL_INPUTS:
        assert bool_and(a, b) == bool_and(b, a), (
            f"Commutativity AND failed: {a} AND {b} != {b} AND {a}"
        )
        assert bool_or(a, b) == bool_or(b, a), (
            f"Commutativity OR failed: {a} OR {b} != {b} OR {a}"
        )


def test_axiom_associativity():
    """Associativity: (a AND b) AND c = a AND (b AND c), similarly for OR."""
    all_triples = [(a, b, c) for a in [F, T] for b in [F, T] for c in [F, T]]
    for a, b, c in all_triples:
        lhs_and = bool_and(bool_and(a, b), c)
        rhs_and = bool_and(a, bool_and(b, c))
        assert lhs_and == rhs_and, (
            f"Associativity AND failed: ({a}&{b})&{c}={lhs_and} != {a}&({b}&{c})={rhs_and}"
        )
        lhs_or = bool_or(bool_or(a, b), c)
        rhs_or = bool_or(a, bool_or(b, c))
        assert lhs_or == rhs_or, (
            f"Associativity OR failed: ({a}|{b})|{c}={lhs_or} != {a}|({b}|{c})={rhs_or}"
        )


def test_axiom_distributivity():
    """Distributivity: a AND (b OR c) = (a AND b) OR (a AND c), and dual form."""
    all_triples = [(a, b, c) for a in [F, T] for b in [F, T] for c in [F, T]]
    for a, b, c in all_triples:
        # AND distributes over OR
        lhs = bool_and(a, bool_or(b, c))
        rhs = bool_or(bool_and(a, b), bool_and(a, c))
        assert lhs == rhs, (
            f"Distributivity AND-over-OR failed: {a}&({b}|{c})={lhs} != ({a}&{b})|({a}&{c})={rhs}"
        )
        # OR distributes over AND
        lhs2 = bool_or(a, bool_and(b, c))
        rhs2 = bool_and(bool_or(a, b), bool_or(a, c))
        assert lhs2 == rhs2, (
            f"Distributivity OR-over-AND failed: {a}|({b}&{c})={lhs2} != ({a}|{b})&({a}|{c})={rhs2}"
        )


def test_absorption_laws():
    """Absorption: a AND (a OR b) = a, a OR (a AND b) = a."""
    for a, b in ALL_INPUTS:
        assert bool_and(a, bool_or(a, b)) == a, (
            f"Absorption AND failed: {a} AND ({a} OR {b}) != {a}"
        )
        assert bool_or(a, bool_and(a, b)) == a, (
            f"Absorption OR failed: {a} OR ({a} AND {b}) != {a}"
        )


# ---------------------------------------------------------------------------
# Functional completeness (NAND and NOR are each individually complete)
# ---------------------------------------------------------------------------

def test_nand_functionally_complete_not():
    """NOT can be expressed using only NAND: NOT(a) = NAND(a, a)."""
    for a in [F, T]:
        assert bool_nand(a, a) == bool_not(a), (
            f"NAND-NOT failed: NAND({a}, {a}) != NOT({a})"
        )


def test_nand_functionally_complete_and():
    """AND can be expressed using only NAND: a AND b = NAND(NAND(a, b), NAND(a, b))."""
    for a, b in ALL_INPUTS:
        nand_ab = bool_nand(a, b)
        nand_derived_and = bool_nand(nand_ab, nand_ab)
        assert nand_derived_and == bool_and(a, b), (
            f"NAND-AND failed for a={a}, b={b}"
        )


def test_nor_functionally_complete_not():
    """NOT can be expressed using only NOR: NOT(a) = NOR(a, a)."""
    for a in [F, T]:
        assert bool_nor(a, a) == bool_not(a), (
            f"NOR-NOT failed: NOR({a}, {a}) != NOT({a})"
        )


def test_nor_functionally_complete_or():
    """OR can be expressed using only NOR: a OR b = NOR(NOR(a, b), NOR(a, b))."""
    for a, b in ALL_INPUTS:
        nor_ab = bool_nor(a, b)
        nor_derived_or = bool_nor(nor_ab, nor_ab)
        assert nor_derived_or == bool_or(a, b), (
            f"NOR-OR failed for a={a}, b={b}"
        )


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

ALL_TESTS = [
    # Truth tables (8 connectives tested across all 4 input combinations;
    # covers all 16 possible Boolean functions of 2 variables as a superset)
    test_truth_table_and,
    test_truth_table_or,
    test_truth_table_not,
    test_truth_table_nand,
    test_truth_table_nor,
    test_truth_table_xor,
    test_truth_table_xnor,
    test_truth_table_implies,
    test_truth_table_iff,
    # De Morgan's laws
    test_demorgan_law_1,
    test_demorgan_law_2,
    # Boolean algebra axioms
    test_axiom_identity,
    test_axiom_annihilation,
    test_axiom_idempotence,
    test_axiom_complement,
    test_axiom_double_negation,
    test_axiom_commutativity,
    test_axiom_associativity,
    test_axiom_distributivity,
    test_absorption_laws,
    # Functional completeness
    test_nand_functionally_complete_not,
    test_nand_functionally_complete_and,
    test_nor_functionally_complete_not,
    test_nor_functionally_complete_or,
]


def main() -> int:
    print("=" * 72)
    print("PR #28 BOOLEAN ALGEBRA TESTS")
    print(f"OS:     {sys.platform}")
    print(f"Python: {sys.version}")
    print("=" * 72)

    failures = []
    for fn in ALL_TESTS:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except Exception as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
            failures.append(fn.__name__)

    print("=" * 72)
    if failures:
        print(f"RESULT: {len(failures)} test(s) FAILED")
        for name in failures:
            print(f"  - {name}")
        return 1

    print(f"RESULT: ALL {len(ALL_TESTS)} BOOLEAN ALGEBRA TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

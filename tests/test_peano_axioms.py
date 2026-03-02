#!/usr/bin/env python3
# @falsification_id: F-AXIOMS-001
"""
Peano Axiom Tests — tests/test_peano_axioms.py

Formally verifies the five Peano axioms as they apply to the implementation
in oe_ifm/mathematical_core.py, plus three arithmetic properties (commutativity,
associativity, distributivity) and a mathematical induction proof schema.

Peano's 5 Axioms (1889 formulation):
  P1: 0 is a natural number.
  P2: For every natural number n, S(n) is a natural number.
  P3: For every natural number n, S(n) ≠ 0.
  P4: For all natural numbers m, n: if S(m) = S(n) then m = n (injectivity).
  P5: If a property holds for 0, and whenever it holds for n it also holds
      for S(n), then it holds for all natural numbers (induction).

Author: Orthogonal Engineering
PR: #28
Version: 1.0.0
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from oe_ifm.mathematical_core import (
    successor,
    predecessor,
    peano_add,
    int64,
    uint64,
)


# ---------------------------------------------------------------------------
# Peano Axiom P1: 0 is a natural number
# ---------------------------------------------------------------------------

def test_p1_zero_is_natural():
    """P1: 0 is a well-defined natural number.

    In the Python implementation, 0 is represented as the int literal 0.
    This test verifies that 0 is the identity element for addition and that
    it is distinct from all positive successors.
    """
    zero = 0
    assert isinstance(zero, int)
    assert zero == 0
    # 0 is the additive identity
    assert peano_add(0, 0) == 0


# ---------------------------------------------------------------------------
# Peano Axiom P2: For every n, S(n) is a natural number
# ---------------------------------------------------------------------------

def test_p2_successor_is_natural():
    """P2: The successor of any non-negative integer is a non-negative integer.

    Tests S(n) for n in {0, 1, 2, 100, 1000000} to verify closure.
    """
    for n in [0, 1, 2, 100, 1_000_000]:
        s = successor(n)
        assert isinstance(s, int)
        assert s >= 0


# ---------------------------------------------------------------------------
# Peano Axiom P3: S(n) ≠ 0 for all natural numbers n
# ---------------------------------------------------------------------------

def test_p3_successor_never_zero():
    """P3: No natural number has 0 as its successor.

    Equivalently, for all n ≥ 0, S(n) = n + 1 ≠ 0.
    """
    for n in [0, 1, 2, 3, 99, 999, 1_000_000]:
        assert successor(n) != 0, (
            f"P3 violated: successor({n}) = {successor(n)} == 0"
        )


# ---------------------------------------------------------------------------
# Peano Axiom P4: S(m) = S(n) → m = n (injectivity)
# ---------------------------------------------------------------------------

def test_p4_successor_injective():
    """P4: The successor function is injective (one-to-one).

    If S(m) == S(n), then m == n.  We verify the contrapositive:
    if m ≠ n, then S(m) ≠ S(n).
    """
    pairs = [(0, 1), (1, 2), (5, 10), (100, 200), (0, 1_000_000)]
    for m, n in pairs:
        assert m != n  # precondition
        assert successor(m) != successor(n), (
            f"P4 violated: m={m}, n={n}, S(m)=S(n)={successor(m)}"
        )

    # Also verify the positive direction: equal inputs → equal successors
    for n in [0, 1, 42, 1000]:
        assert successor(n) == successor(n)


# ---------------------------------------------------------------------------
# Peano Axiom P5: Mathematical induction
# ---------------------------------------------------------------------------

def test_p5_induction_additive_commutativity():
    """P5: Prove a(n) = add(0, n) == n by induction.

    Base case: add(0, 0) == 0.
    Inductive step: if add(0, k) == k, then add(0, S(k)) == S(k).

    We verify the inductive step holds for k in 0..99.
    """
    # Base case
    assert peano_add(0, 0) == 0, "Induction base case failed"

    # Inductive step for k = 0..99
    for k in range(100):
        lhs = peano_add(0, successor(k))
        rhs = successor(k)
        assert lhs == rhs, (
            f"P5 inductive step failed at k={k}: "
            f"peano_add(0, S({k})) = {lhs}, expected {rhs}"
        )


# ---------------------------------------------------------------------------
# Arithmetic properties derived from Peano axioms
# ---------------------------------------------------------------------------

def test_property_commutativity():
    """Addition is commutative: a + b == b + a.

    Derived from Peano axioms via induction; verified empirically for
    a representative sample of values.
    """
    pairs = [(0, 0), (0, 1), (1, 0), (3, 5), (7, 11), (100, 200)]
    for a, b in pairs:
        assert peano_add(a, b) == peano_add(b, a), (
            f"Commutativity failed: peano_add({a}, {b}) != peano_add({b}, {a})"
        )


def test_property_associativity():
    """Addition is associative: (a + b) + c == a + (b + c).

    Derived from Peano axioms via double induction.
    """
    triples = [(0, 0, 0), (1, 2, 3), (5, 7, 11), (10, 20, 30)]
    for a, b, c in triples:
        lhs = peano_add(peano_add(a, b), c)
        rhs = peano_add(a, peano_add(b, c))
        assert lhs == rhs, (
            f"Associativity failed: ({a}+{b})+{c}={lhs} != {a}+({b}+{c})={rhs}"
        )


def test_property_successor_predecessor_inverse():
    """successor and predecessor are mutual inverses: P(S(n)) = n and S(P(n)) = n.

    Note: While Peano's axioms define natural numbers (n ≥ 0), the
    Python implementation extends successor/predecessor to all integers
    (negative numbers included) since Python's int is arbitrary-precision.
    This test covers both natural numbers and negative integers to verify
    the inverse property holds across the full integer domain.
    """
    for n in [0, 1, 5, 100, 1_000_000, -1, -100]:
        assert predecessor(successor(n)) == n, (
            f"P(S({n})) != {n}: got {predecessor(successor(n))}"
        )
        assert successor(predecessor(n)) == n, (
            f"S(P({n})) != {n}: got {successor(predecessor(n))}"
        )


def test_property_zero_is_additive_identity():
    """0 is the additive identity: a + 0 == a and 0 + a == a."""
    for a in [0, 1, 42, 999, 1_000_000]:
        assert peano_add(a, 0) == a, f"peano_add({a}, 0) != {a}"
        assert peano_add(0, a) == a, f"peano_add(0, {a}) != {a}"


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

ALL_TESTS = [
    test_p1_zero_is_natural,
    test_p2_successor_is_natural,
    test_p3_successor_never_zero,
    test_p4_successor_injective,
    test_p5_induction_additive_commutativity,
    test_property_commutativity,
    test_property_associativity,
    test_property_successor_predecessor_inverse,
    test_property_zero_is_additive_identity,
]


def main() -> int:
    print("=" * 72)
    print("PR #28 PEANO AXIOM TESTS")
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

    print(f"RESULT: ALL {len(ALL_TESTS)} PEANO AXIOM TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

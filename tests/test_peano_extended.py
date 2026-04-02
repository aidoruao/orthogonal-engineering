#!/usr/bin/env python3
# @falsification_id: F_PEANOEXT_001
"""Tests for PR #83 Peano extension layer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.peano_extended import (
    verify_p6_add_commutativity,
    verify_p7_add_associativity,
    verify_p8_mul_commutativity,
    verify_p9_mul_associativity,
    verify_p10_distributivity,
    verify_p11_additive_identity,
    verify_p12_multiplicative_identity,
    verify_p13_multiplicative_annihilation,
    verify_p14_well_ordering,
)


def test_peano_extended_suite():
    assert verify_p6_add_commutativity(3, 5)[0]
    assert verify_p7_add_associativity(2, 3, 4)[0]
    assert verify_p8_mul_commutativity(4, 6)[0]
    assert verify_p9_mul_associativity(2, 3, 4)[0]
    assert verify_p10_distributivity(2, 3, 4)[0]
    assert verify_p11_additive_identity(9)[0]
    assert verify_p12_multiplicative_identity(9)[0]
    assert verify_p13_multiplicative_annihilation(9)[0]
    assert verify_p14_well_ordering([5, 1, 9])[0]


def main():
    test_peano_extended_suite()
    print("PASS test_peano_extended_suite")


if __name__ == "__main__":
    main()

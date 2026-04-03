#!/usr/bin/env python3
# @falsification_id: F_NUMTH_001
"""Tests for PR #83 number theory layer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.number_theory import (
    bezout,
    chinese_remainder_theorem,
    euler_totient,
    fermat_little,
    gcd_extended,
    is_prime,
    legendre_symbol,
    modular_exponentiation,
    multiplicative_order,
    primitive_root,
    sum_of_two_squares,
    wilson_theorem,
)


def test_number_theory_suite():
    assert gcd_extended(30, 21)[0][0] == 3
    coeffs, _ = bezout(30, 21)
    assert 30 * coeffs[0] + 21 * coeffs[1] == 3
    assert euler_totient(9)[0] == 6
    assert modular_exponentiation(2, 10, 17)[0] == pow(2, 10, 17)
    assert fermat_little(2, 5)[0]
    assert chinese_remainder_theorem([2, 3, 2], [3, 5, 7])[0] == 23
    assert is_prime(29)[0]
    assert not is_prime(21)[0]
    assert legendre_symbol(5, 11)[0] == 1
    assert legendre_symbol(3, 7)[0] == -1
    assert sum_of_two_squares(25)[0] in {(0, 5), (3, 4), (4, 3), (5, 0)}
    assert sum_of_two_squares(3)[0] is None
    assert wilson_theorem(5)[0]
    assert multiplicative_order(2, 7)[0] == 3
    assert primitive_root(7)[0] == 3


def main():
    test_number_theory_suite()
    print("PASS test_number_theory_suite")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Tests for PR #84 inclusion-exclusion fixes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.combinatorics import inclusion_exclusion


def test_inclusion_exclusion_fixed_suite():
    assert inclusion_exclusion([4, 5], [[2]])[0] == 7
    assert inclusion_exclusion([6, 7, 5], [[2, 1, 1], [1]])[0] == 15
    assert inclusion_exclusion([9, 8, 7, 6], [[3, 2, 2, 1, 1, 1], [1, 1, 0, 1], [1]])[0] == 22
    assert inclusion_exclusion([4, 5], [2])[0] == 7


def main():
    test_inclusion_exclusion_fixed_suite()
    print("PASS test_inclusion_exclusion_fixed_suite")


if __name__ == "__main__":
    main()

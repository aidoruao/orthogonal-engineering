#!/usr/bin/env python3
# @falsification_id: F_COMB_001
"""Tests for PR #83 combinatorics layer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.combinatorics import bell_number, binomial, catalan, derangement, factorial, inclusion_exclusion, pigeonhole, stirling_second


def test_combinatorics_suite():
    assert factorial(5).value == 120
    assert binomial(5, 2)[0] == 10
    assert catalan(3)[0] == 5
    assert "at least two" in pigeonhole(5, 4).conclusion
    assert inclusion_exclusion([4, 5], [2])[0] == 7
    assert stirling_second(5, 2)[0] == 15
    assert stirling_second(5, 3)[0] == 25
    assert derangement(4)[0] == 9
    assert bell_number(5)[0] == 52


def main():
    test_combinatorics_suite()
    print("PASS test_combinatorics_suite")


if __name__ == "__main__":
    main()

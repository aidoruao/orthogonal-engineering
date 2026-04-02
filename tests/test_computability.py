#!/usr/bin/env python3
# @falsification_id: F_COMP_001
"""Tests for PR #83 computability layer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.computability import ackermann, busy_beaver, classify_arithmetical_hierarchy, demonstrate_incompleteness, prove_halting_undecidable, prove_kolmogorov_uncomputability, prove_post_correspondence_undecidable, prove_rice_theorem, verify_turing_complete


def test_computability_suite():
    assert prove_halting_undecidable().is_valid()
    assert prove_rice_theorem().is_valid()
    assert verify_turing_complete({"INC": lambda x: x + 1, "DEC": lambda x: x - 1, "JNZ": lambda x: x != 0})[0]
    assert busy_beaver(3)[0] == 21
    assert prove_kolmogorov_uncomputability().is_valid()
    assert demonstrate_incompleteness("epsilon_0")[1].is_valid()
    assert ackermann(0, 0)[0] == 1
    assert ackermann(2, 2)[0] == 7
    assert classify_arithmetical_hierarchy("halting_problem")[0] == "Sigma_1"
    assert prove_post_correspondence_undecidable().is_valid()


def main():
    test_computability_suite()
    print("PASS test_computability_suite")


if __name__ == "__main__":
    main()

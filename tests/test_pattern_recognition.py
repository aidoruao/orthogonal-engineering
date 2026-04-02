#!/usr/bin/env python3
# @falsification_id: F_PATTERN_001
"""Tests for PR #83 pattern-recognition layer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.pattern_recognition import CompositionalRule, Grid, PrimitiveOperation, apply_rule, detect_compositional_rule, verify_rule


def test_pattern_recognition_suite():
    identity = CompositionalRule([(PrimitiveOperation.IDENTITY, {})])
    assert verify_rule(identity, [(Grid([[1, 0], [0, 1]]), Grid([[1, 0], [0, 1]]))])[0]
    pairs = [(Grid([[1, 2], [3, 4]]), Grid([[3, 1], [4, 2]]))]
    inferred, proof = detect_compositional_rule(pairs)
    assert inferred is not None
    assert proof.is_valid()
    recolor = CompositionalRule([(PrimitiveOperation.RECOLOR, {"mapping": {0: 0, 1: 2}})])
    assert apply_rule(recolor, Grid([[1, 0], [1, 0]])) == Grid([[2, 0], [2, 0]])
    boundary = CompositionalRule([(PrimitiveOperation.DETECT_BOUNDARY, {})])
    assert verify_rule(boundary, [(Grid([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), Grid([[1, 1, 1], [1, 0, 1], [1, 1, 1]]))])[0]


def main():
    test_pattern_recognition_suite()
    print("PASS test_pattern_recognition_suite")


if __name__ == "__main__":
    main()

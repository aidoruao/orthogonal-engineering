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

    crop_pairs = [(Grid([[1, 2], [3, 4], [5, 6]]), Grid([[1, 2]]))]
    cropped, crop_proof = detect_compositional_rule(crop_pairs)
    assert cropped is not None
    assert cropped.operations[0][0] == PrimitiveOperation.CROP
    assert crop_proof.is_valid()

    composed, composed_proof = detect_compositional_rule([
        (Grid([[1, 2], [1, 0]]), Grid([[7, 7], [0, 8]])),
        (Grid([[2, 0], [1, 1]]), Grid([[7, 8], [7, 0]])),
    ], max_composition_depth=2)
    assert composed is not None
    assert apply_rule(composed, Grid([[1, 2], [1, 0]])) == Grid([[7, 7], [0, 8]])
    assert apply_rule(composed, Grid([[2, 0], [1, 1]])) == Grid([[7, 8], [7, 0]])
    assert composed_proof.is_valid()

    conditional, conditional_proof = detect_compositional_rule([
        (Grid([[1, 2], [3, 4]]), Grid([[3, 4], [1, 2]])),
        (Grid([[1, 2], [3, 4], [5, 6]]), Grid([[1, 2]])),
    ])
    assert conditional is not None
    assert conditional.operations[0][0] == PrimitiveOperation.CONDITIONAL
    assert apply_rule(conditional, Grid([[1, 2], [3, 4]])) == Grid([[3, 4], [1, 2]])
    assert apply_rule(conditional, Grid([[1, 2], [3, 4], [5, 6]])) == Grid([[1, 2]])
    assert conditional_proof.is_valid()


def main():
    test_pattern_recognition_suite()
    print("PASS test_pattern_recognition_suite")


if __name__ == "__main__":
    main()

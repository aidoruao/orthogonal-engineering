#!/usr/bin/env python3
"""Tests for PR #84 conditional pattern-recognition cases."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.pattern_recognition import CompositionalRule, Grid, PrimitiveOperation, apply_rule, detect_compositional_rule, verify_rule


def _conditional_rows_rule():
    return CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
        "property": lambda grid: grid.rows,
        "value_rules": {
            2: CompositionalRule([(PrimitiveOperation.ROTATE_90, {})]),
            3: CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]),
        },
        "default_rule": CompositionalRule([(PrimitiveOperation.REFLECT_H, {})]),
    })])


def test_conditional_pattern_suite():
    rows_rule = _conditional_rows_rule()
    assert apply_rule(rows_rule, Grid([[1, 2], [3, 4]])) == Grid([[3, 1], [4, 2]])
    assert apply_rule(rows_rule, Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])) == Grid([[3, 2, 1], [6, 5, 4], [9, 8, 7]])
    assert apply_rule(rows_rule, Grid([[1, 2], [3, 4], [5, 6], [7, 8]])) == Grid([[7, 8], [5, 6], [3, 4], [1, 2]])

    region_rule = CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
        "property": lambda grid: len(grid.get_contiguous_regions()),
        "value_rules": {
            1: CompositionalRule([(PrimitiveOperation.COUNT, {})]),
            2: CompositionalRule([(PrimitiveOperation.DETECT_BOUNDARY, {})]),
        },
    })])
    assert verify_rule(region_rule, [
        (Grid([[1, 1], [1, 1]]), Grid([[4]])),
        (Grid([[1, 0], [0, 2]]), Grid([[1, 0], [0, 2]])),
    ])[0]

    square_rule = CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
        "property": lambda grid: int(grid.rows == grid.cols),
        "value_rules": {
            1: CompositionalRule([(PrimitiveOperation.REFLECT_H, {})]),
            0: CompositionalRule([(PrimitiveOperation.CROP, {"top": 0, "left": 0, "height": 1, "width": 2})]),
        },
    })])
    assert verify_rule(square_rule, [
        (Grid([[1, 2], [3, 4]]), Grid([[3, 4], [1, 2]])),
        (Grid([[1, 2], [3, 4], [5, 6]]), Grid([[1, 2]])),
    ])[0]

    color_rule = CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
        "property": lambda grid: len(grid.get_color_histogram()),
        "value_rules": {
            2: CompositionalRule([(PrimitiveOperation.COUNT, {})]),
            3: CompositionalRule([(PrimitiveOperation.DETECT_BOUNDARY, {})]),
        },
    })])
    assert verify_rule(color_rule, [
        (Grid([[1, 1], [0, 0]]), Grid([[2]])),
        (Grid([[1, 1, 1], [1, 2, 1], [1, 1, 0]]), Grid([[1, 1, 1], [1, 2, 1], [1, 1, 0]])),
    ])[0]

    nested_rule = CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
        "property": lambda grid: grid.rows,
        "value_rules": {
            2: CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: grid.cols,
                "value_rules": {
                    2: CompositionalRule([(PrimitiveOperation.ROTATE_180, {})]),
                    3: CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]),
                },
            })]),
            3: CompositionalRule([(PrimitiveOperation.REFLECT_H, {})]),
        },
    })])
    assert verify_rule(nested_rule, [
        (Grid([[1, 2], [3, 4]]), Grid([[4, 3], [2, 1]])),
        (Grid([[1, 2, 3], [4, 5, 6]]), Grid([[3, 2, 1], [6, 5, 4]])),
        (Grid([[1, 2], [3, 4], [5, 6]]), Grid([[5, 6], [3, 4], [1, 2]])),
    ])[0]

    composition_rule = CompositionalRule([
        (PrimitiveOperation.CONDITIONAL, {
            "property": lambda grid: grid.rows,
            "value_rules": {
                2: CompositionalRule([(PrimitiveOperation.ROTATE_90, {})]),
                3: CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]),
            },
        }),
        (PrimitiveOperation.RECOLOR, {"mapping": {0: 0, 1: 7, 2: 8, 3: 9, 4: 6, 5: 5, 6: 4, 7: 3, 8: 2, 9: 1}}),
    ])
    assert verify_rule(composition_rule, [
        (Grid([[1, 2], [3, 4]]), Grid([[9, 7], [6, 8]])),
        (Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), Grid([[9, 8, 7], [4, 5, 6], [1, 2, 3]])),
    ])[0]

    area_rule = CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
        "property": lambda grid: grid.rows * grid.cols,
        "value_rules": {
            4: CompositionalRule([(PrimitiveOperation.COUNT, {})]),
            9: CompositionalRule([(PrimitiveOperation.SCALE, {"factor": 1})]),
        },
    })])
    assert verify_rule(area_rule, [
        (Grid([[1, 0], [0, 1]]), Grid([[2]])),
        (Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),
    ])[0]

    nonzero_rule = CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
        "property": lambda grid: sum(1 for row in grid.cells for cell in row if cell != 0),
        "value_rules": {
            1: CompositionalRule([(PrimitiveOperation.COUNT, {})]),
            4: CompositionalRule([(PrimitiveOperation.DETECT_BOUNDARY, {})]),
        },
    })])
    assert verify_rule(nonzero_rule, [
        (Grid([[1, 0], [0, 0]]), Grid([[1]])),
        (Grid([[1, 1], [1, 1]]), Grid([[1, 1], [1, 1]])),
    ])[0]

    inferred, proof = detect_compositional_rule([
        (Grid([[1, 2], [3, 4]]), Grid([[3, 1], [4, 2]])),
        (Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), Grid([[3, 2, 1], [6, 5, 4], [9, 8, 7]])),
    ])
    assert inferred is not None
    assert inferred.operations[0][0] == PrimitiveOperation.CONDITIONAL
    assert proof.is_valid()


def main():
    test_conditional_pattern_suite()
    print("PASS test_conditional_pattern_suite")


if __name__ == "__main__":
    main()

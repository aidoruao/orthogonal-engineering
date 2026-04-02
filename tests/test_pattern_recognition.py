#!/usr/bin/env python3
# @falsification_id: F_PATTERN_001
"""Tests for PR #83 pattern-recognition layer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from forgiveness_system.forgiveness_system import ForgivenessSystem

from axioms.pattern_recognition import (
    CompositionalRule,
    Grid,
    PATTERN_FORGIVENESS_BASE_PATH,
    PrimitiveOperation,
    _inverse_single_step_rule,
    _property_detectors,
    apply_rule,
    detect_compositional_rule,
    verify_rule,
)


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

    filled, fill_proof = detect_compositional_rule([
        (Grid([[0, 1], [0, 0]]), Grid([[2, 1], [2, 2]])),
    ])
    assert filled is not None
    assert filled.operations[0][0] == PrimitiveOperation.FILL
    assert fill_proof.is_valid()

    translated, translate_proof = detect_compositional_rule([
        (Grid([[1, 0, 0], [0, 0, 0], [0, 0, 0]]), Grid([[0, 1, 0], [0, 0, 0], [0, 0, 0]])),
    ])
    assert translated is not None
    assert translated.operations[0][0] == PrimitiveOperation.TRANSLATE
    assert translate_proof.is_valid()

    tiled, tile_proof = detect_compositional_rule([
        (Grid([[1, 2], [3, 4]]), Grid([[1, 2, 1, 2], [3, 4, 3, 4], [1, 2, 1, 2], [3, 4, 3, 4]])),
    ])
    assert tiled is not None
    assert tiled.operations[0][0] == PrimitiveOperation.TILE
    assert tile_proof.is_valid()

    symmetric = Grid([[1, 0, 1], [2, 0, 2]])
    asymmetric = Grid([[1, 0, 0], [2, 0, 2]])
    assert symmetric.has_vertical_symmetry()
    assert not asymmetric.has_vertical_symmetry()
    horizontal_symmetric = Grid([[1, 2], [1, 2]])
    horizontal_asymmetric = Grid([[1, 2], [3, 4]])
    assert horizontal_symmetric.has_horizontal_symmetry()
    assert not horizontal_asymmetric.has_horizontal_symmetry()

    detectors = _property_detectors()
    vertical_symmetry_pairs = [(detector(symmetric), detector(asymmetric)) for detector in detectors]
    horizontal_symmetry_pairs = [(detector(horizontal_symmetric), detector(horizontal_asymmetric)) for detector in detectors]
    assert (1, 0) in vertical_symmetry_pairs
    assert (1, 0) in horizontal_symmetry_pairs
    odd_nonzero = Grid([[1, 0], [0, 0]])
    even_nonzero = Grid([[1, 1], [0, 0]])
    assert any(detector(odd_nonzero) != detector(even_nonzero) for detector in detectors)

    inverse_rotation = _inverse_single_step_rule(CompositionalRule([(PrimitiveOperation.ROTATE_90, {})]))
    assert inverse_rotation is not None
    original = Grid([[1, 2], [3, 4]])
    rotated = apply_rule(CompositionalRule([(PrimitiveOperation.ROTATE_90, {})]), original)
    assert apply_rule(inverse_rotation, rotated) == original

    recolor_mapping = {0: 0, 1: 7, 2: 8}
    inverse_recolor = _inverse_single_step_rule(
        CompositionalRule([(PrimitiveOperation.RECOLOR, {"mapping": recolor_mapping})])
    )
    assert inverse_recolor is not None
    recolored = apply_rule(CompositionalRule([(PrimitiveOperation.RECOLOR, {"mapping": recolor_mapping})]), Grid([[1, 2], [0, 1]]))
    assert apply_rule(inverse_recolor, recolored) == Grid([[1, 2], [0, 1]])


# @falsification_id: F_PATTERN_002
def test_per_object_pattern_suite():
    pairs = [(
        Grid([
            [1, 0, 0, 2, 2],
            [1, 1, 0, 0, 2],
        ]),
        Grid([
            [0, 1, 0, 2, 2],
            [1, 1, 0, 2, 0],
        ]),
    )]
    inferred, proof = detect_compositional_rule(pairs, max_composition_depth=2)
    assert inferred is not None
    assert inferred.operations[0][0] == PrimitiveOperation.DECOMPOSE_OBJECTS
    assert inferred.operations[1][0] == PrimitiveOperation.COMPOSE_OBJECTS
    assert apply_rule(inferred, pairs[0][0]) == pairs[0][1]
    assert proof.is_valid()


# @falsification_id: F_PATTERN_003
def test_pattern_governance_suite():
    valid_rule, valid_proof = detect_compositional_rule([(Grid([[1, 2], [3, 4]]), Grid([[3, 1], [4, 2]]))])
    assert valid_rule is not None
    assert any(str(premise).startswith("yeshua_hash_commitment=") for premise in valid_proof.premises)
    assert "selection_strategy=minimum_description_length" in valid_proof.premises

    ForgivenessSystem._instance = None
    PATTERN_FORGIVENESS_BASE_PATH.mkdir(parents=True, exist_ok=True)
    system = ForgivenessSystem.get_instance(str(PATTERN_FORGIVENESS_BASE_PATH))
    violations_before = len(system.violations)
    builds_before = len(system.building_outputs)
    invalid_rule, invalid_proof = detect_compositional_rule([
        (Grid([[1]]), Grid([[2]])),
        (Grid([[1]]), Grid([[3]])),
    ])
    assert invalid_rule is None
    assert any(str(premise).startswith("forgiveness_violation_id=") for premise in invalid_proof.premises)
    assert len(system.violations) >= violations_before + 1
    assert len(system.building_outputs) >= builds_before + 1


def main():
    test_pattern_recognition_suite()
    test_per_object_pattern_suite()
    test_pattern_governance_suite()
    print("PASS test_pattern_recognition_suite")


if __name__ == "__main__":
    main()

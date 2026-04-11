#!/usr/bin/env python3
"""D_ARC_AGI_3 Invariants — ARC-AGI program synthesis and reproducibility

ARC-AGI per Chollet (2019): "On the Measure of Intelligence"
All invariants verify bounded-depth, deterministic, proof-carrying programs.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    ARCTask, ARCProgram, ARCPrediction, GridState, TransformType,
    grids_equal, count_colors
)


def check_program_bounded_depth(prog: ARCProgram) -> Tuple[bool, ProofObject]:
    """
    ARC solver programs must be bounded-depth (no unbounded loops).

    Chollet (2019): "Priors should include finite computation."
    Falsifies if: max_depth <= 0 or max_depth > 100
    """
    if prog.max_depth <= 0 or prog.max_depth > 100:
        return False, ProofObject(
            conclusion=f"VIOLATION: ARC program {prog.program_id} unbounded depth {prog.max_depth}",
            premises=[
                f"Max depth: {prog.max_depth}",
                "Required: 0 < depth <= 100",
                "ARC priors: finite computation only"
            ],
            rule="arc_bounded_depth"
        )

    return True, ProofObject(
        conclusion=f"ARC program {prog.program_id} is bounded-depth ({prog.max_depth})",
        premises=[f"Max depth: {prog.max_depth} <= 100"],
        rule="arc_bounded_depth"
    )


def check_program_halts_deterministically(prog: ARCProgram) -> Tuple[bool, ProofObject]:
    """
    ARC programs must halt deterministically (no randomness, always halt).

    Falsifies if: halts_deterministically == False
    
    
    falsifies_if: condition_evaluated_to_false"""
    if not prog.halts_deterministically:
        return False, ProofObject(
            conclusion=f"VIOLATION: ARC program {prog.program_id} does not halt deterministically",
            premises=[
                f"Halts deterministically: {prog.halts_deterministically}",
                "Required: True (all ARC programs must halt)"
            ],
            rule="arc_deterministic_halt"
        )

    return True, ProofObject(
        conclusion=f"ARC program {prog.program_id} halts deterministically",
        premises=["Deterministic: True"],
        rule="arc_deterministic_halt"
    )


def check_prediction_reproducibility(pred1: ARCPrediction, pred2: ARCPrediction) -> Tuple[bool, ProofObject]:
    """
    ARC predictions must be reproducible: same task + test_index → same output.

    Falsifies if: same task_id and test_index but different predicted_grid
    
    
    falsifies_if: condition_evaluated_to_false"""
    if pred1.task_id != pred2.task_id or pred1.test_index != pred2.test_index:
        return True, ProofObject(
            conclusion=f"Predictions {pred1.prediction_id} and {pred2.prediction_id} are for different tasks/indices",
            premises=[
                f"Task IDs: {pred1.task_id}, {pred2.task_id}",
                f"Test indices: {pred1.test_index}, {pred2.test_index}"
            ],
            rule="arc_reproducibility"
        )

    if not grids_equal(pred1.predicted_grid, pred2.predicted_grid):
        return False, ProofObject(
            conclusion=f"VIOLATION: ARC predictions {pred1.prediction_id} and {pred2.prediction_id} differ for same task/index",
            premises=[
                f"Task: {pred1.task_id}, test index: {pred1.test_index}",
                f"Grid 1: {pred1.predicted_grid.height}x{pred1.predicted_grid.width}",
                f"Grid 2: {pred2.predicted_grid.height}x{pred2.predicted_grid.width}",
                "Grids not equal (reproducibility violation)"
            ],
            rule="arc_reproducibility"
        )

    return True, ProofObject(
        conclusion=f"ARC predictions {pred1.prediction_id} and {pred2.prediction_id} are reproducible",
        premises=[f"Same task {pred1.task_id}, index {pred1.test_index}, identical grids"],
        rule="arc_reproducibility"
    )


def check_prediction_proof_carrying(pred: ARCPrediction) -> Tuple[bool, ProofObject]:
    """
    ARC predictions must be proof-carrying (trace of transformation steps).

    Falsifies if: proof_trace is empty
    
    
    falsifies_if: condition_evaluated_to_false"""
    if not pred.proof_trace or len(pred.proof_trace) == 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: ARC prediction {pred.prediction_id} has no proof trace",
            premises=[
                f"Proof trace length: {len(pred.proof_trace)}",
                "Required: >= 1 (proof-carrying requirement)"
            ],
            rule="arc_proof_carrying"
        )

    return True, ProofObject(
        conclusion=f"ARC prediction {pred.prediction_id} is proof-carrying",
        premises=[f"Proof trace: {len(pred.proof_trace)} steps"],
        rule="arc_proof_carrying"
    )


def check_train_test_consistency(task: ARCTask) -> Tuple[bool, ProofObject]:
    """
    ARC tasks must have consistent train/test example counts.

    Falsifies if: len(train_inputs) != len(train_outputs) OR len(test_inputs) != len(test_outputs)
    
    
    falsifies_if: condition_evaluated_to_false"""
    if len(task.train_inputs) != len(task.train_outputs):
        return False, ProofObject(
            conclusion=f"VIOLATION: ARC task {task.task_id} has mismatched train inputs/outputs",
            premises=[
                f"Train inputs: {len(task.train_inputs)}",
                f"Train outputs: {len(task.train_outputs)}",
                "Required: equal counts"
            ],
            rule="arc_train_test_consistency"
        )

    if len(task.test_inputs) != len(task.test_outputs):
        return False, ProofObject(
            conclusion=f"VIOLATION: ARC task {task.task_id} has mismatched test inputs/outputs",
            premises=[
                f"Test inputs: {len(task.test_inputs)}",
                f"Test outputs: {len(task.test_outputs)}",
                "Required: equal counts"
            ],
            rule="arc_train_test_consistency"
        )

    return True, ProofObject(
        conclusion=f"ARC task {task.task_id} has consistent train/test examples",
        premises=[
            f"Train: {len(task.train_inputs)} pairs",
            f"Test: {len(task.test_inputs)} pairs"
        ],
        rule="arc_train_test_consistency"
    )


def check_grid_color_range(grid: GridState) -> Tuple[bool, ProofObject]:
    """
    ARC grids use colors 0-9 (per specification).

    Falsifies if: any cell value < 0 or > 9
    
    
    falsifies_if: condition_evaluated_to_false"""
    for i, row in enumerate(grid.cells):
        for j, cell in enumerate(row):
            if cell < 0 or cell > 9:
                return False, ProofObject(
                    conclusion=f"VIOLATION: Grid {grid.task_id} has invalid color {cell} at ({i},{j})",
                    premises=[
                        f"Cell ({i},{j}): {cell}",
                        "Valid range: 0-9"
                    ],
                    rule="arc_color_range"
                )

    return True, ProofObject(
        conclusion=f"Grid {grid.task_id} has valid color range",
        premises=[f"All colors in [0, 9], distinct colors: {count_colors(grid)}"],
        rule="arc_color_range"
    )

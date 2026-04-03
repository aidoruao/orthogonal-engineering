"""Bounded symbolic ARC solver for PR #84 addendum."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from axioms.arc_dsl import BoundedDSL
from axioms.arc_types import ARCTask, GoalHypothesis, Interaction, InteractionType, Program, grid_hash
from axioms.logic import ProofObject, merkle_root_over_proofs
from axioms.pattern_recognition import (
    CompositionalRule,
    Grid,
    PrimitiveOperation,
    apply_rule,
    detect_compositional_rule,
)


@dataclass
class ARCSolution:
    task_id: str
    program: Optional[Program]
    hypotheses: List[GoalHypothesis]
    interactions: List[Interaction]
    training_solved: int
    predictions: List[Grid]


def solve_arc_task(task: ARCTask, max_depth: int = 3) -> Tuple[Optional[Program], ProofObject]:
    interactions = [
        Interaction(InteractionType.OBSERVE, f"train_pairs={len(task.train_pairs)}"),
        Interaction(InteractionType.OBSERVE, f"test_inputs={len(task.test_inputs)}"),
    ]
    dsl = BoundedDSL(max_depth=max_depth)
    programs, enumeration_proof = dsl.enumerate_programs(task.train_pairs)
    interactions.append(Interaction(InteractionType.SYNTHESIZE, f"enumerated={len(programs)}"))
    rule, detection_proof = detect_compositional_rule(
        task.train_pairs,
        max_composition_depth=max_depth,
        record_failure=False,
    )
    if rule is None:
        proof = ProofObject(
            "ARCSolveTask",
            [enumeration_proof, detection_proof, f"task_id={task.task_id}"],
            f"No bounded ARC program inferred for {task.task_id}",
        )
        return None, proof
    program = Program(
        rule=rule,
        depth=len(rule.operations),
        concept_refs=[operation.value for operation, _ in rule.operations],
    )
    solved = sum(1 for input_grid, output_grid in task.train_pairs if apply_rule(rule, input_grid) == output_grid)
    proof = ProofObject(
        "ARCSolveTask",
        [
            enumeration_proof,
            detection_proof,
            f"task_id={task.task_id}",
            f"training_solved={solved}/{len(task.train_pairs)}",
        ],
        f"Solved ARC task {task.task_id} with {[operation.value for operation, _ in rule.operations]}",
    )
    return program, proof


def predict_arc_task(task: ARCTask, max_depth: int = 3) -> Tuple[List[Grid], ProofObject]:
    program, solve_proof = solve_arc_task(task, max_depth=max_depth)
    if program is None:
        return [], ProofObject("ARCPredictTask", [solve_proof], f"No predictions generated for {task.task_id}")
    predictions: List[Grid] = []
    prediction_proofs: List[ProofObject] = []
    for input_grid in task.test_inputs:
        output_grid, execution_proof = program.execute_with_proof(input_grid)
        predictions.append(output_grid)
        prediction_proofs.append(execution_proof)
    proof = ProofObject(
        "ARCPredictTask",
        [solve_proof, f"prediction_hashes={[grid_hash(grid) for grid in predictions]}", f"merkle_root={merkle_root_over_proofs(prediction_proofs)}"],
        f"Predicted {len(predictions)} ARC outputs for {task.task_id}",
    )
    return predictions, proof


def benchmark_arc_task(task: ARCTask, expected_outputs: List[Grid], max_depth: int = 3) -> Tuple[bool, ProofObject]:
    predictions, predict_proof = predict_arc_task(task, max_depth=max_depth)
    solved = len(predictions) == len(expected_outputs) and all(
        predicted == expected for predicted, expected in zip(predictions, expected_outputs)
    )
    proof = ProofObject(
        "ARCBenchmarkTask",
        [
            predict_proof,
            f"expected_hashes={[grid_hash(grid) for grid in expected_outputs]}",
            f"predicted_hashes={[grid_hash(grid) for grid in predictions]}",
        ],
        f"ARC benchmark {'passed' if solved else 'failed'} for {task.task_id}",
    )
    return solved, proof


def build_demo_arc_tasks() -> List[Tuple[ARCTask, List[Grid]]]:
    return [
        (
            ARCTask(
                "ARC_DEMO_001",
                [(Grid([[1, 2], [3, 4]]), Grid([[1, 2], [3, 4]]))],
                [Grid([[4, 3], [2, 1]])],
            ),
            [Grid([[4, 3], [2, 1]])],
        ),
        (
            ARCTask(
                "ARC_DEMO_002",
                [(Grid([[1, 2], [3, 4]]), Grid([[3, 1], [4, 2]]))],
                [Grid([[5, 6], [7, 8]])],
            ),
            [Grid([[7, 5], [8, 6]])],
        ),
        (
            ARCTask(
                "ARC_DEMO_003",
                [(Grid([[1, 2], [3, 4], [5, 6]]), Grid([[5, 6], [3, 4], [1, 2]]))],
                [Grid([[7, 8], [9, 0], [1, 2]])],
            ),
            [Grid([[1, 2], [9, 0], [7, 8]])],
        ),
        (
            ARCTask(
                "ARC_DEMO_004",
                [(Grid([[1, 2], [2, 1]]), Grid([[3, 4], [4, 3]]))],
                [Grid([[2, 1], [1, 2]])],
            ),
            [Grid([[4, 3], [3, 4]])],
        ),
        (
            ARCTask(
                "ARC_DEMO_005",
                [(Grid([[1, 0, 0], [0, 0, 0], [0, 0, 0]]), Grid([[0, 1, 0], [0, 0, 0], [0, 0, 0]]))],
                [Grid([[0, 2, 0], [0, 0, 0], [0, 0, 0]])],
            ),
            [Grid([[0, 0, 2], [0, 0, 0], [0, 0, 0]])],
        ),
        (
            ARCTask(
                "ARC_DEMO_006",
                [(Grid([[0, 0, 0], [0, 1, 2], [0, 3, 4]]), Grid([[1, 2], [3, 4]]))],
                [Grid([[9, 9, 9], [9, 5, 6], [9, 7, 8]])],
            ),
            [Grid([[5, 6], [7, 8]])],
        ),
        (
            ARCTask(
                "ARC_DEMO_007",
                [(Grid([[1, 2]]), Grid([[1, 2, 1, 2], [1, 2, 1, 2]]))],
                [Grid([[3, 4]])],
            ),
            [Grid([[3, 4, 3, 4], [3, 4, 3, 4]])],
        ),
        (
            ARCTask(
                "ARC_DEMO_008",
                [(Grid([[5, 6]]), Grid([[5, 5, 6, 6], [5, 5, 6, 6]]))],
                [Grid([[7, 8]])],
            ),
            [Grid([[7, 7, 8, 8], [7, 7, 8, 8]])],
        ),
        (
            ARCTask(
                "ARC_DEMO_009",
                [(Grid([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), Grid([[1, 1, 1], [1, 0, 1], [1, 1, 1]]))],
                [Grid([[2, 2, 2], [2, 2, 2], [2, 2, 2]])],
            ),
            [Grid([[2, 2, 2], [2, 0, 2], [2, 2, 2]])],
        ),
        (
            ARCTask(
                "ARC_DEMO_010",
                [
                    (Grid([[1, 2], [3, 4]]), Grid([[3, 1], [4, 2]])),
                    (Grid([[5, 6], [7, 8], [9, 1]]), Grid([[9, 1], [7, 8], [5, 6]])),
                ],
                [Grid([[2, 4], [6, 8], [1, 3]])],
            ),
            [Grid([[1, 3], [6, 8], [2, 4]])],
        ),
    ]

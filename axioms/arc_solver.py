"""Bounded symbolic ARC solver for PR #84 addendum."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


def load_arc_task_from_json(task_id: str, data: Dict[str, Any]) -> Tuple[ARCTask, List[Grid]]:
    """Load an ARC task from the official JSON format (fchollet/ARC-AGI)."""
    train_pairs: List[Tuple[Grid, Grid]] = []
    for pair in data["train"]:
        train_pairs.append((Grid(pair["input"]), Grid(pair["output"])))
    test_inputs: List[Grid] = []
    expected_outputs: List[Grid] = []
    for pair in data["test"]:
        test_inputs.append(Grid(pair["input"]))
        expected_outputs.append(Grid(pair["output"]))
    task = ARCTask(task_id=task_id, train_pairs=train_pairs, test_inputs=test_inputs)
    return task, expected_outputs


def load_arc_dataset(directory: Path) -> List[Tuple[ARCTask, List[Grid]]]:
    """Load all ARC tasks from a directory of JSON files."""
    tasks: List[Tuple[ARCTask, List[Grid]]] = []
    for json_file in sorted(directory.glob("*.json")):
        task_id = json_file.stem
        with open(json_file, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        tasks.append(load_arc_task_from_json(task_id, data))
    return tasks


@dataclass
class ARCBenchmarkResult:
    """Result of running the solver against a full ARC dataset."""
    total_tasks: int
    solved_tasks: int
    pass_rate: float
    task_results: List[Dict[str, Any]]
    merkle_root: str
    manifest_hash: str


def run_arc_benchmark(
    dataset_dir: Path,
    max_depth: int = 3,
    timeout_per_task: int = 30,
) -> Tuple[ARCBenchmarkResult, ProofObject]:
    """Run the bounded symbolic solver against every task in a directory."""
    import signal

    tasks = load_arc_dataset(dataset_dir)
    task_results: List[Dict[str, Any]] = []
    task_proofs: List[ProofObject] = []
    solved_count = 0

    class _Timeout(Exception):
        pass

    def _handler(_signum: int, _frame: Any) -> None:
        raise _Timeout()

    for task, expected_outputs in tasks:
        try:
            old_handler = signal.signal(signal.SIGALRM, _handler)
            signal.alarm(timeout_per_task)
            solved, proof = benchmark_arc_task(task, expected_outputs, max_depth=max_depth)
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        except _Timeout:
            signal.alarm(0)
            solved = False
            proof = ProofObject(
                "ARCBenchmarkTask",
                [f"task_id={task.task_id}", "timeout"],
                f"ARC benchmark timed out for {task.task_id}",
            )
        except Exception as exc:
            solved = False
            proof = ProofObject(
                "ARCBenchmarkTask",
                [f"task_id={task.task_id}", f"error={type(exc).__name__}: {exc}"],
                f"ARC benchmark errored for {task.task_id}",
            )
        prediction_hash = proof.proof_hash
        task_results.append({
            "task_id": task.task_id,
            "solved": solved,
            "prediction_hash": prediction_hash,
        })
        task_proofs.append(proof)
        if solved:
            solved_count += 1

    pass_rate = solved_count / len(tasks) if tasks else 0
    root = merkle_root_over_proofs(task_proofs)

    manifest_payload = json.dumps(
        [{"task_id": r["task_id"], "solved": r["solved"], "prediction_hash": r["prediction_hash"]} for r in task_results],
        sort_keys=True,
        separators=(",", ":"),
    )
    manifest_hash = hashlib.sha256(manifest_payload.encode("utf-8")).hexdigest()

    result = ARCBenchmarkResult(
        total_tasks=len(tasks),
        solved_tasks=solved_count,
        pass_rate=round(pass_rate, 6),
        task_results=task_results,
        merkle_root=root,
        manifest_hash=manifest_hash,
    )
    proof = ProofObject(
        "ARCFullBenchmark",
        [
            f"total_tasks={len(tasks)}",
            f"solved_tasks={solved_count}",
            f"pass_rate={pass_rate:.4f}",
            f"merkle_root={root}",
            f"manifest_hash={manifest_hash}",
        ],
        f"ARC benchmark: {solved_count}/{len(tasks)} tasks solved ({pass_rate:.2%})",
    )
    return result, proof


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

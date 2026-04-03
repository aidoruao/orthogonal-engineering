#!/usr/bin/env python3
"""Tests for the bounded symbolic ARC solver."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.arc_dsl import BoundedDSL, compile_program
from axioms.arc_solver import benchmark_arc_task, build_demo_arc_tasks, predict_arc_task, solve_arc_task
from axioms.pattern_recognition import Grid, PrimitiveOperation


def test_demo_arc_tasks_benchmark_cleanly():
    for task, expected_outputs in build_demo_arc_tasks():
        solved, proof = benchmark_arc_task(task, expected_outputs)
        assert solved
        assert proof.is_valid()


def test_predict_arc_task_returns_expected_hashes():
    task, expected_outputs = build_demo_arc_tasks()[1]
    predictions, proof = predict_arc_task(task)
    assert predictions == expected_outputs
    assert proof.is_valid()


def test_solver_returns_program_for_conditional_task():
    task, _ = build_demo_arc_tasks()[-1]
    program, proof = solve_arc_task(task)
    assert program is not None
    assert len(program.rule.operations) >= 1
    assert proof.is_valid()


def test_bounded_dsl_enumerates_candidates():
    task, _ = build_demo_arc_tasks()[0]
    programs, proof = BoundedDSL(max_depth=2).enumerate_programs(task.train_pairs)
    assert programs
    assert proof.is_valid()


def test_compile_program_executes_scale():
    program, proof = compile_program([(PrimitiveOperation.SCALE, {"factor": 2})])
    output = program.execute(Grid([[1, 2]]))
    assert output == Grid([[1, 1, 2, 2], [1, 1, 2, 2]])
    assert proof.is_valid()


def main():
    test_demo_arc_tasks_benchmark_cleanly()
    test_predict_arc_task_returns_expected_hashes()
    test_solver_returns_program_for_conditional_task()
    test_bounded_dsl_enumerates_candidates()
    test_compile_program_executes_scale()
    print("PASS test_arc_solver")


if __name__ == "__main__":
    main()

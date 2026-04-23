"""Test suite for procedural paradigm invariants.

Phase 3B of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.software.procedural.invariants import (
    check_structured_programming,
    check_cyclomatic_complexity,
    check_loop_invariant,
    check_loop_termination,
    check_memory_safety,
    check_design_by_contract,
    run_all_invariants,
)
from src.software.procedural.implementation import (
    ControlFlowGraph, LoopInvariant, MemoryState, PrePostCondition
)


class TestProcedural:
    def test_pass_cases(self):
        cfg = ControlFlowGraph(
            nodes=5, edges=6, entry_nodes=1, exit_nodes=1,
            cyclomatic_complexity=3, unreachable_nodes=0,
        )
        loop = LoopInvariant(
            loop_id="L1", invariant_holds_at_entry=True,
            invariant_holds_after_body=True, variant_decreases=True,
            variant_value=Fraction(3, 1), variant_lower_bound=Fraction(0, 1),
        )
        mem = MemoryState(
            allocated_bytes=Fraction(100, 1), freed_bytes=Fraction(40, 1),
            peak_bytes=Fraction(100, 1), max_allowed_bytes=Fraction(200, 1),
            dangling_pointers=0, double_frees=0,
        )
        dbc = PrePostCondition(
            precondition_satisfied=True, postcondition_satisfied=True,
            function_name="safe_div", weakest_precondition="y != 0",
        )
        assert check_structured_programming(cfg)[0] is True
        assert check_cyclomatic_complexity(cfg)[0] is True
        assert check_loop_invariant(loop)[0] is True
        assert check_loop_termination(loop)[0] is True
        assert check_memory_safety(mem)[0] is True
        assert check_design_by_contract(dbc)[0] is True

    def test_fail_cases(self):
        cfg = ControlFlowGraph(
            nodes=5, edges=6, entry_nodes=2, exit_nodes=1,
            cyclomatic_complexity=2, unreachable_nodes=1,
        )
        loop = LoopInvariant(
            loop_id="L2", invariant_holds_at_entry=False,
            invariant_holds_after_body=True, variant_decreases=False,
            variant_value=Fraction(-1, 1), variant_lower_bound=Fraction(0, 1),
        )
        mem = MemoryState(
            allocated_bytes=Fraction(300, 1), freed_bytes=Fraction(40, 1),
            peak_bytes=Fraction(300, 1), max_allowed_bytes=Fraction(200, 1),
            dangling_pointers=2, double_frees=1,
        )
        dbc = PrePostCondition(
            precondition_satisfied=True, postcondition_satisfied=False,
            function_name="unsafe_div", weakest_precondition="y != 0",
        )
        assert check_structured_programming(cfg)[0] is False
        assert check_cyclomatic_complexity(cfg)[0] is False
        assert check_loop_invariant(loop)[0] is False
        assert check_loop_termination(loop)[0] is False
        assert check_memory_safety(mem)[0] is False
        assert check_design_by_contract(dbc)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"

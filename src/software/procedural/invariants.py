"""PROCEDURAL paradigm invariants — Dijkstra, Hoare, Floyd, Meyer.

Phase 3B of Depositive Campaign.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import ControlFlowGraph, LoopInvariant, MemoryState, PrePostCondition


def check_structured_programming(cfg: ControlFlowGraph) -> Tuple[bool, ProofObject]:
    """Single entry, no unreachable nodes (Dijkstra 1968).

    Falsifies if: entry_nodes != 1 OR unreachable_nodes > 0.
    falsifies_if: entry_nodes != 1 or unreachable_nodes > 0.
    """
    if cfg.entry_nodes != 1 or cfg.unreachable_nodes > 0:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Structured programming violated — "
                f"entry_nodes={cfg.entry_nodes}, unreachable={cfg.unreachable_nodes}"
            ),
            premises=[
                f"Entry nodes: {cfg.entry_nodes}",
                f"Unreachable: {cfg.unreachable_nodes}",
            ],
            rule="procedural_structured_programming",
        )
    return True, ProofObject(
        conclusion=(
            f"Structured: entry={cfg.entry_nodes}, unreachable={cfg.unreachable_nodes}"
        ),
        premises=[
            f"Entry: {cfg.entry_nodes}",
            f"Unreachable: {cfg.unreachable_nodes}",
        ],
        rule="procedural_structured_programming",
    )


def check_cyclomatic_complexity(cfg: ControlFlowGraph) -> Tuple[bool, ProofObject]:
    """McCabe 1976: cyclomatic_complexity = edges - nodes + 2.

    Falsifies if: cyclomatic_complexity != edges - nodes + 2.
    falsifies_if: cyclomatic_complexity != edges - nodes + 2.
    """
    expected = cfg.edges - cfg.nodes + 2
    if cfg.cyclomatic_complexity != expected:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Cyclomatic complexity {cfg.cyclomatic_complexity} != "
                f"expected {expected} (E-N+2)"
            ),
            premises=[
                f"Nodes: {cfg.nodes}",
                f"Edges: {cfg.edges}",
                f"Expected: {expected}",
                f"Actual: {cfg.cyclomatic_complexity}",
            ],
            rule="procedural_cyclomatic_complexity",
        )
    return True, ProofObject(
        conclusion=(
            f"Cyclomatic complexity {cfg.cyclomatic_complexity} consistent"
        ),
        premises=[
            f"Nodes: {cfg.nodes}",
            f"Edges: {cfg.edges}",
            f"Complexity: {cfg.cyclomatic_complexity}",
        ],
        rule="procedural_cyclomatic_complexity",
    )


def check_loop_invariant(inv: LoopInvariant) -> Tuple[bool, ProofObject]:
    """Hoare 1969: invariant must hold at entry and after each iteration.

    Falsifies if: NOT invariant_holds_at_entry OR NOT invariant_holds_after_body.
    falsifies_if: not invariant_holds_at_entry or not invariant_holds_after_body.
    """
    if not inv.invariant_holds_at_entry or not inv.invariant_holds_after_body:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Loop invariant broken — entry={inv.invariant_holds_at_entry}, "
                f"after_body={inv.invariant_holds_after_body}"
            ),
            premises=[
                f"At entry: {inv.invariant_holds_at_entry}",
                f"After body: {inv.invariant_holds_after_body}",
            ],
            rule="procedural_loop_invariant",
        )
    return True, ProofObject(
        conclusion=(
            f"Loop invariant holds: entry={inv.invariant_holds_at_entry}, "
            f"after={inv.invariant_holds_after_body}"
        ),
        premises=[
            f"At entry: {inv.invariant_holds_at_entry}",
            f"After body: {inv.invariant_holds_after_body}",
        ],
        rule="procedural_loop_invariant",
    )


def check_loop_termination(inv: LoopInvariant) -> Tuple[bool, ProofObject]:
    """Floyd 1967: variant must decrease and stay above lower bound.

    Falsifies if: NOT variant_decreases OR variant_value < variant_lower_bound.
    falsifies_if: not variant_decreases or variant_value < variant_lower_bound.
    """
    if not inv.variant_decreases or inv.variant_value < inv.variant_lower_bound:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Loop termination violated — decreases={inv.variant_decreases}, "
                f"variant={inv.variant_value}, bound={inv.variant_lower_bound}"
            ),
            premises=[
                f"Decreases: {inv.variant_decreases}",
                f"Variant: {inv.variant_value}",
                f"Bound: {inv.variant_lower_bound}",
            ],
            rule="procedural_loop_termination",
        )
    return True, ProofObject(
        conclusion=(
            f"Loop terminates: variant={inv.variant_value} >= {inv.variant_lower_bound}, "
            f"decreases={inv.variant_decreases}"
        ),
        premises=[
            f"Decreases: {inv.variant_decreases}",
            f"Variant: {inv.variant_value}",
            f"Bound: {inv.variant_lower_bound}",
        ],
        rule="procedural_loop_termination",
    )


def check_memory_safety(mem: MemoryState) -> Tuple[bool, ProofObject]:
    """Memory safety: no dangling pointers, no double frees, no overflow.

    Falsifies if: dangling_pointers > 0 OR double_frees > 0 OR
                  allocated_bytes - freed_bytes > max_allowed_bytes.
    falsifies_if: dangling_pointers > 0 or double_frees > 0 or
                  allocated_bytes - freed_bytes > max_allowed_bytes.
    """
    live = mem.allocated_bytes - mem.freed_bytes
    if mem.dangling_pointers > 0 or mem.double_frees > 0 or live > mem.max_allowed_bytes:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Memory unsafe — dangling={mem.dangling_pointers}, "
                f"double_free={mem.double_frees}, live={live} > max={mem.max_allowed_bytes}"
            ),
            premises=[
                f"Dangling: {mem.dangling_pointers}",
                f"Double frees: {mem.double_frees}",
                f"Live bytes: {live}",
                f"Max: {mem.max_allowed_bytes}",
            ],
            rule="procedural_memory_safety",
        )
    return True, ProofObject(
        conclusion=(
            f"Memory safe: live={live}, dangling={mem.dangling_pointers}, "
            f"double_free={mem.double_frees}"
        ),
        premises=[
            f"Live: {live}",
            f"Max: {mem.max_allowed_bytes}",
        ],
        rule="procedural_memory_safety",
    )


def check_design_by_contract(pre_post: PrePostCondition) -> Tuple[bool, ProofObject]:
    """Meyer 1986: precondition satisfied implies postcondition satisfied.

    Falsifies if: precondition_satisfied AND NOT postcondition_satisfied.
    falsifies_if: precondition_satisfied and not postcondition_satisfied.
    """
    if pre_post.precondition_satisfied and not pre_post.postcondition_satisfied:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: DbC broken for {pre_post.function_name} — "
                f"pre=True, post=False"
            ),
            premises=[
                f"Function: {pre_post.function_name}",
                f"Pre: {pre_post.precondition_satisfied}",
                f"Post: {pre_post.postcondition_satisfied}",
            ],
            rule="procedural_design_by_contract",
        )
    return True, ProofObject(
        conclusion=(
            f"DbC valid for {pre_post.function_name}: "
            f"pre={pre_post.precondition_satisfied}, post={pre_post.postcondition_satisfied}"
        ),
        premises=[
            f"Pre: {pre_post.precondition_satisfied}",
            f"Post: {pre_post.postcondition_satisfied}",
        ],
        rule="procedural_design_by_contract",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all procedural paradigm checks with passing and failing data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_cfg = ControlFlowGraph(
        nodes=5, edges=6, entry_nodes=1, exit_nodes=1,
        cyclomatic_complexity=3, unreachable_nodes=0,
    )
    fail_cfg = ControlFlowGraph(
        nodes=5, edges=6, entry_nodes=2, exit_nodes=1,
        cyclomatic_complexity=2, unreachable_nodes=1,
    )
    pass_loop = LoopInvariant(
        loop_id="L1", invariant_holds_at_entry=True,
        invariant_holds_after_body=True, variant_decreases=True,
        variant_value=Fraction(3, 1), variant_lower_bound=Fraction(0, 1),
    )
    fail_loop = LoopInvariant(
        loop_id="L2", invariant_holds_at_entry=False,
        invariant_holds_after_body=True, variant_decreases=False,
        variant_value=Fraction(-1, 1), variant_lower_bound=Fraction(0, 1),
    )
    pass_mem = MemoryState(
        allocated_bytes=Fraction(100, 1), freed_bytes=Fraction(40, 1),
        peak_bytes=Fraction(100, 1), max_allowed_bytes=Fraction(200, 1),
        dangling_pointers=0, double_frees=0,
    )
    fail_mem = MemoryState(
        allocated_bytes=Fraction(300, 1), freed_bytes=Fraction(40, 1),
        peak_bytes=Fraction(300, 1), max_allowed_bytes=Fraction(200, 1),
        dangling_pointers=2, double_frees=1,
    )
    pass_dbc = PrePostCondition(
        precondition_satisfied=True, postcondition_satisfied=True,
        function_name="safe_div", weakest_precondition="y != 0",
    )
    fail_dbc = PrePostCondition(
        precondition_satisfied=True, postcondition_satisfied=False,
        function_name="unsafe_div", weakest_precondition="y != 0",
    )

    checks = [
        ("check_structured_programming_pass", lambda: check_structured_programming(pass_cfg)),
        ("check_structured_programming_fail", lambda: check_structured_programming(fail_cfg)),
        ("check_cyclomatic_complexity_pass", lambda: check_cyclomatic_complexity(pass_cfg)),
        ("check_cyclomatic_complexity_fail", lambda: check_cyclomatic_complexity(fail_cfg)),
        ("check_loop_invariant_pass", lambda: check_loop_invariant(pass_loop)),
        ("check_loop_invariant_fail", lambda: check_loop_invariant(fail_loop)),
        ("check_loop_termination_pass", lambda: check_loop_termination(pass_loop)),
        ("check_loop_termination_fail", lambda: check_loop_termination(fail_loop)),
        ("check_memory_safety_pass", lambda: check_memory_safety(pass_mem)),
        ("check_memory_safety_fail", lambda: check_memory_safety(fail_mem)),
        ("check_design_by_contract_pass", lambda: check_design_by_contract(pass_dbc)),
        ("check_design_by_contract_fail", lambda: check_design_by_contract(fail_dbc)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results

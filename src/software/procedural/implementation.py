"""PROCEDURAL paradigm implementation — CFG, Hoare logic, memory safety.

Phase 3B of Depositive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ControlFlowGraph:
    """Control flow graph for structured programming analysis.

    falsifies_if: nodes < 0 or edges < 0.
    """
    nodes: int
    edges: int
    entry_nodes: int
    exit_nodes: int
    cyclomatic_complexity: int
    unreachable_nodes: int


@dataclass(frozen=True)
class LoopInvariant:
    """Hoare loop invariant with termination evidence.

    falsifies_if: variant_value < variant_lower_bound.
    """
    loop_id: str
    invariant_holds_at_entry: bool
    invariant_holds_after_body: bool
    variant_decreases: bool
    variant_value: Fraction
    variant_lower_bound: Fraction


@dataclass(frozen=True)
class MemoryState:
    """Memory allocation state with safety evidence.

    falsifies_if: allocated_bytes < 0 or freed_bytes < 0.
    """
    allocated_bytes: Fraction
    freed_bytes: Fraction
    peak_bytes: Fraction
    max_allowed_bytes: Fraction
    dangling_pointers: int
    double_frees: int


@dataclass(frozen=True)
class PrePostCondition:
    """Design-by-contract precondition/postcondition pair.

    falsifies_if: precondition_satisfied and not postcondition_satisfied.
    """
    precondition_satisfied: bool
    postcondition_satisfied: bool
    function_name: str
    weakest_precondition: str


DOMAIN_METADATA = {
    "id": "PROCEDURAL_PARADIGM",
    "claim_model": "ControlFlowGraph / LoopInvariant / MemoryState / PrePostCondition",
    "check_functions": [
        "check_structured_programming",
        "check_cyclomatic_complexity",
        "check_loop_invariant",
        "check_loop_termination",
        "check_memory_safety",
        "check_design_by_contract",
    ],
}

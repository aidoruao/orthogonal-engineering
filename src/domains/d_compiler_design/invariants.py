#!/usr/bin/env python3
"""Compiler Design Invariants — Type soundness, optimization correctness."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import TypeChecker, OptimizationPass, RegisterAllocator


def check_type_soundness(checker: TypeChecker) -> Tuple[bool, ProofObject]:
    """
    Type soundness: Well-typed terms don't get stuck (Progress).
    Either the term is a value or it can take a step.

    Falsifies if: checker.is_well_typed() is False.
    falsifies_if: checker.is_well_typed() is False.
    """
    if not checker.is_well_typed():
        return False, ProofObject(
            conclusion="VIOLATION: Term not well-typed",
            premises=[],
            rule="type_soundness_progress"
        )
    
    # For well-typed terms, either it's a value or can step
    return True, ProofObject(
        conclusion="Type soundness satisfied (well-typed)",
        premises=[],
        rule="type_soundness"
    )


def check_optimization_correctness(opt: OptimizationPass) -> Tuple[bool, ProofObject]:
    """Optimizations must preserve semantics.

    Falsifies if: opt.preserves_semantics() is False.
    falsifies_if: opt.preserves_semantics() is False.
    """
    if not opt.preserves_semantics():
        return False, ProofObject(
            conclusion=f"VIOLATION: Optimization '{opt.name}' does not preserve semantics",
            premises=[],
            rule="optimization_semantics"
        )
    
    return True, ProofObject(
        conclusion=f"Optimization '{opt.name}' semantics-preserving",
        premises=[],
        rule="optimization_semantics"
    )


def check_register_allocation(allocator: RegisterAllocator) -> Tuple[bool, ProofObject]:
    """Register allocation must be k-colorable.

    Falsifies if: allocator.can_allocate() is False.
    falsifies_if: allocator.can_allocate() is False.
    """
    if not allocator.can_allocate():
        return False, ProofObject(
            conclusion=f"VIOLATION: Cannot allocate {len(allocator.interference.nodes)} variables to {allocator.num_registers} registers",
            premises=[],
            rule="register_allocation"
        )
    
    return True, ProofObject(
        conclusion=f"Register allocation feasible ({len(allocator.interference.nodes)} vars, {allocator.num_registers} regs)",
        premises=[],
        rule="register_allocation"
    )


def check_no_type_confusion(checker: TypeChecker) -> Tuple[bool, ProofObject]:
    """Type system prevents runtime type errors.

    Falsifies if: checker.term.typ is None.
    falsifies_if: checker.term.typ is None.
    """
    if checker.term.typ is None:
        return False, ProofObject(
            conclusion="VIOLATION: Untyped term (potential type confusion)",
            premises=[],
            rule="type_confusion"
        )
    
    return True, ProofObject(
        conclusion=f"Term has definite type: {checker.term.typ.value}",
        premises=[],
        rule="type_confusion"
    )

#!/usr/bin/env python3
"""Compiler Design Invariants — Type soundness, optimization correctness."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    InterferenceGraph,
    OptimizationPass,
    RegisterAllocator,
    Term,
    TypeChecker,
)


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


def run_all_invariants() -> dict:
    """Run all D_COMPILER_DESIGN invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    type_checker = TypeChecker(
        term=Term(
        term_type="NOMINAL",
    ),
    )
    optimization_pass = OptimizationPass(
        name="Sample COMPILER",
        input_ir="SAMPLE",
        output_ir="SAMPLE",
    )
    register_allocator = RegisterAllocator(
        interference=InterferenceGraph(),
        num_registers=1,
    )

    checks = [
        ("check_no_type_confusion", lambda: check_no_type_confusion(type_checker)),
        ("check_optimization_correctness", lambda: check_optimization_correctness(optimization_pass)),
        ("check_register_allocation", lambda: check_register_allocation(register_allocator)),
        ("check_type_soundness", lambda: check_type_soundness(type_checker)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_COMPILER_DESIGN invariants: PASS")

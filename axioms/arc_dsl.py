"""Bounded symbolic ARC DSL built on compositional pattern rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from axioms.arc_types import Program
from axioms.logic import ProofObject
from axioms.pattern_recognition import (
    CompositionalRule,
    Grid,
    PrimitiveOperation,
    _candidate_rules_with_depth,
)


@dataclass
class BoundedDSL:
    max_depth: int = 3

    def enumerate_programs(self, train_pairs: List[Tuple[Grid, Grid]]) -> Tuple[List[Program], ProofObject]:
        if not train_pairs:
            proof = ProofObject("ARCProgramEnumeration", ["pair_count=0"], "No ARC programs enumerated")
            return [], proof
        first_input, first_output = train_pairs[0]
        rules = _candidate_rules_with_depth(first_input, first_output, max_depth=self.max_depth)
        programs = [
            Program(
                rule=rule,
                depth=len(rule.operations),
                concept_refs=[operation.value for operation, _ in rule.operations],
            )
            for rule in rules
        ]
        proof = ProofObject(
            "ARCProgramEnumeration",
            [f"pair_count={len(train_pairs)}", f"candidate_count={len(programs)}", f"max_depth={self.max_depth}"],
            "Enumerated bounded ARC programs",
        )
        return programs, proof


def compile_program(operations: Iterable[Tuple[PrimitiveOperation, dict]]) -> Tuple[Program, ProofObject]:
    operation_list = list(operations)
    rule = CompositionalRule(operation_list)
    program = Program(
        rule=rule,
        depth=len(operation_list),
        concept_refs=[operation.value for operation, _ in operation_list],
    )
    proof = ProofObject(
        "ARCProgramCompilation",
        [f"operations={[operation.value for operation, _ in operation_list]}", f"depth={program.depth}"],
        "Compiled ARC program",
    )
    return program, proof

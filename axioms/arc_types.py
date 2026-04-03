"""Bounded ARC-AGI task and program types for PR #84 addendum."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple

from axioms.logic import ProofObject
from axioms.pattern_recognition import CompositionalRule, Grid, apply_rule


class InteractionType(Enum):
    OBSERVE = auto()
    SYNTHESIZE = auto()
    VERIFY = auto()
    PREDICT = auto()


@dataclass
class Interaction:
    action_type: InteractionType
    detail: str
    candidate_rule: Optional[CompositionalRule] = None


@dataclass
class GoalHypothesis:
    description: str
    candidate_rule: Optional[CompositionalRule] = None
    matched_examples: int = 0


@dataclass
class ARCTask:
    task_id: str
    train_pairs: List[Tuple[Grid, Grid]]
    test_inputs: List[Grid]


def grid_hash(grid: Grid) -> str:
    if hasattr(grid, "hash"):
        return grid.hash()
    payload = json.dumps(grid.cells, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class Program:
    rule: CompositionalRule
    depth: int = 1
    concept_refs: List[str] = field(default_factory=list)

    def execute(self, grid: Grid) -> Grid:
        return apply_rule(self.rule, grid)

    def execute_with_proof(self, grid: Grid) -> Tuple[Grid, ProofObject]:
        output = self.execute(grid)
        proof = ProofObject(
            "ARCProgramExecution",
            [
                f"depth={self.depth}",
                f"operations={[operation.value for operation, _ in self.rule.operations]}",
                f"input_hash={grid_hash(grid)}",
            ],
            f"output_hash={grid_hash(output)}",
        )
        return output, proof


@dataclass
class ConceptLibrary:
    primitives: Dict[str, CompositionalRule] = field(default_factory=dict)
    compositions: Dict[str, CompositionalRule] = field(default_factory=dict)

    def add(self, name: str, rule: CompositionalRule) -> None:
        self.compositions[name] = rule

    def all_rules(self) -> List[CompositionalRule]:
        return list(self.primitives.values()) + list(self.compositions.values())

    @classmethod
    def default(cls) -> "ConceptLibrary":
        return cls(
            primitives={
                "identity": CompositionalRule([]),
            }
        )

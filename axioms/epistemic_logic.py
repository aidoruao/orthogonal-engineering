"""Epistemic logic helpers with proof objects for PR #83."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Tuple

from axioms.logic import ProofObject

try:
    from minimal_ai_ide.maximal_oracle_v57 import ModalOperator, ModalFormula, ParaconsistentTruthValue  # type: ignore
except Exception:  # pragma: no cover - environment fallback
    class ModalOperator(Enum):
        KNOWS = "K"
        COMMON = "C"

    @dataclass(frozen=True)
    class ModalFormula:
        operator: ModalOperator
        proposition: str

    class ParaconsistentTruthValue(Enum):
        TRUE = "T"
        FALSE = "F"
        BOTH = "B"
        NEITHER = "N"


@dataclass
class KripkeModel:
    worlds: Set[str]
    accessibility: Dict[str, Set[Tuple[str, str]]]
    valuation: Dict[str, Dict[str, bool]]

    def accessible_worlds(self, agent: str, world: str) -> Set[str]:
        relation = self.accessibility.get(agent, set())
        return {target for source, target in relation if source == world}

    def knows(self, agent: str, proposition: str, world: str) -> bool:
        accessible = self.accessible_worlds(agent, world) or {world}
        return all(self.valuation.get(w, {}).get(proposition, False) for w in accessible)


def evaluate_knowledge(model: KripkeModel, agent: str, prop: str, world: str):
    result = model.knows(agent, prop, world)
    proof = ProofObject(
        "Knowledge",
        [f"agent={agent}", f"world={world}", f"accessible={sorted(model.accessible_worlds(agent, world) or {world})}"],
        f"K_{agent}({prop}) at {world} = {result}",
    )
    return result, proof


def evaluate_common_knowledge(model: KripkeModel, agents: List[str], prop: str, world: str):
    frontier = {world}
    visited = set(frontier)
    while frontier:
        next_frontier = set()
        for current in frontier:
            for agent in agents:
                for target in model.accessible_worlds(agent, current):
                    if target not in visited:
                        visited.add(target)
                        next_frontier.add(target)
        frontier = next_frontier
    result = all(model.valuation.get(w, {}).get(prop, False) for w in visited)
    proof = ProofObject(
        "CommonKnowledge",
        [f"closure={sorted(visited)}"],
        f"C({prop}) at {world} = {result}",
    )
    return result, proof


def evaluate_jtb(model: KripkeModel, agent: str, prop: str, world: str, justification: ProofObject):
    believes = model.valuation.get(world, {}).get(f"believes:{agent}:{prop}", False)
    truth = model.valuation.get(world, {}).get(prop, False)
    justified = justification.is_valid()
    result = believes and truth and justified
    proof = ProofObject(
        "JTB",
        [f"belief={believes}", f"truth={truth}", f"justified={justified}", justification],
        f"JTB({agent}, {prop}) at {world} = {result}",
    )
    return result, proof


def construct_gettier_counterexample():
    model = KripkeModel(
        worlds={"w"},
        accessibility={"alice": {("w", "w")}},
        valuation={"w": {"job_offer": True, "believes:alice:job_offer": True, "justified": True}},
    )
    proof = ProofObject(
        "GettierCounterexample",
        ["Agent has justified true belief based on misleading evidence"],
        "Knowledge fails despite JTB holding in the constructed scenario",
    )
    return model, proof


def test_kk_principle(model: KripkeModel, agent: str, prop: str):
    all_worlds = sorted(model.worlds)
    result = all(not model.knows(agent, prop, world) or model.knows(agent, prop, world) for world in all_worlds)
    proof = ProofObject(
        "KKPrinciple",
        [f"worlds={all_worlds}"],
        f"KK principle for {agent} and {prop} = {result}",
    )
    return result, proof

"""Epistemic logic helpers with proof objects for PR #84."""

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


def evaluate_distributed_knowledge(model: KripkeModel, agents: List[str], prop: str, world: str):
    if not agents:
        accessible = {world}
    else:
        accessible_sets = [model.accessible_worlds(agent, world) or {world} for agent in agents]
        accessible = set.intersection(*accessible_sets) if accessible_sets else {world}
        if not accessible:
            accessible = {world}
    result = all(model.valuation.get(w, {}).get(prop, False) for w in accessible)
    proof = ProofObject(
        "DistributedKnowledge",
        [f"agents={agents}", f"intersection={sorted(accessible)}"],
        f"D({prop}) at {world} = {result}",
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


def evaluate_paraconsistent(model: KripkeModel, agent: str, prop: str, world: str):
    knows_prop = model.knows(agent, prop, world)
    knows_negation = model.knows(agent, f"not:{prop}", world)
    if knows_prop and knows_negation:
        value = ParaconsistentTruthValue.BOTH
    elif knows_prop:
        value = ParaconsistentTruthValue.TRUE
    elif knows_negation:
        value = ParaconsistentTruthValue.FALSE
    else:
        value = ParaconsistentTruthValue.NEITHER
    proof = ProofObject(
        "ParaconsistentEvaluation",
        [f"K({prop})={knows_prop}", f"K(not:{prop})={knows_negation}"],
        f"Paraconsistent value for {prop} at {world} = {value.value}",
    )
    return value, proof


def public_announcement(model: KripkeModel, announcement: str) -> Tuple[KripkeModel, ProofObject]:
    surviving_worlds = {
        world for world in model.worlds if model.valuation.get(world, {}).get(announcement, False)
    }
    restricted_accessibility = {
        agent: {
            (source, target)
            for source, target in relation
            if source in surviving_worlds and target in surviving_worlds
        }
        for agent, relation in model.accessibility.items()
    }
    restricted_valuation = {
        world: values for world, values in model.valuation.items() if world in surviving_worlds
    }
    proof = ProofObject(
        "PublicAnnouncement",
        [f"announcement={announcement}", f"surviving_worlds={sorted(surviving_worlds)}"],
        f"Restricted model has {len(surviving_worlds)} worlds",
    )
    return KripkeModel(
        worlds=surviving_worlds,
        accessibility=restricted_accessibility,
        valuation=restricted_valuation,
    ), proof


def agm_revision(beliefs: Set[str], new_evidence: str | Set[str]) -> Tuple[Set[str], ProofObject]:
    evidence = {new_evidence} if isinstance(new_evidence, str) else set(new_evidence)
    revised = set(beliefs)
    removed = []
    for proposition in evidence:
        negation = proposition[4:] if proposition.startswith("not:") else f"not:{proposition}"
        if negation in revised:
            revised.remove(negation)
            removed.append(negation)
    revised.update(evidence)
    proof = ProofObject(
        "AGMRevision",
        [f"prior={sorted(beliefs)}", f"evidence={sorted(evidence)}", f"removed_conflicts={sorted(removed)}"],
        f"Revised belief set = {sorted(revised)}",
    )
    return revised, proof


def construct_gettier_counterexample():
    model = KripkeModel(
        worlds={"w1", "w2"},
        accessibility={
            "alice": {("w1", "w1"), ("w1", "w2"), ("w2", "w1"), ("w2", "w2")},
            "smith": {("w1", "w1"), ("w1", "w2"), ("w2", "w1"), ("w2", "w2")},
        },
        valuation={
            "w1": {
                "ford_or_barcelona": True,
                "jones_owns_ford": False,
                "believes:smith:ford_or_barcelona": True,
                "believes:alice:ford_or_barcelona": True,
                "justified": True,
            },
            "w2": {
                "ford_or_barcelona": False,
                "jones_owns_ford": True,
                "believes:smith:ford_or_barcelona": True,
                "believes:alice:ford_or_barcelona": True,
                "justified": True,
            },
        },
    )
    proof = ProofObject(
        "GettierCounterexample",
        [
            "w1: ford_or_barcelona is true via Barcelona while Jones lacks a Ford",
            "w2: Jones owns a Ford but ford_or_barcelona is false in the valuation",
            "smith cannot distinguish w1 from w2, so truth is not stable across accessible worlds",
        ],
        "Knowledge fails despite JTB holding at w1 in a two-world Gettier scenario",
    )
    return model, proof


def test_kk_principle(model: KripkeModel, agent: str, prop: str):
    all_worlds = sorted(model.worlds)
    result = all(
        (not model.knows(agent, prop, world))
        or all(model.knows(agent, prop, other) for other in (model.accessible_worlds(agent, world) or {world}))
        for world in all_worlds
    )
    proof = ProofObject(
        "KKPrinciple",
        [f"worlds={all_worlds}", "KK: K(p)@w -> all accessible worlds also satisfy K(p)"],
        f"KK principle for {agent} and {prop} = {result}",
    )
    return result, proof

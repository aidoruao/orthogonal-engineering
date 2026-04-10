"""D_NECESSITY implementation — Modal Logic & Necessity

Layer: 4 (Institutional - Logic/Philosophy)
CardinalStrength: PREDICATIVE

Standards:
- Kripke semantics for modal logic
- Systems K, T, S4, S5
- Possible worlds semantics
- Accessibility relations
- Necessity vs contingency
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set, Dict, List, Callable, FrozenSet
from enum import Enum, auto
from fractions import Fraction


class ModalSystem(Enum):
    """Modal logic axiom systems."""
    K = auto()   # Basic normal modal logic
    T = auto()   # Reflexive (K + T axiom)
    S4 = auto()  # Transitive (T + 4 axiom)
    S5 = auto()  # Euclidean (S4 + 5/B axiom)


@dataclass(frozen=True)
class World:
    """Possible world in Kripke frame."""
    world_id: str
    
    # Propositions true in this world
    true_propositions: FrozenSet[str]
    
    def proposition_true(self, prop: str) -> bool:
        """Check if proposition holds in this world."""
        return prop in self.true_propositions


@dataclass
class KripkeFrame:
    """Frame with worlds and accessibility relation."""
    worlds: Set[World]
    accessibility: Dict[str, Set[str]]  # world_id -> accessible world_ids
    
    def accessible_from(self, world: World) -> Set[World]:
        """Get all worlds accessible from given world."""
        accessible_ids = self.accessibility.get(world.world_id, set())
        return {w for w in self.worlds if w.world_id in accessible_ids}
    
    def is_reflexive(self) -> bool:
        """Every world sees itself."""
        for w in self.worlds:
            if w.world_id not in self.accessibility.get(w.world_id, set()):
                return False
        return True
    
    def is_transitive(self) -> bool:
        """If wRv and vRu then wRu."""
        for w in self.worlds:
            for v_id in self.accessibility.get(w.world_id, set()):
                v = next((world for world in self.worlds if world.world_id == v_id), None)
                if v:
                    for u_id in self.accessibility.get(v_id, set()):
                        if u_id not in self.accessibility.get(w.world_id, set()):
                            return False
        return True
    
    def is_symmetric(self) -> bool:
        """If wRv then vRw."""
        for w in self.worlds:
            for v_id in self.accessibility.get(w.world_id, set()):
                if w.world_id not in self.accessibility.get(v_id, set()):
                    return False
        return True


@dataclass
class ModalFormula:
    """Modal logic formula representation."""
    formula_id: str
    
    def evaluate(self, world: World, frame: KripkeFrame) -> bool:
        """Evaluate formula at world in frame."""
        raise NotImplementedError


@dataclass
class NecessityChecker:
    """Checker for modal logic properties."""
    frames: List[KripkeFrame] = field(default_factory=list)
    
    def system_compliance(self, frame: KripkeFrame, system: ModalSystem) -> bool:
        """Check if frame satisfies modal system axioms."""
        if system == ModalSystem.K:
            return True  # K has no frame conditions
        if system == ModalSystem.T:
            return frame.is_reflexive()
        if system == ModalSystem.S4:
            return frame.is_reflexive() and frame.is_transitive()
        if system == ModalSystem.S5:
            return frame.is_reflexive() and frame.is_transitive() and frame.is_symmetric()
        return False

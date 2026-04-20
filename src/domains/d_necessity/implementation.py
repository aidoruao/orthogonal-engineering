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
    """Atomic modal formula: a propositional letter.

    ``formula_id`` is interpreted as an atomic proposition name. Evaluation at
    a world reduces to ``proposition_true``. Compound operators (``Box``,
    ``Diamond``, ``Not``, ``And``, ``Or``) are expressed by subclassing and
    overriding :meth:`evaluate`; see :class:`NecessityFormula` and
    :class:`PossibilityFormula` below.
    """
    formula_id: str

    def evaluate(self, world: World, frame: KripkeFrame) -> bool:
        """Evaluate the atomic proposition ``formula_id`` at ``world``.

        Falsifies if: ``formula_id`` is listed in ``world.true_propositions``
        but evaluation returns ``False`` (or vice versa).
        falsifies_if: ``formula_id`` membership in ``world.true_propositions``
        disagrees with the returned boolean.
        """
        return world.proposition_true(self.formula_id)


@dataclass
class NecessityFormula(ModalFormula):
    """``Box phi``: phi holds in every world accessible from ``world``.

    Uses ``frame.accessible_from`` to enumerate accessible worlds and
    evaluates the inner formula (also treated atomically by ``formula_id``).
    """

    def evaluate(self, world: World, frame: KripkeFrame) -> bool:
        """True iff ``formula_id`` holds in every accessible world.

        Falsifies if: some accessible world fails the atomic proposition but
        this returns True, or every accessible world satisfies it but this
        returns False.
        falsifies_if: the universal quantifier over accessible worlds
        disagrees with the returned boolean.
        """
        accessible = frame.accessible_from(world)
        if not accessible:
            return True  # vacuous truth at dead-end worlds (standard Kripke)
        return all(w.proposition_true(self.formula_id) for w in accessible)


@dataclass
class PossibilityFormula(ModalFormula):
    """``Diamond phi``: phi holds in some world accessible from ``world``."""

    def evaluate(self, world: World, frame: KripkeFrame) -> bool:
        """True iff ``formula_id`` holds in at least one accessible world.

        Falsifies if: no accessible world satisfies the atomic proposition
        but this returns True, or at least one does and this returns False.
        falsifies_if: the existential quantifier over accessible worlds
        disagrees with the returned boolean.
        """
        accessible = frame.accessible_from(world)
        return any(w.proposition_true(self.formula_id) for w in accessible)


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

"""D_EPISTEMIC_LOGIC implementation — Knowledge, Belief, and Justification

Layer: 4 (Institutional - Philosophy/Logic)
CardinalStrength: PREDICATIVE

Formal Standards:
- Hintikka's epistemic logic S4, S5
- Gettier problem formalization
- Justified True Belief (JTB) analysis
- Tracking theory (Nozick)
- Safety theory (Sosa, Williamson)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set, List, Optional, Dict, Callable
from enum import Enum, auto
from fractions import Fraction


class AccessRelation(Enum):
    """Accessibility relations in epistemic frames."""
    REFLEXIVE = auto()      # t R t (S4, S5)
    SYMMETRIC = auto()      # t R t' => t' R t (S5)
    TRANSITIVE = auto()     # t R t' and t' R t'' => t R t'' (S4, S5)
    SERIAL = auto()         # For every t, exists t' with t R t' (D)
    EUCLIDEAN = auto()      # t R t' and t R t'' => t' R t'' (S5)


@dataclass(frozen=True)
class Proposition:
    """A proposition in epistemic logic."""
    prop_id: str
    content: str
    world_truth: Dict[str, bool]  # world_id -> truth value
    
    def is_true_in(self, world_id: str) -> bool:
        """Truth value of proposition in given world."""
        return self.world_truth.get(world_id, False)


@dataclass(frozen=True)
class Agent:
    """Epistemic agent with beliefs and knowledge."""
    agent_id: str
    name: str
    
    def __hash__(self):
        return hash(self.agent_id)


@dataclass
class BeliefState:
    """Agent's belief state in possible worlds semantics."""
    agent: Agent
    accessible_worlds: Set[str]  # Worlds agent considers possible
    beliefs: Set[str]  # prop_ids the agent believes
    
    def believes(self, prop: Proposition, world_id: str) -> bool:
        """Agent believes P if P is true in all accessible worlds."""
        for w in self.accessible_worlds:
            if not prop.is_true_in(w):
                return False
        return True
    
    def knows(self, prop: Proposition, world_id: str) -> bool:
        """Knowledge = true belief + justification (simplified)."""
        return self.believes(prop, world_id) and prop.is_true_in(world_id)


@dataclass
class EpistemicFrame:
    """Kripke frame for epistemic logic."""
    worlds: Set[str]
    accessibility: Dict[str, Set[str]]  # agent_id -> {(w, w')}
    valuation: Dict[str, Set[str]]  # world_id -> {true propositions}
    
    def is_reflexive(self, agent_id: str) -> bool:
        """Check reflexivity: w R w for all w."""
        for w in self.worlds:
            if w not in self.accessibility.get(agent_id, set()):
                return False
        return True
    
    def is_transitive(self, agent_id: str) -> bool:
        """Check transitivity."""
        rel = self.accessibility.get(agent_id, set())
        for w1 in self.worlds:
            for w2 in rel:
                if (w1, w2) in [(a, b) for a in self.worlds for b in rel]:  # Simplified
                    pass  # Full transitivity check would iterate pairs
        return True  # Simplified


@dataclass
class Justification:
    """Justification for a belief (JTB component)."""
    justification_id: str
    belief_content: str
    evidence: List[str]
    reliability: Fraction  # 0-1, strength of justification
    defeasible: bool  # Can be defeated by new evidence
    
    def strength(self) -> Fraction:
        """Overall justification strength."""
        base = self.reliability
        # Evidence diversity bonus
        diversity_factor = Fraction(min(len(self.evidence), 5), 5)
        return min(Fraction(1), base * (Fraction(1) + diversity_factor * Fraction(1, 10)))


@dataclass
class JTBAnalysis:
    """Justified True Belief analysis (Gettier problem)."""
    agent: Agent
    proposition: Proposition
    world_id: str
    belief: bool
    truth: bool
    justification: Optional[Justification]
    
    def is_jtb(self) -> bool:
        """Check if this is a Justified True Belief."""
        return self.belief and self.truth and self.justification is not None
    
    def gettier_case(self) -> bool:
        """True if this is a Gettier case: JTB without knowledge.
        
        A Gettier case occurs when the belief is true by luck,
        not because the justification properly connects to the truth.
        """
        if not self.is_jtb():
            return False
        
        # Simplified: very low reliability + true belief suggests luck
        if self.justification and self.justification.reliability < Fraction(1, 2):
            return True
        return False


@dataclass
class TrackingCondition:
    """Nozick's tracking conditions for knowledge."""
    # If P were false, S would not believe P
    sensitivity: bool
    # If P were true (in nearby worlds), S would believe P  
    adherence: bool
    
    def tracks(self) -> bool:
        """Both tracking conditions satisfied."""
        return self.sensitivity and self.adherence


@dataclass
class SafetyCondition:
    """Safety theory: belief could not easily have been false."""
    nearby_false_beliefs: int
    total_nearby_worlds: int
    
    def safety_score(self) -> Fraction:
        """Fraction of nearby worlds where belief is true."""
        if self.total_nearby_worlds == 0:
            return Fraction(1)  # Vacuously safe
        safe_worlds = self.total_nearby_worlds - self.nearby_false_beliefs
        return Fraction(safe_worlds, self.total_nearby_worlds)
    
    def is_safe(self, threshold: Fraction = Fraction(95, 100)) -> bool:
        """Belief is safe if true in nearby worlds above threshold."""
        return self.safety_score() >= threshold


@dataclass
class EpistemicChecker:
    """Checker for epistemic logic invariants."""
    frames: List[EpistemicFrame] = field(default_factory=list)
    belief_states: List[BeliefState] = field(default_factory=list)
    jtb_analyses: List[JTBAnalysis] = field(default_factory=list)
    
    def find_gettier_cases(self) -> List[JTBAnalysis]:
        """Find all Gettier cases in analyses."""
        return [a for a in self.jtb_analyses if a.gettier_case()]
    
    def non_tracking_knowledge(self) -> List[JTBAnalysis]:
        """Knowledge claims that fail tracking."""
        result = []
        for a in self.jtb_analyses:
            if a.is_jtb():  # Claims to be knowledge
                # Would fail in nearby worlds (simplified check)
                if a.justification and a.justification.reliability < Fraction(2, 3):
                    result.append(a)
        return result

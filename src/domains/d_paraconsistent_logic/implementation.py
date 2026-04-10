"""D_PARACONSISTENT_LOGIC implementation — Inconsistency-Tolerant Logic

Layer: 4 (Institutional - Logic)
CardinalStrength: PREDICATIVE

Standards:
- LP (Logic of Paradox)
- C1-Cn systems (da Costa)
- Relevant logic
- Dialetheism
- Truth-value gluts and gaps
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional
from enum import Enum, auto
from fractions import Fraction


class TruthValue(Enum):
    """Paraconsistent truth values."""
    TRUE = auto()
    FALSE = auto()
    BOTH = auto()  # Glut: true and false
    NEITHER = auto()  # Gap: neither true nor false


@dataclass(frozen=True)
class Proposition:
    """Proposition with paraconsistent truth status."""
    prop_id: str
    content: str
    
    # Can be both true and false (glut) or neither (gap)
    truth_value: TruthValue
    
    def is_true(self) -> bool:
        """True in LP (includes BOTH)."""
        return self.truth_value in (TruthValue.TRUE, TruthValue.BOTH)
    
    def is_false(self) -> bool:
        """False in LP (includes BOTH)."""
        return self.truth_value in (TruthValue.FALSE, TruthValue.BOTH)
    
    def is_paradoxical(self) -> bool:
        """True contradiction (dialetheia)."""
        return self.truth_value == TruthValue.BOTH


@dataclass
class ParaconsistentTheory:
    """Set of propositions tolerating inconsistency."""
    theory_id: str
    propositions: Set[Proposition] = field(default_factory=set)
    
    def is_inconsistent(self) -> bool:
        """Contains contradictions (not explosive)."""
        for p in self.propositions:
            if p.is_paradoxical():
                return True
        # Check for A and not-A both asserted
        contents = {p.content for p in self.propositions if p.is_true()}
        negations = {p.content[4:] for p in self.propositions 
                     if p.content.startswith("NOT ") and p.is_true()}
        return bool(contents & negations)
    
    def is_trivial(self) -> bool:
        """Everything derivable (collapse)."""
        # In true paraconsistent systems, inconsistency != triviality
        return False  # Paraconsistent systems block explosion
    
    def explosion_blocked(self) -> bool:
        """A and not-A does not entail B for arbitrary B."""
        return True  # By definition of paraconsistent


@dataclass
class InferenceRule:
    """Paraconsistent inference (non-explosive)."""
    rule_name: str
    premises: List[str]
    conclusion: str
    valid_in_lp: bool
    valid_in_classical: bool
    
    def is_paraconsistent_valid(self) -> bool:
        """Valid in LP or other paraconsistent system."""
        return self.valid_in_lp


@dataclass
class ParaconsistentChecker:
    """Checker for paraconsistent logic properties."""
    theories: List[ParaconsistentTheory] = field(default_factory=list)
    rules: List[InferenceRule] = field(default_factory=list)
    
    def inconsistent_theories(self) -> List[ParaconsistentTheory]:
        """Theories with contradictions."""
        return [t for t in self.theories if t.is_inconsistent()]
    
    def explosion_violations(self) -> List[InferenceRule]:
        """Rules that would cause explosion."""
        return [r for r in self.rules 
                if r.valid_in_classical and not r.valid_in_lp]

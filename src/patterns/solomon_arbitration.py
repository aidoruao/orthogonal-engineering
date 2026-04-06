"""Solomon Arbitration Pattern

Biblical basis: 1 Kings 3:16-28 — Solomon's judgment between two women
claiming the same baby. The true mother's love was revealed when she
preferred to give up the child rather than see it harmed.

Application: Resolve conflicting invariants. When two invariants conflict,
the system must determine which takes precedence based on which serves
the deeper value (e.g., protecting the vulnerable).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum, auto


class Precedence(Enum):
    """Precedence levels for invariant resolution."""
    HIGHEST = auto()  # Always wins (e.g., vulnerability protection)
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    LOWEST = auto()   # Usually loses


@dataclass
class Invariant:
    """An invariant with its precedence."""
    invariant_id: str
    statement: str
    precedence: Precedence
    protects_vulnerable: bool = False
    
    def __lt__(self, other: "Invariant") -> bool:
        """Compare invariants by precedence."""
        precedence_order = [
            Precedence.LOWEST,
            Precedence.LOW,
            Precedence.MEDIUM,
            Precedence.HIGH,
            Precedence.HIGHEST,
        ]
        return precedence_order.index(self.precedence) < precedence_order.index(other.precedence)


@dataclass
class Conflict:
    """A conflict between two invariants."""
    conflict_id: str
    invariant_a: Invariant
    invariant_b: Invariant
    context: Dict[str, Any]
    resolved: bool = False
    winner: Optional[Invariant] = None
    reasoning: str = ""


class SolomonArbitration:
    """
    Implements the Solomon arbitration pattern.
    
    When invariants conflict, resolve them based on:
      1. Precedence level (HIGHEST wins)
      2. Vulnerability protection (protects_vulnerable wins)
      3. Mercy weighting (restoration over punishment)
    
    Attributes:
        conflicts: List of conflicts being tracked
        resolution_history: History of resolved conflicts
    """
    
    def __init__(self):
        self.conflicts: List[Conflict] = []
        self.resolution_history: List[Conflict] = []
    
    def register_conflict(
        self,
        conflict_id: str,
        invariant_a: Invariant,
        invariant_b: Invariant,
        context: Dict[str, Any],
    ) -> Conflict:
        """Register a conflict between two invariants."""
        conflict = Conflict(
            conflict_id=conflict_id,
            invariant_a=invariant_a,
            invariant_b=invariant_b,
            context=context,
        )
        self.conflicts.append(conflict)
        return conflict
    
    def arbitrate(self, conflict_id: str) -> Optional[Invariant]:
        """
        Arbitrate a conflict and determine the winner.
        
        Returns:
            The winning invariant, or None if cannot decide
        """
        conflict = next((c for c in self.conflicts if c.conflict_id == conflict_id), None)
        if conflict is None:
            return None
        
        a, b = conflict.invariant_a, conflict.invariant_b
        
        # Rule 1: Compare precedence
        if a.precedence != b.precedence:
            winner = a if a.precedence.value > b.precedence.value else b
            loser = b if winner == a else a
            reasoning = f"{winner.invariant_id} has higher precedence ({winner.precedence.name})"
        
        # Rule 2: Vulnerability protection wins
        elif a.protects_vulnerable and not b.protects_vulnerable:
            winner, loser = a, b
            reasoning = f"{winner.invariant_id} protects vulnerable parties"
        elif b.protects_vulnerable and not a.protects_vulnerable:
            winner, loser = b, a
            reasoning = f"{winner.invariant_id} protects vulnerable parties"
        
        # Rule 3: Cannot decide
        else:
            return None
        
        # Record resolution
        conflict.resolved = True
        conflict.winner = winner
        conflict.reasoning = reasoning
        self.resolution_history.append(conflict)
        self.conflicts.remove(conflict)
        
        return winner
    
    def get_resolution_summary(self) -> Dict[str, Any]:
        """Get summary of conflict resolutions."""
        return {
            "pending_conflicts": len(self.conflicts),
            "resolved_conflicts": len(self.resolution_history),
            "by_invariant": self._count_by_invariant(),
        }
    
    def _count_by_invariant(self) -> Dict[str, int]:
        """Count wins by invariant."""
        counts = {}
        for conflict in self.resolution_history:
            if conflict.winner:
                winner_id = conflict.winner.invariant_id
                counts[winner_id] = counts.get(winner_id, 0) + 1
        return counts
    
    def get_precedence_rules(self) -> List[str]:
        """Get the precedence rules used for arbitration."""
        return [
            "1. Higher precedence level wins",
            "2. Invariant protecting vulnerable parties wins",
            "3. INV-YS-004 (Mercy Weighting) over punishment",
            "4. If tied, escalate to human decision",
        ]

"""Pattern: Mercy Weighting

Implements INV-YS-004: Optimization is weighted toward restoration,
not punishment. argmin minimizes distance to constraint manifold,
not maximizes distance from violation.

Biblical: Luke 15 — The prodigal son is welcomed, not punished further.
The objective is restoration to the father's house, not maximization
of punishment for the son's wastefulness.

Used by: D_CRIMINAL_LAW, D_USE_OF_FORCE, D_RESTORATIVE_JUSTICE,
D_FAMILY_LAW, D_CHILD_WELFARE
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Callable
from fractions import Fraction
import math


@dataclass
class Remedy:
    """A proposed remedy for a violation."""
    remedy_id: str
    description: str
    cost_to_subject: Fraction  # Lower is better (less harm)
    restoration_potential: Fraction  # Higher is better (more restoration)
    
    @property
    def mercy_score(self) -> Fraction:
        """
        Calculate mercy score: high restoration, low cost.
        Score = restoration_potential / (1 + cost_to_subject)
        """
        denominator = Fraction(1) + self.cost_to_subject
        if denominator == 0:
            return Fraction(0)
        return self.restoration_potential / denominator


class MercyWeighting:
    """
    Implements mercy-weighted optimization.
    
    When multiple remedies are available for a violation,
    select the one that maximizes mercy (restoration / cost).
    
    Attributes:
        remedies: List of available remedies
    """
    
    def __init__(self):
        self.remedies: List[Remedy] = []
    
    def add_remedy(self, remedy: Remedy) -> None:
        """Add a remedy option."""
        self.remedies.append(remedy)
    
    def select_optimal_remedy(self) -> Remedy:
        """
        Select the remedy with highest mercy score.
        
        Returns:
            The optimal remedy
        
        Raises:
            ValueError: If no remedies available
        """
        if not self.remedies:
            raise ValueError("No remedies available")
        
        return max(self.remedies, key=lambda r: r.mercy_score)
    
    def compare_remedies(self, remedy_a: Remedy, remedy_b: Remedy) -> Remedy:
        """Compare two remedies and return the more merciful one."""
        return remedy_a if remedy_a.mercy_score >= remedy_b.mercy_score else remedy_b
    
    def is_punitive(self, remedy: Remedy, threshold: Fraction = Fraction(1, 2)) -> bool:
        """
        Check if a remedy is punitive (high cost, low restoration).
        
        Args:
            remedy: The remedy to check
            threshold: Mercy score below which remedy is considered punitive
        
        Returns:
            True if remedy is punitive
        """
        return remedy.mercy_score < threshold
    
    def get_remedy_ranking(self) -> List[tuple]:
        """
        Get all remedies ranked by mercy score.
        
        Returns:
            List of (remedy, mercy_score) tuples, sorted descending
        """
        ranked = [(r, r.mercy_score) for r in self.remedies]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
